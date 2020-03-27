import os
import pandas as pd
import shutil
from landbosse.excelio import XlsxReader
from landbosse.excelio.WeatherWindowCSVReader import read_weather_window
from landbosse.excelio.XlsxDataframeCache import XlsxDataframeCache
from landbosse.model import Manager
from datetime import datetime, timedelta
from landbosse.landbosse_api.turbine_scaling import *


# Call this function - run_landbosse() - to run LandBOSSE.
# this method calls the read_data() method to read the 2 excel input files, and creates a master input dictionary from it.
def run_landbosse(sam_input_dict):
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
    default_date_time = list()
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # override default inputs with user modified inputs (on the SAM UI):
    project_id_with_serial = 'SAM_Run'

    try:
        for key, value in sam_input_dict.items():
            if (type(value) == int or type(value) == float) and value < 0:
                raise NegativeInputError
    except NegativeInputError:
        master_input_dict['error']['NegativeInputError'] = 'User entered a negative value for ' + key +'. This is an ' \
                                                                                                       'invalid entry'


    master_input_dict['interconnect_voltage_kV']            =   sam_input_dict['interconnect_voltage_kV']
    master_input_dict['distance_to_interconnect_mi']        =   sam_input_dict['distance_to_interconnect_mi']
    master_input_dict['num_turbines']                       =   sam_input_dict['num_turbines']
    master_input_dict['turbine_spacing_rotor_diameters']    =   sam_input_dict['turbine_spacing_rotor_diameters']
    master_input_dict['row_spacing_rotor_diameters']        =   sam_input_dict['row_spacing_rotor_diameters']
    master_input_dict['rotor_diameter_m']                   =   sam_input_dict['rotor_diameter_m']
    master_input_dict['hub_height_meters']                  =   sam_input_dict['hub_height_meters']
    master_input_dict['wind_shear_exponent']                =   sam_input_dict['wind_shear_exponent']
    master_input_dict['depth']                              =   sam_input_dict['depth'] # Foundation depth in m
    master_input_dict['rated_thrust_N']                     =   sam_input_dict['rated_thrust_N']
    master_input_dict['labor_cost_multiplier']              =   sam_input_dict['labor_cost_multiplier']
    master_input_dict['gust_velocity_m_per_s']              =   sam_input_dict['gust_velocity_m_per_s']

    # update master input dict based on new labor cost multiplier:
    labor_cost_multiplier = master_input_dict['labor_cost_multiplier']
    xlsx_reader.apply_labor_multiplier_to_project_data_dict(project_data_sheets, labor_cost_multiplier)

    # Ensuring number of turbines is > 10:
    try:
        if sam_input_dict['num_turbines'] > 10:
            master_input_dict['num_turbines'] = sam_input_dict['num_turbines']
        else:
            raise TurbineNumberError
    except TurbineNumberError:
        master_input_dict['error']['TurbineNumberError'] = 'User selected less than 10 turbines. LandBOSSE currently' \
                                                           ' provides BOS estimates for 10 or greater number of turbines' \
                                                           ' in a utility scale project.'

    # Ensuring user is runnning landbosse for turbine in range of [1- 8] MW:
    try:
        if sam_input_dict['turbine_rating_MW'] > 8:
            raise LargeTurbineSizeError
        elif sam_input_dict['turbine_rating_MW'] < 1:
            raise SmallTurbineSizeError
        else:
            master_input_dict['turbine_rating_MW']          =   sam_input_dict['turbine_rating_MW']
    except LargeTurbineSizeError:
        master_input_dict['error']['LargeTurbineSizeError'] = 'User selected turbine of rating greater than 8 MW. ' \
                                                              'LandBOSSE provides reasonable results for turbines ' \
                                                              'in range of 1-8 MW rating for now.'
    except SmallTurbineSizeError:
        master_input_dict['error']['SmallTurbineSizeError'] = 'User selected turbine of rating lesser than 1 MW. ' \
                                                              'LandBOSSE provides reasonable results for turbines ' \
                                                              'in range of 1-8 MW rating for now.'

    # Weather file passed by SAM does NOT have a 'Date UTC' column. So it needs to be manually added to prevent code
    # from breaking. Needs to have 8760 rows worth of date_time to stay consistent with shape of SAM weather data passed.
    start_date = datetime(2011, 12, 31, 00, 00)
    end_date = datetime(2012, 12, 30, 00, 00)
    default_date_time = []
    for single_date in daterange(start_date, end_date):
        default_date_time.append(single_date.strftime("%Y-%m-%d %H:%M"))

    # make sure weather data passed by SAM is hourly.
    try:
        weather_window_input_df = read_weather_data(sam_input_dict['weather_file_path'])
        weather_window_input_df = weather_window_input_df.reset_index(drop=True)
        weather_window_input_df.insert(loc=0, column='time', value=default_date_time)
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

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>

    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
    # Refactoring Components DF based on user input

    # print(master_input_dict['component_data'])

    # nacelle
    nacelle_mass_ton = nacelle_mass(master_input_dict['turbine_rating_MW'])
    master_input_dict['component_data'] = edit_nacelle_info(master_input_dict['component_data'], nacelle_mass_ton,
                                                            master_input_dict['hub_height_meters'])

    master_input_dict['component_data'] = master_input_dict['component_data'].reset_index(drop=True)
    # print(master_input_dict['component_data'])

    # hub
    hub_mass_ton = hub_mass(master_input_dict['turbine_rating_MW'])
    master_input_dict['component_data'] = edit_hub_info(master_input_dict['component_data'], hub_mass_ton,
                                                        master_input_dict['hub_height_meters'])

    master_input_dict['component_data'] = master_input_dict['component_data'].reset_index(drop=True)
    # print(master_input_dict['component_data'])

    # combined 3 blades total mass in tons:
    blade_mass = blade_mass_ton(master_input_dict['rotor_diameter_m'])
    master_input_dict['component_data'] = edit_blade_info(master_input_dict['component_data'], blade_mass,
                                                          master_input_dict['hub_height_meters'],
                                                          master_input_dict['rotor_diameter_m'])

    master_input_dict['component_data'] = master_input_dict['component_data'].reset_index(drop=True)
    # print(master_input_dict['component_data'])

    # tower
    tower_mass_tonne = tower_mass(master_input_dict['turbine_rating_MW'], master_input_dict['hub_height_meters'])
    num_tower_sections, tower_section_height_m = tower_specs(master_input_dict['hub_height_meters'], tower_mass_tonne)
    master_input_dict['component_data'] = edit_tower_sections(master_input_dict['component_data'], num_tower_sections,
                                                              tower_mass_tonne, tower_section_height_m)

    master_input_dict['component_data'] = master_input_dict['component_data'].reset_index(drop=True)
    # print(master_input_dict['component_data'])
    # <><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>



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


def read_weather_data(file_path):
    # weather_data = pd.read_csv('temp_weather_file.txt', sep=",", header=None)
    weather_data = pd.read_csv(file_path, sep=",", header=None, skiprows=5, usecols=[0, 1, 2, 3, 4])
    return weather_data

# Weather file passed by SAM does NOT have a 'Date UTC' column. So it needs to be manually added to prevent code
# from breaking. Needs to have 8765 rows worth of date_time to stay consistent with shape of SAM weather data passed.
def daterange(start_date, end_date):
    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta







# Default inputs on the SAM UI. Commented out since SAM will pass these values down to LandBOSSE.
# TODO: Un-comment these out if running this script directly.
# sam_inputs = dict()
# sam_inputs['interconnect_voltage_kV'] = 137
# sam_inputs['distance_to_interconnect_mi'] = 10
# sam_inputs['num_turbines'] = 100
# sam_inputs['turbine_spacing_rotor_diameters'] = 4
# sam_inputs['row_spacing_rotor_diameters'] = 10
# sam_inputs['turbine_rating_MW'] = 1.5
# sam_inputs['rotor_diameter_m'] = 70
# sam_inputs['hub_height_meters'] = 80
# sam_inputs['wind_shear_exponent'] = 0.20
# sam_inputs['depth'] = 2.36  # Foundation depth in m
# sam_inputs['rated_thrust_N'] =  589000
# sam_inputs['labor_cost_multiplier'] = 1
# sam_inputs['gust_velocity_m_per_s'] = 59.50

# Provide absolute file path of wind weather file (.txt, .srw, or .csv). Wind data used here follows the wind toolkit (WTK) formatted data.
# for instance:
# sam_inputs['weather_file_path'] = '/Users/<username>/Desktop/az_rolling.srw'


class Error(Exception):
   """Base class for other exceptions"""
   pass


class SmallTurbineSizeError(Error):
    """
        Raised when user selects a turbine of rating less than 1 MW since LandBOSSE provides reasonable results for
        turbines greater than 1 MW rating for now.
    """
    pass


class LargeTurbineSizeError(Error):
    """
            Raised when user selects a turbine of rating less than 8 MW since LandBOSSE provides reasonable results for
            turbines greater than 1 MW rating for now.
    """
    pass


class TurbineNumberError(Error):
    """
        Raised when number of turbines is less than 10; since LandBOSSE API does not currently handle BOS calculations
        for < 10 turbines.
    """


class NegativeInputError(Error):
    """
        User entered a negative input. This is an invalid entry.
    """


# print(run_landbosse(sam_inputs))
# run_landbosse()




