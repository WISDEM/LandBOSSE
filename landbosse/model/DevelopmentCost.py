import traceback
from .CostModule import CostModule
import pandas as pd
import math

class DevelopmentCost(CostModule):
    """
    **DevelopmentCost.py

    -Created by Parangat Bhaskar on June 30, 2019

    Creating a simple DevelopmentCost module for now. This module reads in a user input from the detailed input Excel
    file and outputs this in the detailed output excel file.

    """

    def __init__(self, input_dict, output_dict, project_name):
        self.input_dict = input_dict
        self.output_dict = output_dict
        self.project_name = project_name

    def calculate_costs(self):
        """
        Sets the total cost for development.
        Right now these values are defined by the user. Methods could be modified to calculate internally at a later time.

        self.input_dict['development_df'] used as input

        Returns
        ------------------------------------
        total_development_cost : pd.DataFrame
            data frame with total development cost by type of cost (e.g., Labor)
        """

        # get total development cost dataframe from development cost user input
        total_development_cost = self.input_dict['development_df']

        self.output_dict['total_development_cost'] = total_development_cost

        return total_development_cost

    def outputs_for_detailed_tab(self):
        """
        Creates a list of dictionaries which can be used on their own or
        used to make a dataframe.

        Must be called after self.run_module()

        Returns
        -------
        list(dict)
            A list of dicts, with each dict representing a row of the data.
        """

        result = []
        module = type(self).__name__
        for row in self.output_dict['total_development_cost'].itertuples():
            dashed_row = '{} <--> {} <--> {}'.format(row[1], row[3], math.ceil(row[2]))
            result.append({
                'unit': '',
                'type': 'dataframe',
                'variable_df_key_col_name': 'Type of Cost <--> Phase of Construction <--> Cost in USD ',
                'value': dashed_row,
                'last_number': row[2]
            })

        for _dict in result:
            _dict['project_id_with_serial'] = self.project_name
            _dict['module'] = module

        self.output_dict['development_cost_csv'] = result
        return result

    def run_module(self):
        """
        Runs the DevelopmentCost module and populates the IO dictionaries with calculated values.

        """

        try:
            self.calculate_costs()
            self.outputs_for_detailed_tab()
            self.output_dict['development_module_type_operation'] = self.outputs_for_costs_by_module_type_operation(
                input_df=self.output_dict['total_development_cost'],
                project_id=self.project_name,
                total_or_turbine=True
            )
            return 0, 0  # module ran successfully

        except Exception as error:
            traceback.print_exc()
            print(f"Fail {self.project_name} DevelopmentCost")
            return 1, error  # module did not run successfully


