# Healthcare Analytics Business Glossary

| Term | Definition |
|------|-----------|
| HCP | Healthcare Professional — physician or specialist who prescribes products |
| KOL | Key Opinion Leader — influential HCP identified by medical affairs |
| NPI | National Provider Identifier — unique physician ID |
| Tier | HCP classification: Gold, Silver, Bronze based on segmentation score |
| Territory | Geographic sales region assigned to sales reps |
| Net Sales | Gross sales minus discounts (fact.sales_fact.net_sales) |
| Rx | Prescription count (fact.prescription_fact.rx_count) |
| Therapeutic Area | Disease category e.g. Diabetes, Cardiology, Oncology |
| Market Share | Product sales as % of total sales in same therapeutic area |
| Segmentation Score | 0-100 composite score determining HCP tier |
| Referral Network | Graph of HCP-to-HCP REFERS relationships in Neo4j |
| TRx | Total prescriptions including new and refill |
| NRx | New prescriptions (new_rx_count) |

## Canonical Cube Measures
- SalesFact.totalSales — total net sales revenue
- PrescriptionFact.prescriptionCount — total prescriptions
- SalesFact.hcpPerformance — sales by HCP
- SalesFact.territoryPerformance — sales by territory
- SalesFact.productPerformance — sales by product
