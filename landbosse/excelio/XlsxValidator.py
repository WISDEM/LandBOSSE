import pandas as pd

class XlsxValidator:
    """
    XlsxValidator is for comparing the results of a previous model run
    to the results of a current model run.
    """

    def compare_expected_to_actual(self, expected_xlsx, actual_module_type_operation_list):
        """
        This compares the expected costs as calculated by a prior model run
        with the actual results from a current model run.

        It compares the results row by row and prints any differences.

        Parameters
        ----------
        expected_xlsx : str
            The absolute filename of the expected output .xlsx file.

        actual_module_type_operation_list : str
            The module_type_operation_list as returned by a subclass of
            XlsxManagerRunner.

        Returns
        -------
        bool
            True if the expected and actual results are equal. It returns
            False otherwise.
        """
        # First, make the list of dictionaries into a dataframe, and drop
        # the raw_cost and raw_cost_total_or_per_turbine columns.
        actual_df = pd.DataFrame(actual_module_type_operation_list)
        actual_df.drop(['raw_cost', 'raw_cost_total_or_per_turbine'], axis=1, inplace=True)
        expected_df = pd.read_excel(expected_xlsx, 'costs_by_module_type_operation')
        expected_df.rename(columns={
            'Project ID': 'project_id',
            'Number of turbines': 'num_turbines',
            'Turbine rating MW': 'turbine_rating_MW',
            'Module': 'module',
            'Operation ID': 'operation_id',
            'Type of cost': 'type_of_cost',
            'Cost per turbine': 'cost_per_turbine',
            'Cost per project': 'cost_per_project',
            'USD/kW per project': 'usd_per_kw_per_project'
        }, inplace=True)

        # Result will hold all the True/False equalities for each row
        result = []

        # Iterate over each row, reporting results as they come up.
        for (idx, expected_row), (_, actual_row) in zip(expected_df.iterrows(), actual_df.iterrows()):
            equal = self._compare_rows(expected_row, actual_row)
            if equal:
                print(f'{idx} PASS')
            else:
                print(f'------------------ {idx} FAIL --------------------')
                print('EXPECTED')
                print(expected_row)
                print('ACTUAL')
                print(actual_row)
                print('------------------------------------------------')
            result.append(equal)

        # Return True if and only if all expected/actual comparisons were True
        return all(result)

    def _compare_rows(self, expected, actual, ndigits=3):
        """
        This compares two pandas.Series for equality while handling
        rounding errors and string comparisons gracefully.

        Parameters
        ----------
        expected : pandas.Series
            The expected values in the series

        actual : pandas.Series
            The actual values in the series

        ndigits : int
            The number of digits after the decimal place to round to.

        Returns
        -------
        bool
            True if the rows have the same data, False otherwise.
        """
        sorted_expected = expected.sort_index()
        sorted_actual = actual.sort_index()
        for (_, expected_item), (_, actual_item) in zip(sorted_expected.iteritems(), sorted_actual.iteritems()):
            if type(actual_item) == float and type(expected_item) == float:
                match = round(expected_item, ndigits) == round(actual_item, ndigits)
            else:
                match = expected_item == actual_item
            if not match:
                return False
        return True
