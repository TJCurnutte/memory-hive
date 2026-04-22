# Metrics Framework — Measuring What Matters

## The Vanity Metric Problem

**Vanity metrics** look good but can't be acted upon:
- Page views, follower counts, raw impressions
- "Registered users" when most never return
- Revenue when you don't know the cost to acquire

**Actionable metrics** tell you what to do next:
- Retention rates, engagement ratios
- Customer acquisition cost (CAC) vs lifetime value (LTV)
- Conversion rates by cohort/channel

**Rule**: If you can't name a specific decision you'd make based on this number changing, it's probably vanity.

## The Right Metrics Framework

### 1. North Star Metric (NSM)
One metric that best captures the core value you deliver to customers.

**Properties:**
- Represents value delivered, not just activity
- Controllable — you can influence it
- Measurable — you can track it daily
- Universal — everyone from CEO to intern can understand it

**Examples:**
- Airbnb: Nights Booked
- Spotify: Time Spent Listening
- Notion: Weekly Active Editors

**Warning**: One NSM can create perverse incentives. Complement with guardrail metrics.

### 2. Pirate Metrics (AARRR)
| Stage | Metric | Question |
|-------|--------|----------|
| **A**cquisition | CAC, MQLs, Site visits | How do users find you? |
| **A**ctivation | Onboarding completion, "Aha" moment | Do users get value quickly? |
| **R**etention | Day 1/7/30 retention, Churn rate | Do users come back? |
| **R**eferral | NPS, Viral coefficient | Do users tell others? |
| **R**evenue | ARPU, LTV, MRR | How do you make money? |

### 3. Leading vs Lagging Indicators
- **Leading**: Predict future outcomes (sign-ups, engagement, feature usage)
- **Lagging**: Confirm past results (revenue, churn, NPS score)

You need both. Leading indicators give you early warning; lagging confirm your actions worked.

### 4. Input vs Output Metrics
- **Input metrics**: Activities you control (calls made, emails sent, demos run)
- **Output metrics**: Results of those activities (meetings booked, deals closed, pipeline)

**Track both.** Output metrics tell you if you're winning; input metrics tell you what to do more/less of.

## Metric Selection Criteria

Before adopting a metric, ask:

1. **Can I move it?** — If you have no levers, it's just noise
2. **Is it timely?** — Daily > weekly > monthly for operational decisions
3. **Is it auditable?** — Can you trace it back to raw data?
4. **Is it robust?** — Won't shift when you change product slightly
5. **Do people trust it?** — If team doesn't believe it, it won't drive behavior

## Segmentation Is Everything

A single aggregate metric hides everything that matters:

| Segment | Metric | Insight |
|---------|--------|---------|
| By channel | CAC by source | Where are cheapest customers? |
| By cohort | Retention by signup date | Is product improving? |
| By segment | Conversion by company size | Who converts best? |
| By geography | Engagement by region | Where to expand? |
| By usage | Revenue by plan tier | Where is growth? |

**Golden rule**: Always break down your most important metric by at least 3 dimensions before reporting it.

## Common Pitfalls

### Metric Manipulation
- Chasing a metric can hollow out its meaning (SEO traffic → low-quality users)
- Watch for **Goodhart's Law**: "When a measure becomes a target, it ceases to be a good measure"
- **Campbell's Law**: The more a metric is used for decisions, the more it gets gamed

### Relative vs Absolute
- "50% increase" sounds great; "from 2 to 3" is reality
- Always show absolute numbers alongside percentages
- Watch for small-sample percentages (12 users, 50% churn = 6 people)

### Sampling Bias
- Dashboard only shows "active" users — what about churned?
- Reports based on completed surveys miss non-respondents
- A/B tests on logged-in users exclude anonymous visitors

### Correlation Confusion
- Two metrics moving together ≠ cause and effect
- Third variable problem: both caused by something else
- Lagged correlations: does X predict Y or does Y cause X?

## Building a Metrics Dashboard

**Layer 1 — Executive Pulse** (1-3 metrics, reviewed daily)
- NSM + 1-2 guardrails
- Traffic light: green/yellow/red

**Layer 2 — Functional Health** (5-10 metrics per function)
- Sales: Pipeline, Win rate, ACV, CAC
- Marketing: MQLs, CAC, Conversion rates, NPS
- Product: DAU/WAU/MAU, Retention curves, Feature adoption

**Layer 3 — Diagnostic Deep Dives** (ad-hoc)
- Cohort analyses, segment breakdowns, funnel analysis
- Triggered by Layer 1/2 anomalies

## Setting Goals & Tracking Progress

**SMART goals for metrics:**
- **Specific**: "Improve 30-day retention from X to Y"
- **Measurable**: Include the baseline number
- **Achievable**: Stretch but possible (1.2-1.5x current is usually too aggressive)
- **Relevant**: Connected to business outcomes
- **Time-bound**: "By end of Q3" not "soon"

**Tracking cadence:**
- Daily: operational input metrics, key outputs
- Weekly: team dashboards, cohort reports
- Monthly: business reviews, trend analysis, strategic metrics

---

*Auto-generated: 2026-04-22*
