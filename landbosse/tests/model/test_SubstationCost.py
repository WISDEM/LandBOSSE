from unittest import TestCase
import pandas as pd
import pytest

from landbosse.model import SubstationCost


class TestSubstationCost(TestCase):

    def setUp(self):
        self.input_dict = dict()
        self.input_dict['interconnect_voltage_kV'] = 1
        self.input_dict['project_size_megawatts'] = 1   #MW
        self.project_name = 'Project_1'
        self.output_dict = dict()


    def test_SubstationCostModule(self):
        """
        Black box test to check whether module is ran successfully or not
        """
        run_SubstationCost = SubstationCost(input_dict=self.input_dict, output_dict=self.output_dict, project_name=self.project_name)
        trial_run = run_SubstationCost.run_module()


        if trial_run[0] == 0 :
            print('\n\n================== MODULE EXECUTION SUCCESS =========================\n')
            print(' SubstationCost module ran successfully. See the list of inputs'
                  '\n and outputs below used by the module in its calculations:')
            print( '\n=====================================================================\n')


        elif trial_run[0] == 1 :
            print('\n\n================== MODULE EXECUTION FAILURE ==================\n')
            print(' SubstationCost module failed to run successfully. See the list'
                  '\n of inputs below used by the module in its calculations:')
            print('\n================================================================\n')


        print('\nGiven below is the set of inputs fed into SubstationCost module:\n')
        for key, value in self.input_dict.items():
            print(key, ':', value)

        if trial_run[0] == 0:  # Only print outputs if module ran successfully.
            print('\nGiven below is the set of outputs calculated by the SubstationCost module:\n')
            for key, value in self.output_dict.items():
                if isinstance(value, pd.DataFrame):
                    print('\nNow printing DataFrame ->', key, ':\n', value)
                else:
                    print(key, ':', value)