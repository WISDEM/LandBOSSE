SELECT
	 SUM("Cost per turbine") AS "$/turbine summed by module",
	 SUM("Cost per project") AS "$/project summed by module",
	 SUM("USD/kW per project") AS "$/kW summed by module",
	 "Project ID with serial" AS id,
	 "Module",
	 "Turbine rating MW",
 	 "Hub height m",
 	 "Labor cost multiplier" AS "Labor rate",
 	 "Crane breakdown fraction" AS "Crane break",
 	 ROUND("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) AS "Plant size MW"
FROM
	costs_with_extended_project_list
GROUP BY 4, 5, 6, 7, 8, 9, 10
ORDER BY 4, 5
LIMIT 100;
	 