"""
FoundationCost.py
Created by Annika Eberle and Owen Roberts on Apr. 3, 2018

Calculates the costs of constructing foundations for land-based wind projects
(items in brackets are not yet implemented)

Get number of turbines
Get duration of construction
Get daily hours of operation*  # todo: add to process diagram
Get season of construction*  # todo: add to process diagram
[Get region]
Get rotor diameter
Get hub height
Get turbine rating
Get buoyant foundation design flag
[Get seismic zone]
Get tower technology type
Get hourly weather data
[Get specific seasonal delays]
[Get long-term, site-specific climate data]

Get price data
    Get labor rates
    Get material prices for steel and concrete

[Use region to determine weather data,

Calculate the foundation loads using the rotor diameter, hub height, and turbine rating

Determine the foundation size based on the foundation loads, buoyant foundation design flag, and type of tower technology

Estimate the amount of material needed for foundation construction based on foundation size and number of turbines

Estimate the amount of time required to construct foundation based on foundation size, hours of operation,
duration of construction, and number of turbines

Estimate the additional amount of time for weather delays (currently only assessing wind delays) based on
hourly weather data, construction time, hours of operation, and season of construction

Estimate the amount of labor required for foundation construction based on foundation size, construction time, and weather delay
    Calculate number of workers by crew type
    Calculate man hours by crew type

Estimate the amount of equipment needed for foundation construction based on foundation size, construction time, and weather delay
    Calculate number of equipment by equip type
    Calculate equipment hours by equip type

Calculate the total foundation cost based on amount of equipment, amount of labor, amount of material, and price data

"""


def calculate_foundation_loads(rotor_diam, hub_height, turbine_rating):
    """

    :param rotor_diam:
    :param hub_height:
    :param turbine_rating:
    :return:
    """


def determine_foundation_size(foundation_loads, buoyant_design, type_of_tower):
    """

    :param foundation_loads:
    :param buoyant_design:
    :param type_of_tower:
    :return:
    """


def estimate_material_needs(foundation_size, num_turbines):
    """

    :param foundation_size:
    :param num_turbines:
    :return:
    """


def estimate_construction_time(foundation_size, num_turbines, hours_operation, duration_construction):
    """

    :param foundation_size:
    :param num_turbines:
    :param hours_operation:
    :param duration_construction:
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


def estimate_labor(foundation_size, construction_time, weather_delay):
    """

    :param foundation_size:
    :param construction_time:
    :param weather_delay:
    :return:
    """


def estimate_equip(foundation_size, construction_time, weather_delay):
    """

    :param foundation_size:
    :param construction_time:
    :param weather_delay:
    :return:
    """


def calculate_costs(labor, equip, material, price_data):
    """

    :param labor:
    :param equip:
    :param material:
    :param price_data:
    :return:
    """