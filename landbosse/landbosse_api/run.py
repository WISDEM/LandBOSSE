import os
import pandas as pd
from logging import log
from datetime import datetime

from landbosse.excelio import XlsxReader
from landbosse.excelio.XlsxDataframeCache import XlsxDataframeCache
from landbosse.model import Manager
import traceback

def run_landbosse():
    input_output_path = os.path.dirname(__file__)
    os.environ["LANDBOSSE_INPUT_DIR"] = input_output_path
    os.environ["LANDBOSSE_OUTPUT_DIR"] = input_output_path

    extended_project_list_before_parameter_modifications = read_data()
    xlsx_reader = XlsxReader()

    for _, project_parameters in extended_project_list_before_parameter_modifications.iterrows():
        # If project_parameters['Project ID with serial'] is null, that means there are no
        # parametric modifications to the project data dataframes. Hence,
        # just the plain Project ID without a serial number should be used.
        if pd.isnull(project_parameters['Project ID with serial']):
            project_id_with_serial = project_parameters['Project ID']
        else:
            project_id_with_serial = project_parameters['Project ID with serial']
            # Read the project data sheets.

        project_data_basename = project_parameters['Project data file']
        project_data_sheets = XlsxDataframeCache.read_all_sheets_from_xlsx(project_data_basename)
        master_input_dict = xlsx_reader.create_master_input_dictionary(project_data_sheets, project_parameters)
        master_input_dict['error'] = dict()

    output_dict = dict()
    project_id_with_serial = 'SAM_Run'

    mc = Manager(input_dict=master_input_dict, output_dict=output_dict)
    mc.execute_landbosse(project_id_with_serial)


    results = {"total_project_cost": None,
               "total_management_cost": None,
               "total_development_cost": None,
               "total_sitepreparation_cost": None,
               "total_foundation_cost": None,
               "total_erection_cost": None,
               "total_gridconnection_cost": None,
               "total_collection_cost": None,
               "total_substation_cost": None,
                "errors": []
               }

    if master_input_dict['error']:
        for key, value in master_input_dict['error'].items():
            msg = "Error in " + key + ": " + str(value)
            results['errors'].append(msg)
    else:
        results['total_project_cost'] = output_dict['project_value_usd']
        results['total_management_cost'] = output_dict['total_management_cost']
        results['total_development_cost'] = output_dict['summed_development_cost']
        results['total_sitepreparation_cost'] = output_dict['summed_sitepreparation_cost']
        results['total_foundation_cost'] = output_dict['summed_foundation_cost']
        results['total_erection_cost'] = output_dict['total_cost_summed_erection']
        results['total_gridconnection_cost'] = output_dict['trans_dist_usd']
        results['total_collection_cost'] = output_dict['trans_dist_usd']
        results['total_substation_cost'] = output_dict['summed_substation_cost']

    return results



def read_data():
    path_to_project_list = os.path.dirname( __file__ )
    sheets = XlsxDataframeCache.read_all_sheets_from_xlsx('project_list', path_to_project_list)

    # If there is one sheet, make an empty dataframe as a placeholder.
    if len(sheets.values()) == 1:
        first_sheet = list(sheets.values())[0]
        project_list = first_sheet
        parametric_list = pd.DataFrame()

    # If the parametric and project lists exist, read them
    elif 'Parametric list' in sheets.keys() and 'Project list' in sheets.keys():
        project_list = sheets['Project list']
        parametric_list = sheets['Parametric list']

    # Otherwise, raise an exception
    else:
        raise KeyError(
            "Project list needs to have a single sheet or sheets named 'Project list' and 'Parametric list'.")

    # Instantiate and XlsxReader to assemble master input dictionary
    xlsx_reader = XlsxReader()

    # Join in the parametric variable modifications
    parametric_value_list = xlsx_reader.create_parametric_value_list(parametric_list)
    extended_project_list = xlsx_reader.outer_join_projects_to_parametric_values(project_list,
                                                                                 parametric_value_list)

    return extended_project_list



foo = run_landbosse()
print(foo)