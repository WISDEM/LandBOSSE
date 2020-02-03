SELECT
	 "Project ID with serial" AS id,
	 "Module",
	 "Type of cost",
	 ROUND("Cost per turbine"::numeric, 0) AS "$/turbine",
	 ROUND("Cost per project"::numeric, 0) AS "$/project",
	 ROUND("USD/kW per project"::numeric, 0) AS "$/kW",
	 "Turbine rating MW",
	 "Hub height m",
	 "Labor cost multiplier" AS "Labor rate",
	 "Crane breakdown fraction" AS "Crane break",
	 ROUND("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) AS "Plant size MW"
FROM
	costs_with_extended_project_list
WHERE
	ROUND("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) = 150
	AND "Hub height m" = 90
	AND "Turbine rating MW" = 2.5
	AND "Crane breakdown fraction" = 0
	AND "Labor cost multiplier" = 1.0
ORDER BY 1, 2, 3;