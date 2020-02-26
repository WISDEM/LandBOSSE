import os
import pandas as pd
from landbosse.excelio import XlsxReader
from landbosse.excelio.XlsxDataframeCache import XlsxDataframeCache
from landbosse.model import Manager


# Call this function - run_landbosse() - to run LandBOSSE.
# this method calls the read_data() method to read the 2 excel input files, and creates a master input dictionary from it.
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


        # make sure you call create_master_input_dictionary() as soon as labor_cost_multiplier's value is changed.
        master_input_dict = xlsx_reader.create_master_input_dictionary(project_data_sheets, project_parameters)
        master_input_dict['error'] = dict()

    output_dict = dict()
    project_id_with_serial = 'SAM_Run'

    # Manager class (1) manages the distribution of inout data for all modules and (2) executes landbosse
    mc = Manager(input_dict=master_input_dict, output_dict=output_dict)
    mc.execute_landbosse(project_id_with_serial)


    # results dictionary that gets returned by this function:
    results = dict()
    results['errors'] = []
    if master_input_dict['error']:
        for key, value in master_input_dict['error'].items():
            msg = "Error in " + key + ": " + str(value)
            results['errors'].append(msg)
    else:   # if project runs successfully, return a dictionary with results that are 3 layers deep (but 1-D)
        results['total_project_cost']                   =       output_dict['project_value_usd']

        # management cost module results:
        results['total_management_cost']                =       output_dict['total_management_cost']
        results['insurance_usd']                        =       output_dict['insurance_usd']
        results['construction_permitting_usd']          =       output_dict['construction_permitting_usd']
        results['project_management_usd']               =       output_dict['project_management_usd']
        results['bonding_usd']                          =       output_dict['bonding_usd']
        results['markup_contingency_usd']               =       output_dict['markup_contingency_usd']
        results['engineering_usd']                      =       output_dict['engineering_usd']
        results['site_facility_usd']                    =       output_dict['site_facility_usd']
        results['total_management_cost']                =       output_dict['total_management_cost']

        # development cost module results:
        results['total_development_cost']               =       output_dict['summed_development_cost']
        if 'Development labor cost USD' in output_dict:
            results['development_equipment_rental_usd'] =       master_input_dict['development_labor_cost_usd']
        results['development_labor_usd']                =       0
        results['development_material_usd']             =       0
        results['development_mobilization_usd']         =       0

        # site prep cost module results:
        results['total_sitepreparation_cost']           =       output_dict['summed_sitepreparation_cost']
        results['sitepreparation_equipment_rental_usd'] =       output_dict['collection_equipment_rental_usd']
        results['sitepreparation_labor_usd']            =       output_dict['collection_labor_usd']
        results['sitepreparation_material_usd']         =       output_dict['collection_material_usd']
        results['sitepreparation_mobilization_usd']     =       output_dict['collection_mobilization_usd']

        results['total_foundation_cost']                =       output_dict['summed_foundation_cost']
        results['foundation_equipment_rental_usd']      =       output_dict['foundation_equipment_rental_usd']
        results['foundation_labor_usd']                 =       output_dict['foundation_labor_usd']
        results['foundation_material_usd']              =       output_dict['foundation_material_usd']
        results['foundation_mobilization_usd']          =       output_dict['foundation_mobilization_usd']

        # erection cost module results:
        results['total_erection_cost']                  =       output_dict['total_cost_summed_erection']
        results['erection_equipment_rental_usd']        =       output_dict['erection_equipment_rental_usd']
        results['erection_labor_usd']                   =       output_dict['erection_labor_usd']
        results['erection_material_usd']                =       output_dict['erection_material_usd']
        results['erection_other_usd']                   =       output_dict['erection_other_usd']
        results['erection_mobilization_usd']            =       output_dict['erection_mobilization_usd']
        results['erection_fuel_usd']                    =       output_dict['erection_fuel_usd']

        # grid connection cost module results:
        results['total_gridconnection_cost']            =       output_dict['trans_dist_usd']

        #collection cost module results:
        results['total_collection_cost']                =       output_dict['summed_collection_cost']
        results['collection_equipment_rental_usd']      =       output_dict['collection_equipment_rental_usd']
        results['collection_labor_usd']                 =       output_dict['collection_labor_usd']
        results['collection_material_usd']              =       output_dict['collection_material_usd']
        results['collection_mobilization_usd']          =       output_dict['collection_mobilization_usd']

        # substation cost module results:
        results['total_substation_cost']                =       output_dict['summed_substation_cost']

    return results


# This method reads in the two input Excel files (project_list; project_1) and stores them as dataframes.
# This method is called internally in run_landbosse(), where the data read in is converted to a master input dictionary.
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




