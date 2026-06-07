# Operation: Schema DDL

## Purpose
Define the star schema for healthcare analytics with 5 dimension tables and 3 fact tables.

## Tables

### Dimensions
- `dim.territory_master` — sales territories
- `dim.hospital_master` — hospitals and clinics
- `dim.product_master` — pharma products
- `dim.sales_rep_master` — field sales reps
- `dim.hcp_master` — healthcare professionals (500–1,000 rows)

### Facts
- `fact.sales_fact` — sales transactions
- `fact.prescription_fact` — prescription volumes
- `fact.interaction_fact` — rep-HCP interactions

## Files
- `data/ddl/00_extensions.sql`
- `data/ddl/01_init.sql`
- `data/ddl/02_dimensions.sql`
- `data/ddl/03_facts.sql`
- `data/ddl/04_indexes.sql`

## Agent Schema View
`meta.agent_schema` exposes column metadata for LLM SQL generation guardrails.
