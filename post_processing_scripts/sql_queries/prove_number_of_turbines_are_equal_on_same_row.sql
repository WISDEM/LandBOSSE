SELECT
	"Project ID with serial",
	"Number of turbines",
	"Turbine rating MW",
	"Turbine rating MW" * "Number of turbines" AS "Plant size MW",
	"Hub height m",
	"Labor cost multiplier" AS "Labor cost",
	"Crane breakdown fraction" AS "Crane break"
FROM details_with_extended_project_list
WHERE "Number of turbines" != "project list/nan/Number of turbines"
ORDER BY "Project ID with serial"
LIMIT 100;