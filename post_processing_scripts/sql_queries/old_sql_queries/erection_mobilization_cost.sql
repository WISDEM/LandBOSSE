SELECT
	"Project ID with serial" AS id,
	"Module",
	"name",
	"unit",
	"Numeric value"::numeric,
	"Non-numeric value",
	"Number of turbines" * "Turbine rating MW" AS "Project size MW"
FROM
	details_with_extended_project_list
WHERE "Project ID with serial" IN ('Baseline 1.5MW 91m RD 80m HH_0912', 'Baseline 1.5MW 91m RD 80m HH_0916')
		AND "name" = 'erection_selected_detailed_data: mobilization';