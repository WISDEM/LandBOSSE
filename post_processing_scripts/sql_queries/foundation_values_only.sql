CREATE EXTENSION IF NOT EXISTS tablefunc;

SELECT * FROM crosstab(
	$$
	SELECT 
		"Project ID with serial", 
		"name", 
		"Numeric value" 
	FROM details_with_extended_project_list 
	WHERE "name" IN (
		'F_dead',
		'F_horiz',
		'Radius_g',
		'Radius_b',
		'Radius_o',
		'steel_mass_short_ton_per_turbine',
		'foundation_volume_concrete_m3_per_turbine',
		'M_tot_kN'
	)
	ORDER BY 1, 2
	$$
) AS ct(
	id text,
	"F_dead" text,
	"F_horiz" text,
	"Radius_g" text,
	"Radius_b" text,
	"Radius_o" text, 
	"steel_mass_short_ton_per_turbine" text,
	"foundation_volume_concrete_m3_per_turbine" text, 
	"M_tot_kN" text
);