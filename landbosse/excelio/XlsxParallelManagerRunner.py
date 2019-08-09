import os
from concurrent import futures
import logging
import sys

import pandas as pd

from ..model import Manager
from .filename_functions import landbosse_input_dir
from .XlsxReader import XlsxReader
from .XlsxManagerRunner import XlsxManagerRunner


class XlsxParallelManagerRunner(XlsxManagerRunner):
    """
    This subclass implementation of XlsxManagerRunner runs all projects
    with a ProcessPoolExecutor.
    """

    def run_from_project_list_xlsx(self, projects_xlsx, log):
        """
        This function runs all the scenarios in the projects_xlsx file. It creates
        the OrderedDict that holds the results of all the runs. See the return
        section below for more details on what the OrderedDict contains.

        This is a concrete implementation of the super class method.

        Parameters
        ----------
        log : logger
            A logger from Pythons library logger.get_logger() for debug output
            messages.

        projects_xlsx : str
            A path name (preferably created with os.path.join()) specific to the
            operating system that is the main input .xlsx file that controls
            running of all the projects. Crucially, this file contains names of
            other. It is recommended that all input file be kept in the same
            input directory.

        Returns
        -------
        dict, list, module_type_operation_lists
            First element of tuple is a dict that is the result of
            all the runs. Each key is the name of a project and each value
            is the output dictionary of that project. The second element
            is the list of rows for the csv. The third element is the list
            of costs for the spreadsheets.
        """
        # Load the project list
        projects = pd.read_excel(projects_xlsx, 'Sheet1')
        log.debug('>>> Project list loaded')

        # Prep all task for the executor
        all_tasks = []
        for _, project_series in projects.iterrows():
            project_id = project_series['Project ID']
            task = dict()
            task['input_xlsx'] = os.path.join(landbosse_input_dir(), 'project_data', '{}.xlsx'.format(project_id))
            task['project_id'] = project_series['Project ID']
            task['project_series'] = project_series
            all_tasks.append(task)

        # Execute every project
        # res = executor.map(download_one, sorted(cc_list))
        with futures.ProcessPoolExecutor() as executor:
            executor_result = executor.map(run_single_project, all_tasks)

        # Get the output dictionary ready
        runs_dict = {project_id: result for project_id, result in executor_result}

        # .csv lists for all runs
        csv_lists = self.extract_csv_lists(runs_dict)
        module_type_operation_lists = self.extract_module_type_operation_lists(runs_dict)

        # Return the runs for all the scenarios.
        return runs_dict, csv_lists, module_type_operation_lists


"""
The following function is deliberately defined outside of the class.
This makes it easier to think about it being a pure function for
parallel processes.
"""


def run_single_project(task_dict):
    """
    The dictionary project_definition_dict contains the following keys.

    For each process another logger is created, so that each process does
    not attempt to use the same logger.

    input_xlsx : str
        The filename for the input .xlsx that has all the dataframes
        for the for ErectionCost and FoundationCost

    project_series : pd.Series
        The series that has the non-dataframe values for each project,
        including the project name.

    project_id : str
        The string that is the name of the project.

    Basically, the map operation goes like this:

    task_dict -> master_input_dict -> master_output_dict

    Wrapped in a functional executor, this maps projects into their
    output dictionaries.

    Parameters
    ----------
    task_dict : dict
        The configuration of the task.

    Returns
    -------
    tuple : (str, dict)
        The str is the project_id. The dict is the resulting output
        dictionary.
    """
    log = logging.getLogger(__name__)
    out_hdlr = logging.StreamHandler(sys.stdout)
    out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    out_hdlr.setLevel(logging.DEBUG)
    log.addHandler(out_hdlr)
    log.setLevel(logging.DEBUG)

    input_xlsx = task_dict['input_xlsx']
    project_series = task_dict['project_series']
    project_id = task_dict['project_id']

    # Log each project
    log.debug('<><><><><><><><><><><><><><><><><><> {} <><><><><><><><><><><><><><><><><><>'.format(project_id))
    log.debug('>>> project_id: {}'.format(project_id))
    log.debug('>>> Input: {}'.format(input_xlsx))

    # Read the Excel
    xlsx_reader = XlsxReader()
    master_input_dict = xlsx_reader.read_xlsx_and_fill_defaults(input_xlsx, project_series)

    # Now run the manager and accumulate its result into the runs_dict
    output_dict = dict()
    mc = Manager(input_dict=master_input_dict, output_dict=output_dict, log=log)
    mc.execute_landbosse(project_name=project_id)
    return project_id, output_dict
