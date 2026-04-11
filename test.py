import pandas as pd
from layers.layer1_ingestion.cleaner import clean_dataframe

# Simulate a messy DataFrame
messy_data = {
    "First Name": ["Alice", "Bob", "  Charlie  ", "Alice"],  # spaces + duplicate
    "Age ": ["25", "30", "not a number", None],              # string dtype, bad value
    "Salary($)": [50000, 60000, 70000, 50000],
    "Unnamed: 0": [1, 2, 3, 4],                              # meaningless index col
    "notes": [None, None, None, None],                        # 100% empty column
}
df = pd.DataFrame(messy_data)

print("BEFORE cleaning:")
print(df)
print()

result = clean_dataframe(df, use_ai=True)

print("AFTER cleaning:")
print(result["dataframe"])
print()
print("Cleaning log:")
for line in result["log"]:
    print(" ", line)