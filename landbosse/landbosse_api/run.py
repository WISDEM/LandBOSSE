import os
import pandas as pd
import numpy as np
from ..excelio import XlsxReader
from ..excelio import XlsxReader
from ..excelio.WeatherWindowCSVReader import read_weather_window
from ..excelio.XlsxDataframeCache import XlsxDataframeCache
from ..model import Manager
from datetime import datetime, timedelta
from hybridbosse.LandBOSSE.landbosse.landbosse_api.turbine_scaling import nacelle_mass, \
                                            edit_nacelle_info, \
                                            hub_mass, \
                                            edit_hub_info, \
                                            blade_mass_ton, \
                                            edit_blade_info, \
                                            tower_mass, \
                                            tower_specs, \
                                            edit_tower_sections


def run_landbosse(input_dict):
    """
    Call this function - run_landbosse() - to run LandBOSSE.
    This method calls the read_data() method to read the 2 excel input files that
    are packaged with LandBOSSE, and creates a master input dictionary from it.

    The 2 excel input files packaged with LandBOSSE are:
        1. project_list.xlxs : This file defines the high level project inputs
        that define a unique wind farm project
        2. project_data_defaults.xlsx

    Parameters
        ----------
       input_dict : Python Dictionary
           This input dictionary is a required argument for this function. It
           consists of 13 required key:value pairs, and 1 optional key:value
           pair ('weather_file_path'). The key:value pairs are as follows:


                                KEY               | REQUIRED KEY? (Y/N)   | SUGGESTED SAMPLE DEFAULT VALUE  | DESCRIPTION                                               |
                ----------------------------------|-----------------------|---------------------------------|-----------------------------------------------------------|
                'interconnect_voltage_kV'         |           Y           |         137                     | Grid interconnection voltage (kV)                         |
                ---------------------------------------------------------------------------------------------------------------------------------------------------------
                'distance_to_interconnect_mi'     |           Y           |         10                      | Distance to interconnection (miles)                       |
                --------------------------------------------------------------------------------------------------------------------------------------------------------
                'num_turbines'                    |           Y           |         100                     | Total number of turbines in project                       |
                --------------------------------------------------------------------------------------------------------------------------------------------------------|
                'turbine_spacing_rotor_diameters  |           Y           |         4                       | Turbine spacing (in multiples of turbine rotor diameter)  |
                --------------------------------------------------------------------------------------------------------------------------------------------------------|
                'row_spacing_rotor_diameters'     |           Y           |         10                      | Row spacing (in multiples of turbine rotor diameter)      |
                ------------------------------------------------------------------------------------------------------------------------                                |
                'turbine_rating_MW'               |           Y           |         1.5                     | Turbine rating (MW)                                       |
                --------------------------------------------------------------------------------------------------------------------------------------------------------|
                'rotor_diameter_m'                |           Y           |         77                      | Turbine rotor diameter (meters)                           |
                --------------------------------------------------------------------------------------------------------------------------------------------------------|
                'hub_height_meters'               |           Y           |         80                      | Turbine hub height (meters)                               |
                --------------------------------------------------------------------------------------------------------------------------------------------------------|
                'wind_shear_exponent'             |           Y           |         0.2                     | Wind shear exponent                                       |
                ------------------------------------------------------------------------------------------------------------------------                                |
                'depth'                           |           Y           |         2.36                    | Turbine foundation depth (meters)                         |
                ------------------------------------------------------------------------------------------------------------------------                                |
                'rated_thrust_N'                  |           Y           |         589,000                 | Turbine rated thrust (Newtons)                            |
                ------------------------------------------------------------------------------------------------------------------------                                |
                'labor_cost_multiplier'           |           Y           |         1                       | Labor cost mutliplier                                     |
                ------------------------------------------------------------------------------------------------------------------------                                |
                'gust_velocity_m_per_s'           |           Y           |         59.50                   | 50-year max gust velocity (m/s)                           |
                --------------------------------------------------------------------------------------------------------------------------------------------------------|
                'weather_file_path'               |           N           | <OPTIONAL>Provide an            |   This is the                                             |
                                                  |                       |  absolute path to a .srw        |   weather resurce                                         |
                                                  |                       |  hourly weather file            |   that will help                                          |
                                                  |                       |  (8760 rows).                   |   determine whether                                       |
                                                  |                       |                                 |   weather based delays                                    |
                                                  |                       |  Else, default weather          |   in project construction                                 |
                                                  |                       |  file packaged with             |                                                           |
                                                  |                       |  LandBOSSE will be used.        |                                                           |
                                                  |                       |                                 |                                                           |
                                                  |                       |                                 |                                                           |
                                                  |                       |                                 |                                                           |
                --------------------------------------------------------------------------------------------------------------------------------------------------------|

        Returns
        -------
        output_dict : Python Dictionary
            Output dictionary container with balance-of-station costs calculated by the model. Following outputs are
            returned:

                        OUTPUT                                  |               KEY                    |
            ----------------------------------------------------|--------------------------------------|
            Total Management Cost                               |   total_management_cost               |
            --------------------------------------------------------------------------------------------
            Total Insurance Cost (USD)                          |   insurance_usd                       |
            --------------------------------------------------------------------------------------------
            Total Construction Permitting Cost (USD)            |   construction_permitting_usd         |
            --------------------------------------------------------------------------------------------
            Total Project Management Cost (USD)                 |   project_management_usd              |
            --------------------------------------------------------------------------------------------
            Total Bonding Cost (USD)                            |   bonding_usd                         |
            --------------------------------------------------------------------------------------------
            Total Markup Contingency Cost (USD)                 |   markup_contingency_usd              |
            --------------------------------------------------------------------------------------------
            Total Engineering Cost (USD)                        |   engineering_usd                     |
            --------------------------------------------------------------------------------------------
            Total Site Facility Cost (USD)                      |   site_facility_usd                   |
            --------------------------------------------------------------------------------------------
            Total Management Cost (USD)                         |   total_management_cost               |
            --------------------------------------------------------------------------------------------
            Total Development Cost (USD)                        |   summed_development_cost             |
            --------------------------------------------------------------------------------------------
            Total Development Labor Cost (USD)                  |   development_labor_cost_usd          |
            --------------------------------------------------------------------------------------------
            Total Site Preparation Cost (USD)                   |   summed_sitepreparation_cost         |
            --------------------------------------------------------------------------------------------
            Total Site Preparation Equipment Rental Cost (USD)  |   sitepreparation_equipment_rental_usd |
            --------------------------------------------------------------------------------------------
            Total Site Preparation Labor Cost (USD)             |   sitepreparation_labor_usd           |
            --------------------------------------------------------------------------------------------
            Total Site Preparation Material Cost (USD)          |   sitepreparation_material_usd        |
            --------------------------------------------------------------------------------------------
            Total Site Preparation Mobilization Cost (USD)      |   sitepreparation_mobilization_usd    |
            --------------------------------------------------------------------------------------------
            Total Foundation Cost (USD)                         |   summed_foundation_cost              |
            --------------------------------------------------------------------------------------------
            Total Foundation Equipment Rental Cost (USD)        |   foundation_equipment_rental_usd     |
            --------------------------------------------------------------------------------------------
            Total Foundation Labor Cost (USD)                   |   foundation_labor_usd                |
            --------------------------------------------------------------------------------------------
            Total Foundation Material Cost (USD)                |   foundation_material_usd             |
            --------------------------------------------------------------------------------------------
            Total Foundation Mobilization Cost (USD)            |   foundation_mobilization_usd         |
            --------------------------------------------------------------------------------------------
            Total Tower Erection Cost (USD)                     |   total_cost_summed_erection          |
            --------------------------------------------------------------------------------------------
            Total Tower Erection Equipment Rental Cos (USD)     |   erection_equipment_rental_usd       |
            --------------------------------------------------------------------------------------------
            Total Tower Erection Labor Cost (USD)               |   erection_labor_usd                  |
            --------------------------------------------------------------------------------------------
            Total Tower Erection Material Cost (USD)            |   erection_material_usd               |
            --------------------------------------------------------------------------------------------
            Total Tower Erection - Other Cost (USD)             |   erection_other_usd                  |
            --------------------------------------------------------------------------------------------
            Total Tower Erection Mobilization Cost (USD)        |   erection_mobilization_usd           |
            --------------------------------------------------------------------------------------------
            Total Tower Erection Fuel Cost (USD)                |   erection_fuel_usd                   |
            --------------------------------------------------------------------------------------------
            Total Transmission & Distribution Cost (USD)        |   trans_dist_usd                      |
            --------------------------------------------------------------------------------------------
            Total Collection Cost                               |   summed_collection_cost              |
            --------------------------------------------------------------------------------------------
            Total Collection System Equipment Rental Cost (USD) |   collection_equipment_rental_usd     |
            --------------------------------------------------------------------------------------------
            Total Collection System Labor Cost (USD)            |   collection_labor_usd                |
            --------------------------------------------------------------------------------------------
            Total Collection System Material Cost (USD)         |   collection_material_usd             |
            --------------------------------------------------------------------------------------------
            Total Collection System Mobilization Cost (USD)     |   collection_mobilization_usd         |
            --------------------------------------------------------------------------------------------
            Total Substation Cost (USD)                         |   summed_substation_cost              |
            --------------------------------------------------------------------------------------------

    """

    input_output_path = os.path.dirname(__file__)
    os.environ["LANDBOSSE_INPUT_DIR"] = input_output_path
    os.environ["LANDBOSSE_OUTPUT_DIR"] = input_output_path

    extended_project_list_before_parameter_modifications = read_data(input_dict)
    xlsx_reader = XlsxReader()

    for _, project_parameters in \
            extended_project_list_before_parameter_modifications.iterrows():
        # If project_parameters['Project ID with serial'] is null, that means
        # there are no parametric modifications to the project data dataframes.
        # Hence, just the plain Project ID without a serial number should be
        # used.
        if pd.isnull(project_parameters['Project ID with serial']):
            project_id_with_serial = project_parameters['Project ID']
        else:
            project_id_with_serial = project_parameters['Project ID with serial']
            # Read the project data sheets.

        project_data_basename = project_parameters['Project data file']

        project_data_sheets = \
            XlsxDataframeCache.read_all_sheets_from_xlsx(project_data_basename)

        # make sure you call create_master_input_dictionary() as soon as
        # labor_cost_multiplier's value is changed.
        # The weather dataframe key in input_dict is 'user_weather_DF':
        master_input_dict = xlsx_reader.create_master_input_dictionary(project_data_sheets,
                                                                       project_parameters)
        master_input_dict['error'] = dict()

    output_dict = dict()
    default_date_time = list()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # override default inputs with user modified inputs (on the SAM UI):
    if 'project_id' in input_dict:
        project_id_with_serial = input_dict['project_id']

    try:
        for key, value in input_dict.items():
            if (type(value) == int or type(value) == float) and value < 0:
                raise NegativeInputError
    except NegativeInputError:
        master_input_dict['error']['NegativeInputError'] = \
            'User entered a negative value for ' + key + '. This is an invalid entry'

    # Loop to collect user provided inputs that will override defaults:

    for key, _ in input_dict.items():

        if key == 'weather_file_path':  # weather_file_path is handled later in
            # this codebase. Skip storing it for now.
            pass

        elif key in master_input_dict:
            master_input_dict[key] = input_dict[key]

        elif key == 'path_to_project_list' or key == 'name_of_project_list':
            pass

        # Allows user to override default development cost:
        elif key == 'development_labor_cost_usd':
            master_input_dict[key] = input_dict['development_labor_cost_usd']

        # New functionality that lets a user run model with a user defined
        # grid interconnection rating:
        elif key == 'grid_system_size_MW':
            master_input_dict['grid_system_size_MW'] = input_dict['grid_system_size_MW']

        elif key == 'substation_rating_MW':
            master_input_dict['substation_rating_MW'] = input_dict['substation_rating_MW']

        else:
            exit(1)

    # update master input dict based on new labor cost multiplier:
    labor_cost_multiplier = master_input_dict['labor_cost_multiplier']
    xlsx_reader.apply_labor_multiplier_to_project_data_dict(project_data_sheets,
                                                            labor_cost_multiplier)

    # Ensuring number of turbines is > 10:
    try:
        if 'num_turbines' in input_dict:
            if input_dict['num_turbines'] > 0:
                master_input_dict['num_turbines'] = input_dict['num_turbines']
            else:
                raise TurbineNumberError
    except TurbineNumberError:
        master_input_dict['error']['TurbineNumberError'] = \
            'User selected less than 1 turbine. LandBOSSE currently ' \
            'provides BOS estimates for 1 or greater number of turbines.'

    # Ensuring user is runnning landbosse for turbine in range of [1- 8] MW:
    try:
        if 'turbine_rating_MW' in input_dict:
            if input_dict['turbine_rating_MW'] > 8:
                raise LargeTurbineSizeError
            elif input_dict['turbine_rating_MW'] < 1:
                raise SmallTurbineSizeError
            else:
                master_input_dict['turbine_rating_MW'] = input_dict['turbine_rating_MW']
    except LargeTurbineSizeError:
        master_input_dict['error']['LargeTurbineSizeError'] = \
                        'User selected turbine of rating greater than 8 MW. ' \
                        'LandBOSSE provides reasonable results for turbines ' \
                        'in range of 1-8 MW rating for now.'

    except SmallTurbineSizeError:
        master_input_dict['error']['SmallTurbineSizeError'] = \
                        'User selected turbine of rating lesser than 1 MW. ' \
                        'LandBOSSE provides reasonable results for turbines ' \
                        'in range of 1-8 MW rating for now.'

    # Weather file passed by SAM does NOT have a 'Date UTC' column. So it needs
    # to be manually added to prevent code from breaking. Needs to have 8760
    # rows worth of date_time to stay consistent with shape of SAM weather data
    # passed.
    start_date = datetime(2011, 12, 31, 00, 00)
    end_date = datetime(2012, 12, 30, 00, 00)
    default_date_time = []
    for single_date in daterange(start_date, end_date):
        default_date_time.append(single_date.strftime("%Y-%m-%d %H:%M"))

    # make sure weather data passed by SAM is hourly.
    try:
        if 'project_id' in input_dict:
            pass

        else:
            if 'weather_file_path' in input_dict:  # if user provides weather file, use it
                weather_window_input_df = read_weather_data(input_dict['weather_file_path'])

            elif 'user_weather_DF' in input_dict:  # if user provides weather DF, use it
                weather_window_input_df = input_dict['user_weather_DF']

            else:   # if user doesn't provide weather data, use default file
                weather_file_path = input_output_path + \
                                    '/project_data/az_rolling.srw'
                weather_window_input_df = read_weather_data(weather_file_path)


            weather_window_input_df = weather_window_input_df.reset_index(
                                                                    drop=True)
            weather_window_input_df.insert(loc=0,
                                           column='time',
                                           value=default_date_time
                                           )
            column_names = weather_window_input_df.columns
            renamed_columns = {
                column_names[0]: 'Date UTC',
                column_names[1]: 'Temp C',
                column_names[2]: 'Pressure atm',
                column_names[3]: 'Direction deg',
                column_names[4]: 'Speed m per s'
            }
            weather_data = weather_window_input_df.rename(columns=renamed_columns)
            weather_data = weather_data.reset_index(drop=True)
            weather_data = weather_data[renamed_columns.values()]
            master_input_dict['weather_window'] = read_weather_window(weather_data)
    except Exception as error:  # exception handling for landbosse_api
        master_input_dict['error']['Weather_Data'] = error

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # If user provides 'project_id' in input_dict, it is because they want to use the
    # default detailed data input file either shipped w/ LandBOSSE, or provided by the
    # user. In this case, skip re-scaling of turbine components.
    #
    # ELSE, if user doesn't provide 'project_id', use the scaling relations to refactor
    # Components DF based on user inputs.

    if 'project_id' in input_dict:

        pass

    # Else, use the scaling relations to refactor Components DF based on user inputs:
    else:
        # nacelle
        nacelle_mass_ton = nacelle_mass(master_input_dict['turbine_rating_MW'])
        master_input_dict['component_data'] = edit_nacelle_info(
                                            master_input_dict['component_data'],
                                            nacelle_mass_ton,
                                            master_input_dict['hub_height_meters']
                                            )

        master_input_dict['component_data'] = master_input_dict[
                                        'component_data'].reset_index(drop=True)

        # hub
        hub_mass_ton = hub_mass(master_input_dict['turbine_rating_MW'])
        master_input_dict['component_data'] = edit_hub_info(
                                            master_input_dict['component_data'],
                                            hub_mass_ton,
                                            master_input_dict['hub_height_meters']
                                            )

        master_input_dict['component_data'] = master_input_dict[
                                        'component_data'].reset_index(drop=True)

        # combined 3 blades total mass in tons:
        blade_mass = blade_mass_ton(master_input_dict['rotor_diameter_m'])
        master_input_dict['component_data'] = edit_blade_info(
                                            master_input_dict['component_data'],
                                            blade_mass,
                                            master_input_dict['hub_height_meters'],
                                            master_input_dict['rotor_diameter_m']
                                            )

        master_input_dict['component_data'] = master_input_dict[
                                        'component_data'].reset_index(drop=True)

        # tower
        tower_mass_tonne = tower_mass(master_input_dict['turbine_rating_MW'],
                                      master_input_dict['hub_height_meters']
                                      )

        num_tower_sections, tower_section_height_m = tower_specs(
                                            master_input_dict['hub_height_meters'],
                                            tower_mass_tonne
                                            )

        master_input_dict['component_data'] = edit_tower_sections(
                                            master_input_dict['component_data'],
                                            num_tower_sections,
                                            tower_mass_tonne,
                                            tower_section_height_m
                                            )

        master_input_dict['component_data'] = master_input_dict[
                                        'component_data'].reset_index(drop=True)
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><

    # Ensure plant size is getting updated based on user provided num turbines and
    # turbine rating
    master_input_dict['project_size_megawatts'] = master_input_dict['num_turbines'] * \
                                                  master_input_dict['turbine_rating_MW']

    master_input_dict['plant_capacity_MW'] = master_input_dict['num_turbines'] * \
                                                  master_input_dict['turbine_rating_MW']

    # Manager class (1) manages the distribution of inout data for all modules
    # and (2) executes landbosse
    mc = Manager(input_dict=master_input_dict, output_dict=output_dict)
    mc.execute_landbosse(project_id_with_serial)

    # results dictionary that gets returned by this function:
    results = dict()
    results['errors'] = []
    if master_input_dict['error']:
        for key, value in master_input_dict['error'].items():
            msg = "Error in " + key + ": " + str(value)
            results['errors'].append(msg)
    else:
        # if project runs successfully, return a dictionary with results that are 3
        # layers of results deep (but 1-D). The layers of results here refers to:
        # 1) Total BOS cost
        # 2) Total module cost (that is, foundation cost, collection cost etc.)
        # 3) Breakdown of each module cost into:
        #   a) Labor
        #   b) Equipment rental
        #   c) Materials
        #   d) Mobilization
        #   e) Other [only in some modules]
        #   f) Fuel [only in some modules]

        results['total_bos_cost'] = \
            output_dict['project_value_usd']

        # management cost module results:
        results['total_management_cost'] = \
            output_dict['total_management_cost']

        results['insurance_usd'] = \
            output_dict['insurance_usd']

        results['construction_permitting_usd'] = \
            output_dict['construction_permitting_usd']

        results['project_management_usd'] = \
            output_dict['project_management_usd']

        results['bonding_usd'] = \
            output_dict['bonding_usd']

        results['markup_contingency_usd'] = \
            output_dict['markup_contingency_usd']

        results['engineering_usd'] = \
            output_dict['engineering_usd']

        results['site_facility_usd'] = \
            output_dict['site_facility_usd']

        results['total_management_cost'] = \
            output_dict['total_management_cost']

        # development cost module results:
        results['total_development_cost'] = \
            output_dict['summed_development_cost']

        if 'Development labor cost USD' in output_dict:
            results['development_equipment_rental_usd'] = \
                master_input_dict['development_labor_cost_usd']

        results['development_labor_usd'] = 0
        results['development_material_usd'] = 0
        results['development_mobilization_usd'] = 0

        # site prep cost module results:
        results['total_sitepreparation_cost'] = \
            output_dict['summed_sitepreparation_cost']

        results['sitepreparation_equipment_rental_usd'] = \
            output_dict['sitepreparation_equipment_rental_usd']

        results['sitepreparation_labor_usd'] = \
            output_dict['sitepreparation_labor_usd']

        results['sitepreparation_material_usd'] = \
            output_dict['sitepreparation_material_usd']

        results['sitepreparation_mobilization_usd'] = \
            output_dict['sitepreparation_mobilization_usd']

        results['sitepreparation_other_usd'] = \
            output_dict['sitepreparation_other_usd']

        # foundation cost module results:
        results['total_foundation_cost'] = \
            output_dict['summed_foundation_cost']

        results['foundation_equipment_rental_usd'] = \
            output_dict['foundation_equipment_rental_usd']

        results['foundation_labor_usd'] = \
            output_dict['foundation_labor_usd']

        results['foundation_material_usd'] = \
            output_dict['foundation_material_usd']

        results['foundation_mobilization_usd'] = \
            output_dict['foundation_mobilization_usd']

        # erection cost module results:
        results['total_erection_cost'] = \
            output_dict['total_cost_summed_erection']

        results['erection_equipment_rental_usd'] = \
            output_dict['erection_equipment_rental_usd']

        results['erection_labor_usd'] = \
            output_dict['erection_labor_usd']

        results['erection_material_usd'] = \
            output_dict['erection_material_usd']

        results['erection_other_usd'] = \
            output_dict['erection_other_usd']

        results['erection_mobilization_usd'] = \
            output_dict['erection_mobilization_usd']

        results['erection_fuel_usd'] = \
            output_dict['erection_fuel_usd']

        # grid connection cost module results:
        results['total_gridconnection_cost'] = \
            output_dict['trans_dist_usd']

        # collection cost module results:
        results['total_collection_cost'] = \
            output_dict['summed_collection_cost']

        results['collection_equipment_rental_usd'] = \
            output_dict['collection_equipment_rental_usd']

        results['collection_labor_usd'] = \
            output_dict['collection_labor_usd']

        results['collection_material_usd'] = \
            output_dict['collection_material_usd']

        results['collection_mobilization_usd'] = \
            output_dict['collection_mobilization_usd']

        # substation cost module results:
        results['total_substation_cost'] = \
            output_dict['summed_substation_cost']

    return results


# This method reads in the two input Excel files (project_list; project_1)
# and stores them as data frames. This method is called internally in
# run_landbosse(), where the data read in is converted to a master input
# dictionary.
def read_data(modified_path_dict):
    if 'path_to_project_list' in modified_path_dict:
        path_to_project_list = modified_path_dict['path_to_project_list']
    else:
        path_to_project_list = os.path.dirname(__file__)

    if 'name_of_project_list' in modified_path_dict:
        project_list = modified_path_dict['name_of_project_list']
    else:
        project_list = 'project_list'

    sheets = XlsxDataframeCache.read_all_sheets_from_xlsx(project_list,
                                                          path_to_project_list)

    # If there is one sheet, make an empty dataframe as a placeholder.
    if len(sheets.values()) == 1:
        first_sheet = list(sheets.values())[0]
        project_list = first_sheet
        parametric_list = pd.DataFrame()

    # If the parametric and project lists exist, read them
    elif 'Parametric list' in sheets.keys() \
            and 'Project list' in sheets.keys():

        project_list = sheets['Project list']
        parametric_list = sheets['Parametric list']

    # Otherwise, raise an exception
    else:
        raise KeyError(
            "Project list needs to have a single sheet or sheets named "
            "'Project list' and 'Parametric list'."
        )

    # Instantiate and XlsxReader to assemble master input dictionary
    xlsx_reader = XlsxReader()

    # Join in the parametric variable modifications
    parametric_value_list = xlsx_reader.create_parametric_value_list(parametric_list)
    extended_project_list = xlsx_reader.\
        outer_join_projects_to_parametric_values(project_list,
                                                 parametric_value_list)

    return extended_project_list


def read_weather_data(file_path):
    weather_data = pd.read_csv(file_path,
                               sep=",",
                               header=None,
                               skiprows=5,
                               usecols=[0, 1, 2, 3, 4]
                               )
    return weather_data


# Weather file passed by SAM does NOT have a 'Date UTC' column. So it needs to
# be manually added to prevent code from breaking. Needs to have 8765 rows
# worth of date_time to stay consistent with shape of SAM weather data passed.


def daterange(start_date, end_date):
    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta


class Error(Exception):
    """
        Base class for other exceptions
    """
    pass


class SmallTurbineSizeError(Error):
    """
        Raised when user selects a turbine of rating less than 1 MW since
        LandBOSSE provides reasonable results for turbines greater than
        1 MW rating for now.
    """
    pass


class LargeTurbineSizeError(Error):
    """
            Raised when user selects a turbine of rating less than 8 MW
            since LandBOSSE provides reasonable results for turbines greater
            than 1 MW rating for now.
    """
    pass


class TurbineNumberError(Error):
    """
        Raised when number of turbines is less than 10; since LandBOSSE API
        does not currently handle BOS calculations for < 10 turbines.
    """
    pass


class NegativeInputError(Error):
    """
        User entered a negative input. This is an invalid entry.
    """
    pass


# <><><><><><><><> EXAMPLE OF RUNNING THIS LANDBOSSE API <><><><><><><><><><><>

# Default inputs on the SAM UI. Commented out since SAM will pass these values
# down to LandBOSSE.
# TODO: Un-comment these out if running this script directly.
# input_dict = dict()
# input_dict['interconnect_voltage_kV'] = 137
# input_dict['distance_to_interconnect_mi'] = 0.31
# input_dict['num_turbines'] = 1
# input_dict['project_id'] = 'ge15_public_dist'
# input_dict['turbine_spacing_rotor_diameters'] = 4
# input_dict['row_spacing_rotor_diameters'] = 10
# input_dict['turbine_rating_MW'] = 2.5
# input_dict['rotor_diameter_m'] = 77
# input_dict['hub_height_meters'] = 80
# input_dict['wind_shear_exponent'] = 0.20
# input_dict['depth'] = 2.36  # Foundation depth in m
# input_dict['rated_thrust_N'] = 589000
# input_dict['labor_cost_multiplier'] = 1
# input_dict['gust_velocity_m_per_s'] = 59.50
# input_dict['path_to_project_list'] = '/Users/<username>/Desktop/...'
# input_dict['name_of_project_list'] = 'project_list_alternative'


# (Optional) Provide absolute file path of wind weather file (.txt, .srw, or
# .csv). Wind data used here follows the wind toolkit (WTK) formatted data.
# If you do not provide a path to a weather file, this API will use the
# default weather file shipped with LandBOSSE.

# Alternatively, provide a [8760 x 4] dataframe with WTK formatted data:
# [Temp (C), Pressure (atm), Wind Direction (deg), Wind Speed(m/s)]

# Example of how to provide path to weather file:
# input_dict['weather_file_path'] = '/Users/<username>/Desktop/az_rolling.srw'

# Example of how to provide weather input dataframe:
# input_dict['user_weather_DF'] = pd.DataFrame(np.column_stack((15*np.ones((8760, 1)),
#                                                               np.ones((8760, 1)),
#                                                               180*np.ones((8760, 1)),
#                                                               9*np.ones((8760, 1)))))
#
# BOS_results = run_landbosse(input_dict)
# print(BOS_results)
# <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><
