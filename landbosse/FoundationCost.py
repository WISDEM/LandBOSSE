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
import math

# constants
kg_per_tonne = 1000


def calculate_foundation_loads(component_data, rotor_diam, hub_height, turbine_rating):
    """

    :param component_data: data on components (weight, height, area, etc.)
    :param rotor_diam:
    :param hub_height:
    :param turbine_rating:
    :return:
    """

    # set exposure constants
    a = 9.5
    z_g = 274.32

    # get section height
    z = component_data['Section height m']

    # get cross-sectional area
    A_f = component_data['Surface area sq m']

    # get lever arm
    L = component_data['Lever arm m']

    # Equations from Shrestha, S. 2015. DESIGN AND ANALYSIS OF FOUNDATION FOR ONSHORE TALL WIND TURBINES. All Theses. Paper 2291.
    # https: // tigerprints.clemson.edu / cgi / viewcontent.cgi?referer = https: // www.google.com / & httpsredir = 1 & article = 3296 & context = all_theses

    # calculate wind pressure
    K_z = 2.01 * (z / z_g) ** (2 / a)  # exposure factor
    K_d = 0.95  # wind directionality factor
    K_zt = 1  # topographic factor
    V = 70  # critical velocity in m/s
    wind_pressure = 0.613 * K_z * K_zt * K_d * V ** 2

    # calculate wind loads of each component
    G = 0.85  # gust factor
    C_f = 0.8  # coefficient of force
    F = wind_pressure * G * C_f * A_f

    # calculate moment from each component at base of tower
    M = F * L

    # get total lateral load (N) and moment (N * m)
    F_d_tot = F.sum()
    M_tot = M.sum()

    # calculate dead load in N
    g = 9.8  # m / s ^ 2
    F_vert = component_data['Weight tonne'].sum() * g * kg_per_tonne

    foundation_loads = {'F_vert': F_vert,
                        'F_d_tot': F_d_tot,
                        'M_tot': M_tot}

    return foundation_loads


def determine_foundation_size(foundation_loads, buoyant_design, type_of_tower):
    """
    Calculates the radius of a round, raft foundation
    Assumes foundation made of concrete with 1 m thickness

    :param foundation_loads: dictionary of foundation loads
    :param buoyant_design: flag for buoyant design - currently unused
    :param type_of_tower: flag for type of tower - currently unused
    :return:
    """

    F_vert = foundation_loads['F_vert']
    F_d_tot = foundation_loads['F_d_tot']
    M_tot = foundation_loads['M_tot']

    # get radius of foundation based on vertical loads
    t = 1  # assume foundation thickness equals 1 m
    density_material = 2403  # density of concrete in kg / m^3
    SF = 1.7  # safety factor
    diam_base = 12  # diameter at base of tower in m
    R = math.sqrt(((F_vert / SF) / (math.pi * (diam_base / 2) ** 2)) / (density_material / SF * math.pi * t))

    # check to make sure sliding loads are satisfied
    sliding_loads_ok = abs(math.tan(25) * F_vert) > F_d_tot

    # check to make sure overturning moment is satisfied
    overturn_ok = (F_vert * diam_base / 2) > M_tot

    if overturn_ok & sliding_loads_ok:
        foundation_volume = math.pi * R ** 2 * t
    else:
        # todo: develop methodology for calculating size based on sliding and overturning loads
        print('Error calculating foundation size')

    return foundation_volume


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

