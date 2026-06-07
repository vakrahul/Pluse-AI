# Sales Call Planning Standard Operating Procedure

## Pre-Call Research
1. Review HCP tier and segmentation score in hcp_master
2. Check recent interactions in interaction_fact
3. Analyze prescription trends via PrescriptionFact cube
4. For Gold tier: review referral network in Neo4j

## Call Frequency Targets
| Tier | Minimum Visits/Quarter |
|------|----------------------|
| Gold | 4 |
| Silver | 2 |
| Bronze | 1 |

## Sample Question Support
"Show top cardiologists in Bangalore" → Filter HcpMaster.specialty=Cardiology, city=Bangalore, order by SalesFact.hcpPerformance

"Why is Dr. X Gold?" → Check segmentation rules + RAG segmentation docs + HCP tier field

## Post-Call
- Log interaction in CRM within 24 hours
- Record outcome: Positive, Neutral, Follow-up Required
