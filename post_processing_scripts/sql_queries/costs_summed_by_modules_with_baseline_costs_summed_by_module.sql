WITH baseline_costs_summed_by_module AS (SELECT
	 "Cost per turbine" AS "$/turbine baseline",
	 "Cost per project" AS "$/project baseline",
	 "USD/kW per project" AS "$/kW baseline",
	 "Project ID with serial" AS id,
	 "Module",
	 "Type of cost",
	 "Turbine rating MW" AS "Baseline turbine rating MW",
	 "Hub height m" AS "Baseline hub height m",
	 "Labor cost multiplier" AS "Baseline labor rate",
	 "Crane breakdown fraction" AS "Baseline crane break",
	 ROUND("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) AS "Baseline plant size MW"
FROM
	costs_with_extended_project_list
WHERE
	ROUND("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) = 150
	AND "Hub height m" = 110
	AND "Turbine rating MW" = 2.5
	AND "Crane breakdown fraction" = 0
	AND "Labor cost multiplier" = 1.0
ORDER BY "Project ID with serial", "Module", "Type of cost")

SELECT
	c."Project ID with serial" AS id,
	 c."Cost per turbine" AS "$/turbine",
	 c."Cost per project" AS "$/project",
	 c."USD/kW per project" AS "$/kW",
	 b."$/turbine baseline",
	 b."$/project baseline",
	 b."$/kW baseline",
	 c."Module",
	 c."Type of cost",
	 c."Turbine rating MW",
 	 c."Hub height m",
 	 c."Labor cost multiplier" AS "Labor rate",
 	 c."Crane breakdown fraction" AS "Crane break",
 	 ROUND(c."Number of turbines"::numeric * c."Turbine rating MW"::numeric, -1) AS "Plant size MW",
	 b."Baseline turbine rating MW",
	 b."Baseline hub height m",
	 b."Baseline labor rate",
	 b."Baseline crane break",
	 b."Baseline plant size MW"
FROM
	costs_with_extended_project_list c
JOIN
	baseline_costs_summed_by_module b
	ON c."Module" = b."Module" AND c."Type of cost" = b."Type of cost"
ORDER BY
	c."Project ID with serial",
	c."Module";