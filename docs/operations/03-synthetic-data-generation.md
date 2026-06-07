# Operation: Synthetic Data Generation

## Purpose
Generate realistic healthcare data using Faker with 500–1,000 HCPs and 100K+ fact rows.

## Configuration

| Env Var | Default | Range |
|---------|---------|-------|
| HCP_COUNT | 1000 | 500–1000 |
| SALES_FACT_COUNT | 50000 | — |
| PRESCRIPTION_FACT_COUNT | 45000 | — |
| INTERACTION_FACT_COUNT | 30000 | — |
| SEED | 42 | any int |

## Step-by-step

```powershell
cd data/seed
pip install -r requirements.txt
python generate_synthetic_data.py
python load_to_postgres.py
```

## HCP Distribution
- Specialties: Cardiology 15%, Endocrinology 12%, Oncology 10%, others
- Cities: Bangalore 20%, Mumbai 18%, Delhi 15%, others
- Tiers: Gold (score ≥75), Silver (≥45), Bronze (<45)

## Validation
Generator asserts:
- `500 <= hcp_count <= 1000`
- `total_fact_rows >= 100000`
