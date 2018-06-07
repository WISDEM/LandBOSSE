"""
ErectionCost.py
Created by Annika Eberle and Owen Roberts on Mar. 16, 2018

Calculates the costs for erecting the tower and rotor nacelle assembly for land-based wind projects
(items in brackets are not yet implemented)

[Get terrain complexity]
[Get site complexity]
Get number of turbines
Get duration of construction
Get rate of deliveries
Get daily hours of operation
Get turbine rating
Get component specifications
[Get crane availability]

Get price data
    Get labor mobilization_prices by crew type
    Get labor prices by crew type
    Get equipment mobilization prices by equipment type
    Get fuel prices
    Get equipment prices by equipment type

Calculate operational time for lifting components

Estimate potential time delays due to weather

Calculate required labor and equip for erection (see equip_labor_by_type method below)
    Calculate number of workers by crew type
    Calculate man hours by crew type
    Calculate number of equipment by equip type
    Calculate equipment hours by equip type

Calculate erection costs by type (see methods below)
    Calculate mobilization costs as function of number of workers by crew type, number of equipment by equipment type, labor_mobilization_prices, and equip_mobilization_prices
    Calculate labor costs as function of man_hours and labor prices by crew type
    Calculate fuel costs as function of equipment hours by equipment type and fuel prices by equipment type
    Calculate equipment costs as function of equipment hours by equipment type and equipment prices by equipment type

Sum erection costs over all types to get total costs

Find the least cost option

Return total erection costs

"""

import pandas as pd
import numpy as np
from scipy import sqrt
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import WeatherDelay as WD

# constants
km_per_m = 0.001
hr_per_min = 1/60
m_per_ft = 0.3048


def calculate_erection_operation_time(project_data, construct_duration, operational_construction_time):
    """
    Calculates operation time required for each type of equipment included in project data.

    :param project_data: dictionary of data frames for each of the csv files loaded for the project
    :param construct_duration: duration of construction (in months)
    :return: list of possible cranes that could be used to erect tower and turbine
    """
    erection_construction_time = 1/3 * construct_duration

    print('Calculating operation time')
    # group project data by project ID
    project = project_data['project'].where(project_data['project']['Project ID'] == 'Conventional')
    project = project.dropna(thresh=1)
    # project_grouped = data_csv['project'].groupby(['Project ID', 'Turbine rating MW', 'Hub height m'])

    # for components in component list determine if base or topping
    project_data['components']['Operation'] = project_data['components']['Lift height m'] > (float(project['Hub height m'] * project['Breakpoint between base and topping (percent)']))
    boolean_dictionary = {True: 'Top', False: 'Base'}
    project_data['components']['Operation'] = project_data['components']['Operation'].map(boolean_dictionary)

    # create groups for operations
    top_v_base = project_data['components'].groupby(['Operation'])

    # group crane data by boom system and crane name to get distinct cranes
    crane_grouped = project_data['crane_specs'].groupby(['Equipment name', 'Crane name', 'Boom system', 'Crane capacity tonne'])

    crane_poly = pd.DataFrame(columns=['Equipment name', 'Crane name', 'Boom system', 'Crane capacity tonne', 'Crane poly'])
    for name, crane in crane_grouped:
        crane = crane.reset_index(drop=True)
        x = crane['Max capacity tonne']
        y = crane['Hub height m']
        wind_speed = min(crane['Max wind speed m per s'])
        hoist_speed = min(crane['Hoist speed m per min'])
        travel_speed = min(crane['Speed of travel km per hr'])
        setup_time = max(crane['Setup time hr'])
        crew_type = crane['Crew type ID'][0]  # todo: fix this so it's not a hack... need to rethink data structure - right now just picking first crew type - this is correct because same for all crane/boom combinations but we should come up with a better way to do it
        polygon = Polygon([(0, 0), (0, max(y)), (min(x), max(y)), (max(x), min(y)), (max(x), 0)])
        df = pd.DataFrame([[name[0],
                            name[1],
                            name[2],
                            name[3],
                            wind_speed,
                            setup_time,
                            hoist_speed,
                            travel_speed,
                            crew_type,
                            polygon]],
                            columns=['Equipment name', 'Crane name', 'Boom system', 'Crane capacity tonne',
                                     'Max wind speed m per s', 'Setup time hr',
                                     'Hoist speed m per min', 'Speed of travel km per hr',
                                     'Crew type ID', 'Crane poly'])
        crane_poly = crane_poly.append(df)

    # loop through operation type (topping vs. base)
    rownew = pd.Series()
    component_max_speed = pd.DataFrame()
    crane_poly_new = crane_poly
    for name_operation, component_group in top_v_base:
        # calculate polygon for crane capacity and check if component can be lifted by each crane without wind loading
        bool_list = list()
        for idx, crane in crane_poly.iterrows():
            polygon = crane['Crane poly']

            for component in component_group['Component']:
                # get weight and height of component in each component group
                component_only = component_group.where(component_group['Component'] == component).dropna(thresh=1)
                point = Point(component_only['Weight tonne'], component_only['Lift height m'])
                crane['Lift boolean {component}'.format(component=component)] = polygon.contains(point)

            rownew = rownew.append(crane)

            for component in component_group['Component']:
                if crane['Lift boolean {component}'.format(component=component)] is False:
                    crane_bool = False
                else:
                    crane_bool = True

            bool_list.append(crane_bool)

            # calculate max permissible wind speed
            # equation for calculating permissible wind speed:
            # vmax = max_TAB * sqrt(1.2 * mh / AW), where
            # mh = hoist load
            # AW = area exposed to wind = surface area * coeff drag
            # 1.2 = constant in m^2 / t
            # vmax_TAB = maximum load speed per load chart
            # source: pg. 33 of Liebherr

            mh = component_group['Weight tonne']
            AW = component_group['Surface area sq m'] * component_group['Coeff drag']
            vmax_TAB = crane['Max wind speed m per s']
            vmax_calc = vmax_TAB * sqrt(1.2 * mh / AW)

            # if vmax_calc is less than vmax_TAB then vmax_calc, otherwise vmax_TAB (based on pg. 33 of Liebherr)
            # todo: check vmax - should it be set to calculated value rather than vmax_TAB if greater?
            component_group_new = pd.DataFrame(component_group,
                                               columns=list(component_group.columns.values) + ['vmax',
                                                                                               'Crane name',
                                                                                               'Boom system',
                                                                                               'crane_bool'])
            component_group_new['vmax'] = list((min(vmax_TAB, x) for x in vmax_calc))
            component_group_new['Crane name'] = crane['Crane name']
            component_group_new['Boom system'] = crane['Boom system']
            component_group_new['crane_bool'] = crane_bool

            component_max_speed = component_max_speed.append(component_group_new)

        crane_poly_new['Crane bool {operation}'.format(operation=name_operation)] = list(bool_list)

    crane_poly = crane_poly_new

    # join crane polygon to crane specs
    crane_component = pd.merge(crane_poly, component_max_speed, on=['Crane name', 'Boom system'])

    # select only cranes that could lift the component
    possible_cranes = crane_component.where(crane_component['crane_bool'] == True).dropna(thresh=1).reset_index(drop=True)

    # calculate travel time per cycle
    turbine_spacing = float(project['Turbine spacing (times rotor diameter)'] * project['Rotor diameter m'] * km_per_m)
    turbine_num = float(project['Number of turbines'])
    possible_cranes['Travel time hr'] = turbine_spacing / possible_cranes['Speed of travel km per hr'] * turbine_num

    # calculate erection time
    possible_cranes['Operation time hr'] = ((possible_cranes['Lift height m'] / possible_cranes['Hoist speed m per min'] * hr_per_min)
                                            + (possible_cranes['Cycle time installation hrs'])
                                            ) * turbine_num

    # store setup time
    possible_cranes['Setup time hr'] = possible_cranes['Setup time hr'] * turbine_num

    erection_time = possible_cranes.groupby(['Crane name', 'Equipment name', 'Crane capacity tonne', 'Crew type ID',
                                             'Boom system', 'Operation'])['Operation time hr'].sum()
    travel_time = possible_cranes.groupby(['Crane name', 'Equipment name', 'Crane capacity tonne', 'Crew type ID',
                                           'Boom system', 'Operation'])['Travel time hr'].max()
    setup_time = possible_cranes.groupby(['Crane name', 'Equipment name', 'Crane capacity tonne', 'Crew type ID',
                                          'Boom system', 'Operation'])['Setup time hr'].max()
    rental_time_without_weather = erection_time + travel_time + setup_time

    operation_time = rental_time_without_weather.reset_index()
    operation_time = operation_time.rename(columns={0: 'Operation time all turbines hrs'})
    operation_time['Operational construct days'] = (operation_time['Operation time all turbines hrs'] /
                                                    operational_construction_time)

    # if more than one crew needed to complete within construction duration then assume that all construction happens
    # within that window and use that timeframe for weather delays; if not, use the number of days calculated
    operation_time['time_construct_bool'] = (operation_time['Operational construct days'] >
                                             erection_construction_time * 30)
    boolean_dictionary = {True: erection_construction_time * 30, False: np.NAN}
    operation_time['time_construct_bool'] = operation_time['time_construct_bool'].map(boolean_dictionary)
    operation_time['Time construct days'] = operation_time[['time_construct_bool', 'Operational construct days']].min(axis=1)

    return possible_cranes, operation_time

def calculate_offload_operation_time(project_data, construct_duration, operational_construction_time,
                                      rate_of_deliveries):
    """

    :param project_data:
    :param construct_duration:
    :param operational_construction_time:
    :return:
    """

    erection_construction_time = 1 / 3 * construct_duration

    print('Calculating offload operation time')
    # group project data by project ID
    project = project_data['project'].where(project_data['project']['Project ID'] == 'Conventional')
    project = project.dropna(thresh=1)
    # project_grouped = data_csv['project'].groupby(['Project ID', 'Turbine rating MW', 'Hub height m'])

    offload_cranes = project_data['crane_specs'].where(project_data['crane_specs']['Equipment name'] == 'Offload crane')


    # group crane data by boom system and crane name to get distinct cranes
    crane_grouped = offload_cranes.groupby(
        ['Equipment name', 'Crane name', 'Boom system', 'Crane capacity tonne'])

    crane_poly = pd.DataFrame(
        columns=['Equipment name', 'Crane name', 'Boom system', 'Crane capacity tonne', 'Crane poly'])
    for name, crane in crane_grouped:
        crane = crane.reset_index(drop=True)
        x = crane['Max capacity tonne']
        y = crane['Hub height m']
        wind_speed = min(crane['Max wind speed m per s'])
        hoist_speed = min(crane['Hoist speed m per min'])
        travel_speed = min(crane['Speed of travel km per hr'])
        setup_time = max(crane['Setup time hr'])
        crew_type = crane['Crew type ID'][
            0]  # todo: fix this so it's not a hack... need to rethink data structure - right now just picking first crew type - this is correct because same for all crane/boom combinations but we should come up with a better way to do it
        polygon = Polygon([(0, 0), (0, max(y)), (min(x), max(y)), (max(x), min(y)), (max(x), 0)])
        df = pd.DataFrame([[name[0],
                            name[1],
                            name[2],
                            name[3],
                            wind_speed,
                            setup_time,
                            hoist_speed,
                            travel_speed,
                            crew_type,
                            polygon]],
                          columns=['Equipment name', 'Crane name', 'Boom system', 'Crane capacity tonne',
                                   'Max wind speed m per s', 'Setup time hr',
                                   'Hoist speed m per min', 'Speed of travel km per hr',
                                   'Crew type ID', 'Crane poly'])
        crane_poly = crane_poly.append(df)


    rownew = pd.Series()
    component_max_speed = pd.DataFrame()
    crane_poly_new = crane_poly

    component_group = project_data['components']

    bool_list = list()
    for idx, crane in crane_poly.iterrows():
        polygon = crane['Crane poly']

        for component in component_group['Component']:
            # get weight and height of component in each component group
            component_only = component_group.where(component_group['Component'] == component).dropna(thresh=1)
            point = Point(component_only['Weight tonne'], component_only['Offload hook height m'])
            crane['Lift boolean {component}'.format(component=component)] = polygon.contains(point)

        rownew = rownew.append(crane)

        for component in component_group['Component']:
            if crane['Lift boolean {component}'.format(component=component)] is False:
                crane_bool = False
            else:
                crane_bool = True

        bool_list.append(crane_bool)

        # calculate max permissible wind speed
        # equation for calculating permissible wind speed:
        # vmax = max_TAB * sqrt(1.2 * mh / AW), where
        # mh = hoist load
        # AW = area exposed to wind = surface area * coeff drag
        # 1.2 = constant in m^2 / t
        # vmax_TAB = maximum load speed per load chart
        # source: pg. 33 of Liebherr

        mh = component_group['Weight tonne']
        AW = component_group['Surface area sq m'] * component_group['Coeff drag']
        vmax_TAB = crane['Max wind speed m per s']
        vmax_calc = vmax_TAB * sqrt(1.2 * mh / AW)

        # if vmax_calc is less than vmax_TAB then vmax_calc, otherwise vmax_TAB (based on pg. 33 of Liebherr)
        # todo: check vmax - should it be set to calculated value rather than vmax_TAB if greater?
        component_group_new = pd.DataFrame(component_group,
                                           columns=list(component_group.columns.values) + ['vmax',
                                                                                           'Crane name',
                                                                                           'Boom system',
                                                                                           'crane_bool'])
        component_group_new['vmax'] = list((min(vmax_TAB, x) for x in vmax_calc))
        component_group_new['Crane name'] = crane['Crane name']
        component_group_new['Boom system'] = crane['Boom system']
        component_group_new['crane_bool'] = crane_bool

        component_max_speed = component_max_speed.append(component_group_new)

    crane_poly_new['Crane bool {operation}'.format(operation='offload')] = list(bool_list)

    crane_poly = crane_poly_new

    # join crane polygon to crane specs
    crane_component = pd.merge(crane_poly, component_max_speed, on=['Crane name', 'Boom system'])

    # select only cranes that could lift the component
    possible_cranes = crane_component.where(crane_component['crane_bool'] == True).dropna(thresh=1).reset_index(
        drop=True)

    # calculate travel time per cycle
    turbine_spacing = float(project['Turbine spacing (times rotor diameter)'] * project['Rotor diameter m'] * km_per_m)
    turbine_num = float(project['Number of turbines'])
    possible_cranes['Travel time hr'] = turbine_spacing / possible_cranes['Speed of travel km per hr'] * turbine_num

    # calculate erection time
    possible_cranes['Operation time hr'] = ((possible_cranes['Lift height m'] / possible_cranes[
        'Hoist speed m per min'] * hr_per_min)
                                            + (possible_cranes['Offload cycle time hrs'])
                                            ) * turbine_num

    # store setup time
    possible_cranes['Setup time hr'] = possible_cranes['Setup time hr'] * turbine_num

    erection_time = possible_cranes.groupby(['Crane name', 'Equipment name', 'Crane capacity tonne', 'Crew type ID',
                                             'Boom system'])['Operation time hr'].sum()
    travel_time = possible_cranes.groupby(['Crane name', 'Equipment name', 'Crane capacity tonne', 'Crew type ID',
                                           'Boom system'])['Travel time hr'].max()
    setup_time = possible_cranes.groupby(['Crane name', 'Equipment name', 'Crane capacity tonne', 'Crew type ID',
                                          'Boom system'])['Setup time hr'].max()
    rental_time_without_weather = erection_time + travel_time + setup_time

    operation_time = rental_time_without_weather.reset_index()
    operation_time = operation_time.rename(columns={0: 'Operation time all turbines hrs'})
    operation_time['Operational construct days'] = (operation_time['Operation time all turbines hrs'] /
                                                    operational_construction_time)

    # if more than one crew needed to complete within construction duration then assume that all construction happens
    # within that window and use that timeframe for weather delays; if not, use the number of days calculated
    operation_time['time_construct_bool'] = (turbine_num / operation_time['Operational construct days'] * 6
                                             > float(rate_of_deliveries))
    boolean_dictionary = {True: (float(turbine_num) / (float(rate_of_deliveries) / 6)), False: np.NAN}
    operation_time['time_construct_bool'] = operation_time['time_construct_bool'].map(boolean_dictionary)
    operation_time['Time construct days'] = operation_time[['time_construct_bool', 'Operational construct days']].max(
        axis=1)

    possible_cranes['Operation'] = 'Offload'
    operation_time['Operation'] = 'Offload'

    return possible_cranes, operation_time


def calculate_wind_delay_by_component(crane_specs, weather_window):
    """
    Calculates wind delay for each component in the project.

    :param crane_specs: data frame with crane specifications and component properties
    :param weather_window: filtered weather window containing data specific to season and time of construction
    :return: data frame with crane specifications and component properties joined with wind delays for each case
    """

    # calculate wind delay for each component and crane combination
    crane_specs = crane_specs.reset_index()
    crane_specs['Wind delay percent'] = np.nan
    print('Calculating wind delay')
    for i in range(0, len(crane_specs.index)):
        # print for debugging
        # print("Calculating weather delay for {operation}, {component},
        #                                               {crane} {boom}".format(operation=crane_specs['Operation'][i],
        #                                                                      component=crane_specs['Component'][i],
        #                                                                      crane=crane_specs['Crane name'][i],
        #                                                                      boom=crane_specs['Boom system'][i]))

        # assume we don't know when the operation occurs
        operation_window = len(weather_window.index)  # operation window = entire construction weather window
        operation_start = 0  # start time is at beginning of construction weather window

        # extract critical wind speed
        critical_wind_operation = crane_specs['vmax'][i]

        # compute weather delay
        wind_delay = WD.calculate_wind_delay(weather_window=weather_window,
                                             start_delay=operation_start,
                                             mission_time=operation_window,
                                             critical_wind_speed=critical_wind_operation)
        wind_delay = pd.DataFrame(wind_delay)

        # if greater than 4 hour delay, then shut down for full day (10 hours)
        wind_delay[(wind_delay > 4)] = 10
        wind_delay_time = float(wind_delay.sum())

        # store weather delay for operation, component, crane, and boom combination
        crane_specs.loc[i, 'Wind delay percent'] = wind_delay_time / len(weather_window)

    return crane_specs


def aggregate_erection_costs(crane_data, operation_time, project_data, hour_day, construct_time, overtime_multiplier,
                             project_size):
    """
    Aggregates labor, equipment, mobilization and fuel costs for erection.

    :param crane_data: data frame with crane specifications and component properties joined with wind delays for each case
    :param project_data: dictionary of data frames for each of the csv files loaded for the project
    :return: two data frames that have aggregated labor, equipment, mobilization, and fuel costs for
             1) utilizing the same crane for base and topping and
             2) utilizing separate cranes for base and topping
    """

    average_wind_delay = crane_data.groupby(['Crane name', 'Boom system', 'Operation'])['Wind delay percent'].mean().reset_index()
    join_wind_operation = pd.merge(operation_time, average_wind_delay, on=['Crane name', 'Boom system', 'Operation'])

    join_wind_operation['Total time per op with weather'] = join_wind_operation['Operation time all turbines hrs'] * (1 + join_wind_operation['Wind delay percent'])

    possible_crane_cost = pd.merge(join_wind_operation, project_data['equip_price'], on=['Equipment name', 'Crane capacity tonne'])

    possible_crane_cost['Equipment rental cost USD'] = possible_crane_cost['Total time per op with weather'] * possible_crane_cost['Equipment price USD per hour']

    # merge crew type and crew cost data
    crew_cost = pd.merge(project_data['crew'], project_data['crew_price'], on=['Labor type ID'])

    # increase management crews by project size
    crew_cost.loc[crew_cost['Crew name'] == "Management - project size", 'Number of workers'] = \
        round(crew_cost[crew_cost['Crew name'] == "Management - project size"]['Number of workers'] *
              np.ceil(project_size / 100))

    # increase management crews by rate of construction (scale if greater than 10/wk)
    rate_construction = float(project_data['project']['Rate of deliveries (turbines per week)'].dropna())

    crew_cost.loc[crew_cost['Crew name'] == "Management - rate construction", 'Number of workers'] = \
        round(crew_cost[crew_cost['Crew name'] == "Management - rate construction"]['Number of workers'] *
              np.ceil(rate_construction / 10))

    crew_cost.loc[crew_cost['Crew name'] == "Mechanical completion", 'Number of workers'] = \
        round(crew_cost[crew_cost['Crew name'] == "Mechanical completion"]['Number of workers'] *
              np.ceil(rate_construction / 10))

    # calculate crew costs
    crew_cost['Hourly rate for all workers'] = (crew_cost['Hourly rate USD per hour'] * crew_cost['Number of workers']) * overtime_multiplier
    crew_cost['Per diem all workers'] = crew_cost['Per diem USD per day'] * crew_cost['Number of workers']

    # group crew costs by crew type and operation
    crew_cost_grouped = crew_cost.groupby(['Crew type ID', 'Operation', 'Crew type']).sum().reset_index()

    # merge crane data with grouped crew costs
    possible_crane_cost = pd.merge(possible_crane_cost, crew_cost_grouped, on=['Crew type ID', 'Operation'])

    # get total rate for management crew
    management_rates = crew_cost_grouped[(crew_cost_grouped['Operation'] == 'Management') |
                                         (crew_cost_grouped['Operation'] == 'Mechanical completion')].sum()
    per_diem_management = management_rates['Per diem all workers']
    hourly_management = management_rates['Hourly rate for all workers']

    # calculate labor costs
    labor_day_operation = round(possible_crane_cost['Total time per op with weather'] / hour_day[construct_time])
    possible_crane_cost['Labor cost USD'] = (possible_crane_cost['Total time per op with weather'] *
                                             (possible_crane_cost['Hourly rate for all workers'] + hourly_management) +
                                             labor_day_operation *
                                             (crew_cost['Per diem all workers'] + per_diem_management))

    # calculate fuel costs
    project = project_data['project'].where(project_data['project']['Project ID'] == 'Conventional')
    project = project.dropna(thresh=1)
    possible_crane_cost['Fuel cost USD'] = possible_crane_cost['Fuel consumption gal per day'] * float(project['Fuel cost USD per gal']) * labor_day_operation

    # calculate costs if top and base cranes are the same
    base_cranes = possible_crane_cost[possible_crane_cost['Operation'] == 'Base']
    crane_topbase_bool = possible_crane_cost['Crane name'].isin(base_cranes['Crane name'])
    boom_topbase_bool = possible_crane_cost['Boom system'].isin(base_cranes['Boom system'])
    possible_crane_topbase = possible_crane_cost[boom_topbase_bool & crane_topbase_bool]
    possible_crane_topbase_sum = possible_crane_topbase.groupby(['Crane name',
                                                                 'Boom system'])['Labor cost USD',
                                                                                 'Equipment rental cost USD',
                                                                                 'Fuel cost USD'].sum().reset_index()

    #possible_crane_topbase = possible_crane_cost.where(possible_crane_cost['Crane bool Base'] == possible_crane_cost['Crane bool Top']).dropna()
    #possible_crane_topbase_sum = possible_crane_topbase.groupby(['Crane name', 'Boom system'])['Labor cost USD', 'Equipment rental cost USD', 'Fuel cost USD'].sum().reset_index() # must group together because can't use separate cranes in this case

    # group crane spec data for mobilization
    mobilization_costs = project_data['crane_specs'].groupby(['Crane name', 'Boom system'])['Mobilization cost USD'].max().reset_index()

    # join top and base crane data with mobilization data
    topbase_same_crane_cost = pd.merge(possible_crane_topbase_sum, mobilization_costs, on=['Crane name', 'Boom system'])

    # compute total project cost for erection
    topbase_same_crane_cost['Total cost USD'] = topbase_same_crane_cost['Labor cost USD'] + \
                                                topbase_same_crane_cost['Equipment rental cost USD'] + \
                                                topbase_same_crane_cost['Fuel cost USD'] + \
                                                topbase_same_crane_cost['Mobilization cost USD'] * 2  # for mobilization and demobilizaton


    # calculate costs if top and base use separate cranes
    separate_topbase = possible_crane_cost.groupby(['Operation', 'Crane name', 'Boom system'])['Labor cost USD', 'Equipment rental cost USD', 'Fuel cost USD'].sum().reset_index()

    # join mobilization data to separate top base crane costs
    separate_topbase_crane_cost = pd.merge(separate_topbase, mobilization_costs, on=['Crane name', 'Boom system'])

    # compute total project cost for erection
    separate_topbase_crane_cost['Total cost USD'] = separate_topbase_crane_cost['Labor cost USD'] + \
                                                    separate_topbase_crane_cost['Equipment rental cost USD'] + \
                                                    separate_topbase_crane_cost['Fuel cost USD'] + \
                                                    separate_topbase_crane_cost['Mobilization cost USD'] * 2  # for mobilization and demobilizaton

    return separate_topbase_crane_cost, topbase_same_crane_cost


def find_minimum_cost_cranes(separate_basetop, same_basetop, allow_same_flag):
    """
    Finds the minimum cost crane(s) based on the aggregated labor, equipment, mobilization and fuel costs for erection.

    :param separate_basetop: data frame with aggregated labor, equipment, mobilization, and fuel costs for utilizing
                             separate cranes for base and topping
    :param same_basetop: data frame with aggregated labor, equipment, mobilization, and fuel costs for utilizing the
                         same crane for base and topping
    :param allow_same_flag: flag to indicate whether choosing same base and topping crane is allowed
    :return: data frame with the lowest cost crane option for erection
    """
    total_separate_cost = pd.DataFrame()
    for operation in separate_basetop['Operation'].unique():
        # find minimum cost option for separate base and topping cranes
        min_val = min(separate_basetop['Total cost USD'].where(separate_basetop['Operation'] == operation).dropna())

        # find the crane that corresponds to the minimum cost for each operation
        crane = separate_basetop[separate_basetop['Total cost USD'] == min_val]
        cost = crane.groupby('Operation').min()
        total_separate_cost = total_separate_cost.append(cost)

    # reset index for separate crane costs
    total_separate_cost = total_separate_cost.reset_index()

    # sum costs for separate cranes to get total for all cranes
    cost_chosen_separate = total_separate_cost['Total cost USD'].sum()

    if allow_same_flag is True:
        # get the minimum cost for using the same crane for all operations
        cost_chosen_same = min(same_basetop['Total cost USD'])

        # check if separate or same crane option is cheaper and choose crane cost
        if cost_chosen_separate < cost_chosen_same:
            cost_chosen = total_separate_cost.groupby(by="Boom system").sum()
        else:
            cost_chosen = same_basetop.where(same_basetop['Total cost USD'] == cost_chosen_same).dropna()
    else:
        cost_chosen = total_separate_cost.groupby(by="Boom system").sum()

    print(total_separate_cost)

    return cost_chosen


def calculate_costs(project_data, hour_day, time_construct, weather_window, construction_time, rate_of_deliveries,
                    overtime_multiplier, project_size):
    """
    Calculates BOS costs for erection including selecting cranes that can lift components, incorporating wind delays,
    and finding the least cost crane options for erection.

    :param project_data: dictionary of data frames for each of the csv files loaded for the project
    :param hour_day: dictionary of hours for each type of operational time (e.g., normal vs. long hours)
    :param time_construct: string that describes operational time (e.g., normal vs. long hours)
    :param weather_window: window of weather data for project of interest
    :param construction_time: time allowed for construction (in months)
    :param rate_of_deliveries: rate of deliveries (number of turbines per week)
     :return:
    """
    [crane_specs, operation_time] = calculate_erection_operation_time(project_data=project_data,
                                                                      construct_duration=construction_time,
                                                                      operational_construction_time=hour_day[time_construct])

    [offload_specs, offload_time] = calculate_offload_operation_time(project_data=project_data,
                                                                     construct_duration=construction_time,
                                                                     operational_construction_time=hour_day[time_construct],
                                                                     rate_of_deliveries=rate_of_deliveries)

    # append data for offloading
    crane_specs = crane_specs.append(offload_specs)
    operation_time = operation_time.append(offload_time)

    cranes_wind_delay = calculate_wind_delay_by_component(crane_specs=crane_specs,
                                                          weather_window=weather_window)

    [separate_basetop, same_basetop] = aggregate_erection_costs(crane_data=cranes_wind_delay,
                                                                operation_time=operation_time,
                                                                project_data=project_data,
                                                                hour_day=hour_day,
                                                                construct_time=time_construct,
                                                                overtime_multiplier=overtime_multiplier,
                                                                project_size=project_size)

    erection_cost = find_minimum_cost_cranes(separate_basetop=separate_basetop,
                                             same_basetop=same_basetop,
                                             allow_same_flag=False)

    return erection_cost


if __name__ == "__main__":
    crane_specs_project = calculate_erection_operation_time(project_data=data_csv)

    weather_window_project = WD.create_weather_window(weather_data=data_csv['weather'],
                                                      season_id=season_dict,
                                                      season_construct=['spring', 'summer'],
                                                      time_construct='normal')

    possible_cranes = calculate_wind_delay_by_component(crane_specs=crane_specs_project,
                                                        weather_window=weather_window_project)

    [separate_basetop_cranes, same_basetop_cranes] = aggregate_erection_costs(crane_data=possible_cranes,
                                                                              project_data=data_csv)

    crane_cost = find_minimum_cost_cranes(separate_basetop=separate_basetop_cranes, same_basetop=same_basetop_cranes)

    print(crane_cost[['Operation', 'Crane name', 'Boom system']])

# OTHER NOTES ABOUT WEATHER DELAYS

# fit weibull to wind speed

# WILL NEED TO MODIFY wind speed distribution for period of time of interest (need to modify to use day only and pick only season of interest)
# could do weibull shapes by factor by month

# increases the time of construction by % above vmax
# ex) exceeds vmax 20% of time, then operation time = 1.2 * no weather operation time

# MIGHT WANT TO MODIFY LATER to consider frequency of gust during operation
# if gust exceeds vmax,
# if one gust above vmax then shutdown for 1 hr
# if gust repeated then assume

# MIGHT WANT TO ADD LATER
# these time adders are only for short-term delays due to rain
# also have other delays (severe weather)
# not accounting for these now