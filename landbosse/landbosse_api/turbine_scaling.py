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


def edit_tower_sections(components_DF, number_of_sections, tower_mass_tonne, tower_section_height):
    tower_section_mass = tower_mass_tonne / number_of_sections
    # print(components_DF)
    remove_existing_tower_sections = components_DF[components_DF['Component'].str.match('Tower')].index
    components_DF = components_DF.drop(components_DF.index[remove_existing_tower_sections])

    lever_arm_m = list()
    i = 0
    while i < number_of_sections:
        lift_height_m = (i+1) * tower_section_height
        tower_radius = 1.35 #TODO: confirm this number. I've read this is closer to ~4.5m.
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



