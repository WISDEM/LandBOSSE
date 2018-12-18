
"""
TransDistCost.py
Created by Annika Eberle and Owen Roberts on Dec. 17, 2018

Calculates the costs associated with transmission and distribution for land-based wind projects
(module is currently based on curve fit of empirical data)

Get distance to interconnection
Get interconnection voltage
Get toggle for new switchyard

Return total transmission and distribution costs

"""

import pandas as pd


def calculate_costs(distance_to_interconnect, new_switchyard, interconnect_voltage):
    """

    :param distance_to_interconnect: distance to interconnection in miles
    :param new_switchyard: Boolean for new switchyard
    :param interconnect_voltage: interconnect voltage in kV
    :return: total costs for transmission and distribution
    """

    if distance_to_interconnect == 0:
        trans_dist = 0
    else:
        if new_switchyard is True:
            interconnect_adder = 18115 * interconnect_voltage + 165944
        else:
            interconnect_adder = 0
        trans_dist = ((1176 * interconnect_voltage + 218257) * (distance_to_interconnect ** (-0.1063))
                              * distance_to_interconnect) + interconnect_adder

    # because empirical fit, put data into "Other" category within cost dataframe
    trans_dist_output = pd.DataFrame([['Transmission and distribution', 'Other', trans_dist]], columns=['Phase of construction', 'Type of cost', 'Cost USD'])

    return trans_dist_output


