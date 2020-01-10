import os
import pandas as pd

landbosse_output_path = "landbosse-output.xlsx"
landbosse_extended_project_list_path = os.path.join("calculated_parametric_inputs", "extended_project_list.xlsx")

print("Reading costs...")
landbosse_output_costs = pd.read_excel(landbosse_output_path, "costs_by_module_type_operation")
print(landbosse_output_costs.head())

print("Reading details...")
landbosse_output_details = pd.read_excel(landbosse_output_path, "details")
print(landbosse_output_details.head())

print("Reading extended project list...")
extended_project_list = pd.read_excel(landbosse_extended_project_list_path)
print(extended_project_list.head())

print("Joining extended project list onto costs")
join_landbosse_output_costs = landbosse_output_costs.merge(right=extended_project_list, on="Project ID with serial")

print("Joining extended project list onto details...")
join_landbosse_details_costs = landbosse_output_details.merge(right=extended_project_list, on="Project ID with serial")

print("Writing the sheets...")
with pd.ExcelWriter("extended_landbosse_output.xlsx", mode="w") as writer:
    join_landbosse_output_costs.to_excel(writer, index=False, sheet_name="Costs extended")
    join_landbosse_details_costs.to_excel(writer, index=False, sheet_name="Details extended")
