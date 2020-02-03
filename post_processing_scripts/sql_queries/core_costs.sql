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
	 round("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) AS "Plant size MW"
FROM
	costs_with_extended_project_list
ORDER BY 1, 2, 3
LIMIT 100;
	 