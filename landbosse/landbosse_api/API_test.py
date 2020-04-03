from landbosse.landbosse_api.run import *
from unittest import TestCase



class TestLandBOSSE_API(TestCase):
    def setUp(self):
        self.file_path = os.path.dirname(__file__) + '/project_data/az_rolling.srw'
        self.api_inputs = dict()
        self.api_inputs['interconnect_voltage_kV'] = 137
        self.api_inputs['distance_to_interconnect_mi'] = 10
        self.api_inputs['num_turbines'] = 100
        self.api_inputs['turbine_spacing_rotor_diameters'] = 4
        self.api_inputs['row_spacing_rotor_diameters'] = 10
        self.api_inputs['turbine_rating_MW'] = 1.5
        self.api_inputs['rotor_diameter_m'] = 77
        self.api_inputs['hub_height_meters'] = 80
        self.api_inputs['wind_shear_exponent'] = 0.20
        self.api_inputs['depth'] = 2.36  # Foundation depth in m
        self.api_inputs['rated_thrust_N'] = 589000
        self.api_inputs['labor_cost_multiplier'] = 1
        self.api_inputs['gust_velocity_m_per_s'] = 59.50
        self.results = run_landbosse(self.api_inputs)
        print(self.results)

    def test_total_BOS_cost(self):
        self.assertEqual(self.results['total_bos_cost'], 44648532.791873954)

    def test_total_management_cost(self):
        self.assertEqual(self.results['total_management_cost'], 10616123.290804042)

    def test_total_siteprep_cost(self):
           self.assertEqual(self.results['total_sitepreparation_cost'], 3195070.1679882305)

    def test_total_foundation_cost(self):
           self.assertEqual(self.results['total_foundation_cost'], 10411261.424160697)


    def test_total_erection_cost(self):
           self.assertEqual(self.results['total_erection_cost'], 5231110.226456955)

    def test_total_gridconnection_cost(self):
           self.assertEqual(self.results['total_gridconnection_cost'], 5617735.863912535)


    def test_total_collection_cost(self):
           self.assertEqual(self.results['total_collection_cost'], 4869435.746468595)

    def test_total_substation_cost(self):
           self.assertEqual(self.results['total_substation_cost'], 4940746.072082901)

    def test_read_weather_data(self):
        weather_data = read_weather_data(self.file_path)
        self.assertEqual(len(weather_data), 8760)

    def test_read_data(self):
        project_list = read_data()
        self.assertEqual(len(project_list.columns), 43)
