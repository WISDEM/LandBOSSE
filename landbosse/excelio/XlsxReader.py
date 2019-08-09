import pandas as pd
import numpy as np

from .WeatherWindowCSVReader import read_weather_window
from ..model import DefaultMasterInputDict


class XlsxReader:
    """
    This class is for reading input data from .xlsx files.
    """

    def read_xlsx_and_fill_defaults(self, input_xlsx, project):
        """
        This method takes an input .xlsx file, reads the tabs as
        dataframes, unites the dataframes with the "project" series
        which has non-dataframe inputs to the model and fills
        missing values with defaults.

        Parameters
        ----------
        input_xlsx : str
            The filename of an Excel workbook that contains input data.

        project : pandas.Series
            Series representing the project.

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

        erection_input_worksheets = [
            'crane_specs',
            'equip',
            'crew',
            'equip_price',
            'crew_price',
            'material_price',
            'rsmeans'
        ]
        erection_project_data_dict = dict()

        erection_project_data_dict['components'] = pd.read_excel(input_xlsx, 'components')

        # The other dataframes are tabs in the same workbook.
        for worksheet in erection_input_worksheets:
            erection_project_data_dict[worksheet] = pd.read_excel(input_xlsx, worksheet)

        # TODO This is a hack: project_specs requires a subset of all the keys and values
        # in the complete project dictionary, so it is just referenced here.
        incomplete_input_dict['project_specs'] = project

        # The erection module takes in a bunch of keys and values under the
        # 'project_data' key
        incomplete_input_dict['project_data'] = erection_project_data_dict

        # Get the input dataframes from the .xlsx
        weather_window_input_df = pd.read_excel(input_xlsx, 'weather_window')
        incomplete_input_dict['weather_window'] = read_weather_window(weather_window_input_df)
        incomplete_input_dict['rsmeans'] = pd.read_excel(input_xlsx, 'rsmeans')
        incomplete_input_dict['site_facility_building_area_df'] = pd.read_excel(input_xlsx,
                                                                                'site_facility_building_area')
        incomplete_input_dict['component_data'] = erection_project_data_dict['components']
        for component in incomplete_input_dict['component_data'].keys():
            incomplete_input_dict[component] = np.array(incomplete_input_dict['component_data'][component])
        incomplete_input_dict['material_price'] = pd.read_excel(input_xlsx, 'material_price')

        # These columns come from the columns in the project definition .xlsx
        incomplete_input_dict['project_id'] = project['Project ID']
        incomplete_input_dict['num_turbines'] = project['Number of turbines']
        incomplete_input_dict['construct_duration'] = project['Total project construction time (months)']
        incomplete_input_dict['hub_height_meters'] = project['Hub height m']
        incomplete_input_dict['rotor_diameter_m'] = project['Rotor diameter m']
        incomplete_input_dict['wind_shear_exponent'] = project['Wind shear exponent']
        incomplete_input_dict['turbine_rating_MW'] = project['Turbine rating MW']
        incomplete_input_dict['breakpoint_between_base_and_topping_percent'] = \
            project['Breakpoint between base and topping (percent)']
        incomplete_input_dict['fuel_usd_per_gal'] = project['Fuel cost USD per gal']
        incomplete_input_dict['rate_of_deliveries'] = project['Rate of deliveries (turbines per week)']
        incomplete_input_dict['turbine_spacing_rotor_diameters'] = project['Turbine spacing (times rotor diameter)']
        incomplete_input_dict['depth'] = project['Foundation depth m']
        incomplete_input_dict['rated_thrust_N'] = project['Rated Thrust (N)']
        incomplete_input_dict['bearing_pressure_n_m2'] = project['Bearing Pressure (n/m2)']
        incomplete_input_dict['gust_velocity_m_per_s'] = project['50-year Gust Velocity (m/s)']
        incomplete_input_dict['project_size_megawatts'] = project['Number of turbines'] * project['Turbine rating MW']

        incomplete_input_dict['road_length_adder_m'] = project['Road length adder (m)']
        incomplete_input_dict['fraction_new_roads'] = project['Percent of roads that will be constructed']
        incomplete_input_dict['road_quality'] = project['Road Quality (0-1)']

        incomplete_input_dict['cable_specs_pd'] = pd.read_excel(input_xlsx, 'cable_specs')
        incomplete_input_dict['line_frequency_hz'] = project['Line Frequency (Hz)']
        incomplete_input_dict['plant_capacity_MW'] = project['Turbine rating MW'] * project['Number of turbines']
        incomplete_input_dict['row_spacing_rotor_diameters'] = project['Row spacing (times rotor diameter)']
        incomplete_input_dict['user_defined_home_run_trench'] = project['Flag for user-defined home run trench length (0 = no; 1 = yes)']
        incomplete_input_dict['trench_len_to_substation_km'] = project['Combined Homerun Trench Length to Substation (km)']
        incomplete_input_dict['crew'] = incomplete_input_dict['project_data']['crew']
        incomplete_input_dict['crew_cost'] = incomplete_input_dict['project_data']['crew_price']

        #read in RSMeans per diem:
        crew_cost = incomplete_input_dict['project_data']['crew_price']
        crew_cost = crew_cost.set_index("Labor type ID", drop=False)
        incomplete_input_dict['rsmeans_per_diem'] = crew_cost.loc['RSMeans', 'Per diem USD per day']

        incomplete_input_dict['fuel_cost_usd_per_gal'] = project['Fuel cost USD per gal']

        incomplete_input_dict['cable_specs_pd'] = pd.read_excel(input_xlsx, 'cable_specs')
        incomplete_input_dict['line_frequency_hz'] = project['Line Frequency (Hz)']
        incomplete_input_dict['plant_capacity_MW'] = project['Turbine rating MW'] * project['Number of turbines']
        incomplete_input_dict['row_spacing_rotor_diameters'] = project['Row spacing (times rotor diameter)']
        incomplete_input_dict['user_defined_home_run_trench'] = project[
            'Flag for user-defined home run trench length (0 = no; 1 = yes)']
        incomplete_input_dict['trench_len_to_substation_km'] = project[
            'Combined Homerun Trench Length to Substation (km)']

        # Add inputs for transmission & Substation modules:
        incomplete_input_dict['distance_to_interconnect_mi'] = project['Distance to interconnect (miles)']
        incomplete_input_dict['interconnect_voltage_kV'] = project['Interconnect Voltage (kV)']
        new_switchyard = True
        if project['New Switchyard (y/n)'] == 'y':
            new_switchyard = True
        else:
            new_switchyard = False
        incomplete_input_dict['new_switchyard'] = new_switchyard

        incomplete_input_dict['critical_speed_non_erection_wind_delays_m_per_s'] = project['Non-Erection Wind Delay Critical Speed (m/s)']
        incomplete_input_dict['critical_height_non_erection_wind_delays_m'] = project['Non-Erection Wind Delay Critical Height (m)']

        incomplete_input_dict['road_width_ft'] = project['Road width (ft)']
        incomplete_input_dict['road_thickness'] = project['Road thickness (in)']
        incomplete_input_dict['crane_width'] = project['Crane width (m)']
        incomplete_input_dict['num_hwy_permits'] = project['Number of highway permits']
        incomplete_input_dict['num_access_roads'] = project['Number of access roads']
        incomplete_input_dict['overtime_multiplier'] = project['Overtime multiplier']
        incomplete_input_dict['allow_same_flag'] = True if project['Allow same flag'] == 'y' else False

        # self.default_input_dict['markup_contingency'] = 0.03  # management cost
        # self.default_input_dict['markup_warranty_management'] = 0.0002
        # self.default_input_dict['markup_sales_and_use_tax'] = 0  # management cost
        # self.default_input_dict['markup_overhead'] = 0.05  # management cost
        # self.default_input_dict['markup_profit_margin'] = 0.05  # management cost

        incomplete_input_dict['markup_contingency'] = project['Markup contingency']
        incomplete_input_dict['markup_warranty_management'] = project['Markup warranty management']
        incomplete_input_dict['markup_sales_and_use_tax'] = project['Markup sales and use tax']
        incomplete_input_dict['markup_overhead'] = project['Markup overhead']
        incomplete_input_dict['markup_profit_margin'] = project['Markup profit margin']

        #Read development tab:
        incomplete_input_dict['development_df'] = pd.read_excel(input_xlsx, 'development')

        # Now fill any missing values with sensible defaults.
        defaults = DefaultMasterInputDict()
        master_input_dict = defaults.populate_input_dict(incomplete_input_dict=incomplete_input_dict)
        return master_input_dict

