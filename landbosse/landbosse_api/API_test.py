import unittest
from unittest import TestCase


class TestLandBOSSE_API(TestCase):
    def setUp(self):
        api_inputs = dict()
        api_inputs['interconnect_voltage_kV'] = 137
        api_inputs['distance_to_interconnect_mi'] = 10
        api_inputs['num_turbines'] = 100
        api_inputs['turbine_spacing_rotor_diameters'] = 4
        api_inputs['row_spacing_rotor_diameters'] = 10
        api_inputs['turbine_rating_MW'] = 1.5
        api_inputs['rotor_diameter_m'] = 77
        api_inputs['hub_height_meters'] = 80
        api_inputs['wind_shear_exponent'] = 0.20
        api_inputs['depth'] = 2.36  # Foundation depth in m
        api_inputs['rated_thrust_N'] = 589000
        api_inputs['labor_cost_multiplier'] = 1
        api_inputs['gust_velocity_m_per_s'] = 59.50

    def test_total_BOS_cost(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
