import pandas as pd
import numpy as np

from .WeatherWindowCSVReader import read_weather_window
from ..model import DefaultMasterInputDict


class XlsxReader:
    """
    This class is for reading input data from .xlsx files.

    There are two sets of data to be read from .xlsx files. The first set
    of data is read from the following sheets:

    - components

    - cable_specs

    - equip

    - crane_specs

    - development

    - crew_price

    - crew

    - equip_price

    - material_price

    - rsmeans

    - site_facility_building_area

    - weather_window

    The second set of data are read from a single sheet as described below.

    The first set of data represent a database used by the various modules. Queries
    on these data allow calculation based on labor, material, crane capacity
    and so on. These data can be shared among different projects. These data
    are called project_data.

    The second set of data represent the parameters specific to each project.
    These parameters include things values like hub height, rotor diameter,
    etc. These data are particular to a single project. These data are
    referred to as the project.

    This class also handles modifications of project data dataframes for
    parametric runs and all the other dataframe manipulations that make that
    possible.
    """

    def create_parametric_step_list(self, parametric_list, steps):
        """
        Assume that there are fixed number of steps in a parametric run.
        Lets say, for this example, 3 steps.

        Also assume that we have the following data frame for the parametric
        variables. This was in the "Parametric list" sheet of the project list
        spreadsheet.

        | Project ID | Dataframe name       | Row name | Column name | Start | End |
        |------------|----------------------|----------|-------------|-------|-----|
        | project1   | alpha                | fizz     | buzz        | 0     | 12  |
        | project1   | beta                 | foo      | bar         | 0     | 9   |
        | project2   | gamma                | spam     | eggs        | 21    | 27  |

        Translate this data frame into a data frame of the following format:

        | Project ID | serial | alpha/fizz/buzz | beta/foo/bar | gamma/spam/eggs
        |------------|--------|-----------------|--------------|---------------|
        | project1   | 0      | 0               | 0            | NaN           |
        | project1   | 1      | 6               | 3            | NaN           |
        | project1   | 2      | 12              | 9            | NaN           |
        | project2   | 0      | NaN             | NaN          | 21            |
        | project2   | 1      | NaN             | NaN          | 24            |
        | project2   | 2      | NaN             | NaN          | 27            |

        Here NaN is used in its role as the Pandas equivalent to the SQL
        NULL. It means that, for a particular project, no modification
        to the dataframe/row/column is needed and that the value in that
        dataframe cell should remain unchanged.

        Also, note that the serial numbers are strings that should be left
        padded with zeros. The left padding means that when the strings are
        sorted alphabetically, they will end up in the same order as numeric
        sorting.

        Parameters
        ----------
        parametric_list : pandas.DataFrame
            The first dataframe shown above.

        steps : int
            The number of steps between start and end values in each
            sequence.

        Returns
        -------
        pandas.DataFrame
            The second dataframe shown above.
        """
        # A list of dictionaries to be transformed into a dataframe at the end
        enhanced_project_list = []

        # A dictionary of numpy arrays will contain all the values in our
        # sequences
        sequences_dict = dict()

        # Add project IDs to the top level dictionary
        for project_id in parametric_list['Project ID'].unique():
            sequences_dict[project_id] = dict()

        # Make NumPy arrays that hold the values at each step in all
        # the sequences.
        for _, row in parametric_list.iterrows():
            project_id = row['Project ID']
            key = f"{row['Row name']}/{row['Column name']}"
            value = np.linspace(float(row['Start value']), float(row['End value']), steps)
            sequences_dict[project_id][key] = value

        # Now, expand all sequences into their values.

        # First, group them by Project ID
        for project_id, sequences in sequences_dict.items():

            # Next group them by steps and make a serial number
            for step in range(steps):
                row_dict = {
                    'Project ID': project_id,
                    'Serial': self.create_serial_number(step, steps)
                }

                # Then, line all variable modifications on the same row.
                # This allows one more parametric variables to be modified
                # simultaneously.
                for parametric_variable, xs in sequences.items():
                    row_dict[parametric_variable] = xs[step]
                enhanced_project_list.append(row_dict)

        # Make a dataframe out of the list of dictionaries
        enhanced_project_df = pd.DataFrame(enhanced_project_list)

        return enhanced_project_df

    def read_xlsx_and_fill_defaults(self, project_data_sheets, project_parameters):
        """
        This method takes a dictionary of dataframes that are the project data
        and unites them with the project parameters as found in the project list
        sheet.

        Parameters
        ----------
        project_data_sheets : dict
            This is a dictionary for the project data .xlsx file. The keys
            are names of sheets and the values are the dataframe contents of
            the sheets.

        project_parameters : pandas.Series
            Series representing the project data, which is the second set
            of data described in the XlsxReader class docstring. The caller
            of this function is responsible for parsing out the project
            data into a series from which these data can be extracted.
            See the subclasses of XlsxManagerRunner for examples on how this
            project series is read from a spreadsheet.

        Returns
        -------
        dict
            An master input dictionary suitable to pass to an instance
            of Manager to run all the cost module sin LandBOSSE.
        """
        # First, read all inputs that come from .csv or .xlsx files.
        # erection_input_worksheets come from the input data spreadsheet.
        # Their string values are the names of the sheets in the Excel
        # workbook and the keys in the erection_project_data_dict dictionary.

        # Incomplete project dict will hold the input dictionary
        # configurations.
        incomplete_input_dict = dict()

        # Read all project_data sheets.
        # The erection module takes in a bunch of keys and values under the
        # 'project_data' key in the incomplete_input_dict

        erection_input_worksheets = [
            'crane_specs',
            'equip',
            'crew',
            'equip_price',
            'crew_price',
            'material_price',
            'components'
        ]

        erection_project_data_dict = dict()
        for worksheet in erection_input_worksheets:
            erection_project_data_dict[worksheet] = project_data_sheets[worksheet]

        # Add the erection project data to the incomplete_input_dict
        incomplete_input_dict['project_data'] = erection_project_data_dict

        # Get the first set of data
        incomplete_input_dict['rsmeans'] = project_data_sheets['rsmeans']
        incomplete_input_dict['site_facility_building_area_df'] = project_data_sheets['site_facility_building_area']
        incomplete_input_dict['material_price'] = project_data_sheets['material_price']

        # The weather window is stored on a sheet of the project_data, but
        # needs preprocessing after it is read. The preprocessing changes it
        # from wind toolkit format to a dataframe.
        weather_window_input_df = project_data_sheets['weather_window']
        incomplete_input_dict['weather_window'] = read_weather_window(weather_window_input_df)

        # Read development tab:
        # incomplete_input_dict['development_df'] = project_data.parse('development')
        incomplete_input_dict['development_df'] = project_data_sheets['development']

        # FoundationCost needs to have all the component data split into separate
        # NumPy arrays.
        incomplete_input_dict['component_data'] = erection_project_data_dict['components']
        for component in incomplete_input_dict['component_data'].keys():
            incomplete_input_dict[component] = np.array(incomplete_input_dict['component_data'][component])

        incomplete_input_dict['cable_specs_pd'] = project_data_sheets['cable_specs']

        # These columns come from the columns in the project definition .xlsx
        incomplete_input_dict['project_id'] = project_parameters['Project ID']
        incomplete_input_dict['num_turbines'] = project_parameters['Number of turbines']
        incomplete_input_dict['construct_duration'] = project_parameters['Total project construction time (months)']
        incomplete_input_dict['hub_height_meters'] = project_parameters['Hub height m']
        incomplete_input_dict['rotor_diameter_m'] = project_parameters['Rotor diameter m']
        incomplete_input_dict['wind_shear_exponent'] = project_parameters['Wind shear exponent']
        incomplete_input_dict['turbine_rating_MW'] = project_parameters['Turbine rating MW']
        incomplete_input_dict['breakpoint_between_base_and_topping_percent'] = \
            project_parameters['Breakpoint between base and topping (percent)']
        incomplete_input_dict['fuel_usd_per_gal'] = project_parameters['Fuel cost USD per gal']
        incomplete_input_dict['rate_of_deliveries'] = project_parameters['Rate of deliveries (turbines per week)']
        incomplete_input_dict['turbine_spacing_rotor_diameters'] = project_parameters['Turbine spacing (times rotor diameter)']
        incomplete_input_dict['depth'] = project_parameters['Foundation depth m']
        incomplete_input_dict['rated_thrust_N'] = project_parameters['Rated Thrust (N)']
        incomplete_input_dict['bearing_pressure_n_m2'] = project_parameters['Bearing Pressure (n/m2)']
        incomplete_input_dict['gust_velocity_m_per_s'] = project_parameters['50-year Gust Velocity (m/s)']
        incomplete_input_dict['project_size_megawatts'] = project_parameters['Number of turbines'] * project_parameters['Turbine rating MW']

        incomplete_input_dict['road_length_adder_m'] = project_parameters['Road length adder (m)']
        incomplete_input_dict['fraction_new_roads'] = project_parameters['Percent of roads that will be constructed']
        incomplete_input_dict['road_quality'] = project_parameters['Road Quality (0-1)']
        incomplete_input_dict['line_frequency_hz'] = project_parameters['Line Frequency (Hz)']
        incomplete_input_dict['plant_capacity_MW'] = project_parameters['Turbine rating MW'] * project_parameters['Number of turbines']
        incomplete_input_dict['row_spacing_rotor_diameters'] = project_parameters['Row spacing (times rotor diameter)']
        incomplete_input_dict['user_defined_distance_to_grid_connection'] = project_parameters['Flag for user-defined home run trench length (0 = no; 1 = yes)']
        incomplete_input_dict['distance_to_grid_connection_km'] = project_parameters['Combined Homerun Trench Length to Substation (km)']
        incomplete_input_dict['crew'] = incomplete_input_dict['project_data']['crew']
        incomplete_input_dict['crew_cost'] = incomplete_input_dict['project_data']['crew_price']

        #read in RSMeans per diem:
        crew_cost = incomplete_input_dict['project_data']['crew_price']
        crew_cost = crew_cost.set_index("Labor type ID", drop=False)
        incomplete_input_dict['rsmeans_per_diem'] = crew_cost.loc['RSMeans', 'Per diem USD per day']

        incomplete_input_dict['fuel_cost_usd_per_gal'] = project_parameters['Fuel cost USD per gal']

        incomplete_input_dict['line_frequency_hz'] = project_parameters['Line Frequency (Hz)']
        incomplete_input_dict['plant_capacity_MW'] = project_parameters['Turbine rating MW'] * project_parameters['Number of turbines']
        incomplete_input_dict['row_spacing_rotor_diameters'] = project_parameters['Row spacing (times rotor diameter)']
        incomplete_input_dict['user_defined_home_run_trench'] = project_parameters[
            'Flag for user-defined home run trench length (0 = no; 1 = yes)']
        incomplete_input_dict['trench_len_to_substation_km'] = project_parameters[
            'Combined Homerun Trench Length to Substation (km)']

        # Add inputs for transmission & Substation modules:
        incomplete_input_dict['distance_to_interconnect_mi'] = project_parameters['Distance to interconnect (miles)']
        incomplete_input_dict['interconnect_voltage_kV'] = project_parameters['Interconnect Voltage (kV)']
        new_switchyard = True
        if project_parameters['New Switchyard (y/n)'] == 'y':
            new_switchyard = True
        else:
            new_switchyard = False
        incomplete_input_dict['new_switchyard'] = new_switchyard

        incomplete_input_dict['critical_speed_non_erection_wind_delays_m_per_s'] = project_parameters['Non-Erection Wind Delay Critical Speed (m/s)']
        incomplete_input_dict['critical_height_non_erection_wind_delays_m'] = project_parameters['Non-Erection Wind Delay Critical Height (m)']

        incomplete_input_dict['road_width_ft'] = project_parameters['Road width (ft)']
        incomplete_input_dict['road_thickness'] = project_parameters['Road thickness (in)']
        incomplete_input_dict['crane_width'] = project_parameters['Crane width (m)']
        incomplete_input_dict['num_hwy_permits'] = project_parameters['Number of highway permits']
        incomplete_input_dict['num_access_roads'] = project_parameters['Number of access roads']
        incomplete_input_dict['overtime_multiplier'] = project_parameters['Overtime multiplier']
        incomplete_input_dict['allow_same_flag'] = True if project_parameters['Allow same flag'] == 'y' else False

        override_total_mgmt_cost_col_name = 'Override total management cost (0 does not override)'
        if override_total_mgmt_cost_col_name in project_parameters and project_parameters[override_total_mgmt_cost_col_name] > 0:
            incomplete_input_dict['override_total_management_cost'] = \
                project_parameters[override_total_mgmt_cost_col_name]
        else:
            incomplete_input_dict['markup_contingency'] = project_parameters['Markup contingency']
            incomplete_input_dict['markup_warranty_management'] = project_parameters['Markup warranty management']
            incomplete_input_dict['markup_sales_and_use_tax'] = project_parameters['Markup sales and use tax']
            incomplete_input_dict['markup_overhead'] = project_parameters['Markup overhead']
            incomplete_input_dict['markup_profit_margin'] = project_parameters['Markup profit margin']

        # Now fill any missing values with sensible defaults.
        defaults = DefaultMasterInputDict()
        master_input_dict = defaults.populate_input_dict(incomplete_input_dict=incomplete_input_dict)
        return master_input_dict

    def create_serial_number(self, index, total_project_count):
        """
        create_serial_number creates serial numbers left padded with
        zeros. By left padding the numbers, alphabetic sorts and numeric
        sorts create the same sequence.

        Parameters
        ----------
        index : int
            The index of the project in the sequence of projects

        total_project_count : int
            The total number of projects in the sequence.

        Returns
        -------
        str
            The project name with the serial number appended.
        """
        total_digit_count = 1
        index_digit_count = len(str(index))

        if 0 < total_project_count < 1e1 - 1:
            total_digit_count = 1
        elif 1e1 <= total_project_count < 1e2 - 1:
            total_digit_count = 2
        elif 1e2 <= total_project_count < 1e3 - 1:
            total_digit_count = 3
        elif 1e3 <= total_project_count < 1e4 - 1:
            total_digit_count = 4
        elif 1e4 <= total_project_count < 1e5 - 1:
            total_digit_count = 5
        elif 1e5 <= total_project_count < 1e6 - 1:
            total_digit_count = 6
        elif 1e6 <= total_project_count < 1e7 - 1:
            total_digit_count = 7
        elif 1e7 <= total_project_count < 1e8 - 1:
            total_digit_count = 8
        else:
            total_digit_count = 9

        padding = '0' * (total_digit_count - index_digit_count)
        return f'{padding}{index}'
