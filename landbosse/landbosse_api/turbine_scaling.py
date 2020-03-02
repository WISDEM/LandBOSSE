from math import ceil
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
    number_of_sections = ceil(HH/30)
    tower_section_height = HH/number_of_sections
    return number_of_sections, tower_section_height


def edit_tower_sections(components_DF, number_of_sections, tower_mass_tonne):
    tower_section_mass = tower_mass_tonne / number_of_sections
    print(components_DF)
    remove_existing_tower_sections = components_DF[components_DF['Component'].str.match('Tower')].index
    components_DF = components_DF.drop(components_DF.index[remove_existing_tower_sections])
    i=0
    while i < number_of_sections:
        # tower_section_df = pd.DataFrame([['Equipment rental', 10, 'Foundation']])
        tower_section_df = pd.DataFrame(
            [['Tower section ' + str(i + 1), tower_section_mass, 20, 85, 0.6, 1.1, 20, 10, 1, 6, 0.5, 0, 1]],
            columns=['Component', 'Mass tonne', 'Lift height m', 'Surface area sq m', 'Coeff drag',
                     'Coeff drag (installed)',
                     'Section height m', 'Lever arm m', 'Cycle time installation hrs', 'Offload hook height m',
                     'Offload cycle time hrs',
                     'Multplier drag rotor', 'Multiplier tower drag'])
        components_DF = components_DF.append(tower_section_df)
        i+=1
    print(components_DF)
    return components_DF



