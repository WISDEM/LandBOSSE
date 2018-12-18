
"""
DevelopmentCost.py
Created by Annika Eberle and Owen Roberts on Dec. 17, 2018

Calculates the development costs associated land-based wind projects
(module is currently based on user input)

Get development cost from user

Return total development costs data frame

"""

import pandas as pd


def calculate_costs(development_cost):
    """

    :param development_cost: development cost in USD (from user)
    :return: development cost data frame
    """

    # store development cost from user in data frame
    development_cost_output = pd.DataFrame([['Development', 'Development', development_cost]], columns=['Phase of construction', 'Type of cost', 'Cost USD'])

    return development_cost_output