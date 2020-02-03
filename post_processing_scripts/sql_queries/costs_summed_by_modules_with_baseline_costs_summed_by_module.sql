WITH baseline_costs_summed_by_module AS (SELECT
	 SUM("Cost per turbine") AS "$/turbine baseline summed by module",
	 SUM("Cost per project") AS "$/project baseline summed by module",
	 SUM("USD/kW per project") AS "$/kW baseline summed by module",
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
ORDER BY 4, 5)

SELECT
	c."Project ID with serial" AS id,
	 SUM(c."Cost per turbine") AS "$/turbine summed by module",
	 SUM(c."Cost per project") AS "$/project summed by module",
	 SUM(c."USD/kW per project") AS "$/kW summed by module",
	 b."$/turbine baseline summed by module",
	 b."$/project baseline summed by module",
	 b."$/kW baseline summed by module",
	 c."Module",
	 c."Turbine rating MW",
 	 c."Hub height m",
 	 c."Labor cost multiplier" AS "Labor rate",
 	 c."Crane breakdown fraction" AS "Crane break",
 	 ROUND(c."Number of turbines"::numeric * c."Turbine rating MW"::numeric, -1) AS "Plant size MW",
	 b."Turbine rating MW" AS "Baseline turbine rating MW",
	 b."Hub height m" AS "Baseline hub height m",
	 b."Labor rate" AS "Baseline labor rate",
	 b."Crane break" AS "Baseline crane break",
	 b."Plant size MW" AS "Baseline plant size MW"
FROM
	costs_with_extended_project_list c
JOIN
	baseline_costs_summed_by_module b
	ON c."Module" = b."Module"
GROUP BY 1, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18
ORDER BY
	c."Project ID with serial",
	c."Module"
LIMIT 100;