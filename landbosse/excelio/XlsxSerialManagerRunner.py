from collections import OrderedDict
import os

import pandas as pd

from ..model import Manager
from .filename_functions import landbosse_input_dir
from .XlsxReader import XlsxReader
from .XlsxManagerRunner import XlsxManagerRunner


class XlsxSerialManagerRunner(XlsxManagerRunner):
    """
    This subclass implementation of XlsxManagerRunner runs all projects
    in a serial loop.
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
        OrderedDict, list, list, list
            First element of tuple is an ordered dict that is the result of
            all the runs. Each key is the name of a project and each value
            is the output dictionary of that project. The second element
            is the list of rows for the csv. The third element is the list
            of costs for the spreadsheets. The fourth element is the same as
            module_type_operation_lists, but every row has all the inputs
            on each row.
        """
        # Load the project list
        projects = pd.read_excel(projects_xlsx, 'Sheet1')
        log.debug('>>> Project list loaded')

        # Get the output dictionary ready
        runs_dict = OrderedDict()

        # Loop over every project
        for _, project_series in projects.iterrows():
            project_id = project_series['Project ID']
            project_data_basename = project_series['Project data file']

            # Input path for the Xlsx
            project_data_xlsx = os.path.join(landbosse_input_dir(), 'project_data', f'{project_data_basename}.xlsx')

            # Log each project
            log.debug(f'<><><><><><><><><><><><><><><><><><> {project_id} <><><><><><><><><><><><><><><><><><>')
            log.debug('>>> project_id: {}'.format(project_id))
            log.debug('>>> Project data: {}'.format(project_data_xlsx))

            # Create the master input dictionary.
            xlsx_reader = XlsxReader()
            master_input_dict = xlsx_reader.read_xlsx_and_fill_defaults(project_data_xlsx, project_series)

            # Now run the manager and accumulate its result into the runs_dict
            output_dict = dict()
            mc = Manager(input_dict=master_input_dict, output_dict=output_dict, log=log)
            mc.execute_landbosse(project_name=project_id)
            output_dict['project_series'] = project_series
            runs_dict[project_id] = output_dict

        final_result = dict()
        final_result['details_list'] = self.extract_details_lists(runs_dict)
        final_result['module_type_operation_list'] = self.extract_module_type_operation_lists(runs_dict)

        # Return the runs for all the scenarios.
        # return runs_dict, details_list, module_type_operation_list, module_type_operation_list_with_inputs
        return final_result
