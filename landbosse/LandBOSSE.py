"""
BOSModel.py
Created by Annika Eberle and Owen Roberts on Feb. 28, 2018

Calculates the following balance of system costs for land-based wind projects:

- Development (currently input by the user)
- Management
- Roads
- Foundations
- Erection
- Collection system
- Transmission and interconnection
"""

import WeatherDelay as WD
import ErectionCost
import ManagementCost
import FoundationCost
import RoadsCost
from itertools import product
import pandas as pd
import numpy as np

# constants
kilowatt_per_megawatt = 1000


class Project(object):
    def __init__(self, project_value, num_turbines, turbine_rating_kilowatt, construction_time_months):
        # Set input variables (project_value, builder_size, num_turbines, turbine_rating_kilowatt, region)
        self.project_value = project_value  # set project value
        self.num_turbines = num_turbines  # set number of turbines
        self.turbine_rating = turbine_rating_kilowatt  # set turbine rating in kilowatts

        # Construction time
        self.construction_time_months = construction_time_months

        # Calculate project_size (project_size = num_turbines * turbine_rating_kilowatt / kilowatt_per_megawatt)
        kilowatt_per_megawatt = 1000
        self.project_size = num_turbines * turbine_rating_kilowatt / kilowatt_per_megawatt  # project size in megawatts

        # Get regional parameters (regulatory_environment, environmental_characteristics, infrastructure_interface,
        # soil_type, and rock_type) THESE DATA ARE CURRENTLY UNUSED
        # self.region = region  # set region
        # self.regulatory_environment = regulatory_environment_by_region[region]
        # self.environmental_characteristics = environmental_characteristics_by_region[region]
        # self.infrastructure_interface = public_infrastructure_interface_by_region[region]
        # self.soil_type = soil_type_by_region[region]
        # self.rock_type = rock_type_by_region[region]


project_value = 1e8  # todo: change to use value calculated by all modules except management

# model inputs
# todo: replace with function call for user input
# dictionary of file names for input data
file_list = {'crane_specs': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/crane_specs.csv",
             'equip': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/equip.csv",
             'crew': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/crews.csv",
             'components': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/components.csv",
             'project': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/project.csv",
             'equip_price': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/equip_price.csv",
             'crew_price': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/crew_price.csv",
             'material_price': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/material_price.csv",
             'weather': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/weather_withtime.csv",
             'rsmeans': "/Users/aeberle/Documents/Wind FY18/Land based BOS/Pseudocode/rsmeans_data.csv"}

development_cost = 5e6  # value input by the user (generally ranges from $3-10 million)
per_diem = 144  # USD per day
season_construct = ['spring', 'summer']
time_construct = 'normal'
construction_time_months = 13
num_hwy_permits = 1  # assuming number of highway permits = 1

# Financial parameters
markup_constants = {'contingency': 0.03,
                    'warranty_management': 0.0002,
                    'sales_and_use_tax': 0,
                    'overhead': 0.05,
                    'profit_margin': 0.05}

# dictionary of seasons
season_dict = {'winter':   [12, 1, 2],
               'spring':   [3, 4, 5],
               'summer':   [6, 7, 8],
               'fall':     [9, 10, 11]}

operational_hour_dict = {'long': 24,
                         'normal': 10}


phase_list = {'Collection system': '',
              'Development': '',
              'Erection': '',
              'Management': '',
              'Foundations': '',
              'Roads': '',
              'Transmission and interconnection': '',
              'Substation': ''}
type_of_cost = ['Labor', 'Equipment rental', 'Mobilization', 'Fuel', 'Materials', 'Development', 'Management', 'Other']


# create object that contains the properties of a land-based wind project
#project = Project(project_value, num_turbines, turbine_rating_kilowatt, construction_time_months)


def calculate_bos_cost(files, season, season_month, development, list_of_phases):
    """
    Executes the calculate costs functions for each module/phase in the balance of system

    :param files: dictionary of files with input data from the user
    :param season: list of strings that describe season(s) of interest for analysis
    :param season_month: dictionary that maps seasons to months
    :param development: float of development costs input by the user
    :param list_of_phases: list of strings that describe the phases to be modeled
    :return: total BOS costs for by phase and type
    """
    # read csv files and load data into dictionary
    data_csv = dict()
    for file in files:
        data_csv[file] = pd.DataFrame(pd.read_csv(files[file], engine='python'))

    # define project parameters
    project_data = data_csv['project'].where(data_csv['project']['Project ID'] == 'Conventional')
    project_data = project_data.dropna(thresh=1)
    num_turbines = project_data['Number of turbines'][0]
    turbine_spacing = project_data['Turbine spacing (times rotor diameter)'][0]
    rotor_diameter = project_data['Rotor diameter m'][0]
    turbine_rating_kilowatt = project_data['Turbine rating MW'][0] * kilowatt_per_megawatt
    rate_of_deliveries = project_data['Rate of deliveries (turbines per week)']
    hub_height = project_data['Hub height m'][0]

    # electrical
    interconnect_voltage = 137
    pad_mount_transformer = True
    MV_thermal_backfill_mi = 0
    MV_overhead_collector_mi = 0
    rock_trenching_percent = 0.1
    distance_to_interconnect = 5
    new_switchyard = True

    project_size = num_turbines * turbine_rating_kilowatt / kilowatt_per_megawatt  # project size in megawatts
    road_length_m = ((np.sqrt(num_turbines) - 1) ** 2 * turbine_spacing * rotor_diameter)
    road_width_ft = 16  # feet
    road_thickness_in = 8  # inches
    crane_width_m = 10.7  # meters
    overtime_multiplier = 1.4  # multiplier for labor overtime rates due to working 60 hr/wk rather than 40 hr/wk

    num_access_roads = 5

    # create data frame to store cost data for each module
    bos_cost = pd.DataFrame(list(product(phase_list, type_of_cost)), columns=['Phase of construction', 'Type of cost'])
    bos_cost['Cost USD'] = np.nan

    # create weather window for project
    weather_window = WD.create_weather_window(weather_data=data_csv['weather'],
                                              season_id=season_dict,
                                              season_construct=season_construct,
                                              time_construct=time_construct)

    operational_hrs_per_day = operational_hour_dict[time_construct]

    # calculate road costs
    road_cost = RoadsCost.calculate_costs(road_length=road_length_m,
                                          road_width=road_width_ft,
                                          road_thickness=road_thickness_in,
                                          input_data=data_csv,
                                          construction_time=construction_time_months,
                                          weather_window=weather_window,
                                          crane_width_m=crane_width_m,
                                          operational_hrs_per_day=operational_hrs_per_day,
                                          num_turbines=num_turbines,
                                          rotor_diam=rotor_diameter,
                                          access_roads=num_access_roads,
                                          per_diem_rate=per_diem,
                                          overtime_multiplier=overtime_multiplier)

    # calculate foundation costs
    foundation_cost = FoundationCost.calculate_costs(input_data=data_csv,
                                                     num_turbines=num_turbines,
                                                     construction_time=construction_time_months,
                                                     weather_window=weather_window,
                                                     operational_hrs_per_day=operational_hrs_per_day,
                                                     overtime_multiplier=overtime_multiplier)

    # set values in bos_cost data frame - since formatting is already correct for foundation_cost, then overwrite values
    for value in foundation_cost['Type of cost']:
        bos_cost.loc[(bos_cost['Phase of construction'] == 'Foundations') &
                     (bos_cost['Type of cost'] == value), ['Cost USD']] = foundation_cost.loc[
        (foundation_cost['Phase of construction'] == 'Foundations') &
        (foundation_cost['Type of cost'] == value), ['Cost USD']].values

    # set values in bos_cost data frame - since formatting is already correct for road_cost, then overwrite values
    for value in foundation_cost['Type of cost']:
        bos_cost.loc[(bos_cost['Phase of construction'] == 'Roads') &
                     (bos_cost['Type of cost'] == value), ['Cost USD']] = road_cost.loc[
        (road_cost['Phase of construction'] == 'Roads') &
        (road_cost['Type of cost'] == value), ['Cost USD']].values


    substation = 11652 * (interconnect_voltage + project_size) + 11795 * (project_size ** 0.3549) + 1526800

    if distance_to_interconnect == 0:
        trans_interconnect = 0
    else:
        if new_switchyard is True:
            interconnect_adder = 18115 * interconnect_voltage + 165944
        else:
            interconnect_adder = 0
        trans_interconnect = ((1176 * interconnect_voltage + 218257) * (distance_to_interconnect ** (-0.1063))
                              * distance_to_interconnect) + interconnect_adder

    if pad_mount_transformer is True:
        multipier_material = 66733.4
    else:
        multipier_material = 27088.4
    electrical_materials = num_turbines * multipier_material + int(project_size / 25) * 35375 + \
                         int(project_size / 100) * 50000 + rotor_diameter * num_turbines * 545.4 + \
                         MV_thermal_backfill_mi * 5 + 41945
    if project_size > 200:
        material_adder = 300000
    else:
        material_adder = 155000
    electrical_installation = int(project_size / 25) * 14985 + material_adder + \
                           num_turbines * (7059.3 + rotor_diameter * (352.4 + 297 * rock_trenching_percent)) + \
                           MV_overhead_collector_mi * 200000 + 10000

    bos_cost.loc[(bos_cost['Phase of construction'] == 'Transmission and interconnection') &
                 (bos_cost['Type of cost'] == 'Other'), ['Cost USD']] = trans_interconnect

    bos_cost.loc[(bos_cost['Phase of construction'] == 'Substation') &
                 (bos_cost['Type of cost'] == 'Other'), ['Cost USD']] = substation

    bos_cost.loc[(bos_cost['Phase of construction'] == 'Collection system') &
                 (bos_cost['Type of cost'] == 'Other'), ['Cost USD']] = electrical_installation + electrical_materials

    # calculate erection costs
    erection_cost = ErectionCost.calculate_costs(project_data=data_csv,
                                                 hour_day=operational_hour_dict,
                                                 construction_time=construction_time_months,
                                                 time_construct=time_construct,
                                                 weather_window=weather_window,
                                                 rate_of_deliveries=rate_of_deliveries,
                                                 overtime_multiplier=overtime_multiplier,
                                                 project_size=project_size
                                                 )

    bos_cost = save_cost_data(phase='Erection',
                              phase_cost=erection_cost,
                              bos_cost=bos_cost)

    bos_cost = save_cost_data(phase='Development',
                              phase_cost=pd.DataFrame([[development]], columns=['Development cost USD']),
                              bos_cost=bos_cost)

    project_value = float(bos_cost['Cost USD'].sum())

    # calculate management costs
    management_cost = ManagementCost.calculate_costs(project_value=project_value,  #57552441 #
                                                     foundation_cost=foundation_cost,
                                                     num_hwy_permits=num_hwy_permits,
                                                     construction_time_months=construction_time_months,
                                                     markup_constants=markup_constants,
                                                     num_turbines=num_turbines,
                                                     project_size=project_size,
                                                     hub_height=hub_height,
                                                     num_access_roads=num_access_roads)
    bos_cost = save_cost_data(phase='Management',
                              phase_cost=management_cost,
                              bos_cost=bos_cost)



    print('Final cost matrix:')
    print(bos_cost)

    print('Total cost by phase:')
    print(bos_cost.groupby(by=bos_cost['Phase of construction']).sum())

    print('Total cost USD:')
    print(bos_cost['Cost USD'].sum())

    return bos_cost


def save_cost_data(phase, phase_cost, bos_cost):
    """
    Saves phase-specific cost data to a data frame for total BOS costs

    :param phase: string that describes the phase of interest
    :param phase_cost: data frame with costs for phase of interest
    :param bos_cost: data frame of BOS costs
    :return: updated data frame with BOS costs for phase of interest
    """

    for index in bos_cost[bos_cost['Phase of construction'] == phase]['Type of cost'].index:
        if '{type} cost USD'.format(type=bos_cost['Type of cost'][index]) in phase_cost.columns:
            bos_cost.loc[index, 'Cost USD'] = phase_cost['{type} cost USD'.format(type=bos_cost['Type of cost'][index])].sum()

    return bos_cost


if __name__ == '__main__':
    bos_cost = calculate_bos_cost(files=file_list,
                                  season=season_construct,
                                  season_month=season_dict,
                                  development=development_cost,
                                  list_of_phases=phase_list)
