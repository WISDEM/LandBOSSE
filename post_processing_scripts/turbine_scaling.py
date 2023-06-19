import csv
import numpy as np
import openmdao.api as om

from wisdem.nrelcsm.nrel_csm import aep_csm
from wisdem.turbine_costsse.nrel_csm_tcc_2015 import nrel_csm_2015

blade_number   = 3
machine_rating = 1e3 * np.array([1.5, 2., 2.5, 3.5, 5., 6., 10.])  # kW
rotor_diameter = np.array([91., 105., 117., 139., 166., 182., 235.])  # m
blade_mass_exp = np.arange(1.7, 2.41, 0.1)
max_tip_speed  = 90.0 # m/s
opt_tsr        = 9.0  # Optimal tip speed ratio
max_Cp         = 0.49 
rotor_Ct       = 0.8  # Max thrust coefficient
max_eff        = 0.95 # Drivetrain efficiency
cut_in         = 4.0 # m
cut_out        = 25.0 # m
altitude       = 0.0
rho_air        = 1.225 # kg/m^3
shear_exp      = 0.0 # No variation in z-height
array_losses   = 0.0 # Focusing on single turbine
availability   = 1.0
soiling_losses = 0.0
turbine_number = 1
weibull_k      = 2.0
wind_speed     = np.arange(5.0, 15.1, 1.0) # m/s

# Output containers
tcc = [['Rating [kW]', 'Rotor Diam [m]', 'Blade Mass Exp', 'Hub Height [m]', 'TCC [USD/kW]']]
aep = [['Rating [kW]', 'Rotor Diam [m]', 'Wind Speed [m/s]', 'AEP [kWh/yr]']]

# Compute object instances
prob_tcc = om.Problem()
prob_tcc.model = nrel_csm_2015()
prob_tcc.setup()
prob_tcc['blade_number']   = blade_number
prob_tcc['max_efficiency'] = max_eff
prob_tcc['max_tip_speed']  = max_tip_speed
prob_tcc['turbine_class']  = -1 # Sets blade mass based on user input, not auto-determined

aep_instance = aep_csm()

# Calculation loop
for irating, rating in enumerate(machine_rating):
    for idiam, diam in enumerate(rotor_diameter):
        # Diameter or radius?
        # hub_height = diam + 20.0

        # Assume hub height = radius + 20 m (for tip clearance)
        hub_height = (diam / 2.) + 20

        for iexp, bexp in enumerate(blade_mass_exp):
            prob_tcc['machine_rating'] = rating
            prob_tcc['rotor_diameter'] = diam
            prob_tcc['blade_user_exp'] = bexp
            prob_tcc['hub_height'] = hub_height
            
            prob_tcc.run_model()
            
            tcc.append([rating, diam, bexp, hub_height, float(prob_tcc['turbine_cost_kW'])])
            
        for iwind, wind in enumerate(wind_speed):
            aep_instance.compute(rating, max_tip_speed, diam, max_Cp, opt_tsr,
                cut_in, cut_out, hub_height, altitude, rho_air,
                max_eff, rotor_Ct, soiling_losses, array_losses, availability,
                turbine_number, shear_exp, wind, weibull_k)
            
            aep.append([rating, diam, wind, aep_instance.aep.net_aep])

            
# Write out data to csv files
with open('aep.csv', 'w') as fwrite:
    writer = csv.writer(fwrite)
    writer.writerows(aep)
    
with open('tcc.csv', 'w') as fwrite:
    writer = csv.writer(fwrite)
    writer.writerows(tcc)    


