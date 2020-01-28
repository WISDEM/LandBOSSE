SELECT
	"Project ID with serial",
	split_part("Non-numeric value", '-', 1) AS "Operation",
	split_part("Non-numeric value", '-', 2) AS "Crane name",
	split_part("Non-numeric value", '-', 3) AS "Boom system",
	"Numeric value"::bigint AS "Op days over construct days",
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
	"name" = 'erection_selected_detailed_data: Operation-Crane name-Boom system-Operational construct days over time construct days'
ORDER BY 
	"Project ID with serial",
	"Operation"
LIMIT 100;