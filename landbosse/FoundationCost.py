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
import pandas as pd
import numpy as np
import WeatherDelay as WD

# constants
kg_per_tonne = 1000
cubicm_per_cubicft = 0.0283168
steel_density = 9490  # kg / m^3
cubicyd_per_cubicm = 1.30795
ton_per_tonne = 0.907185


def calculate_foundation_loads(component_data):
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

    # get coefficient of drag
    C_d = component_data['Coeff drag']

    # get lever arm
    L = component_data['Lever arm m']

    # get multipliers for tower and rotor
    multiplier_rotor = component_data['Multplier drag rotor']
    multiplier_tower = component_data['Multiplier tower drag']

    # Equations from Shrestha, S. 2015. DESIGN AND ANALYSIS OF FOUNDATION FOR ONSHORE TALL WIND TURBINES. All Theses. Paper 2291.
    # https: // tigerprints.clemson.edu / cgi / viewcontent.cgi?referer = https: // www.google.com / & httpsredir = 1 & article = 3296 & context = all_theses
    # Also from
    # http://ir.uiowa.edu/cgi/viewcontent.cgi?article=2427&context=etd

    # calculate wind pressure
    K_z = 2.01 * (z / z_g) ** (2 / a)  # exposure factor
    K_d = 0.95  # wind directionality factor
    K_zt = 1  # topographic factor
    V = 60  # critical velocity in m/s
    wind_pressure = 0.613 * K_z * K_zt * K_d * V ** 2

    # calculate wind loads on each tower component
    G = 0.85  # gust factor
    C_f = 0.4  # coefficient of force
    F_t = (wind_pressure * G * C_f * A_f) * multiplier_tower

    # calculate drag rotor
    rho = 1.225  # air density in kg/m^3
    F_r = (0.5 * rho * C_d * A_f * V ** 2) * multiplier_rotor

    F = (F_t + F_r)

    # calculate dead load in N
    g = 9.8  # m / s ^ 2
    F_dead = component_data['Weight tonne'].sum() * g * kg_per_tonne / 1.15  # scaling factor to adjust dead load for uplift

    # calculate moment from each component at base of tower
    M_overturn = F * L
    M_resist = F_dead * 5  # resising moment is function of dead weight and foundation diameter (this equation assumes foundation radius is on the order of 5 meters (diam = 10 m))

    # get total lateral load (N) and moment (N * m)
    F_lat = F.sum()
    M_tot = (M_overturn.sum() - M_resist) * 1.8  # safety factor of 1.8 for moment only

    foundation_loads = {'F_dead': F_dead,
                        'F_lat': F_lat,
                        'M_tot': M_tot}

    return foundation_loads


def determine_foundation_size(foundation_loads):
    """
    Calculates the radius of a round, raft foundation
    Assumes foundation made of concrete with 1 m thickness

    :param foundation_loads: dictionary of foundation loads (forces in N; moments in N*m)
    :param buoyant_design: flag for buoyant design - currently unused
    :param type_of_tower: flag for type of tower - currently unused
    :return:
    """

    # get foundation loads and convert N to kN
    F_dead = foundation_loads['F_dead']
    F_lat = foundation_loads['F_lat']
    M_tot = foundation_loads['M_tot']

    foundation_cubic_meters = 1.012 * (0.0000034 * (M_tot * (M_tot / (71 * F_lat)) * (M_tot / (20 * F_dead))) + 168) / cubicyd_per_cubicm

    return foundation_cubic_meters


def estimate_material_needs(foundation_volume, num_turbines):
    """
    Estimate amount of material based on foundation size and number of turbines

    :param foundation_volume: volume of foundation material in m^3
    :param num_turbines: number of turbines
    :return: table of material needs
    """

    steel_mass = (foundation_volume * 0.012 * steel_density / kg_per_tonne * ton_per_tonne * num_turbines)
    concrete_volume = foundation_volume * 0.985 * cubicyd_per_cubicm * num_turbines

    material_needs = pd.DataFrame([['Steel - rebar', steel_mass, 'ton (short)'],
                                   ['Concrete 5000 psi', concrete_volume, 'cubic yards'],
                                   ['Excavated dirt', foundation_volume * 3.2 * cubicyd_per_cubicm * num_turbines, 'cubic_yards'],
                                   ['Backfill', foundation_volume * 3.2 * cubicyd_per_cubicm * num_turbines, 'cubic_yards']],
                                  columns=['Material type ID', 'Quantity of material', 'Units'])
    return material_needs


def estimate_construction_time(throughput_operations, material_needs, duration_construction):
    """

    :param material_needs:
    :param duration_construction:
    :return:
    """

    foundation_construction_time = duration_construction * 1/3
    operation_data = throughput_operations.where(throughput_operations['Module'] == 'Foundations').dropna(thresh=4)
    operation_data = pd.merge(material_needs, operation_data, on=['Material type ID'], how='outer')
    operation_data['Number of days'] = operation_data['Quantity of material'] / operation_data['Daily output']
    operation_data['Number of crews'] = np.ceil((operation_data['Number of days'] / 30) / foundation_construction_time)
    operation_data['Cost USD without weather delays'] = operation_data['Quantity of material'] * operation_data['Rate USD per unit']

    # if more than one crew needed to complete within construction duration then assume that all construction happens
    # within that window and use that timeframe for weather delays; if not, use the number of days calculated
    operation_data['time_construct_bool'] = operation_data['Number of days'] > foundation_construction_time * 30
    boolean_dictionary = {True: foundation_construction_time * 30, False: np.NAN}
    operation_data['time_construct_bool'] = operation_data['time_construct_bool'].map(boolean_dictionary)
    operation_data['Time construct days'] = operation_data[['time_construct_bool', 'Number of days']].min(axis=1)

    return operation_data


def calculate_weather_delay(weather_window, duration_construction, start_delay, critical_wind_speed,
                            operational_hrs_per_day):
    """
    Calculates wind delay for foundations.

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
                                         critical_wind_speed=critical_wind_speed)
    wind_delay = pd.DataFrame(wind_delay)

    # if greater than 4 hour delay, then shut down for full day (10 hours)
    wind_delay[(wind_delay > 4)] = 10
    wind_delay_time = float(wind_delay.sum())

    return wind_delay_time


def calculate_costs(input_data, num_turbines, construction_time, weather_window, operational_hrs_per_day, overtime_multiplier):
    """

    :param input_data:
    :param num_turbines:
    :param construction_time:
    :param weather_window:
    :param operational_hrs_per_day:
    :return:
    """

    foundation_loads = calculate_foundation_loads(component_data=input_data['components'])
    foundation_volume = determine_foundation_size(foundation_loads=foundation_loads)
    material_vol = estimate_material_needs(foundation_volume=foundation_volume, num_turbines=num_turbines)
    material_data = pd.merge(material_vol, input_data['material_price'], on=['Material type ID'])
    material_data['Cost USD'] = material_data['Quantity of material'] * pd.to_numeric(material_data['Material price USD per unit'])

    operation_data = estimate_construction_time(throughput_operations=input_data['rsmeans'],
                                                material_needs=material_vol,
                                                duration_construction=construction_time)

    wind_delay = calculate_weather_delay(weather_window=weather_window,
                                         duration_construction=operation_data['Time construct days'].max(skipna=True),
                                         start_delay=0,
                                         critical_wind_speed=13,
                                         operational_hrs_per_day=operational_hrs_per_day)

    wind_multiplier = 1 + (wind_delay / operational_hrs_per_day) / operation_data['Time construct days'].max(skipna=True)

    labor_equip_data = pd.merge(material_vol, input_data['rsmeans'], on=['Material type ID'])
    per_diem = operation_data['Number of workers'] * operation_data['Number of crews'] * (operation_data['Time construct days'] + round(operation_data['Time construct days'] / 7)) * 144
    where_are_NaNs = np.isnan(per_diem)
    per_diem[where_are_NaNs] = 0
    labor_equip_data['Cost USD'] = (labor_equip_data['Quantity of material'] * labor_equip_data['Rate USD per unit'] * overtime_multiplier + per_diem) * wind_multiplier

    foundation_cost = labor_equip_data[['Operation ID', 'Type of cost', 'Cost USD']]

    material_costs = pd.DataFrame(columns=['Operation ID', 'Type of cost', 'Cost USD'])
    material_costs['Operation ID'] = material_data['Material type ID']
    material_costs['Type of cost'] = 'Materials'
    material_costs['Cost USD'] = material_data['Cost USD']

    foundation_cost = foundation_cost.append(material_costs)

    # calculate mobilization cost as percentage of total foundation cost
    mob_cost = pd.DataFrame([['Mobilization', 'Mobilization', foundation_cost['Cost USD'].sum() * 0.1]], columns=['Operation ID', 'Type of cost', 'Cost USD'])
    foundation_cost = foundation_cost.append(mob_cost)

    total_foundation_cost = foundation_cost.groupby(by=['Type of cost']).sum().reset_index()
    total_foundation_cost['Phase of construction'] = 'Foundations'

    return total_foundation_cost

