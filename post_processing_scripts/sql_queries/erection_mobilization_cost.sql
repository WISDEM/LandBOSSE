SELECT
	"Project ID with serial" AS id,
	"Module",
	"name",
	"unit",
	"Numeric value",
	"Non-numeric value"
FROM
	details_with_extended_project_list
WHERE "Project ID with serial" IN ('Baseline 1.5MW 91m RD 80m HH_0912', 'Baseline 1.5MW 91m RD 80m HH_0916')
		AND "name" = 'erection_selected_detailed_data: mobilization';