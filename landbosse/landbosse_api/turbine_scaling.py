from math import ceil, pi
import pandas as pd
pd.set_option('display.width', 6000)
pd.set_option('display.max_columns', 20)

def tower_mass(nameplate, HH):
    # nameplate = nameplate_MW * 1000
    tower_mass_tonne = (nameplate / ((-0.0408 * (nameplate ** 2)) + (0.6734 * nameplate) + 0.632)) * (
                0.0401 * (HH ** 2)) - (4.4775 * HH) + 230.88
    return tower_mass_tonne

# number of tower sections:
def tower_specs(HH, tower_mass):
    number_of_sections = max(ceil(HH/30), ceil(tower_mass/80))
    # print(number_of_sections)
    tower_section_height = HH/number_of_sections
    return number_of_sections, tower_section_height

#TODO: Add addl. argument (hub height) for storing component's lift height and lever arm m.
def edit_tower_sections(components_DF, number_of_sections, tower_mass_tonne, tower_section_height):
    tower_section_mass = tower_mass_tonne / number_of_sections
    # print(components_DF)
    remove_existing_tower_sections = components_DF[components_DF['Component'].str.match('Tower')].index
    components_DF = components_DF.drop(components_DF.index[remove_existing_tower_sections])

    lever_arm_m = list()
    i = 0
    while i < number_of_sections:
        lift_height_m = (i+1) * tower_section_height
        tower_radius = 1.35 #in m. TODO: confirm this number. I've read this is closer to ~4.5m.
        surface_area_m2 = pi * tower_section_height * (tower_radius**2)
        if i == 0:
            lever_arm_m.append(0.5 * tower_section_height)
        else:
            lever_arm_m.append((i * tower_section_height) + (0.5 * tower_section_height))
        tower_section_df = pd.DataFrame(
            [['Tower section ' + str(i + 1), tower_section_mass, lift_height_m, surface_area_m2, 0.6, 1.1,
              tower_section_height, lever_arm_m[i], 1, 6, 0.5, 0, 1]],
            columns=['Component', 'Mass tonne', 'Lift height m', 'Surface area sq m', 'Coeff drag',
                     'Coeff drag (installed)',
                     'Section height m', 'Lever arm m', 'Cycle time installation hrs', 'Offload hook height m',
                     'Offload cycle time hrs',
                     'Multplier drag rotor', 'Multiplier tower drag'])
        components_DF = components_DF.append(tower_section_df)
        i += 1
    # print(components_DF)
    return components_DF

def blade_mass_ton(rotor_diameter_m):
    combined_blade_mass_ton = (0.0056 * (rotor_diameter_m ** 2)) - (0.3818 * rotor_diameter_m) + 11.753
    return combined_blade_mass_ton

def edit_blade_info(components_DF, blade_mass_ton, HH, rotor_diameter_m):
    # print(components_DF)
    rotor_solidity = 0.1 # https://www.slideshare.net/pawanrm1/wind-turbine-design
    swept_area_m2 = pi * (rotor_diameter_m ** 2)
    blade_surface_area_m2 = rotor_solidity * swept_area_m2 / 3
    single_blade_mass_ton = blade_mass_ton / 3  # since LandBOSSE assumes it's a 3-bladed machine
    remove_existing_blade_rows = components_DF[components_DF['Component'].str.match('Blade')].index
    components_DF = components_DF.drop(components_DF.index[remove_existing_blade_rows])

    lift_height_m = HH
    lever_arm_m = HH

    blade_1 = pd.DataFrame(
        [['Blade 1', single_blade_mass_ton, lift_height_m, blade_surface_area_m2, 0.1, 1.4,
          0, lever_arm_m, 1, 6, 0.5, 0.667, 0]],
        columns=['Component', 'Mass tonne', 'Lift height m', 'Surface area sq m', 'Coeff drag',
                 'Coeff drag (installed)',
                 'Section height m', 'Lever arm m', 'Cycle time installation hrs', 'Offload hook height m',
                 'Offload cycle time hrs',
                 'Multplier drag rotor', 'Multiplier tower drag'])

    blade_2 = pd.DataFrame(
        [['Blade 2', single_blade_mass_ton, lift_height_m, blade_surface_area_m2, 0.1, 1.4,
          0, lever_arm_m, 1, 6, 0.5, 0.667, 0]],
        columns=['Component', 'Mass tonne', 'Lift height m', 'Surface area sq m', 'Coeff drag',
                 'Coeff drag (installed)',
                 'Section height m', 'Lever arm m', 'Cycle time installation hrs', 'Offload hook height m',
                 'Offload cycle time hrs',
                 'Multplier drag rotor', 'Multiplier tower drag'])

    blade_3 = pd.DataFrame(
        [['Blade 3', single_blade_mass_ton, lift_height_m, blade_surface_area_m2, 0.1, 1.4,
          0, lever_arm_m, 1, 6, 0.5, 0.667, 0]],
        columns=['Component', 'Mass tonne', 'Lift height m', 'Surface area sq m', 'Coeff drag',
                 'Coeff drag (installed)',
                 'Section height m', 'Lever arm m', 'Cycle time installation hrs', 'Offload hook height m',
                 'Offload cycle time hrs',
                 'Multplier drag rotor', 'Multiplier tower drag'])

    components_DF = components_DF.append(blade_1)
    components_DF = components_DF.append(blade_2)
    components_DF = components_DF.append(blade_3)
    # print(components_DF)
    return components_DF

def hub_mass(nameplate):
    nameplate = nameplate * 1000    # convert form MW to kW
    hub_mass_ton = ((1e-06) * (nameplate ** 2)) + (0.0039 * nameplate) + 3.652
    return hub_mass_ton

def edit_hub_info(components_DF, hub_mass, HH):
    remove_existing_hub_rows = components_DF[components_DF['Component'].str.match('Hub')].index
    components_DF = components_DF.drop(components_DF.index[remove_existing_hub_rows])
    lift_height_m = HH

    #TODO: find a relationship for hub surface area.
    hub_surface_area = 12.16
    lever_arm_m = HH
    hub = pd.DataFrame(
        [['Hub', hub_mass, lift_height_m, hub_surface_area, 1.1, 1.1,
          0, lever_arm_m, 1, 6, 0.5, 0, 0]],
        columns=['Component', 'Mass tonne', 'Lift height m', 'Surface area sq m', 'Coeff drag',
                 'Coeff drag (installed)',
                 'Section height m', 'Lever arm m', 'Cycle time installation hrs', 'Offload hook height m',
                 'Offload cycle time hrs',
                 'Multplier drag rotor', 'Multiplier tower drag'])
    components_DF = components_DF.append(hub)
    return components_DF


def nacelle_mass(nameplate):
    nameplate = nameplate * 1000  # convert form MW to kW
    nacelle_mass_ton = ((4e-06) * (nameplate**2)) + (0.0233 * nameplate) + 3.7349
    return nacelle_mass_ton



def edit_nacelle_info(components_DF, nacelle_mass_ton, HH):
    # print(components_DF)
    components_DF = components_DF[components_DF.Component != 'Nacelle']
    lift_height_m = HH

    # TODO: find a relationship for nacelle surface area.
    nacelle_surface_area = 33
    lever_arm_m = HH
    nacelle = pd.DataFrame(
        [['Nacelle', nacelle_mass_ton, lift_height_m, nacelle_surface_area, 0.8, 0.8,
          0, lever_arm_m, 1.5, 6, 0.5, 1, 0]],
        columns=['Component', 'Mass tonne', 'Lift height m', 'Surface area sq m', 'Coeff drag',
                 'Coeff drag (installed)',
                 'Section height m', 'Lever arm m', 'Cycle time installation hrs', 'Offload hook height m',
                 'Offload cycle time hrs',
                 'Multplier drag rotor', 'Multiplier tower drag'])

    components_DF = components_DF.append(nacelle)
    # print(components_DF)
    return components_DF

