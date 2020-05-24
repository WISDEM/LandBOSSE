import os
from ..run import *
from unittest import TestCase


class TestLandBOSSE_API(TestCase):
    def setUp(self):
        self.file_path = os.path.dirname(__file__) + '/project_data/az_rolling.srw'
        api_inputs = dict()
        api_inputs['num_turbines'] = 100
        api_inputs['project_id'] = 'foundation_validation_ge15'
        self.results = run_landbosse(api_inputs)
        print(self.results)

    def test_total_BOS_cost(self):\
        self.assertEqual(44208796.36106637, self.results['total_bos_cost'])

    def test_total_management_cost(self):
        delta = 0.002    # max % tolerance in expected and actual value
        self.assertAlmostEqual(10570956.97,
                               self.results['total_management_cost'],
                               delta=int(delta * 10570956.97))

        self.assertAlmostEqual(188371.90,
                               self.results['insurance_usd'],
                               delta=int(delta * 188371.90))

        self.assertAlmostEqual(400723.14,
                               self.results['construction_permitting_usd'],
                               delta=int(delta * 400723.14))

        self.assertAlmostEqual(1887763.492,
                               self.results['project_management_usd'],
                               delta=int(delta * 1887763.492))

        self.assertAlmostEqual(336378.394,
                               self.results['bonding_usd'],
                               delta=int(delta * 336378.394))

        self.assertAlmostEqual(4379646.689,
                               self.results['markup_contingency_usd'],
                               delta=int(delta * 4379646.689))

        self.assertAlmostEqual(2071325,
                               self.results['engineering_usd'],
                               delta=int(delta * 2071325))

        self.assertAlmostEqual(1306748.35,
                               self.results['site_facility_usd'],
                               delta=int(delta * 1306748.35))

        total_management_cost = self.results['insurance_usd'] + \
                                self.results['construction_permitting_usd'] + \
                                self.results['project_management_usd'] + \
                                self.results['bonding_usd'] + \
                                self.results['markup_contingency_usd'] + \
                                self.results['engineering_usd'] + \
                                self.results['site_facility_usd']

        self.assertAlmostEqual(self.results['total_management_cost'],
                               total_management_cost,
                               delta=int(delta * self.results['total_management_cost']))

    def test_siteprep_cost(self):
        self.assertEqual(self.results['total_sitepreparation_cost'], 3209538.616279147)
        self.assertEqual(round(self.results['sitepreparation_equipment_rental_usd'], 2), 412013.84)
        self.assertEqual(round(self.results['sitepreparation_labor_usd'], 4), 609463.1297)
        self.assertEqual(round(self.results['sitepreparation_material_usd'], 4), 797751.5346)
        self.assertEqual(round(self.results['sitepreparation_mobilization_usd'], 5), 83009.35197)
        self.assertEqual(self.results['sitepreparation_other_usd'], 1307300.76)

        total_siteprep_cost = self.results['sitepreparation_equipment_rental_usd'] + \
                              self.results['sitepreparation_labor_usd'] + \
                              self.results['sitepreparation_material_usd'] + \
                              self.results['sitepreparation_mobilization_usd'] + \
                              self.results['sitepreparation_other_usd']

        self.assertEqual(self.results['total_sitepreparation_cost'], total_siteprep_cost)

    def test_foundation_cost(self):
        self.assertEqual(self.results['total_foundation_cost'], 10036157.011254452)
        self.assertEqual(self.results['foundation_equipment_rental_usd'], 307553.56983444514)
        self.assertEqual(round(self.results['foundation_labor_usd'], 3), 3677659.987)
        self.assertEqual(round(self.results['foundation_material_usd'], 3), 5573031.216)
        self.assertEqual(round(self.results['foundation_mobilization_usd'], 4), 477912.2386)

        total_foundation_cost = self.results['foundation_equipment_rental_usd'] + \
                                self.results['foundation_labor_usd'] + \
                                self.results['foundation_material_usd'] + \
                                self.results['foundation_mobilization_usd']

        self.assertEqual(self.results['total_foundation_cost'], total_foundation_cost)

    def test_total_erection_cost(self):
        self.assertEqual(6811700.7960274285, self.results['total_erection_cost'])
        self.assertEqual(748911.4927891536, self.results['erection_equipment_rental_usd'])
        self.assertEqual(5134653.8032382745, self.results['erection_labor_usd'])
        self.assertEqual(0, self.results['erection_material_usd'])
        self.assertEqual(0, self.results['erection_other_usd'])
        self.assertEqual(28825.5, self.results['erection_fuel_usd'])
        self.assertEqual(899310, self.results['erection_mobilization_usd'])

        total_erection_cost = self.results['erection_equipment_rental_usd'] + \
                              self.results['erection_labor_usd'] + \
                              self.results['erection_material_usd'] + \
                              self.results['erection_other_usd'] + \
                              self.results['erection_fuel_usd'] + \
                              self.results['erection_mobilization_usd']

        self.assertEqual(self.results['total_erection_cost'], total_erection_cost)

    def test_total_gridconnection_cost(self):
           self.assertEqual(4084775.152898776, self.results['total_gridconnection_cost'])

    def test_total_collection_cost(self):
           self.assertEqual(self.results['total_collection_cost'], 4869435.746468595)
           self.assertEqual(self.results['collection_equipment_rental_usd'], 426614.6862960762)
           self.assertEqual(self.results['collection_labor_usd'], 1402888.0267842393)
           self.assertEqual(self.results['collection_material_usd'], 2808055.140699299)
           self.assertEqual(self.results['collection_mobilization_usd'], 231877.89268898076)

    def test_total_substation_cost(self):
           self.assertEqual(4859182.072082901, self.results['total_substation_cost'])

    def test_read_weather_data(self):
        weather_data = read_weather_data(self.file_path)
        self.assertEqual(len(weather_data), 8760)

    def test_read_data(self):
        input_dictionary = dict()
        project_list = read_data(input_dictionary)
        self.assertEqual(len(project_list.columns), 47)
