
def tower_mass(nameplate, HH):
    tower_mass_kg = (nameplate / ((-0.0408 * (nameplate ** 2)) + (0.6734 * nameplate) + 0.632)) * (
                0.0401 * (HH ** 2)) - (4.4775 * HH) + 230.88


