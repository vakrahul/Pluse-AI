# Operation: Cube Semantic Layer

## Purpose

Cube.js provides the governed semantic layer between natural language questions and PostgreSQL. All analytics agents MUST query through Cube — never invent metrics or write raw SQL for business measures.

## Prerequisites

- PostgreSQL running with healthcare data loaded
- Docker or Node.js 18+ for Cube server
- `CUBEJS_API_SECRET` configured

## Architecture

```
User Question → SQL Agent → Cube Query JSON → Cube Server → PostgreSQL SQL → Results
```

## Cubes (8 models)

| Cube | Source Table | Key Measures |
|------|-------------|--------------|
| TerritoryMaster | dim.territory_master | count, salesTarget |
| HospitalMaster | dim.hospital_master | count, totalBeds |
| ProductMaster | dim.product_master | count, avgUnitPrice |
| SalesRepMaster | dim.sales_rep_master | count |
| HcpMaster | dim.hcp_master | count, avgSegmentationScore, kolCount |
| SalesFact | fact.sales_fact | totalSales, grossSales, hcpPerformance, territoryPerformance, productPerformance |
| PrescriptionFact | fact.prescription_fact | prescriptionCount, newPrescriptionCount |
| InteractionFact | fact.interaction_fact | count, avgDurationMinutes |

## Canonical Measures (7 business metrics)

| Measure | Cube Path | Definition |
|---------|-----------|------------|
| Total Sales | SalesFact.totalSales | Sum of net_sales after discounts |
| Prescription Count | PrescriptionFact.prescriptionCount | Sum of rx_count |
| Revenue Growth | SalesFact.totalSales + time compare | MoM % change via Cube date ranges |
| Product Performance | SalesFact.productPerformance | Sales ranked by product |
| Territory Performance | SalesFact.territoryPerformance | Sales ranked by territory |
| HCP Performance | SalesFact.hcpPerformance | Sales attributed to HCP |
| Market Share | SalesFact.totalSales / area total | % within therapeutic area |

## Step-by-step: Start Cube

```powershell
# From project root
docker compose -f infrastructure/docker/docker-compose.yml up -d cube

# Verify
python scripts/test_cube.py
```

## Step-by-step: Run a query via API

```bash
curl -X POST http://localhost:8000/api/v1/analytics/query \
  -H "Content-Type: application/json" \
  -d '{
    "measures": ["SalesFact.totalSales"],
    "dimensions": ["ProductMaster.therapeuticArea"],
    "filters": [{"member": "ProductMaster.therapeuticArea", "operator": "equals", "values": ["Diabetes"]}]
  }'
```

## Step-by-step: Cube Playground

1. Open http://localhost:4000
2. Select measures from SalesFact, dimensions from HcpMaster
3. Build query visually
4. Copy generated JSON for agent prompts

## Code References

- Models: `cube/model/*.js`
- Views: `cube/views/executive_dashboard.js`, `cube/views/market_share.js`
- Metric registry: `backend/semantic/metric_registry.py`
- API client: `backend/semantic/cube_client.py`
- Test script: `scripts/test_cube.py`

## Failure Modes & Recovery

| Error | Cause | Fix |
|-------|-------|-----|
| Cube can't connect to DB | Postgres not ready | `docker compose up -d postgres`, wait for healthcheck |
| "Can't find join path" | Missing join in model | Check joins in `SalesFact.js` |
| Measure not found | Typo in measure name | Use `/api/v1/analytics/measures` for allowed list |
| Empty results | Data not loaded | Run `data/seed/load_to_postgres.py` |

## Security Considerations

- `CUBEJS_API_SECRET` must be set in production
- Cube runs read-only against PostgreSQL
- Backend validates measures against `metric_registry` before execution
