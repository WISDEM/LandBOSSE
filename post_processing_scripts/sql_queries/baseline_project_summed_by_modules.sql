SELECT
	 SUM("Cost per turbine") AS "$/turbine total",
	 SUM("Cost per project") AS "$/project total",
	 SUM("USD/kW per project") AS "$/kW total",
	 "Project ID with serial" AS id,
	 "Module",
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
GROUP BY 4, 5, 6, 7, 8, 9, 10
ORDER BY 4, 5;