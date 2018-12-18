
"""
SubstationCost.py
Created by Annika Eberle and Owen Roberts on Dec. 17, 2018

Calculates the costs associated with substations for land-based wind projects
(module is currently based on curve fit of empirical data)

Get project size (project_size = num_turbines * turbine_rating_kilowatt / kilowatt_per_megawatt)
Get interconnect voltage

Return total substation costs

"""

import math
import pandas as pd


def calculate_costs(interconnect_voltage, project_size):
    """

    :param interconnect_voltage: voltage of interconnection in kV
    :param project_size: size of project in MW
    :return:
    """

    substation_cost = 11652 * (interconnect_voltage + project_size) + 11795 * (project_size ** 0.3549) + 1526800

    # because empirical fit, put data into "Other" category within cost dataframe
    substation_cost_output = pd.DataFrame([['Substation', 'Other', substation_cost]], columns=['Phase of construction', 'Type of cost', 'Cost USD'])

    return substation_cost_output
