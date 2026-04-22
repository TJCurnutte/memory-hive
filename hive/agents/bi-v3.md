# Business Intelligence (v3)

**Author:** Data-Analyst Agent  
**Date:** 2026-04-22  
**Topics:** BI Dashboards, Looker/Metabase/Grafana, SaaS KPI Frameworks, Cohort Analysis, Attribution Modeling, LTV/CAC Analysis

---

## 1. Building BI Dashboards

Business intelligence consists of strategies, methodologies, and technologies used by enterprises for data analysis and management of business information to inform business strategies and operations. Common BI functions include reporting, analytics, dashboard development, data mining, predictive analytics, and benchmarking. A well-designed BI dashboard is the primary interface between data and decision-makers.

### 1.1 Design Principles

**Know Your Audience:** The most important design decision. A dashboard for the CEO looks completely different from one for a product manager or an ops team.

| Audience | Primary Focus | Update Frequency | Complexity |
|---|---|---|---|
| Executive | Revenue, growth, strategic metrics | Weekly/monthly | Low (summarized) |
| Manager | Team KPIs, progress vs. targets | Daily/weekly | Medium |
| Analyst | Detailed drill-down, raw data | Daily/hourly | High (full detail) |
| Operations | Real-time alerts, system health | Real-time | Medium-high |

**Start with the Question, Not the Data:** Every dashboard should answer specific business questions. Before placing a single chart, define:
1. Who is the audience?
2. What decisions will this dashboard inform?
3. What is the single most important thing they need to know?
4. What is the next level of detail they'll need?

**Visual Hierarchy:** Guide the viewer's eye:
- Most important metrics at the top left (Western reading pattern)
- Use size to indicate importance
- Use whitespace to separate logical groups
- Avoid decorative elements that don't convey information

### 1.2 Data Storytelling

A dashboard is not just a collection of charts — it's a narrative about the business:

**The 3-Second Rule:** A viewer should understand the main insight of any chart within 3 seconds without needing to read any text.

**Context is Everything:** Always provide context for metrics:
- vs. previous period (MoM, WoW, DoD)
- vs. target/goal
- vs. industry benchmark
- Trend line with clear direction

**Annotate Key Events:** Mark significant events on trend lines (product launches, marketing campaigns, outages, seasonality). This turns a chart into a story.

**Color for Communication, Not Decoration:**
- Use red/green consistently (red = bad, green = good)
- Use one color as the "primary metric" and grays for context
- Use blue for neutral or positive, red for alerts/negative
- Use color sparingly — too many colors create noise

### 1.3 Dashboard Types by Function

**Operational Dashboards:** Monitor real-time business operations. Examples: order fulfillment rates, server uptime, support ticket queue depth. Focus on current state and exceptions. Updated in real-time or near-real-time.

**Strategic/Executive Dashboards:** Answer high-level business health questions. Focus on KPIs vs. targets, trends over time, and exception highlighting. Updated daily or weekly. Often sparse — one page.

**Analytical Dashboards:** Deep-dive exploration tools for analysts. Feature filters, date ranges, drill-downs, and detailed data tables. Higher density, longer time to insight.

**Self-Service Dashboards:** Allow non-technical users to explore data without needing analyst support. Require robust data modeling upstream. Examples: Metabase question-browser, Looker Explore.

### 1.4 Best Practices

**Avoid Chart Junk:**
- Remove gridlines (or make them very faint)
- Remove 3D effects
- Remove unnecessary legends when the label is on the chart
- Remove duplicate axis labels

**Date Range Defaults:** Set defaults that make sense for the audience. Executives typically want "this period vs. last period." Analysts often need "custom range." Always allow date range filtering.

**Comparison Metrics:** Side-by-side comparison is more powerful than raw numbers. Show current vs. prior period, plan vs. actual, or cohort A vs. cohort B side by side.

**Alert Thresholds:** Define what "good" and "bad" look like. Use conditional formatting — cells or chart elements change color when metrics cross thresholds. This makes exceptions immediately visible without manual review.

**Performance:** Large dashboards with many visualizations can be slow. Use materialized views, summarized tables, and query optimization to ensure dashboards load in under 3 seconds.

---

## 2. Looker vs. Metabase vs. Grafana

Choosing the right BI tool is one of the most consequential decisions for a data team. The right tool depends on your team's technical skill, data maturity, budget, and primary use case.

### 2.1 Overview Comparison

| Feature | Looker | Metabase | Grafana |
|---|---|---|---|
| **Primary Focus** | Semantic layer & governed metrics | Self-service exploration | Metrics & monitoring |
| **Ease of Use** | Medium (requires training) | High (very approachable) | Medium (technical users) |
| **Underlying Database** | Looker ML (LookML) | PostgreSQL, MySQL, etc. | Time-series DB (InfluxDB, Prometheus) |
| **Pricing Model** | SaaS subscription (per user) | Free (open-source) / SaaS | Free (open-source) / Cloud/Enterprise |
| **Learning Curve** | Moderate (LookML) | Low | Low-moderate |
| **Customization** | High (via LookML) | Medium | High (plugins, dashboards) |
| **Best For** | Enterprise BI, governed metrics | Broad team self-service | DevOps, APM, IoT monitoring |
| **Connectors** | 70+ databases | 15+ databases | Many (via plugins) |
| **Embedded Analytics** | Yes (Looker Embedded) | Yes (Metabase Embed) | Limited |

### 2.2 Looker

Looker is a modern BI platform built around a semantic layer called LookML. It is designed for enterprise organizations that need a single source of truth for metrics.

**Key Strengths:**
- **LookML Semantic Layer:** Defines metrics once in code, ensuring every chart and dashboard uses the same definition. No more "different numbers from different teams."
- **Governed Exploration:** Users can explore data through predefined "Explores" — controlled pathways through the data model. Balances self-service with data governance.
- **Looker Block ML:** Marketplace of pre-built data models for popular SaaS tools (Salesforce, Stripe, HubSpot). Speeds up initial setup.
- **Embedded Analytics:** Strong embedded BI product for ISVs and product teams wanting analytics in their product.
- **Version Control:** LookML code is stored in git repositories, enabling code review and rollback.

**Weaknesses:**
- Requires learning LookML syntax (a custom DSL)
- Higher cost than open-source alternatives
- Less flexible for ad-hoc, one-off explorations
- Less suitable for raw data exploration (more suited for governed metric consumption)

**Pricing:** Per-user pricing, starts at ~$3,000/month for smaller deployments. Google Cloud acquired Looker in 2019 and rebranded it as Looker (now part of the Google Cloud BI ecosystem).

### 2.3 Metabase

Metabase is an open-source BI tool with an extremely low barrier to entry. It's designed for non-technical users to explore data without needing SQL knowledge (though SQL is available for power users).

**Key Strengths:**
- **Self-Service by Default:** Simple point-and-click query builder. Non-technical users can create charts without SQL.
- **Simple Deployment:** One command to get started with Docker, or use the hosted Metabase Cloud.
- **SQL Snippets:** Power users can write SQL but share snippets across the organization for reusability.
- **Question Browser:** Users browse through tables and columns intuitively to build their own analyses.
- **Dashboard Embedding:** Embed dashboards into external applications with filter passing.
- **Pulse/Alerting:** Schedule reports and set up alerts when metrics cross thresholds.
- **Open Source:** Free self-hosted option. Full transparency, no vendor lock-in.

**Weaknesses:**
- No semantic layer (metrics defined at query level — risk of inconsistency)
- Limited version control compared to LookML
- Performance can degrade on very large datasets (no columnar optimization)
- Less suitable for enterprise governance needs

**Pricing:** Free (open-source, self-hosted) or ~$85/user/month for Metabase Pro Cloud.

### 2.4 Grafana

Grafana is primarily a metrics and monitoring platform, originally built for DevOps and infrastructure monitoring. It has evolved into a general-purpose visualization platform but excels at time-series data.

**Key Strengths:**
- **Time-Series Expertise:** Purpose-built for metrics that change over time — server performance, application response times, sensor data, stock prices.
- **Alerting:** Industry-leading alerting. Set complex multi-condition alerts with notification routing to Slack, PagerDuty, email, etc.
- **Plugins Ecosystem:** Vast library of plugins for data sources (Prometheus, InfluxDB, Elasticsearch, CloudWatch, Azure Monitor, etc.) and visualizations.
- **Provisioning:** Full configuration-as-code via YAML files and APIs. Excellent for GitOps workflows.
- **Loki:** Native log aggregation system from Grafana Labs (logs + metrics + traces = full observability).
- **Panel Types:** Huge variety including heatmaps, histograms, flux diagrams, geomaps, state timelines — specialized visualizations not available in most BI tools.

**Weaknesses:**
- Not a general-purpose BI tool — optimized for metrics, not business analysis
- No semantic layer
- Dashboard building UX can be clunky compared to dedicated BI tools
- User management and permissions are less mature than enterprise BI tools

**Pricing:** Free (open-source), Grafana Cloud (~$8/month per user + usage), Grafana Enterprise (contact sales).

### 2.5 Which Tool to Choose?

**Choose Looker if:** You need enterprise-wide metric consistency, have a technical team comfortable with LookML, want strong embedded analytics, and budget allows for it.

**Choose Metabase if:** You have diverse non-technical users who need self-service access to data, you're budget-conscious, or you want an open-source option with minimal maintenance.

**Choose Grafana if:** You are a DevOps/data engineering team monitoring systems, infrastructure, or applications, you need strong alerting, or you're building an observability stack (metrics + logs + traces).

**Hybrid Approach:** Many mature data organizations use multiple tools — Grafana for operational monitoring, Metabase for analyst self-service, Looker for executive dashboards. The key is a unified semantic layer (in dbt or a separate metrics store) so all tools query the same consistent numbers.

---

## 3. SaaS KPI Frameworks

SaaS companies live and die by their metrics. A well-designed KPI framework aligns the entire organization around the metrics that drive sustainable growth.

### 3.1 The SaaS Metrics Funnel

The classic SaaS funnel maps to the customer's lifecycle stages:

**Activation → Engagement → Retention → Revenue → Referral**

| Stage | Key Questions | Core Metrics |
|---|---|---|
| **Activation** | Did users reach the "aha" moment? | Time to value, activation rate, feature adoption |
| **Engagement** | Are users using the product? | DAU/WAU/MAU, session frequency, feature usage |
| **Retention** | Do users come back? | Day-N retention, churn rate, NPS |
| **Revenue** | Are users paying us? | MRR, ARPU, LTV, expansion revenue |
| **Referral** | Do users recommend us? | NPS, referral rate, viral coefficient |

### 3.2 The North Star Metric

The North Star Metric (NSM) is the single metric that best captures the core value your product delivers to customers. Every team in the company should be able to connect their work to moving the NSM.

**Characteristics of a Good NSM:**
- It measures customer value, not company value (revenue is often a lagging indicator)
- It's actionable for most teams in the organization
- It's trackable in near real-time
- It's hard to game (difficult to inflate without creating real value)

**Examples by Company:**
- Facebook: Daily Active Users
- Salesforce: Weekly Active Users
- Slack: Daily Active Users (connected to teams)
- HubSpot: Marketingqualified leads per month
- Shopify: Merchants whose stores process at least one order per month
- Airbnb: Booked Nights
- Zoom: Daily Active Meeting Minutes

**Avoid Vanity Metrics:** Metrics that look good but don't correlate with long-term customer value or business health. Examples: total registered users, total page views, total revenue (without context of cost to acquire).

### 3.3 SaaS KPI Framework by Growth Stage

**Stage 1: Product-Market Fit (Pre-Seed to Seed)**
Primary focus: Finding product-market fit.

- **Retention Rate:** If weekly or monthly users aren't returning, nothing else matters. Target: 20-30% Day-7 retention as a signal of PMF.
- **Engagement Rate:** Which user actions correlate with retention? Define your activation criterion.
- **NPS:** Is the product delighting early users?
- **Churn Rate:** Are users leaving? What's the early cohort behavior?

**Stage 2: Scaling (Series A to Series B)**
Primary focus: Growing efficiently while demonstrating retention.

- **Customer Acquisition Cost (CAC):** Cost to acquire a new customer. Target: decreasing over time as marketing scales.
- **LTV:CAC Ratio:** Efficiency of customer acquisition. Target: >3:1 for healthy SaaS.
- **Viral Coefficient:** How many new users each user brings. Target: >1.0 for viral growth.
- **Net Revenue Retention (NRR):** Revenue from existing customers including expansions minus churn. Target: >100% (expansion revenue exceeds churn).
- **Gross Margin:** SaaS should target 70%+ gross margin. Target: 75-85%.

**Stage 3: Efficiency (Series B to IPO)**
Primary focus: Unit economics, operational efficiency, predictable growth.

- **Magic Number:** Sales efficiency metric. Magic Number > 1.0 means you're growing efficiently.
- **Rule of 40:** Growth rate + profit margin > 40% indicates healthy SaaS. A company growing at 80% can be -40% margin and still pass the Rule of 40.
- **Payback Period:** Months to recover CAC from a customer's revenue. Target: <12 months, ideally <6 months.
- **ARR (Annual Recurring Revenue) Growth Rate:** Target: 50-100%+ for high-growth SaaS.

---

## 4. Cohort Analysis Deep Dive

Cohort analysis is one of the most powerful analytical techniques in product and business analytics. It reveals patterns that aggregate metrics obscure entirely.

### 4.1 What Is Cohort Analysis?

Cohort analysis groups users by a shared characteristic and tracks their behavior over time. Unlike aggregate metrics (which show averages across all users), cohort analysis reveals how different groups behave differently — and why.

**The Fundamental Insight:** Not all customers are the same. A user acquired today likely behaves very differently from a user acquired 2 years ago. Aggregate metrics mix these different populations together, masking important trends.

### 4.2 Types of Cohorts

**Signup Date Cohort (Acquisition Cohort):** Group by when the user signed up.
- Example: "All users who signed up in January 2026"
- Best for: Understanding how acquisition quality has changed over time, measuring the impact of marketing campaigns, identifying seasonality

**First Purchase Cohort:** Group by when the user made their first transaction.
- Example: "All users who made their first purchase in Q3 2025"
- Best for: E-commerce, SaaS companies where the first paid conversion is a meaningful milestone

**Cohort by Feature Usage:** Group by which feature users adopted first.
- Example: "Users who used the [X] feature within their first week"
- Best for: Product-led growth, understanding which product areas drive retention

**Cohort by Geography, Channel, or Plan:** Group by any meaningful segment.
- Example: "Users acquired through organic search" vs. "Users acquired through paid ads"
- Best for: Understanding channel efficiency, geographic expansion strategy

### 4.3 Building Retention Cohorts

The retention cohort table is the most common and most powerful application of cohort analysis:

**How to Build It:**

| | Month 0 | Month 1 | Month 2 | Month 3 |
|---|---|---|---|---|
| Jan 2026 cohort | 1,000 | 400 | 280 | 210 |
| Feb 2026 cohort | 1,200 | 480 | 336 | — |
| Mar 2026 cohort | 1,500 | 600 | — | — |
| Apr 2026 cohort | 1,800 | — | — | — |

**Reading the Table:**
- Each row is a cohort (users who joined in the same time period)
- Each column is a time period after acquisition
- Cells show the number (or %) of cohort members still active

**Retention Rate:** (Cohort members active in Month N) / (Cohort size at Month 0)

**What Retention Curves Reveal:**
- **Shape of the curve:** Early drop-off signals activation problems. Late drop-off signals engagement issues.
- **Comparison across cohorts:** If the April 2026 cohort retains at 50% in Month 1 while January 2026 retained at 40%, you know recent acquisition or product changes are working
- **Stabilization point:** Most SaaS products see retention stabilize after a certain period (often 30-90 days)

### 4.4 Churn Analysis via Cohorts

Churn is the mirror image of retention. Cohort analysis answers the critical question: "When do users churn, and what predicts it?"

**Common Patterns:**
- **Early Churn (Week 1-2):** Users who don't reach the activation event churn. Fix: improve onboarding.
- **Mid-term Churn (Month 1-3):** Users who activated but didn't find ongoing value. Fix: improve core product value, email campaigns, feature discovery.
- **Late Churn (Month 6+):** Users who tried the product but switched to a competitor or their needs changed. Fix: win-back campaigns, deeper customer success.

### 4.5 Revenue Cohort Analysis

Apply the same cohort logic to revenue metrics:

**Revenue Cohort Table:**

| Cohort | Month 0 MRR | Month 3 MRR | Month 6 MRR | Expansion Rate |
|---|---|---|---|---|
| Q1 2025 | $10,000 | $12,500 | $15,000 | +50% |
| Q2 2025 | $12,000 | $14,400 | $16,800 | +40% |
| Q3 2025 | $15,000 | $18,000 | — | +20% |

This reveals:
- How revenue from each cohort grows (or shrinks) over time
- Net Revenue Retention by cohort
- Whether product/price changes affect revenue expansion

---

## 5. Attribution Modeling

Attribution modeling answers the question: "Which marketing channels and touchpoints actually drive conversions?" Without attribution, you can't optimize your marketing spend effectively.

### 5.1 The Attribution Problem

A customer might interact with your brand 20+ times before converting: they see a Facebook ad, search for your brand name on Google, read a blog post, watch a YouTube review, click a retargeting ad, and finally convert via email. Which touchpoint deserves credit for the sale?

This is the fundamental attribution problem, and different attribution models answer it differently — each with trade-offs.

### 5.2 Common Attribution Models

**First-Touch Attribution:**
- 100% credit goes to the first touchpoint in the journey
- Pro: Simple, easy to track and act on. Identifies which channels bring new customers into the funnel.
- Con: Ignores everything that happened between first touch and conversion. Undervalues channels that nurture customers through the consideration phase (retargeting, email, SEO).
- Best for: Awareness-stage optimization. Good for identifying top-of-funnel channels.

**Last-Touch Attribution:**
- 100% credit goes to the last touchpoint before conversion
- Pro: Captures the channel most directly responsible for closing. Easy to implement with UTM parameters.
- Con: Ignores the entire awareness and consideration phases. Overvalues retargeting at the expense of content, SEO, and brand building.
- Best for: Direct-response campaigns where the last touch is typically a conversion event.

**Linear Attribution:**
- Equal credit distributed across all touchpoints in the journey
- Pro: Fairer to all channels, easy to understand.
- Con: Equal weight to a brand awareness ad and a retargeting ad is rarely accurate.
- Best for: Balanced view across the funnel.

**Time-Decay Attribution:**
- Credit decays exponentially based on recency — the last touchpoint gets the most credit, but earlier touchpoints still get some
- Pro: Balances recency with a nod to the full journey.
- Con: Still somewhat arbitrary in how the decay curve is set. Favors lower-funnel channels.

**U-Shaped Attribution (Position-Based):**
- 40% credit each to first and last touchpoints; remaining 20% split among middle touchpoints
- Pro: Acknowledges that discovery (first touch) and closing (last touch) are most important.
- Con: Arbitrary percentages. Doesn't account for journeys with only 2 touchpoints or 20 touchpoints.

**Data-Driven Attribution (DDA):**
- Machine learning determines credit allocation based on actual impact on conversion probability
- Uses algorithms (e.g., Shapley value, game theory) to determine each channel's marginal contribution
- Requires large data volumes (typically millions of conversions)
- Available in: Google Analytics 4, Adobe Analytics, Mixpanel, Attribution (attributiomodelingtools)
- Pro: Most accurate — reflects actual contribution, not assumptions
- Con: Requires significant data and statistical expertise. Results can be hard to explain to stakeholders.

### 5.3 Multi-Touch Attribution Challenges

**Cross-Device Tracking:** A user researches on their phone, converts on desktop. Without a logged-in state, this appears as two separate users.

**Privacy:** Third-party cookie deprecation (Chrome ended support in 2024) has disrupted cookie-based attribution. Solutions include: server-side tagging, first-party data strategies, Google Privacy Sandbox APIs.

**Offline Attribution:** How do you track a customer who saw a TV ad and then converted via your website? Solutions: econometric modeling, incrementality testing, geographic Holdout tests.

**View-Through Attribution:** A user saw a display ad but didn't click. Does the view deserve credit? View-through attribution says yes (extends attribution window), but it's debated because no intent was signaled.

### 5.4 Attribution Tools

**Google Analytics 4 (GA4):** Provides data-driven attribution out of the box (for qualifying data volumes). Cross-platform via User-ID. Free tier available.

**Mixpanel:** Product analytics with cohort analysis and attribution. Strong for in-product funnel analysis. Data-driven attribution available at higher tiers.

**Amplitude:** Product analytics focused on product-led growth. Features behavioral cohorts, advanced segmentation, and predictive analytics.

**Heap:** Auto-capture analytics (no event tracking required). Retroactive analysis possible on historical data.

**Attribution Software (Rockerbox, Hyros, Northbeam, Mutiny):** Purpose-built attribution platforms. Rockerbox and Northbeam focus on incrementality testing and clean room-based attribution for privacy-safe measurement.

---

## 6. LTV/CAC Analysis

Lifetime Value (LTV or CLV) and Customer Acquisition Cost (CAC) are the two foundational metrics for understanding the economics of growth. The LTV:CAC ratio is the single most important metric for evaluating sustainable growth.

### 6.1 Customer Acquisition Cost (CAC)

CAC is the total cost to acquire a new customer, including all sales and marketing spend.

**CAC Components:**
- Advertising spend (paid search, display, social)
- Content marketing costs (blog, videos, case studies)
- SEO/content production costs
- Sales team salaries, commissions, and bonuses
- Marketing technology (CRM, attribution tools, email platforms)
- Partner/referral program costs
- Overhead allocation (facilities, tools)

**CAC Calculation:**

Simple CAC:
```
CAC = Total Sales & Marketing Cost / Number of New Customers Acquired
```

Blended CAC (includes all customers, new and existing):
```
Blended CAC = Total Sales & Marketing Cost / Total New Customers
```

Paid CAC (acquisition through paid channels only):
```
Paid CAC = Paid Marketing Spend / Customers from Paid Channels
```

**CAC by Channel:**
Calculate CAC separately for each acquisition channel to understand efficiency:
- Organic CAC (from SEO, content, referrals)
- Paid Search CAC
- Social CAC
- Sales-Assisted CAC

### 6.2 Lifetime Value (LTV/CLV)

LTV is the total revenue a customer generates over their entire relationship with your company.

**Simple LTV (Average Revenue Model):**
```
LTV = Average Revenue Per User (ARPU) × Average Customer Lifetime
```

Where:
- ARPU = MRR (Monthly Recurring Revenue) / Number of Active Customers
- Average Lifetime = 1 / Monthly Churn Rate

**More Accurate LTV (With Discount Rate):**
For a more precise LTV that accounts for the time value of money:

```
LTV = Σ (ARPU × Gross Margin × Retention Probability) / (1 + Discount Rate)^t
```

For SaaS with relatively flat retention:
```
LTV = ARPU × Gross Margin / Monthly Churn Rate
```

**Predictive LTV:**
Machine learning models can predict individual customer LTV based on behavior patterns:
- Features: acquisition channel, first product used, engagement patterns, billing cycle
- Algorithm: Survival models (Cox proportional hazards), gradient boosting, regression

### 6.3 The LTV:CAC Ratio

This ratio tells you how efficiently you're growing. Each dollar spent on acquisition returns how many dollars over the customer's lifetime?

```
LTV:CAC Ratio = LTV / CAC
```

**Benchmarks:**

| LTV:CAC Ratio | Interpretation | Action |
|---|---|---|
| < 1:1 | Losing money on every acquisition | Reduce CAC, increase prices, improve retention |
| 1:1 – 3:1 | Healthy but low efficiency | Optimize marketing channels, improve conversion rates |
| 3:1 – 5:1 | Healthy growth | Optimal range for sustainable growth |
| > 5:1 | Under-investing in growth | You're leaving growth on the table. Scale acquisition. |

The classic "ideal" LTV:CAC ratio is often cited as 3:1, with the reasoning that the ratio should reflect the business's payback period and risk tolerance.

### 6.4 Payback Period

How long does it take to recover the CAC from a customer's revenue? This is critical for cash flow management.

```
Payback Period (months) = CAC / (ARPU × Gross Margin)
```

**Benchmarks:**
- < 6 months: Excellent. Fast cash flow recovery.
- 6-12 months: Healthy. Standard for SaaS.
- 12-18 months: Acceptable but capital-intensive. Requires longer runway.
- > 18 months: Generally not sustainable without large venture backing.

### 6.5 LTV:CAC in Practice

**Cohort LTV:** Calculate LTV separately for each cohort (by acquisition month/quarter). If the newest cohorts have lower LTV:CAC, it signals acquisition channel degradation or increased competition.

**Segment LTV:** Different customer segments have dramatically different economics:
- Enterprise customers often have 5-10x the LTV of SMB customers
- Product-qualified leads (PQLs) typically have 2-3x the LTV of cold leads
- High-engagement users from specific acquisition channels may have the best LTV:CAC

**Using LTV:CAC to Make Decisions:**
- **Channel allocation:** Shift budget toward channels with the best LTV:CAC ratio
- **Pricing strategy:** If LTV:CAC is healthy, you may have room to discount to grow faster
- **Feature investment:** Features that improve retention improve LTV and therefore LTV:CAC
- **Sales vs. marketing mix:** If sales-assisted CAC vs. marketing CAC differ dramatically, optimize the split

---

## Summary: Key Takeaways

1. **Dashboard Design:** Start with the business question, not the data. Prioritize visual hierarchy, provide context with comparisons (vs. last period, vs. target), and follow the 3-second rule. Different audiences need different dashboards.

2. **Tool Selection:** Looker for enterprise metric governance and a semantic layer. Metabase for broad self-service access (open-source or cloud). Grafana for metrics, monitoring, and alerting (DevOps and infrastructure). Consider a hybrid approach with a unified dbt semantic layer.

3. **SaaS KPI Framework:** Start with the North Star Metric and build a KPI hierarchy from activation → engagement → retention → revenue → referral. The right metrics vary by growth stage — PMF stage needs retention focus; scaling stage needs CAC and LTV:CAC focus; efficiency stage needs Rule of 40 and payback period focus.

4. **Cohort Analysis:** The most powerful technique for understanding how different customer groups behave over time. Always build retention cohort tables — they reveal patterns that aggregate metrics completely hide. Use cohorts to measure the impact of product changes, marketing campaigns, and pricing decisions.

5. **Attribution Modeling:** No single attribution model is "correct" — each represents a different assumption about channel value. Use multi-touch attribution as a strategic guide (DDA or U-shaped), but validate with incrementality testing (A/B tests where you hold out channels for a test group) to understand true causal impact.

6. **LTV:CAC Analysis:** The LTV:CAC ratio is the cornerstone of growth economics. Target > 3:1 with a payback period under 12 months. Track it by cohort, by segment, and by channel. Invest in improving retention — a 1% improvement in monthly churn rate dramatically increases LTV.
