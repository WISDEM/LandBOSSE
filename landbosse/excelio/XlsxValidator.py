import pandas as pd

class XlsxValidator:
    """
    XlsxValidator is for comparing the results of a previous model run
    to the results of a current model run.
    """

    @classmethod
    def compare_expected_to_actual(cls, expected_xlsx, actual_module_type_operation_list):
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
        actual_df = pd.DataFrame(actual_module_type_operation_list)
        print(actual_df)
