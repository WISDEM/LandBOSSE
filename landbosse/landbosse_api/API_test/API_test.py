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
        self.assertEqual(self.results['insurance_usd'], 190581.4932059915)
        self.assertEqual(self.results['construction_permitting_usd'], 408225.2284832139)
        self.assertEqual(self.results['project_management_usd'], 1871041.064287057)
        self.assertEqual(self.results['bonding_usd'], 340324.0950106991)
        self.assertEqual(self.results['markup_contingency_usd'], 4431019.717039302)
        self.assertEqual(self.results['engineering_usd'], 2071325.0)
        self.assertEqual(self.results['site_facility_usd'], 1303606.6927777778)
        total_management_cost = self.results['insurance_usd'] + self.results['construction_permitting_usd'] + \
                                self.results['project_management_usd'] + self.results['bonding_usd'] + self.results[
                                    'markup_contingency_usd'] + self.results['engineering_usd'] + self.results[
                                    'site_facility_usd']
        self.assertEqual(self.results['total_management_cost'], total_management_cost)



    def test_siteprep_cost(self):
        self.assertEqual(self.results['total_sitepreparation_cost'], 3195070.1679882305)
        self.assertEqual(self.results['sitepreparation_equipment_rental_usd'], 403790.6149495621)
        self.assertEqual(self.results['sitepreparation_labor_usd'], 603592.1087067176)
        self.assertEqual(self.results['sitepreparation_material_usd'], 797751.5345973179)
        self.assertEqual(self.results['sitepreparation_mobilization_usd'], 82635.14973463301)
        self.assertEqual(self.results['sitepreparation_other_usd'], 1307300.76)
        total_siteprep_cost = self.results['sitepreparation_equipment_rental_usd'] + self.results[
            'sitepreparation_labor_usd'] + self.results['sitepreparation_material_usd'] + self.results[
                                  'sitepreparation_mobilization_usd'] + self.results['sitepreparation_other_usd']
        self.assertEqual(self.results['total_sitepreparation_cost'], total_siteprep_cost)


    def test_foundation_cost(self):
        self.assertEqual(self.results['total_foundation_cost'], 10411261.424160697)
        self.assertEqual(self.results['foundation_equipment_rental_usd'], 304259.58127751213)
        self.assertEqual(self.results['foundation_labor_usd'], 3649178.419738848)
        self.assertEqual(self.results['foundation_material_usd'], 5511345.111857001)
        self.assertEqual(self.results['foundation_mobilization_usd'], 946478.311287336)
        total_foundation_cost = self.results['foundation_equipment_rental_usd'] + self.results['foundation_labor_usd'] + \
                                self.results['foundation_material_usd'] + self.results['foundation_mobilization_usd']
        self.assertEqual(self.results['total_foundation_cost'], total_foundation_cost)


    def test_total_erection_cost(self):
        self.assertEqual(self.results['total_erection_cost'], 5231110.226456955)
        self.assertEqual(self.results['erection_equipment_rental_usd'], 443521.60298406926)
        self.assertEqual(self.results['erection_labor_usd'], 4287043.623472886)
        self.assertEqual(self.results['erection_material_usd'], 0)
        self.assertEqual(self.results['erection_other_usd'], 0)
        self.assertEqual(self.results['erection_fuel_usd'], 18369.0)
        self.assertEqual(self.results['erection_mobilization_usd'], 482176)
        total_erection_cost = self.results['erection_equipment_rental_usd'] + self.results['erection_labor_usd'] + \
                              self.results['erection_material_usd'] + self.results['erection_other_usd'] + self.results[
                                  'erection_fuel_usd'] + self.results['erection_mobilization_usd']
        self.assertEqual(self.results['total_erection_cost'], total_erection_cost)


    def test_total_gridconnection_cost(self):
           self.assertEqual(self.results['total_gridconnection_cost'], 5617735.863912535)


    def test_total_collection_cost(self):
           self.assertEqual(self.results['total_collection_cost'], 4869435.746468595)
           self.assertEqual(self.results['collection_equipment_rental_usd'], 426614.6862960762)
           self.assertEqual(self.results['collection_labor_usd'], 1402888.0267842393)
           self.assertEqual(self.results['collection_material_usd'], 2808055.140699299)
           self.assertEqual(self.results['collection_mobilization_usd'], 231877.89268898076)


    def test_total_substation_cost(self):
           self.assertEqual(self.results['total_substation_cost'], 4940746.072082901)

    def test_read_weather_data(self):
        weather_data = read_weather_data(self.file_path)
        self.assertEqual(len(weather_data), 8760)

    def test_read_data(self):
        project_list = read_data()
        self.assertEqual(len(project_list.columns), 43)
