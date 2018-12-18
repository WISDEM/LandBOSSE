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
import SubstationCost
import TransDistCost
import CollectionCost
from itertools import product
import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt

# constants
kilowatt_per_megawatt = 1000
development_cost = 5e6  # value input by the user (generally ranges from $3-10 million)
per_diem = 144  # USD per day
season_construct = ['spring', 'summer']
time_construct = 'normal'
construction_time_months = 13
num_hwy_permits = 1  # assuming number of highway permits = 1

# financial parameters
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

    # default electrical parameters
    interconnect_voltage = 137
    pad_mount_transformer = True
    MV_thermal_backfill_mi = 0
    MV_overhead_collector_mi = 0
    rock_trenching_percent = 0.1
    distance_to_interconnect = 5
    new_switchyard = True

    # default road parameters
    road_length_m = ((np.sqrt(num_turbines) - 1) ** 2 * turbine_spacing * rotor_diameter)
    road_width_ft = 20  # feet 16
    road_thickness_in = 8  # inches
    crane_width_m = 12.2  # meters 10.7
    num_access_roads = 5

    # default labor parameters
    overtime_multiplier = 1.4  # multiplier for labor overtime rates due to working 60 hr/wk rather than 40 hr/wk

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
                                                                             tower_type=tower_type,
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
    collection_system_cost = CollectionCost.calculate_costs(pad_mount_transformer, num_turbines, project_size,
                                                                  rotor_diameter, MV_thermal_backfill_mi,
                                                                  rock_trenching_percent, MV_overhead_collector_mi)

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
                                                                         project_size=project_size,
                                                                         wind_shear_exponent=wind_shear_exponent
                                                                         )

    # set values in bos_cost data frame
    data_dict = {'Collection system': collection_system_cost,
              'Erection': erection_cost,
              'Foundations': foundation_cost,
              'Roads': road_cost,
              'Transmission and distribution': trans_dist_cost,
              'Substation': substation_cost}

    for key in data_dict:
        for value in data_dict[key]['Type of cost']:
            bos_cost.loc[(bos_cost['Phase of construction'] == key) &
                         (bos_cost['Type of cost'] == value), ['Cost USD']] = data_dict[key].loc[
            (data_dict[key]['Phase of construction'] == key) &
            (data_dict[key]['Type of cost'] == value), ['Cost USD']].values

    bos_cost = save_cost_data(phase='Development',
                              phase_cost=pd.DataFrame([[development]], columns=['Development cost USD']),
                              bos_cost=bos_cost)

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

    return bos_cost, wind_multiplier, road_length_m, num_turbines, project_size


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

    # define file paths for inputs and outputs
    # current NREL filepath for inputs: "//nrel.gov/shared/Wind/Public/Projects/Projects T-Z/TAMA/WTT/BOS modeling/current_model_inputs_and_example_outputs/"
    # suggest creating a local copy of this folder when you run the model
    input_data_path = "/Users/aeberle/Desktop/bos_model/inputs_open_release_real/"
    component_folder = "component_data_proprietary/"  # subfolder for component data
    output_data_path = "/Users/aeberle/Desktop/bos_model/outputs/"

    # define file names for outputs
    file_name_main_outputs = 'output_100turbine.csv'  # main outputs are costs
    file_name_other_outputs = 'output_other_params_100turbine.csv'  # other outputs currently include road length and wind multiplier

    # open project data file
    project_path = os.path.join(input_data_path, "project_scenario_list.csv")
    project_data = pd.read_csv(project_path)

    # initialize output data frames
    scenario_data_compiled = pd.DataFrame(columns=["Scenario", "Phase of construction", "Cost USD"])
    scenario_data_full_compiled = pd.DataFrame(columns=["Scenario", "Phase of construction", "Cost USD"])
    other_scenario_data_compiled = pd.DataFrame(columns=["Scenario", "Parameter", "Value"])

    # loop project ids (scenarios) in project data file and execute model
    for i in range(0, len(project_data)):
        # extract name and hub height for scenario
        scenario = project_data['Project ID'][i]
        height = project_data['Hub height m'][i]
        scenario_filename = scenario + ".csv"
        print("\n" + scenario)
        #print(height)

        # define model inputs
        # todo: replace with function call for user input

        # dictionary of file names for input data (currently only "components" file changes by scenario)
        file_list = {'crane_specs':     os.path.join(input_data_path, "crane_specs_columnO-proprietary.csv"),
                     'equip':           os.path.join(input_data_path, "equip.csv"),
                     'crew':            os.path.join(input_data_path, "crews.csv"),
                     'components':      os.path.join(input_data_path + component_folder, scenario_filename),
                     'project':         project_path,
                     'equip_price':     os.path.join(input_data_path, "equip_price_proprietary.csv"),
                     'crew_price':      os.path.join(input_data_path, "crew_price_proprietary.csv"),
                     'material_price':  os.path.join(input_data_path, "material_price_proprietary.csv"),
                     'weather':         os.path.join(input_data_path, "weather_withtime.csv"),
                     'rsmeans':         os.path.join(input_data_path, "rsmeans_data_proprietary.csv")}

        # execute BOS model
        [bos_cost_1, wind_mult_1, road_length, num_turbines, project_size] = calculate_bos_cost(files=file_list,
                                                       scenario_name=scenario,
                                                       scenario_height=height,
                                                       development=development_cost)

        # compile results into output data frames
        sum_bos = bos_cost_1.groupby(by="Phase of construction").sum()
        scenario_data = pd.DataFrame(columns=["Scenario", "Phase of construction", "Cost USD"])
        scenario_data['Scenario'] = ([scenario] * 8)
        scenario_data['Phase of construction'] = sum_bos.index.values.tolist()
        scenario_data['Cost USD'] = sum_bos['Cost USD'].values.tolist()
        scenario_data_compiled = scenario_data_compiled.append(scenario_data, sort=False)

        # add row for total costs (sum of all module costs)
        scenario_sum = pd.DataFrame(columns=["Scenario", "Phase of construction", "Cost USD"])
        scenario_sum['Scenario'] = [scenario] * 3
        scenario_sum['Phase of construction'] = ['Total', 'Total per turbine', 'Total per MW']
        scenario_sum['Cost USD'] = [scenario_data['Cost USD'].sum(), scenario_data['Cost USD'].sum()/num_turbines, scenario_data['Cost USD'].sum()/project_size]
        scenario_data_compiled = scenario_data_compiled.append(scenario_sum, sort=False)

        # other outputs
        scenario_weather = pd.DataFrame(columns=["Scenario", "Parameter", "Value"])
        scenario_weather['Scenario'] = [scenario] * 2
        scenario_weather['Parameter'] = ['Wind delay multiplier', 'Road length m']
        scenario_weather['Value'] = [wind_mult_1.iloc[0]['Wind multiplier'], road_length]
        other_scenario_data_compiled = other_scenario_data_compiled.append(scenario_weather, sort=False)

        # save data to csv files
        scenario_data_compiled.to_csv(os.path.join(output_data_path, file_name_main_outputs), index=False)
        other_scenario_data_compiled.to_csv(os.path.join(output_data_path, file_name_other_outputs), index=False)

        scenario_data_full = pd.DataFrame(columns=["Scenario", "Phase of construction", "Cost USD"])
        scenario_data_full['Scenario'] = ([scenario] * 64)
        scenario_data_full['Phase of construction'] = bos_cost_1['Phase of construction'].values.tolist()
        scenario_data_full['Type of cost'] = bos_cost_1['Type of cost'].values.tolist()
        scenario_data_full['Cost USD'] = bos_cost_1['Cost USD'].values.tolist()
        scenario_data_full_compiled = scenario_data_full_compiled.append(scenario_data_full, sort=False)

    # data frame manipulation for plotting
    split_names = pd.DataFrame(scenario_data_full_compiled['Scenario'].str.split('_', expand=True))
    scenario_data_full_compiled['Hub height'] = split_names[1]
    scenario_data_full_compiled['Turbine'] = split_names[0]
    data_total_by_phase = scenario_data_full_compiled.groupby(by=['Phase of construction', 'Scenario']).sum().reset_index(drop=False)
    data_total_by_type = scenario_data_full_compiled.groupby(by=['Type of cost', 'Scenario']).sum().reset_index(drop=False)
    data_total = scenario_data_full_compiled.groupby(by=['Scenario']).sum().reset_index(drop=False)


    sns.set()
    sns.set_style("darkgrid")
    sns.set_context("poster")
    phase_plot = sns.factorplot(x="Scenario", y="Cost USD", data=data_total_by_phase, hue="Phase of construction",
                                kind="bar", size=8, palette=sns.cubehelix_palette(8, start=0.3, rot=-.75), margin_titles=True)
    phase_plot.fig.subplots_adjust(top=0.9)
    phase_plot.fig.suptitle('Cost by Phase', fontsize=16)
    phase_plot.savefig(os.path.join(output_data_path, "scenario_totals_by_phase_construction.png"))

    type_plot = sns.factorplot(x="Scenario", y="Cost USD", data=data_total_by_type, hue="Type of cost",
                               kind="bar", size=8, palette=sns.cubehelix_palette(8))
    type_plot.fig.subplots_adjust(top=0.9)
    type_plot.fig.suptitle('Cost by Type', fontsize=16)
    type_plot.savefig(os.path.join(output_data_path, "scenario_totals_by_type_cost.png"))

    total_plot = sns.factorplot(x="Scenario", y="Cost USD", data=data_total, kind="bar", size=8,
                                palette=sns.color_palette("muted"))
    total_plot.fig.subplots_adjust(top=0.9)
    total_plot.fig.suptitle('Total Cost', fontsize=16)
    total_plot.savefig(os.path.join(output_data_path, "scenario_total.png"))
