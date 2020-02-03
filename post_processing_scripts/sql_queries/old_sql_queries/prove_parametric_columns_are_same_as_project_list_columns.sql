SELECT
	"Project ID with serial"
FROM
	costs_with_extended_project_list
WHERE
	"Crane breakdown fraction" <> "project list/nan/Crane breakdown fraction"
	OR "Labor cost multiplier" <> "project list/nan/Labor cost multiplier"
	OR "Number of turbines_x" <> "project list/nan/Number of turbines"
	OR "Number of turbines_y" <> "project list/nan/Number of turbines";