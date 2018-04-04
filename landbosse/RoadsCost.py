"""
RoadsCost.py
Created by Annika Eberle and Owen Roberts on Apr. 3, 2018

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
Calculate project size based on number of turbines and turbine rating

[Get regional values from database/lookup tables for the following parameters
    Land cover
    Weather
    Soil type
    Rock type]

[Estimate road thickness based on soil type]
Calculate volume of road based on road thickness, road width, and road length

[Lookup equipment size based on project size]

Calculate road labor, equipment, and material requirements by type
    Calculate engineering hours for road survey based on terrain complexity and road length
    Calculate man hours and equipment hours for clearing and grubbing based on terrain complexity, road length, and land cover
    Calculate man hours and equipment hours for stormwater pollution measures and culverts based on terrain complexity, road length, and weather
    Calculate man hours and equipment hours for compaction of soil based on road length, road thickness, soil type, road width, and equipment size
    Calculate man hours and equipment hours for mass material movement based on land cover, terrain complexity, and road length
    Calculate man hours and equipment hours for rock placement based on equipment size, distance to quarry, and volume of road
    Calculate man hours and equipment hours for compaction of rock based on road length, road thickness, and rock type
    Calculate man hours and equipment hours for final grading based on road length
    Calculate man hours and equipment hours for road maintenance based on road thickness, road length, and weather
    Calculate man hours and equipment hours for decompaction of crane paths based on road length
    Calculate quantity of materials based on volume of materials

Calculate road costs by type
    Calculate labor costs using man hours by crew type and labor prices by crew type
    Calculate fuel costs using equipment hours by equipment type and fuel prices by equipment type
    Calculate equipment costs using equipment hours by equipment type and equipment prices by equipment type
    Calculate material costs using quantity of materials by material type and material prices by material type
    Calculate costs for fencing, gates, utility drops, etc. based on project size

Sum road costs over all types to get total costs

Return total road costs
"""


def calculate_volume_material(road_length, road_width, road_thickness):
    """
    Calculates the volume of road materials need based on length, width, and thickness of roads

    :param road_length: float of road length in meters
    :param road_width: float of road width in meters
    :param road_thickness: float of road thickness in meters
    :return: road volume in cubic meters
    """

    road_volume = road_length * road_width * road_thickness

    return road_volume


def lookup_equipment_size(project_size, road_length):
    """
    Gets equipment size needed for a given project size and road length

    For now this function does not use inputs to calculate equipment size,
    assumes one size for all projects and road lengths

    :param project_size:
    :param road_length:
    :return: equipment multiplier
    """


def estimate_construction_time(rsmeans_data, duration_construction, road_volume):
    """

    :param rsmeans_data:
    :param duration_construction:
    :param road_volume:
    :return:
    """

def calculate_weather_delay(weather_data, season_dict, season_construct, time_construct,
                            duration_construction, start_delay, critical_wind_speed):
    """

    :param weather_data:
    :param season_dict:
    :param season_construct:
    :param time_construct:
    :param duration_construction:
    :param start_delay:
    :param critical_wind_speed:
    :return:
    """


def calculate_costs(road_volume, material_price, rsmeans_data, construction_time, weather_delay, equip_multiplier):
    """

    :param road_volume:
    :param material_price:
    :param rsmeans_data:
    :param construction_time:
    :param weather_delay:
    :param equip_multiplier:
    :return:
    """