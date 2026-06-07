# PulseIQ FAQ — Frequently Asked Questions

## General

Q: What is PulseIQ?
A: PulseIQ is a healthcare pharma analytics copilot that answers natural language questions about sales, prescriptions, HCP profiles, referral networks, and compliance policies. It connects to Cube.js (analytics), Neo4j (graph), and a knowledge base (ChromaDB RAG).

Q: What kinds of questions can I ask?
A: You can ask about:
- Sales performance by product, territory, or HCP
- Prescription volumes by doctor, specialty, or tier
- Referral networks and HCP influence scores
- HCP tier classification (Gold, Silver, Bronze)
- Compliance rules and call planning guidelines
- Market share by therapeutic area

Q: What roles are supported?
A: PulseIQ supports four user perspectives:
- Field Sales Rep: territory calls, HCP engagement, visit planning
- Territory Manager: team performance, coverage, target tracking
- Medical Affairs: KOL identification, clinical engagement, off-label policies
- Commercial Analyst: revenue trends, market share, prescriber rankings

## Analytics

Q: How are HCPs classified into tiers?
A: HCPs are scored 0-100 using a composite segmentation formula combining prescription volume (40%), referral influence (30%), territory fit (20%), and engagement history (10%). Gold = score 75+, Silver = 45-74, Bronze = below 45.

Q: What is the difference between TRx and NRx?
A: TRx (Total Prescriptions) includes both new and refill prescriptions. NRx (New Prescriptions) counts only first-time prescriptions for a product.

Q: What does Net Sales mean?
A: Net Sales is gross revenue minus discounts, rebates, and returns. This is the canonical revenue metric stored as SalesFact.totalSales in Cube.

Q: How is market share calculated?
A: Market share = (product net sales / total net sales in same therapeutic area) x 100.

Q: What is a KOL?
A: A Key Opinion Leader is an HCP with high referral influence (referral_out >= 20), Gold tier classification, and specialty recognition. KOLs are identified by Medical Affairs for clinical engagement programs.

## Data Sources

Q: Where does the data come from?
A: Sales and prescription data comes from PostgreSQL through the Cube.js semantic layer. Referral networks come from Neo4j. Policy and tier rules come from the ChromaDB knowledge base.

Q: How fresh is the data?
A: Analytics data is updated as per your ETL schedule (typically daily). The knowledge base is updated when new policy documents are ingested.

Q: Can PulseIQ invent data?
A: No. PulseIQ only answers using data retrieved from Cube, Neo4j, or the knowledge base. If no data is found, it will say so.

## Troubleshooting

Q: Why did I get no answer?
A: This may happen if Cube.js or Neo4j is unavailable, the question is outside the data scope, or the API key hit its rate limit. Try rephrasing your question or contact your admin.

Q: What should I do if the chart looks wrong?
A: The chart is generated based on the data returned. If the x-axis shows technical measure names (e.g. SalesFact.totalSales), this indicates the agent retrieved raw data. Try asking a more specific question like "Show total sales by territory" instead of a vague query.
