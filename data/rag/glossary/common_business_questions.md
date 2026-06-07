# Common Business Questions & Model Answers

This document provides canonical answers to frequently asked business questions in the PulseIQ platform. Use these as authoritative reference responses.

---

## Sales Performance Questions

**Q: What is the total revenue?**
Total revenue in the demo dataset is approximately $128.4M (SalesFact.totalSales). This represents net sales across all products, territories, and time periods.

**Q: Which products generate the most revenue?**
Revenue is tracked by product through SalesFact.productPerformance. Top therapeutic areas by revenue are typically Oncology, Cardiology, and Diabetes in this dataset.

**Q: Which territory performs best?**
Territory performance is measured by SalesFact.territoryPerformance. South and West territories typically lead in the demo dataset. Ask "Show sales by territory" for live rankings.

**Q: How do I compare quarterly performance?**
Use SalesFact.totalSales with a time dimension. Ask: "Show monthly sales trend" or "Compare Q1 vs Q2 revenue."

---

## HCP & Prescription Questions

**Q: Who are the top prescribers?**
Top prescribers are ranked by PrescriptionFact.prescriptionCount grouped by HCP. Ask: "Top 10 HCPs by prescription count."

**Q: How many Gold tier doctors do we have?**
There are 100 Gold tier HCPs in the demo dataset (10% of 1,000 total HCPs). Gold HCPs have a segmentation score of 75 or above.

**Q: What is the prescription split by tier?**
- Bronze tier: approximately 3.65M prescriptions (highest volume, lowest engagement)
- Silver tier: approximately 880K prescriptions
- Gold tier: approximately 12.4K prescriptions (highest quality, most engaged)

**Q: Which specialty has the most HCPs?**
- Cardiology: 150 HCPs
- Diabetes: 120 HCPs
- Oncology: 100 HCPs
- Neurology: 80 HCPs
- Endocrinology: 70 HCPs

**Q: What is the prescription market share by specialty?**
Market share is calculated as specialty prescriptions / total prescriptions x 100. Cardiology and Diabetes typically lead in this dataset.

---

## HCP Tier & Segmentation Questions

**Q: How is a doctor classified as Gold?**
A doctor is classified Gold if their segmentation score is 75 or above. The score combines: prescription volume (40%), referral network influence (30%), territory fit (20%), and engagement history (10%).

**Q: What is the call frequency target for Gold tier HCPs?**
Gold tier HCPs should receive 6 calls per quarter minimum. Silver tier: 4 calls/quarter. Bronze tier: 2 calls/quarter.

**Q: What does Silver tier mean?**
Silver tier HCPs have segmentation scores between 45 and 74. They represent 30% of HCPs (300 doctors). They have moderate prescription volumes and referral activity.

**Q: Can a doctor move from Bronze to Silver?**
Yes. Tier upgrades are evaluated quarterly based on updated segmentation scores. A Bronze HCP who increases prescription volume or gains referral connections can be reclassified.

---

## Referral Network Questions

**Q: Who are the most influential doctors?**
Influence is measured by referral_out (outgoing referrals) and influence_score in Neo4j. Ask: "Top doctors by referral influence" to see the ranked list.

**Q: What is a KOL?**
A Key Opinion Leader (KOL) is an HCP who meets all three criteria: Gold tier classification, referral_out >= 20, and specialty recognition. KOLs are the primary target for Medical Affairs engagement.

**Q: Which doctors have the strongest referral network?**
Ask: "Which HCPs have the most referrals" or "Top referring doctors in Cardiology." The system queries Neo4j's REFERS relationship graph.

**Q: What is the average referral count?**
In this dataset, the average referral_out per HCP is approximately 8-12. Gold tier HCPs average 25+ referrals.

---

## Compliance & Policy Questions

**Q: What is the off-label promotion policy?**
PulseIQ follows strict pharma compliance guidelines. Off-label promotion is prohibited. Sales reps may only discuss FDA-approved indications. All promotional materials must be approved by Medical Affairs.

**Q: What is the gift and entertainment limit?**
Per pharma compliance policy, gifts to HCPs are limited to items of nominal value (under $10). Meals during sales calls must be occasional, modest, and related to a genuine educational component.

**Q: How many calls can I make to a doctor per month?**
Per call planning SOP: Gold tier — maximum 2 calls/month (6/quarter). Silver — 1-2 calls/month. Bronze — 1 call/month. Exceeding these limits triggers a compliance flag.

**Q: What documentation is required after each HCP call?**
Each call must be logged in the CRM within 24 hours with: HCP name, NPI, date, call type (in-person/virtual), topics discussed, and materials shared. Failure to log is a compliance violation.

---

## System & Technical Questions

**Q: What data does PulseIQ have access to?**
PulseIQ accesses: PostgreSQL (sales and prescription facts, HCP master data), Neo4j (referral network graph), and ChromaDB (policy documents, tier rules, glossary, FAQs).

**Q: Is the data real-time?**
Analytics data reflects the last ETL run (typically daily). The knowledge base is updated when new documents are ingested.

**Q: What happens if a query returns no data?**
If no data is found, PulseIQ will say so clearly and suggest alternative questions. It will never fabricate numbers.

**Q: Who should I contact for data issues?**
Contact your Commercial Analytics team or system administrator for data quality issues. For platform issues, contact the PulseIQ support team.
