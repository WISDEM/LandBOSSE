from typing import Dict
import pandas as pd

# The extended_landbosse_details dataframe includes all the details along side
# all the project list inputs
print("Reading extended details")
df = pd.read_csv("extended_landbosse_details.csv")

# Extract the crane choice data
print("Selecting crane data")
crane_choice_df = df.query("`Variable name` == 'crane_choice: Crew name - Boom system - Operation'")[[
    "Project ID with serial",
    "Variable name",
    "Non-numeric value",
    "Number of turbines",
    "Turbine rating MW",
    "Hub height m",
    "Labor cost multiplier",
    "Crane breakdown fraction",
    "Breakpoint between base and topping (percent)",
    "Total project construction time (months)"
]]

aligned_crane_choices = []

print("Selecting unique projects...")
unique_project_id_with_serial = crane_choice_df['Project ID with serial'].unique()

print("Aligning crane types")
for project_id_with_serial in unique_project_id_with_serial:
    crane_rows_df = crane_choice_df.query("`Project ID with serial` == @project_id_with_serial")
    top_row = crane_rows_df[crane_rows_df["Non-numeric value"].str.contains("Top")]
    base_row = crane_rows_df[crane_rows_df["Non-numeric value"].str.contains("Base")]
    offload_row = crane_rows_df[crane_rows_df["Non-numeric value"].str.contains("Offload")]

    offload = " ".join(offload_row["Non-numeric value"].values[0].split(" - ")[:-1])
    top = " ".join(top_row["Non-numeric value"].values[0].split(" - ")[:-1])

    if len(base_row) > 0:
        base = " ".join(base_row["Non-numeric value"].values[0].split(" - ")[:-1])
    else:
        base = "No base crane"

    aligned_crane_choice = {
        "Project ID with serial": project_id_with_serial,
        "Number of turbines": top_row["Number of turbines"].values[0],
        "Breakpoint between base and topping (percent)": \
            top_row["Breakpoint between base and topping (percent)"].values[0],
        "Turbine rating MW": top_row["Turbine rating MW"].values[0],
        "Crane breakdown fraction": top_row["Crane breakdown fraction"].values[0],
        "Labor cost multiplier": top_row["Labor cost multiplier"].values[0],
        "Hub height m": top_row["Hub height m"].values[0],
        "Base": base,
        "Offload": offload,
        "Top": top
    }

    aligned_crane_choices.append(aligned_crane_choice)

print("Writing crane choices...")
aligned_crane_choice_df = pd.DataFrame(aligned_crane_choices)
aligned_crane_choice_df.to_csv("crane_choices.csv", index=False)
