import pandas as pd
import json
import sys

try:
    file_path = "Oasis Payer360 - Data Dictionary.xlsx"
    xl = pd.ExcelFile(file_path)
    
    output = {}
    for sheet in xl.sheet_names:
        df = xl.parse(sheet)
        output[sheet] = {
            "columns": list(df.columns),
            "rows": len(df)
        }
    
    with open("excel_analysis.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"Successfully analyzed {len(xl.sheet_names)} sheets.")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
