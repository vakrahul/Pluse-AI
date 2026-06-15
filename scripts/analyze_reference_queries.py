import pandas as pd
import json

file_path = "Oasis Payer360 - Data Dictionary.xlsx"
df = pd.read_excel(file_path, sheet_name="Reference SQL Queries")

questions = []
for index, row in df.iterrows():
    q = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else ""
    table = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
    if len(q) > 10:
        questions.append({
            "question": q,
            "target_table": table
        })

print(f"Found {len(questions)} reference queries.")
with open("reference_queries.json", "w") as f:
    json.dump(questions, f, indent=2)

# Print a summary of required tables
tables = {}
for q in questions:
    t = q['target_table']
    tables[t] = tables.get(t, 0) + 1

print("\n--- Required Tables for Reference Queries ---")
for t, count in sorted(tables.items(), key=lambda x: x[1], reverse=True):
    print(f"{count} queries -> {t}")
