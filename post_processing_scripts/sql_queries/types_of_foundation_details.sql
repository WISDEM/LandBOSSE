SELECT 
	DISTINCT("name")
FROM details_with_extended_project_list 
WHERE 
	"Module" = 'FoundationCost'
	AND "Variable or DataFrame" = 'variable';