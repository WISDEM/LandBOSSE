WITH baseline AS (SELECT
	 "Project ID with serial" AS "Baseline project ID with serial",
	 "Module",
	 "Type of cost",
	 ROUND("Cost per turbine"::numeric, 0) AS "Baseline $/turbine",
	 ROUND("Cost per project"::numeric, 0) AS "Baseline $/project",
	 ROUND("Cost per kW"::numeric, 0) AS "Baseline $/kW",
	 "Turbine rating MW" AS "Baseline turbine rating (MW)",
	 "Hub height m" AS "Baseline hub height",
	 "Labor cost multiplier" AS "Baseline labor cost multiplier",
	 "Crane breakdown fraction" AS "Baseline crane breakdown fraction",
	 ROUND("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) AS "Baseline plant size (MW)"
FROM
	landbosse_costs
WHERE
	ROUND("Number of turbines"::numeric * "Turbine rating MW"::numeric, -1) = 150
	AND "Hub height m" = 90
	AND "Turbine rating MW" = 2.5
	AND "Crane breakdown fraction" = 0
	AND "Labor cost multiplier" = 1.0
ORDER BY 1, 2, 3)

SELECT
	lc."Project ID with serial",
	lc."Module",
	lc."Type of cost",
	ROUND(lc."Cost per turbine"::numeric, 0) AS "$/turbine",
	ROUND(lc."Cost per project"::numeric, 0) AS "$/project",
	ROUND(lc."Cost per kW"::numeric, 0) AS "$/kW",
	b."Baseline $/turbine",
	b."Baseline $/project",
	b."Baseline $/kW",
	lc."Turbine rating MW" AS "Turbine rating (MW)",
	lc."Hub height m",
	lc."Labor cost multiplier",
	lc."Crane breakdown fraction",
	ROUND(lc."Number of turbines"::numeric * lc."Turbine rating MW"::numeric, -1) AS "Plant size (MW)",
	b."Baseline turbine rating (MW)",
	b."Baseline hub height",
	b."Baseline labor cost multiplier",
	b."Baseline crane breakdown fraction",
	b."Baseline plant size (MW)"
FROM landbosse_costs lc
JOIN baseline b
	ON b."Module" = lc."Module"
	AND b."Type of cost" = lc."Type of cost"
ORDER BY 1, 2, 3;