from collections import OrderedDict
import os

import pandas as pd

from ..model import Manager
from .filename_functions import landbosse_input_dir
from .XlsxReader import XlsxReader


class XlsxManagerRunner:
    """
    This class runs a new instance of Manager for each project listed
    in the project_xlsx file.

    This class is meant to be subclassed depending on whether a serial
    or parallel manager runner is needed.
    """

    def run_from_project_list_xlsx(self, projects_xlsx, log):
        """
        This function runs all the scenarios in the projects_xlsx file. It creates
        the OrderedDict that holds the results of all the runs. See the return
        section below for more details on what the OrderedDict contains.

        This method is meant to be overriden by subclasses. If this method is
        called directly on this class, a NotImplementedError is raised. However, this
        docstring does specify the contract that the inheriting class should raise.

        Parameters
        ----------
        log : logger
            A logger from Pythons library loger.get_logger() for debug output
            messages.

        projects_xlsx : str
            A path name (preferably created with os.path.join()) specific to the
            operating system that is the main input .xlsx file that controls
            running of all the projects. Crucially, this file contains names of
            other. It is recommended that all input file be kept in the same
            input directory. Each line of projects_xlsx becomes a project_series.

        Returns
        -------
        OrderedDict or dict, list
            First element of tuple is an ordered dict that is the result of
            all the runs. Each key is the name of a project and each value
            is the output dictionary of that project. The second element
            is the list of rows for the csv. The third element is the list
            of costs for the spreadsheets. For the first element, serial
            processes implement an OrderedDict (because order can be guaranteed)
            and for the second element processes implement a dict (because
            order cannot be guaranteed).

        Raises
        ------
        NotImplementedError
            NotImplementedError is raised if the method is called on the
            superclass.
        """
        raise NotImplementedError('run_from_project_list_xlsx() can only be called on subclasses')

    def extract_module_type_operation_lists(self, runs_dict):
        """
        This method extract all the cost_by_module_type_operation lists for
        output in an Excel file.

        It finds values for the keys ending in '_module_type_operation'. It
        then concatenates them
        together so they can be easily written to a .csv or .xlsx

        Parameters
        ----------
        runs_dict : dict
            Values are the names of the projects. Keys are the lists of
            dictionaries that are lines for the .csv

        Returns
        -------
        list
            List of dicts to write to the .csv.
        """
        result = []
        for project_results in runs_dict.values():
            for key, value in project_results.items():
                if key.endswith('_module_type_operation'):
                    result.extend(value)
        return result

    def extract_csv_lists(self, runs_dict):
        """
        This method extract all .csv lists from the OrderDict of runs to output
        into an Excel or .csv file.

        It finds values for the keys ending in '_csv'. It then concatenates them
        together so they can be easily written to a .csv, .xlsx or other
        columnar format. (The actual writing is left to other functions.

        Parameters
        ----------
        runs_dict : dict
            Values are the names of the projects. Keys are the lists of
            dictionaries that are lines for the .csv

        Returns
        -------
        list
            List of dicts to write to the .csv.
        """
        runs_for_csv = []
        for project_results in runs_dict.values():
            for key, value in project_results.items():
                if key.endswith('_csv'):
                    runs_for_csv.extend(value)
        return runs_for_csv
