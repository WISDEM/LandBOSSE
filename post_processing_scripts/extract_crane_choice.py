from typing import Dict
import pandas as pd

# The extended_landbosse_details dataframe includes all the details along side
# all the project list inputs
df = pd.read_csv("extended_landbosse_details.csv")

# Extract the crane choice data
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

# The "Project ID with serial" is the key on the outer dictionary and the
# the crane operations are the keys on the inner dictionary. The values on
# the inner dictionary are the crane choices for each operation.
projects: Dict[str, Dict[str, str]] = {}

unique_project_id_with_serial = crane_choice_df['Project ID with serial'].unique()

def separate_crane_row(row):
    crane_choice = str(row["Non-numeric value"])
    return crane_choice.split(" - ")


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

    projects[project_id_with_serial] = {
        "Project ID with serial": project_id_with_serial,
        "Base": base,
        "Offload": offload,
        "Top": top
    }

    print(projects[project_id_with_serial])
