"""
ManagementCost.py
Created by Annika Eberle and Owen Roberts on Feb. 28, 2018

Calculates the management costs associated with balance of system for land-based wind projects
(items in brackets are not yet implemented)

Get project value
[Get builder size]
Get number of turbines
Get turbine rating
[Get region]

Calculate project size (project_size = num_turbines * turbine_rating_kilowatt / kilowatt_per_megawatt)

Get regional values from database/lookup tables for the following parameters
    Regulatory environment
    Environmental characteristics
    Infrastructure interface
    Soil type
    Rock type

Calculate management costs by type (variables in brackets are not yet implemented)
    Calculate insurance costs based on project value, [builder size, and project size]
    Calculate construction permitting costs based on [site-specific regulations,
        site-specific environmental characteristics, and site-specific interface with public infrastructure]
    Calculate bonding costs based on project size [and builder size]
    Calculate project management costs based on project size and [site-specific interface with public infrastructure]
    Calculate mark-up and contingency costs based on project value [and builder size]
    Calculate site-specific engineering costs for foundations and collection system

Sum management costs over all types to get total costs

Return total management costs

"""

import math
import pandas as pd
import numpy as np


def calculate_costs(project_value, foundation_cost, num_hwy_permits, construction_time_months,
                    markup_constants, num_turbines, project_size, hub_height, num_access_roads):
    """
    Calculate management costs by type (insurance, construction permitting, bonding, project management,
    markup and contingency, and site-specific engineering) and then sum to get total

    :param project_value: float that represents the sum of all other BOS costs (e.g., roads, foundations, erection)
    :param foundation_cost: float that equals the foundation costs for the project
    :param num_hwy_permits: integer that equals the number of highway permits needed for the project
    :param construction_time_months: float that equals the project duration (in months)
    :param markup_constants: dictionary of markup and contingency costs that can be set by user
    :param num_turbines: integer number of turbines for project
    :param project_size: float representing the size of the project in megawatts
    :return: total management costs
    """

    # Calculate costs by type
    insurance_cost = insurance(project_value=project_value)
    construction_permitting_cost = construction_permitting(foundation_cost=foundation_cost,
                                                           num_hwy_permits=num_hwy_permits)
    bond_cost = bonding(project_value=project_value)
    project_management_cost = project_management(construction_time_months)
    markup_contingency_cost = markup_contingency(markup_constants=markup_constants,
                                                 project_value=project_value)
    development_engineering_cost = engineering_foundations_collection_sys(num_turbines=num_turbines,
                                                                          project_size=project_size)
    met_mast_cost = met_mast(project_size=project_size,
                             hub_height=hub_height)
    site_security_cost = site_security(project_size=project_size,
                                       num_access_roads=num_access_roads,
                                       construction_time_months=construction_time_months)
    site_facility_cost = site_facility(project_size=project_size)

    # Sum management costs over all types
    total_management_cost = insurance_cost + construction_permitting_cost + bond_cost + project_management_cost + \
                            markup_contingency_cost + development_engineering_cost + met_mast_cost + \
                            site_security_cost + site_facility_cost

    total_management_cost = pd.DataFrame([[total_management_cost]], columns=['Management cost USD'])

    return total_management_cost


def insurance(project_value):
    """
    Calculate insurance costs based on project value, builder size, and project size. Includes:

    Builder's risk
    General liability
    Umbrella policy
    Professional liability

    :param project_value: float that represents the sum of all other BOS costs (e.g., roads, foundations, erection)
    :return: insurance costs
    """
    # Calculate insurance costs based on project value, [builder size, and project size]
    insurance_cost = project_value / 1000 * 5.6

    return insurance_cost


def construction_permitting(foundation_cost, num_hwy_permits):
    """
    Calculate construction permitting costs based empirical data from industry.
    Includes:

    Building and highway permits

    :param foundation_cost: float that equals the foundation costs for the project
    :param num_hwy_permits: integer that equals the number of highway permits needed for the project
    :return: construction permitting cost
    """

    # todo: add relationship to site-specific regulations, environmental characteristics, and public infrastructure
    building_permits = 0.02 * foundation_cost['Cost USD'].sum()
    highway_permits = 20000 * num_hwy_permits

    construction_permitting_cost = building_permits + highway_permits

    return construction_permitting_cost


def bonding(project_value):
    """
    Calculate bonding costs based on project size based on empirical data from industry.

    :param project_value: float that represents the sum of all other BOS costs (e.g., roads, foundations, erection)
    :return: bonding cost
    """

    # Calculate bonding costs based on project size
    # todo: add relationship to builder size
    performance_bond_cost = project_value / 1000 * 10

    return performance_bond_cost


def project_management(construction_time_months):
    """
    Calculate project management costs based on project size based on empirical data from industry.
    Includes:

    Project manager and assistant project manager for site
    Site managers for civil, electrical, and erection
    QA/QC management
    QA/QC inspections for civil, structural, electrical, and mechanical
    Administrative support for the site
    Health and safety supervisors
    Environmental supervisors
    Office equipment & materials
    Site radios, communication, and vehicles
    Management team per diem and travel
    Legal and public relations

    :param construction_time_months: float that equals the project duration (in months)
    :return: project management cost
    """

    # Calculate project management costs based on project size and
    # todo: add relationship to site-specific interface with public infrastructure
    if construction_time_months < 28:
        project_management_cost = (53.333 * construction_time_months ** 2 -
                                   3442 * construction_time_months +
                                   209542) * (construction_time_months + 2)
    else:
        project_management_cost = (construction_time_months + 2) * 155000

    return project_management_cost


def markup_contingency(markup_constants, project_value):
    """
    Calculate mark-up and contingency costs based on project value based on empirical data from industry.
    Includes:

    Contingency
    Warranty management
    Sales and use tax
    Overhead
    Profit margin

    :param markup_constants: dictionary of markup and contingency costs that can be set by user
    :param project_value: float that represents the sum of all other BOS costs (e.g., roads, foundations, erection)
    :return: mark-up and contingency costs
    """

    # Calculate mark-up and contingency costs based on project value
    # todo: add relationship to builder size
    markup_contingency_cost = (markup_constants['contingency'] + markup_constants['warranty_management'] +
                               markup_constants['sales_and_use_tax'] + markup_constants['overhead'] +
                               markup_constants['profit_margin']) * project_value

    return markup_contingency_cost


def engineering_foundations_collection_sys(num_turbines, project_size):
    """
    Calculate site-specific engineering costs for foundations and collection system
    based on empirical data from industry.

    :param num_turbines: integer number of turbines for project
    :param project_size: float representing the size of the project in megawatts
    :return: site-specific engineering costs (development_engineering_costs)
    """

    if project_size < 200:
        development_engineering_cost = 7188.5 * num_turbines + \
                                            round(3.4893 * math.log(num_turbines) - 7.3049, 0) * 16800 + \
                                            161675 + 4000
    else:
        development_engineering_cost = 7188.5 * num_turbines + \
                                            round(3.4893 * math.log(num_turbines) - 7.3049, 0) * 16800 + \
                                            2 * 161675 + 4000
    return development_engineering_cost


def site_facility(project_size):
    """
    Uses empirical data to estimate cost of building O&M facility, including

    Building design and construction
    Drilling and installing a water well, including piping
    Electric power for a water well
    Septic tank and drain field

    :param project_size: project size in megawatts (MW)
    :return: cost of O&M building in USD
    """
    building_area_df = pd.DataFrame([[0, 200, 3000], [200, 500, 5000], [500, 800, 7000], [800, 1000, 9000], [1000, 5000, 12000]],
                                  columns=['Size Min (MW)', 'Size Max (MW)', 'Building area (sq. ft.)'])
    building_area = building_area_df[(building_area_df['Size Max (MW)'] > project_size) &
                                     (building_area_df['Size Min (MW)'] <= project_size)]['Building area (sq. ft.)']

    site_facility_cost = float(building_area) * 125 + 176125

    return site_facility_cost


def site_security(project_size, num_access_roads, construction_time_months):
    """
    Uses empirical data to estimate cost of site security, including

    Constructing and reinstating the compound
    Constructing and reinstating the batch plant site
    Setting up and removing the site offices for the contractor, turbine supplier, and owner
    Restroom facilities
    Electrical and telephone hook-up
    Monthly office costs
    Signage for project information, safety and directions
    Cattle guards and gates

    :param project_size: project size in megawatts (MW)
    :param num_access_roads: number of access roads
    :param construction_time_months: duration of construction in months
    :return: cost of site security in USD
    """
    if project_size > 30:
        adder = 90000
        if project_size > 100:
            multiplier = 10
        else:
            multiplier = 5
    else:
        adder = 0
        multiplier = 3

    site_security_cost = ((num_access_roads * 9825) + (29850 * construction_time_months) + (multiplier * 30000) + adder
                          + (project_size / 5 * 300) + 62400)

    return site_security_cost


def met_mast(project_size, hub_height):
    """
    Uses empirical data to estimate cost of permanent and temporary met masts and power performance

    :param project_size: project size in megawatts (MW)
    :param hub_height: hub height in meters
    :return: cost of met masts and power performance in USD
    """

    if (project_size >= 30) & (project_size <= 100):
        num_perm_met_mast = 2
        num_temp_met_mast = 2
    elif (project_size > 100) & (project_size <= 300):
        num_perm_met_mast = 2
        num_temp_met_mast = 4
    elif project_size > 300:
        num_perm_met_mast = round(project_size / 100)
        num_temp_met_mast = round(project_size / 100) * 2
    else:
        num_perm_met_mast = 1
        num_temp_met_mast = 1

    if hub_height < 90:
        multiplier_perm = 232600
        multiplier_temp = 92600
    else:
        multiplier_perm = 290000
        multiplier_temp = 116800

    met_mast_cost = (num_perm_met_mast * multiplier_perm) + (num_temp_met_mast * multiplier_temp) + 200000

    return met_mast_cost
