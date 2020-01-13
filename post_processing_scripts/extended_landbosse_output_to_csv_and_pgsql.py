import os
import io

import psycopg2
from sqlalchemy import create_engine
import pandas as pd


landbosse_output_path = "landbosse-output.xlsx"
landbosse_extended_project_list_path = os.path.join("calculated_parametric_inputs", "extended_project_list.xlsx")

print("Reading costs...")
landbosse_output_costs = pd.read_excel(landbosse_output_path, "costs_by_module_type_operation")

print("Reading details...")
landbosse_output_details = pd.read_excel(landbosse_output_path, "details")

print("Reading extended project list...")
extended_project_list = pd.read_excel(landbosse_extended_project_list_path)

print("Joining extended project list onto costs...")
join_landbosse_output_costs = landbosse_output_costs.merge(right=extended_project_list, on="Project ID with serial")

print("Joining extended project list onto details...")
join_landbosse_output_details = landbosse_output_details.merge(right=extended_project_list, on="Project ID with serial")

print("Writing .csv files...")
join_landbosse_output_costs.to_csv("extended_landbosse_costs.csv", index=False)
join_landbosse_output_details.to_csv("extended_landbosse_details.csv", index=False)

etl_into_database_enabled = True
if etl_into_database_enabled:
    print("ETL into database...")

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

    cost_table_name = "costs_with_extended_project_list"
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

    details_table_name = "details_with_extended_project_list"
    join_landbosse_output_details.head(0).to_sql(details_table_name, engine, if_exists="replace", index=False)
    output = io.StringIO()
    join_landbosse_output_details.to_csv(output, sep="\t", header=False, index=False)
    output.seek(0)
    contents = output.getvalue()
    cur.copy_from(output, details_table_name, null="")
    conn.commit()
