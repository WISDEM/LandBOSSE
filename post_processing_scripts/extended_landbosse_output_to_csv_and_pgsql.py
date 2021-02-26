import os
import io

from sqlalchemy import create_engine
import pandas as pd


costs_path = "landbosse-costs.csv"
details_path = "landbosse-details.csv"
extended_project_list_path = os.path.join("calculated_parametric_inputs", "extended_project_list.csv")

print("Reading costs...")
costs = pd.read_csv(costs_path)
costs.drop(columns=['Number of turbines', 'Turbine rating MW', 'Rotor diameter m'], inplace=True)

print("Reading details...")
details = pd.read_csv(details_path)

print("Reading extended project list...")
extended_project_list = pd.read_csv(extended_project_list_path)

# Projects that are not parametrically modified will have a null in "Project ID with serial"
# In that case, those non-parametric projects will not be joined onto the extended project
# list.

print("Joining extended project list onto costs...")
join_landbosse_output_costs = costs.merge(right=extended_project_list, on="Project ID with serial")

print("Joining extended project list onto details...")
join_landbosse_output_details = details.merge(right=extended_project_list, on="Project ID with serial")

print("Writing joined .csv files...")
join_landbosse_output_costs.to_csv("extended_landbosse_costs.csv", index=False)
join_landbosse_output_details.to_csv("extended_landbosse_details.csv", index=False)

load_into_database_enabled = False
if load_into_database_enabled:
    print("Load into database...")

    # Get the security credentials and DB config from the environment
    # variables to maintain security.

    pg_password = os.environ.get("PG_PASSWORD", "no pasword was specified")
    pg_user = os.environ.get("PG_USER", "no pg pasword was specified")
    pg_database = os.environ.get("PG_DATABASE", "no pg database was specified")
    pg_port = os.environ.get("PG_PORT", "no pg port was specified")
    pg_host = os.environ.get("PG_HOST", "localhost")
    pg_port = os.environ.get("PG_PORT", "5432")
    engine_string = f"postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
    engine = create_engine(engine_string)

    # For ann explanation of how Pandas is creating SQL, see
    # https://pandas.pydata.org/pandas-docs/version/0.23/generated/pandas.DataFrame.to_sql.html
    #
    # Also, with respect to the string IO, the code is writing a CSV file into an
    # in memory buffer to insert all rows into each table in a single transaction
    # See https://stackoverflow.com/questions/23103962/how-to-write-dataframe-to-postgres-table

    cost_table_name = "landbosse_costs"
    join_landbosse_output_costs.head(0).to_sql(cost_table_name, engine, if_exists="replace", index=False)
    conn = engine.raw_connection()
    cur = conn.cursor()

    # Create buffer to hold the .csv. Write it into the buffer.
    output = io.StringIO()
    join_landbosse_output_costs.to_csv(output, sep="\t", header=False, index=False)

    # Rewind to beginning of the buffer and then dump it into the database
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, cost_table_name, null="")
    conn.commit()

    details_table_name = "landbosse_details"
    join_landbosse_output_details.head(0).to_sql(details_table_name, engine, if_exists="replace", index=False)
    output = io.StringIO()
    join_landbosse_output_details.to_csv(output, sep="\t", header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, details_table_name, null="")
    conn.commit()
