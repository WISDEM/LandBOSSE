SELECT
	"Project ID with serial",
	"Module",
	"name",
	"unit",
	"Numeric value",
	"Non-numeric value",
	"Number of turbines",
	"Turbine rating MW",
	"Turbine rating MW" * "Number of turbines" AS "Plant size MW",
	"Hub height m",
	"Labor cost multiplier" AS "Labor cost",
	"Crane breakdown fraction" AS "Crane break"
FROM 
	details_with_extended_project_list
ORDER BY 
	"Project ID with serial",
	"Module",
	"name"
LIMIT 100;