import pandas as pd

# The extended_landbosse_details dataframe includes all the details along side
# all the project list inputs
df = pd.read_csv("extended_landbosse_details.csv")

# Extract the crane choice data
crane_choice_df = df.query("`Variable name` == 'crane_choice: Crew name - Boom system - Operation'")

print(crane_choice_df.head())

# The "Project ID with serial" is the key on the outer dictionary and the
# the crane operations are the keys on the inner dictionary. The values on
# the inner dictionary are the crane choices for each operation.
# projects: Dict[str, Dict[str, str]] = {}
