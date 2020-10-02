import pandas as pd

# The extended_landbosse_details dataframe includes all the details along side
# all the project list inputs
print("Reading extended details...")
df = pd.read_csv("extended_landbosse_details.csv")

# Extract the crane choice data
print("Selecting erection data...")
erection_df = df.query("`Module` == 'ErectionCost'")[[
    "Project ID with serial",
    "Variable name",
    "Numeric value",
    "Non-numeric value",
    "Number of turbines",
    "Turbine rating MW",
    "Hub height m",
    "Labor cost multiplier",
    "Crane breakdown fraction",
    "Breakpoint between base and topping (percent)",
    "Total project construction time (months)"
]]

aligned_erection_rows = []

print("Selecting unique projects...")
unique_project_id_with_serial = erection_df['Project ID with serial'].unique()

print("Rearranging crane detail data from rows into columns...")
for project_id_with_serial in unique_project_id_with_serial:
    print(f"\t{project_id_with_serial}")

    # Crane data output
    crane_data_df = erection_df.query(
        "`Project ID with serial` == @project_id_with_serial and `Variable name` == 'crane_data_output: crane_boom_operation_concat - variable - value'"
    )
    top_wind_multiplier_row = crane_data_df[crane_data_df["Non-numeric value"].str.contains("Top - Wind multiplier")]
    base_wind_multiplier_row = crane_data_df[crane_data_df["Non-numeric value"].str.contains("Base - Wind multiplier")]
    offload_wind_multiplier_row = crane_data_df[crane_data_df["Non-numeric value"].str.contains("Offload - Wind multiplier")]
    top_wind_multiplier = top_wind_multiplier_row["Numeric value"].values[0]
    offload_wind_multiplier = offload_wind_multiplier_row["Numeric value"].values[0]
    if len(base_wind_multiplier_row) > 0:
        base_wind_multiplier = base_wind_multiplier_row["Numeric value"].values[0]
    else:
        base_wind_multiplier = None

    # Re-using crane_data_df from above, operation time for all turbines
    top_operation_time_hours_row = crane_data_df[
        crane_data_df["Non-numeric value"].str.contains("Top - Operation time all turbines hrs")]
    offload_operation_time_hours_row = crane_data_df[
        crane_data_df["Non-numeric value"].str.contains("Offload - Operation time all turbines hrs")]
    base_operation_time_hours_row = crane_data_df[
        crane_data_df["Non-numeric value"].str.contains("Base - Operation time all turbines hrs")]
    top_operation_time_hours = top_operation_time_hours_row["Numeric value"].values[0]
    offload_operation_time_hours = offload_operation_time_hours_row["Numeric value"].values[0]
    if len(base_operation_time_hours_row) > 0:
        base_operation_time_hours = base_operation_time_hours_row["Numeric value"].values[0]
    else:
        base_operation_time_hours = None

    # Crane cost details
    crane_cost_df = erection_df.query(
        "`Project ID with serial` == @project_id_with_serial and `Variable name` == 'crane_cost_details: Operation ID - Type of cost - Cost'"
    )
    top_total_cost_row = crane_cost_df[crane_cost_df["Non-numeric value"].str.contains("Top - Total cost USD")]
    base_total_cost_row = crane_cost_df[crane_cost_df["Non-numeric value"].str.contains("Base - Total cost USD")]
    offload_total_cost_row = crane_cost_df[crane_cost_df["Non-numeric value"].str.contains("Offload - Total cost USD")]
    top_total_cost = top_total_cost_row["Numeric value"].values[0]
    offload_total_cost = offload_total_cost_row["Numeric value"].values[0]
    if len(base_total_cost_row) > 0:
        base_total_cost = base_total_cost_row["Numeric value"].values[0]
    else:
        base_total_cost = None

    # Crane choice
    crane_choice_rows_df = erection_df.query(
        "`Project ID with serial` == @project_id_with_serial and `Variable name` == 'crane_choice: Crew name - Boom system - Operation'"
    )
    top_row = crane_choice_rows_df[crane_choice_rows_df["Non-numeric value"].str.contains("Top")]
    base_row = crane_choice_rows_df[crane_choice_rows_df["Non-numeric value"].str.contains("Base")]
    offload_row = crane_choice_rows_df[crane_choice_rows_df["Non-numeric value"].str.contains("Offload")]
    offload = " ".join(offload_row["Non-numeric value"].values[0].split(" - ")[:-1])
    top = " ".join(top_row["Non-numeric value"].values[0].split(" - ")[:-1])
    if len(base_row) > 0:
        base = " ".join(base_row["Non-numeric value"].values[0].split(" - ")[:-1])
    else:
        base = None

    aligned_erection_row = {
        "Project ID with serial": project_id_with_serial,
        "Number of turbines": top_row["Number of turbines"].values[0],
        "Breakpoint between base and topping (percent)": \
            top_row["Breakpoint between base and topping (percent)"].values[0],
        "Turbine rating MW": top_row["Turbine rating MW"].values[0],
        "Crane breakdown fraction": top_row["Crane breakdown fraction"].values[0],
        "Labor cost multiplier": top_row["Labor cost multiplier"].values[0],
        "Hub height m": top_row["Hub height m"].values[0],
        "Base crane choice": base,
        "Offload crane choice": offload,
        "Top crane choice": top,
        "Base total cost":
            round(float(base_total_cost), 0) if base_total_cost is not None else None,
        "Offload total cost": round(float(offload_total_cost), 0),
        "Top total cost": round(float(top_total_cost), 0),
        "Base wind multiplier":
            round(float(base_wind_multiplier), 2) if base_wind_multiplier is not None else None,
        "Offload wind multiplier": round(float(offload_wind_multiplier), 2),
        "Top wind multiplier": round(float(top_wind_multiplier), 2),
        "Base operation time all turbines (hours)":
            round(float(base_operation_time_hours), 0) if base_operation_time_hours is not None else None,
        "Offload operation time all turbines (hours)": round(float(offload_operation_time_hours), 0),
        "Top operation time all turbines (hours)": round(float(top_operation_time_hours), 0)
    }

    aligned_erection_rows.append(aligned_erection_row)

print("Writing crane choices...")
aligned_crane_choice_df = pd.DataFrame(aligned_erection_rows)
aligned_crane_choice_df.to_csv("crane_details.csv", index=False)
