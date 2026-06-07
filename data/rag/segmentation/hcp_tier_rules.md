# HCP Segmentation Rules

## Tier Definitions

### Gold Tier (segmentation_score >= 75)
- High prescribing volume in therapeutic area
- Active in key opinion leader (KOL) programs
- Strong referral network (referral_count >= 20)
- Regular engagement with sales representatives
- Located in priority metro markets (Bangalore, Mumbai, Delhi)

**Business rationale:** Gold HCPs drive disproportionate share of revenue. Target for premium engagement.

### Silver Tier (segmentation_score 45-74)
- Moderate prescribing volume
- Some referral activity
- Periodic rep interactions
- Growth potential in assigned territory

### Bronze Tier (segmentation_score < 45)
- Low prescribing volume
- Minimal referral network
- Infrequent rep contact
- Maintain awareness-level engagement

## Segmentation Score Formula
```
score = (rx_volume_weight * 0.35)
      + (sales_contribution_weight * 0.30)
      + (referral_network_weight * 0.20)
      + (engagement_weight * 0.15)
```

## KOL Criteria
- Must be Gold tier
- is_kol = true flag set by medical affairs review
- Publishes or speaks at medical conferences
- Influences >= 5 referring physicians

## Example: Why is Dr. X classified as Gold?
1. Segmentation score >= 75
2. High net sales attributed via sales_fact
3. Active prescription volume in core therapeutic areas
4. Referral network with multiple REFERS relationships
5. Regular rep visits logged in interaction_fact
