from ingestion import ingest_file

# Test with a CSV — we'll create a dummy one
import pandas as pd

# Create a sample CSV to test with
sample = pd.DataFrame({
    "Product Name": ["Apple", "Banana", "Mango"],
    "Sales": [100, 200, 150],
    "Region": ["North", "South", "East"]
})
sample.to_csv("../../uploads/test_data.csv", index=False)

# Now test ingestion
df = ingest_file("../../uploads/test_data.csv")
print(df)
print(df.dtypes)