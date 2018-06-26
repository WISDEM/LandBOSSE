"""
RoadsCost.py
Created by Annika Eberle and Owen Roberts on Apr. 3, 2018
Last updated April 27, 2018

Calculates cost of constructing roads for land-based wind projects

Get terrain complexity
Get turbine spacing
[Get region]
[Get distance to quarry]
Get road width
Get number of turbines
Get turbine rating
Get duration of construction*  #todo: add to process diagram

Added input variables (because relationships could not be determined for inputs in process diagram):
Get road length
Get weather data
Get road thickness

[Estimate road length based on turbine spacing and project size]

[Get regional values from database/lookup tables for the following parameters
    Land cover
    Weather
    Soil type
    Rock type]

[Estimate road thickness based on soil type]
Calculate volume of road based on road thickness, road width, and road length

Calculate road labor and equipment costs by operation and type using RSMeans data
    [Calculate engineering hours for road survey based on terrain complexity and road length]
    [Calculate man hours and equipment hours for clearing and grubbing based on terrain complexity, road length, and land cover]
    [Calculate man hours and equipment hours for stormwater pollution measures and culverts based on terrain complexity, road length, and weather]
    Calculate man hours and equipment hours for compaction of soil based on road length, road thickness, soil type, road width, and equipment size
    Calculate man hours and equipment hours for mass material movement based on land cover, terrain complexity, and road length
    Calculate man hours and equipment hours for rock placement based on equipment size, distance to quarry, and volume of road
    Calculate man hours and equipment hours for compaction of rock based on road length, road thickness, and rock type
    Calculate man hours and equipment hours for final grading based on road length
    [Calculate man hours and equipment hours for road maintenance based on road thickness, road length, and weather]
    [Calculate man hours and equipment hours for decompaction of crane paths based on road length]
    Calculate quantity of materials based on volume of materials

Calculate material costs by type
    Calculate material costs using quantity of materials by material type and material prices by material type

Sum road costs over all operations and material types to get total costs by type of cost (e.g., material vs. equipment)

Return total road costs by type of cost
"""

import pandas as pd
import numpy as np
import math
import WeatherDelay as WD

# conversion factors
meters_per_foot = 0.3
meters_per_inch = 0.025
cubic_yards_per_cubic_meter = 1.30795
square_feet_per_square_meter = 10.7639


def calculate_road_properties(road_length, road_width, road_thickness, crane_width, num_turbines):
    """
    Calculates the volume of road materials need based on length, width, and thickness of roads

    :param road_length: float of road length in meters
    :param road_width: float of road width in feet
    :param road_thickness: float of road thickness in inches
    :param crane_width: float of crane width in meters
    :param num_turbines: number of turbines
    :return: road volume in cubic meters
    """

    # units of cubic meters
    road_volume = road_length * (road_width * meters_per_foot) * (road_thickness * meters_per_inch)

    # cubic meters for crane pad and maintenance ring for each turbine
    # (from old BOS model - AI - Access Roads & Site Imp. tab cell J33)
    crane_pad_volume = 125

    # conversion factor for converting packed cubic yards to loose cubic yards
    # material volume is about 1.4 times greater than road volume due to compaction
    yards_loose_per_yards_packed = 1.39

    road_properties = {'road_volume': road_volume + crane_pad_volume * num_turbines,  # in cubic meters
                       'depth_to_subgrade_m': 0.1,
                       'crane_path_width_m': crane_width + 1.5,  # todo: replace with actual crane path width from erection module
                       'road_length_m': road_length,
                       'road_thickness_m': (road_thickness * meters_per_inch),
                       'road_width_m': (road_width * meters_per_foot),
                       'material_volume': (road_volume * cubic_yards_per_cubic_meter * yards_loose_per_yards_packed)
                       }

    return road_properties


def estimate_construction_time(throughput_operations, road_properties, duration_construction):
    """

    :param throughput_operations: data frame with operation data including throughput for each operation
    :param road_properties: properties of the road, including the thickness, width, length, volume, depth to subgrade
    :param duration_construction: the length of construction time for the entire project (in months)
    :return: data frame with the total construction time for each operation
    """

    road_construction_time = duration_construction * 1/5

    # select operations for roads module that have data
    operation_data = throughput_operations.where(throughput_operations['Module'] == 'Roads').dropna(thresh=4)

    # create list of unique material units for operations
    list_units = operation_data['Units'].unique()

    lift_depth_m = 0.2
    topsoil_volume = (road_properties['crane_path_width_m']) * road_properties['road_length_m'] * (road_properties['depth_to_subgrade_m'])
    embankment_volume_crane = (road_properties['crane_path_width_m']) * road_properties['road_length_m'] * (road_properties['depth_to_subgrade_m'])
    embankment_volume_road = road_properties['road_volume'] * cubic_yards_per_cubic_meter * math.ceil(road_properties['road_thickness_m'] / lift_depth_m)
    material_volume = road_properties['material_volume']
    rough_grading_area = road_properties['road_length_m'] * road_properties['road_width_m'] * square_feet_per_square_meter * math.ceil(road_properties['road_thickness_m'] / lift_depth_m) / 100000

    material_quantity_dict = {'cubic yard': topsoil_volume,
                              'embankment cubic yards crane': embankment_volume_crane,
                              'embankment cubic yards road': embankment_volume_road,
                              'loose cubic yard': material_volume,
                              'Each (100000 square feet)': rough_grading_area}

    material_needs = pd.DataFrame(columns=['Units', 'Quantity of material'])
    for unit in list_units:
        unit_quantity = pd.DataFrame([[unit, material_quantity_dict[unit]]], columns=['Units', 'Quantity of material'])
        material_needs = material_needs.append(unit_quantity)

    operation_data = pd.merge(operation_data, material_needs, on=['Units']).dropna(thresh=3)
    operation_data = operation_data.where((operation_data['Daily output']).isnull() == False).dropna(thresh=4)

    operation_data['Number of days'] = operation_data['Quantity of material'] / operation_data['Daily output']
    operation_data['Number of crews'] = np.ceil((operation_data['Number of days'] / 30) / road_construction_time)
    operation_data['Cost USD without weather delays'] = operation_data['Quantity of material'] * operation_data['Rate USD per unit']

    # if more than one crew needed to complete within construction duration then assume that all construction happens
    # within that window and use that timeframe for weather delays; if not, use the number of days calculated
    operation_data['time_construct_bool'] = operation_data['Number of days'] > road_construction_time * 30
    boolean_dictionary = {True: road_construction_time * 30, False: np.NAN}
    operation_data['time_construct_bool'] = operation_data['time_construct_bool'].map(boolean_dictionary)
    operation_data['Time construct days'] = operation_data[['time_construct_bool', 'Number of days']].min(axis=1)

    return operation_data


def calculate_weather_delay(weather_window, duration_construction, start_delay, critical_wind_speed,
                            operational_hrs_per_day, wind_shear_exponent):
    """
    Calculates wind delay for roads.

    :param weather_window: data frame with weather data for time window associated with construction period
    :param duration_construction: the length of construction time for the entire project (in months)
    :param start_delay: the delay from the start of the weather window for the operation of interest
    :param critical_wind_speed: the critical wind speed for determining wind delay
    :param operational_hrs_per_day: number of hours of operation per day
    :return: the total wind delay (in hours) as estimated based on the input parameters
    """

    # convert days of work to hours of work
    mission_time_hrs = duration_construction * operational_hrs_per_day

    # compute weather delay
    wind_delay = WD.calculate_wind_delay(weather_window=weather_window,
                                         start_delay=start_delay,
                                         mission_time=mission_time_hrs,
                                         critical_wind_speed=critical_wind_speed,
                                         height_interest=20,
                                         wind_shear_exponent=wind_shear_exponent)
    wind_delay = pd.DataFrame(wind_delay)

    # if greater than 4 hour delay, then shut down for full day (10 hours)
    wind_delay[(wind_delay > 4)] = 10
    wind_delay_time = float(wind_delay.sum())

    return wind_delay_time


def calculate_costs(road_length, road_width, road_thickness, input_data, construction_time, weather_window,
                    crane_width_m, operational_hrs_per_day, num_turbines, rotor_diam, access_roads, per_diem_rate,
                    overtime_multiplier, wind_shear_exponent):
    """

    :param road_length: float of road length in meters
    :param road_width: float of road width in feet
    :param road_thickness: float of road thickness in inches
    :param input_data: data frame with input data from csv files (includes RSMeans data, project data, etc.)
    :param construction_time: the length of construction time for the entire project (in months)
    :param weather_window: data frame with weather data for time window associated with construction period
    :param crane_width_m: float of crane width in meters
    :param operational_hrs_per_day: number of hours of operation per day
    :param num_turbines: number of turbines
    :param rotor_diam: rotor diameter in meters
    :param access_roads: number of access roads for project
    :param per_diem_rate: per diem (USD per day)
    :return: data frame with total road costs by phase of construction
    """

    road_properties = calculate_road_properties(road_length=road_length,
                                                road_thickness=road_thickness,
                                                road_width=road_width,
                                                crane_width=crane_width_m,
                                                num_turbines=num_turbines)
    material_name = input_data['rsmeans']['Material type ID'].where(input_data['rsmeans']['Module'] == 'Roads').dropna().unique()
    material_vol = pd.DataFrame([[material_name[0], road_properties['material_volume'], 'Loose cubic yard']],
                                columns=['Material type ID', 'Quantity of material', 'Units'])

    material_data = pd.merge(material_vol, input_data['material_price'], on=['Material type ID'])
    material_data['Cost USD'] = material_data['Quantity of material'] * pd.to_numeric(
        material_data['Material price USD per unit'])

    operation_data = estimate_construction_time(throughput_operations=input_data['rsmeans'],
                                                road_properties=road_properties,
                                                duration_construction=construction_time)

    wind_delay = calculate_weather_delay(weather_window=weather_window,
                                         duration_construction=operation_data['Time construct days'].max(skipna=True),
                                         start_delay=0,
                                         critical_wind_speed=13,
                                         operational_hrs_per_day=operational_hrs_per_day,
                                         wind_shear_exponent=wind_shear_exponent)

    wind_delay_percent = (wind_delay / operational_hrs_per_day) / operation_data['Time construct days'].max(skipna=True)
    wind_multiplier = 1 / (1 - wind_delay_percent)
    
    labor_equip_data = pd.merge(operation_data[['Operation ID', 'Units', 'Quantity of material']], input_data['rsmeans'], on=['Units', 'Operation ID'])
    labor_equip_data['Cost USD'] = (labor_equip_data['Quantity of material'] * labor_equip_data['Rate USD per unit'] * overtime_multiplier
                                    + round(labor_equip_data['Quantity of material'] *
                                            labor_equip_data['Per Diem Hours (per unit)'] / operational_hrs_per_day / 6
                                            ) * 7 * per_diem_rate * labor_equip_data['Number of workers']) * wind_multiplier

    road_cost = labor_equip_data[['Operation ID', 'Type of cost', 'Cost USD']]

    material_costs = pd.DataFrame([[material_data['Material type ID'][0], 'Materials', float(material_data['Cost USD'])]],
                                  columns=['Operation ID', 'Type of cost', 'Cost USD'])

    cost_adder = (float(num_turbines) * 17639 +
                  float(num_turbines) * float(rotor_diam) * 24.8 +
                  float(construction_time) * 55500 +
                  float(access_roads) * 3800)
    additional_costs = pd.DataFrame([['Other operations for roads', 'Other', float(cost_adder)]],
                                    columns=['Operation ID', 'Type of cost', 'Cost USD'])

    road_cost = road_cost.append(material_costs)
    road_cost = road_cost.append(additional_costs)

    # set mobilization cost equal to 5% of total road cost
    mobilization_costs = pd.DataFrame([['Mobilization', 'Mobilization', float(road_cost["Cost USD"].sum()) * 0.05]],
                                      columns=['Operation ID', 'Type of cost', 'Cost USD'])

    road_cost = road_cost.append(mobilization_costs)

    # print(road_cost.groupby(by=['Operation ID']).sum())

    total_road_cost = road_cost.groupby(by=['Type of cost']).sum().reset_index()
    total_road_cost.loc[total_road_cost['Type of cost'] == 'Labor', 'Cost USD'] = float(
        total_road_cost.loc[total_road_cost['Type of cost'] == 'Labor', 'Cost USD']) + 48.8 * road_length
    total_road_cost['Phase of construction'] = 'Roads'

    # print(total_road_cost)

    return total_road_cost, wind_multiplier