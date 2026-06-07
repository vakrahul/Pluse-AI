# Analytics Definitions — PulseIQ Semantic Layer Reference

## Cube.js Measures (Official Metric Names)

### Sales Metrics
- **SalesFact.totalSales** — Total net sales revenue in INR/USD. Formula: sum of net_sales column. Use for: overall revenue, product revenue, territory revenue.
- **SalesFact.hcpPerformance** — Net sales grouped by HCP. Shows which doctors drive the most revenue.
- **SalesFact.territoryPerformance** — Net sales grouped by territory. Shows geographic revenue contribution.
- **SalesFact.productPerformance** — Net sales grouped by product. Shows top-selling brands.

### Prescription Metrics
- **PrescriptionFact.prescriptionCount** — Total prescription count (TRx). Includes new and refill. Use for: volume analysis, market share.
- **PrescriptionFact.newPrescriptionCount** — New prescription count (NRx). First-time prescriptions only.

### HCP Metrics
- **HcpMaster.count** — Total number of HCPs in the database (1,000 in demo).
- **HcpMaster.tier** — Dimension: Gold, Silver, or Bronze. Use as a filter or group-by.
- **HcpMaster.specialty** — Dimension: Cardiology, Diabetes, Oncology, Neurology, Endocrinology.
- **HcpMaster.territory** — Dimension: geographic territory name.

## Cube.js Dimensions (Grouping Attributes)

| Dimension | Values | Use For |
|-----------|--------|---------|
| HcpMaster.tier | Gold, Silver, Bronze | Filter by HCP quality |
| HcpMaster.specialty | Cardiology, Diabetes, Oncology, Neurology, Endocrinology | Therapeutic area breakdown |
| HcpMaster.city | Bangalore, Mumbai, Delhi, Chennai, Hyderabad | Geographic filter |
| HcpMaster.territory | North, South, East, West | Territory analysis |
| SalesFact.productName | Brand names | Product-level breakdown |

## Neo4j Graph Metrics

- **referral_out** — Number of outgoing referrals. Measures how many other HCPs this doctor refers patients to. High referral_out = strong influence.
- **referral_in** — Number of incoming referrals. Measures how many HCPs refer TO this doctor. High referral_in = high demand specialist.
- **influence_score** — Composite graph centrality score. Used to identify KOLs (Key Opinion Leaders).
- **REFERS relationship** — Neo4j edge type connecting HCP nodes. Query: MATCH (a:HCP)-[:REFERS]->(b:HCP).

## Business KPIs Explained

### Revenue KPIs
- **Total Revenue**: Sum of all net_sales. Benchmark: $128M in demo dataset.
- **Revenue per HCP**: Total Revenue / Active HCPs. Measures rep productivity.
- **Revenue per Territory**: Total Revenue / Territory Count. Measures geographic efficiency.

### Prescription KPIs
- **Total Prescriptions (TRx)**: 892,000 in demo dataset.
- **Prescription Market Share**: Product prescriptions / Total therapeutic area prescriptions x 100.
- **Gold Tier Rx Share**: Prescriptions written by Gold HCPs as % of total. Target: >40%.

### HCP Engagement KPIs
- **Coverage Rate**: % of target HCPs visited at least once. Target: >85% for sales reps.
- **Call Frequency**: Average visits per HCP per quarter. Gold tier target: 6 calls/quarter.
- **Reach**: Number of unique HCPs contacted in a period.

## Chart Type Rules

- **Revenue by product or territory** → Bar chart
- **Prescription trend over time** → Line or Area chart
- **HCP tier distribution** → Pie or Donut chart
- **Top N doctors ranked** → Horizontal bar chart
- **Referral network strength** → Bar chart (referral_out as y-axis)

## Common Query Patterns

- "Top 10 doctors by revenue" → SalesFact.hcpPerformance, descending, limit 10
- "Gold tier prescriptions" → PrescriptionFact.prescriptionCount, filter HcpMaster.tier = Gold
- "Which territory performs best" → SalesFact.territoryPerformance, descending
- "Market share by specialty" → PrescriptionFact.prescriptionCount grouped by HcpMaster.specialty
