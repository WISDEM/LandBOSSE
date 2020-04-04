"""
LandBOSSE
=====
This documentation will give you a brief summary of the LandBOSSE model, and also provide a step-by-step of how to run
this model in Python:

The Land-based Balance-of-System Systems Engineering (LandBOSSE) model is a systems engineering tool that estimates the
balance-of-system (BOS) costs associated with installing utility scale wind plants (10, 1.5 MW turbines or larger). It
can execute on macOS and Windows. At this time, for both platforms, it is a command line tool that needs to be accessed
from the command line.

The methods used to develop this model (specifically, LandBOSSE Version 2.1.0)
are described in greater detail the following report:

Eberle, Annika, Owen Roberts, Alicia Key, Parangat Bhaskar, and Katherine Dykes. 2019. NREL’s Balance-of-System Cost
Model for Land-Based Wind. Golden, CO: National Renewable Energy Laboratory. NREL/TP-6A20-72201.
https://www.nrel.gov/docs/fy19osti/72201.pdf.

LandBOSSE Provides:
  1. Calculated estimate of total Balance-of-Station (BOS) cost of a utility  scale land-based wind farm

  2. Total BOS cost broken down in to the following cost buckets:

    a. Total Foundation Cost --> this is the cost of cummulative cost of
    constructing wind turbine foundations. Total foundation cost is broken down
    into the following buckets:
        i. Total labor cost
        ii. Total equipment rental cost
        iii. Total material cost
        iv. Total mobilization cost

    b. Total collection cost --> this is the total wind farm's cost of constructing the wind farm's cable collection
    system. Total collection cost is broken down into the following buckets:
         i. Total labor cost
        ii. Total equipment rental cost
        iii. Total material cost
        iv. Total mobilization cost

    c. Total management cost --> this is the total project management cost. Shown below are all the cost buckets
    considered in management cost:
        i. Total insurance cost
        ii. Construction permitting cost
        iii. Project management cost
        iv. Bonding cost
        v. Markup contingency cost
        vi. Engineering cost
        vii. Site facility cost

    d. Total erection cost --> this is the total cost of tower erection of all turbines in the project. Shown below are
    all the cost buckets considered in tower erection:
        i. Total quipment rental cost
        ii. Total labor cost
        iii. Total material cost
        iv. Total mobilization cost
        v. Total fuel cost
        vi. Total other costs

    e. Total substation cost --> this is the cost of building a substation for the wind farm

    f. Total grid connection cost --> this is the cost of connecting to the grid interconnection

    g. Total site preparation cost --> this is the cost of preparing the project site for wind farm construction and
     constructing roads. Shown below are the all the cost buckets considered in the site preparation cost:
        i. Total labor cost
        ii. Total equipment rental cost
        iii. Total material cost
        iv. Total mobilization cost



  3. Here is a list of inputs required (and optional) to run LandBOSSE:

  input_dict : Python Dictionary
           This input dictionary is a required argument for this function. It consists of 13 required key:value pairs,
           and 1 optional key:value pair ('weather_file_path'). The key:value pairs are as follows:

                                KEY               | REQUIRED KEY? (Y/N)   | SUGGESTED SAMPLE DEFAULT VALUE  | DESCRIPTION                                               |
                ----------------------------------|-----------------------|---------------------------------|---------------------------                                |
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

Here is an example of initializing a Python input dictionary based on the table above:
input_dictionary = dict()
input_dictionary = {
                    'depth':2.36,
                    'distance_to_interconnect_mi':10.0,
                    'gust_velocity_m_per_s':59.5,
                    'hub_height_meters':80.0,
                    'interconnect_voltage_kV':137.0,
                    'labor_cost_multiplier':1.0,
                    'num_turbines':100,
                    'rated_thrust_N':589000.0,
                    'rotor_diameter_m':77.0,
                    'row_spacing_rotor_diameters':10.0,
                    'turbine_rating_MW':1.5,
                    'turbine_spacing_rotor_diameters':4.0,
                    'wind_shear_exponent':0.14
                    }

(OPTIONAL - Provide an absolute path to a .srw hourly weather file as follows):
input_dictionary['weather_file_path']  = '/Users/<username>/Desktop/az_rolling.srw'



<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
IF YOU ARE USING LANDBOSSE's API, PLEASE FOLLOW THESE STEPS:

STEP 1:

import landbosse

STEP 2:

from landbosse.landbosse_api.run import run_landbosse

# run_landbosse(input_dictionary) is the main function for executing LandBOSSE.

STEP 3:

# initialize an input dictionary. run_landbosse() function takes in a single argument which is an input dictionary.

input_dictionary = dict()


STEP 4:

# Populate the input_dictionary with inputs required for running run_landbosse()
# For instance:

input_dictionary['num_turbines'] = 100
input_dictionary['distance_to_interconnect_mi'] = 10
...

# For a complete list of required dictionary keys, refer to the inputs table above.

STEP 5:

# Execute LandBOSSE:

results = run_landbosse(input_dictionary)

print(results)

<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
Here is a table of all the outputs returned by LandBOSSE:

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