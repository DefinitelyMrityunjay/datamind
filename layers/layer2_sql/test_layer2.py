import sys
sys.path.append("../../")
sys.path.append("../layer1_ingestion")

from ingestion import ingest_file
from sql_engine import push_to_postgres, run_query, get_table_schema
import pandas as pd

print("--- LAYER 1: Creating test CSV ---")
sample = pd.DataFrame({
    "Product Name": ["Apple", "Banana", "Mango", "Grapes", "Orange"],
    "Sales": [100, 200, 150, 300, 175],
    "Revenue": [500.50, 800.00, 600.75, 1200.00, 700.25],
    "Region": ["North", "South", "East", "West", "North"],
    "Sale Date": ["2024-01-15", "2024-02-20", "2024-03-10", "2024-04-05", "2024-05-18"]
})
sample.to_csv("../../uploads/test_data.csv", index=False)
print("CSV created")

print("\n--- LAYER 1: Ingesting ---")
df = ingest_file("../../uploads/test_data.csv")
print(df)

print("\n--- LAYER 2: Pushing to PostgreSQL ---")
metadata = push_to_postgres(df, file_name="test_data.csv")
print(metadata)

print("\n--- LAYER 2: Running SQL query ---")
table = metadata["table_name"]
result = run_query(f"SELECT * FROM {table} ORDER BY sales DESC")
print(result)

print("\n--- LAYER 2: Schema ---")
schema = get_table_schema(table)
for col in schema["columns"]:
    print(f"  {col['name']} → {col['type']}")