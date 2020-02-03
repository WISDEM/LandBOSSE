SELECT
	"Project ID with serial",
	split_part("Non-numeric value", '-', 1) AS "Operation",
	split_part("Non-numeric value", '-', 2) AS "Crane name",
	split_part("Non-numeric value", '-', 3) AS "Boom system",
	"Numeric value"::bigint AS "Number of equipment",
	"Total project construction time (months)",
	"Number of turbines",
	"Turbine rating MW",
	round("Turbine rating MW" * "Number of turbines") AS "Plant size MW",
	"Hub height m",
	"Labor cost multiplier" AS "Labor cost",
	"Crane breakdown fraction" AS "Crane break"
FROM 
	details_with_extended_project_list
WHERE
	"name" = '_number_of_equip: Operation-Crane name-Boom system-Number of equipment'
ORDER BY 
	"Plant size MW",
	"Project ID with serial",
	"Operation"
LIMIT 100;