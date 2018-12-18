
"""
CollectionCost.py
Created by Annika Eberle and Owen Roberts on Dec. 17, 2018

Calculates the costs associated with collection systems for land-based wind projects
(module is currently based on curve fit of empirical data)

Get toggle for pad mount transformer
Get number of turbines
Get project size
Get rotor diameter
Get MV thermal backfill and overhead collector distances
Get percent rock trenching

Return total collection system costs

"""

import pandas as pd


def calculate_costs(pad_mount_transformer, num_turbines, project_size, rotor_diameter, MV_thermal_backfill_mi,
                    rock_trenching_percent, MV_overhead_collector_mi):
    """

    :param pad_mount_transformer: Boolean for pad mount transformer requirements
    :param num_turbines: number of turbines
    :param project_size: project size in MW
    :param rotor_diameter: rotor diameter in meters
    :param MV_thermal_backfill_mi: distance for thermal backfill in miles
    :param rock_trenching_percent: percent of rock trenching (unitless)
    :param MV_overhead_collector_mi: distance for overhead collectors in miles
    :return: total collection system costs
    """

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

    collection_cost = electrical_installation + electrical_materials

    collection_cost_output = pd.DataFrame([['Collection system', 'Other', collection_cost]], columns=['Phase of construction', 'Type of cost', 'Cost USD'])

    return collection_cost_output