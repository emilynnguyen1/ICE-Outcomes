from google.cloud import bigquery
import pandas as pd

# Initialize the client. It automatically uses your secure gcloud login.
client = bigquery.Client(project="ice-data-project")

# This returns the first 5 rows with ALL (106) columns
query = """
    SELECT *
    FROM `ice-data-project.ice_data_clean.master_50k_12`
    LIMIT 5
"""

print("Connecting to BigQuery...")
df = client.query(query).to_dataframe()

print("Success! Here is your data:")
#print(df.head())


# SHOW ALL COLUMNS IN DATAFRAME
record_columns = ['arrests', 'decisions', 'detentions', 'removals']
for col in record_columns:
    # 1. Convert any missing records (NaN) into empty dictionaries to prevent crashes
    df[col] = df[col].apply(lambda x: x if isinstance(x, dict) else {})
    
    # 2. Flatten the dictionary into its own temporary DataFrame
    # Adding a prefix ensures we know where the data came from (e.g., 'detentions_Case ID')
    flat_df = pd.json_normalize(df[col]).add_prefix(f'{col}_')
    
    # 3. Attach the newly flattened columns back to the main DataFrame
    df = pd.concat([df, flat_df], axis=1)
    
    # 4. Drop the original nested column to keep the DataFrame clean
    df = df.drop(columns=[col])
print("\nData successfully flattened!")
for col in df.columns:
    print(col)

# HOW TO GET SPECIFIC COLUMNS FROM DIFFERENT PARTS OF THE TABLE
spec_query = """
    SELECT 
        arrests.`Case ID` AS `arrests_Case ID`,
        decisions.RCA_DECISION_DATE AS decisions_RCA_DECISION_DATE,
        detentions.Ethnicity AS detentions_Ethnicity,
        removals.`MSC Charge` AS `removals_MSC Charge`
    FROM `ice-data-project.ice_data_clean.all_info_12`
    LIMIT 5
"""
print("Fetching targeted columns from BigQuery...")
df = client.query(spec_query).to_dataframe()
print("Success! Here is your cleanly formatted data:")
print(df.head())
