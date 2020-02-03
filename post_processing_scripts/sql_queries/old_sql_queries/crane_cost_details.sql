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
WHERE
	"Project ID with serial" = 'Baseline 1.5MW 91m RD 100m HH_0000'
	AND "Module" = 'ErectionCost'
	AND "name" IN ('crane_data_output: crane_boom_operation_concat - variable - value', 'total_erection_cost: Phase of construction - Type of cost - Cost USD')
ORDER BY 
	"Project ID with serial",
	"Module",
	"name",
	"Non-numeric value"
LIMIT 100;