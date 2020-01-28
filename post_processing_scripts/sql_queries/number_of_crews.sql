SELECT
	"Project ID with serial",
	"Module",
	"name",
	"unit",
	"Numeric value" AS "Operational construct days over time construct days",
	"Non-numeric value" AS "Operation-Crane name-Boom system-Operational construct days over time construct days",
	"Total project construction time (months)",
	"Number of turbines",
	"Turbine rating MW",
	"Turbine rating MW" * "Number of turbines" AS "Plant size MW",
	"Hub height m",
	"Labor cost multiplier" AS "Labor cost",
	"Crane breakdown fraction" AS "Crane break"
FROM 
	details_with_extended_project_list
WHERE
	"name" = 'erection_selected_detailed_data: Operation-Crane name-Boom system-Operational construct days over time construct days'
ORDER BY 
	"Project ID with serial",
	"Module",
	"name"
LIMIT 100;