# Supply Chain Risk & Demand Analytics — Business Narrative

## Problem

Late deliveries directly damage customer trust and create downstream costs — 
missed SLAs, expedited-shipping overruns, and lost repeat business. This analysis 
examines ~180,000 orders from a global e-commerce supply chain dataset (DataCo) 
to understand where and why deliveries are failing, and what can realistically 
be done about it.

## Key Findings

**1. Over half of all orders arrive late.**
54.8% of all orders in the dataset were delivered later than scheduled — not an 
occasional failure, but the dominant outcome. The most common single delay is a 
modest, predictable 1-day overrun, not chaotic multi-day slippage.

**2. The problem is systemic, not regional or category-specific.**
Late delivery rates are remarkably consistent across all 23 order regions 
(48.8%–58.0%) and across all 50 product categories (mostly 55–58%). No single 
region or product line is meaningfully driving the problem — this rules out 
localized fixes (e.g. blaming a specific warehouse or supplier) and points to a 
structural, company-wide issue instead.

**3. Shipping mode is the real driver — and it's counterintuitive.**
This is the standout finding. Premium shipping tiers are dramatically *less* 
reliable than the standard option:

| Shipping Mode   | Scheduled Days | Late Delivery Rate |
|-----------------|----------------|---------------------|
| First Class     | 1 day          | 95.3%               |
| Second Class    | 2 days         | 76.6%               |
| Same Day        | 0 days         | 45.7%               |
| Standard Class  | 4 days         | 38.1%               |

The pattern is clear: the shorter the promised delivery window, the higher the 
failure rate. Standard Class succeeds not because fulfillment is faster for it, 
but because its 4-day window gives enough buffer to absorb normal operational 
delays. First and Second Class promise windows the fulfillment process cannot 
consistently meet.

**4. The issue has been stable for three years — not improving, not worsening.**
Monthly late-delivery rates stayed in a tight 52–57% band from 2015 through 2018, 
with one notable anomaly: a sharp dip to ~52% around mid-2016, followed by a 
rebound to ~57%. This dip is worth further investigation (possibly a temporary 
process change or data artifact) but doesn't change the overall picture — this 
is a chronic, structural issue rather than a recent regression.

## Recommendation

The current shipping-mode SLAs are not aligned with actual fulfillment capability. 
Two paths forward:

1. **Re-calibrate promised delivery windows** for First and Second Class to 
   realistic fulfillment timelines (e.g. extend to 2–3 days), reducing the gap 
   between promise and delivery without requiring operational changes.
2. **Invest in fulfillment speed specifically for premium tiers** before 
   continuing to market and charge for "faster" shipping — as currently 
   structured, these tiers actively erode customer trust rather than building it.

Given that the effect size here (95.3% vs 38.1%) is far larger than any 
regional or category-level variation, this is the highest-leverage fix 
available in the dataset.

## Methodology Notes

- Source: DataCo Smart Supply Chain dataset (Kaggle), ~180,519 orders, 
  53 original columns.
- Cleaning: removed 8 PII columns (email, password, names, address, 
  coordinates) and 7 redundant/empty columns; standardized inconsistent 
  country naming (mixed English/Spanish labels); converted date fields to 
  proper datetime; engineered `delivery_delay_days` (actual − scheduled 
  shipping days).
- Long-tail country names (144 of 164 unique values, low order volume each) 
  were left untranslated as a scoping decision — the top 20 countries by 
  volume, which were translated, account for the large majority of orders.
- Full cleaning and EDA code: `notebooks/01_cleaning.ipynb`
- Live interactive dashboard: see `powerbi/README.md`