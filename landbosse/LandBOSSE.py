"""
LandBOSSE.py
Created by Annika Eberle and Owen Roberts on Feb. 28, 2018

Calculates the following balance-of-system costs for utility-scale, land-based wind projects:

- Development (currently input by the user)
- Management
- Roads
- Foundations
- Erection
- Collection system
- Transmission and distribution
- Substation
"""

from landbosse import WeatherDelay as WD
from landbosse import ErectionCost
from landbosse import ManagementCost
from landbosse import FoundationCost
from landbosse import RoadsCost
from landbosse import SubstationCost
from landbosse import TransDistCost
from landbosse import CollectionCost
from landbosse import DevelopmentCost
from itertools import product
import pandas as pd
import numpy as np
import warnings

# constants
kilowatt_per_megawatt = 1000
per_diem = 144  # USD per day
season_construct = ['spring', 'summer']
time_construct = 'normal'
construction_time_months = 9
num_hwy_permits = 1  # assuming number of highway permits = 1

# default financial parameters
markup_constants = {'contingency': 0.03,
                    'warranty_management': 0.0002,
                    'sales_and_use_tax': 0,
                    'overhead': 0.05,
                    'profit_margin': 0.05}

# default electrical parameters
interconnect_voltage = 137
pad_mount_transformer = True
MV_thermal_backfill_mi = 0
MV_overhead_collector_mi = 0
rock_trenching_percent = 0.1
distance_to_interconnect = 5
new_switchyard = True

# default road parameters
road_width_ft = 20  # feet 16
road_thickness_in = 8  # inches
crane_width_m = 12.2  # meters 10.7
num_access_roads = 5

# default labor parameters
overtime_multiplier = 1.4  # multiplier for labor overtime rates due to working 60 hr/wk rather than 40 hr/wk

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
              'Transmission and distribution': '',
              'Substation': ''}

type_of_cost = ['Labor', 'Equipment rental', 'Mobilization', 'Fuel', 'Materials', 'Development', 'Management', 'Other']


def calculate_bos_cost(files, scenario_name, scenario_height, development):
    """
    Executes the calculate costs functions for each module/phase in the balance of system

    :param files: [dict] dictionary of files with input data from the user
    :param scenario_name: [str] name of scenario to be run (must be in project file)
    :param scenario_height: [str] hub height of scenario to be run (must be in project file)
    :param development: [float] development costs input by the user
    :return: total BOS costs for by phase and type; weather delay by phase
    """

    print("Running LandBOSSE...")
    # read csv files and load data into dictionary
    data_csv = dict()
    for file in files:
        data_csv[file] = pd.DataFrame(pd.read_csv(files[file], engine='python'))

    # check for fake data that has not been replaced; proprietary data that are not available are flagged with 99
    check_files = [True in [99 in data_csv[key][col].values for col in data_csv[key].columns] for key in data_csv.keys()]
    proprietary_flag = True in check_files
    if proprietary_flag is True:
        warnings.warn("WARNING: Flags for fake data were found in the input data files. Make sure you replace 99 flags with real data. Check output carefully to ensure results are reasonable.", category=Warning)
        check_results_carefully = 1
    else:
        check_results_carefully = 0

    # extract project parameters from input data
    project_data = data_csv['project'].where((data_csv['project']['Project ID'] == scenario_name) & (data_csv['project']['Hub height m'] == scenario_height))
    project_data = project_data.dropna(thresh=1)
    num_turbines = float(project_data['Number of turbines'])
    turbine_spacing = float(project_data['Turbine spacing (times rotor diameter)'])
    rotor_diameter = float(project_data['Rotor diameter m'])
    turbine_rating_kilowatt = float(project_data['Turbine rating MW']) * kilowatt_per_megawatt
    rate_of_deliveries = float(project_data['Rate of deliveries (turbines per week)'])
    hub_height = float(project_data['Hub height m'])
    wind_shear_exponent = float(project_data['Wind shear exponent'])
    tower_type = project_data['Tower type'].values[0]
    foundation_depth = float(project_data['Foundation depth m'])
    project_size = num_turbines * turbine_rating_kilowatt / kilowatt_per_megawatt  # project size in megawatts


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
    print("Calculating road costs...")
    road_length_m = ((np.sqrt(num_turbines) - 1) ** 2 * turbine_spacing * rotor_diameter)
    [road_cost, road_wind_mult] = RoadsCost.calculate_costs(road_length=road_length_m,
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
                                                            overtime_multiplier=overtime_multiplier,
                                                            wind_shear_exponent=wind_shear_exponent
                                                            )

    # calculate foundation costs
    print("Calculating foundation costs...")
    [foundation_cost, foundation_wind_mult] = FoundationCost.calculate_costs(input_data=data_csv,
                                                                             num_turbines=num_turbines,
                                                                             construction_time=construction_time_months,
                                                                             weather_window=weather_window,
                                                                             operational_hrs_per_day=operational_hrs_per_day,
                                                                             overtime_multiplier=overtime_multiplier,
                                                                             wind_shear_exponent=wind_shear_exponent,
                                                                             depth=foundation_depth)


    # calculate substation costs
    print("Calculating substation costs...")
    substation_cost = SubstationCost.calculate_costs(interconnect_voltage=interconnect_voltage,
                                                     project_size=project_size)

    # calculate transmission and distribution costs
    print("Calculating transmission and distribution costs...")
    trans_dist_cost = TransDistCost.calculate_costs(distance_to_interconnect=distance_to_interconnect,
                                                       new_switchyard=new_switchyard,
                                                       interconnect_voltage=interconnect_voltage)

    # calculate collection system costs
    print("Calculating collection system costs...")
    collection_system_cost = CollectionCost.calculate_costs(pad_mount_transformer=pad_mount_transformer,
                                                            num_turbines=num_turbines,
                                                            project_size=project_size,
                                                            rotor_diameter=rotor_diameter,
                                                            MV_thermal_backfill_mi=MV_thermal_backfill_mi,
                                                            rock_trenching_percent=rock_trenching_percent,
                                                            MV_overhead_collector_mi=MV_overhead_collector_mi)

    # calculate erection costs
    print("Calculating erection costs...")
    [erection_cost, erection_wind_mult] = ErectionCost.calculate_costs(project_specs=project_data,
                                                                         project_data=data_csv,
                                                                         hour_day=operational_hour_dict,
                                                                         construction_time=construction_time_months,
                                                                         time_construct=time_construct,
                                                                         weather_window=weather_window,
                                                                         rate_of_deliveries=rate_of_deliveries,
                                                                         overtime_multiplier=overtime_multiplier,
                                                                         wind_shear_exponent=wind_shear_exponent
                                                                         )

    # calculate development costs -- based on user input right now
    print ("Calculating development costs... ")
    development_cost = DevelopmentCost.calculate_costs(development_cost=development)

    # set values in bos_cost data frame
    data_dict = {'Collection system': collection_system_cost,
              'Erection': erection_cost,
              'Foundations': foundation_cost,
              'Roads': road_cost,
              'Transmission and distribution': trans_dist_cost,
              'Substation': substation_cost,
              'Development': development_cost}

    for key in data_dict:
        for value in data_dict[key]['Type of cost']:
            bos_cost.loc[(bos_cost['Phase of construction'] == key) &
                         (bos_cost['Type of cost'] == value), ['Cost USD']] = data_dict[key].loc[
            (data_dict[key]['Phase of construction'] == key) &
            (data_dict[key]['Type of cost'] == value), ['Cost USD']].values

    # sum total costs except management (management requires total of all other costs)
    project_value = float(bos_cost['Cost USD'].sum())

    # calculate management costs
    print("Calculating management costs...")
    management_cost = ManagementCost.calculate_costs(project_value=project_value,
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

    # weather delays
    wind_multiplier = pd.DataFrame([['Erection', erection_wind_mult],
                                    ['Foundation', foundation_wind_mult],
                                    ['Road', road_wind_mult]], columns=['Operation', 'Wind multiplier'])

    # print statements for debugging
    #print('Final cost matrix:')
    #print(bos_cost)

    #print('Total cost by phase:')
    #print(bos_cost.groupby(by=bos_cost['Phase of construction']).sum())

    #print('\n Total cost USD:')
    #print(bos_cost['Cost USD'].sum())

    #print(wind_multiplier)

    return bos_cost, wind_multiplier, road_length_m, num_turbines, project_size, check_results_carefully


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

