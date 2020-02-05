SELECT
	MIN("Hub height m"),
	"Turbine rating MW"
FROM
	costs_with_extended_project_list
GROUP BY 2;