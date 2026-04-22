# Pipeline Management — SDR-2 Research v3
> Researched: $(date)

## 1. Pipeline Forecasting

### Methods
- **Bottom-up forecasting**: Sum of expected revenue from individual deals weighted by stage probability. Most accurate for SDRs who track each deal closely.
- **Top-down forecasting**: Market-based assumptions applied across the whole pipeline. Less granular.
- **Multiplying factor method**: Multiply total pipeline by historical close rate (e.g., 20% close rate × pipeline value = forecast).
- **Stage-weighted pipeline**: Apply stage-by-stage win rates. SDRs most commonly track: Lead → MQL → SQL → Opportunity → Demo Scheduled → Proposal → Closed Won.

### Key Metrics
- **Pipeline Coverage Ratio**: Total pipeline value / Quota. Target 3× quota minimum.
- **Forecast Accuracy**: Predicted vs. actual. Track per stage to refine.
- **Ramping time**: Days from hire to first closed deal.

## 2. Deal Velocity Optimization

### Drivers of Velocity
- **Time to first contact**: Target <5 min from lead creation.
- **Response time**: Fastest responder wins. Auto-dialers + email sequences critical.
- **Meeting booked velocity**: Track days from initial contact to meeting booked.
- **Decision-maker engagement speed**: Deals stall when only influencers engage.

### Acceleration Tactics
- Multi-channel sequences (email + LinkedIn + phone).
- Personalized messaging referencing specific pain points.
- Urgency anchoring (limited seats, price changes, cohort deadlines).
- Social proof (case studies, similar company logos).
- Meeting-first approach: push to book demo/meeting immediately.

### Stages and Expected Velocity
| Stage | Avg Days | Red Flag |
|---|---|---|
| New Lead → First Contact | 0-1 days | >3 days |
| First Contact → Demo Booked | 1-7 days | >14 days |
| Demo → Proposal | 7-21 days | >30 days |
| Proposal → Close | 7-30 days | >60 days |

## 3. Stage Conversion Rates

### Industry Benchmarks
- **Lead → MQL**: 15-25%
- **MQL → SQL**: 20-40%
- **SQL → Opportunity Created**: 40-60%
- **Opportunity → Demo**: 50-70%
- **Demo → Proposal/Quote**: 40-60%
- **Proposal → Closed Won**: 20-35%
- **Overall Lead → Close**: 5-15% (highly variable by industry/ICP)

### Conversion Analysis
- Track conversion at EVERY stage — not just end-to-end.
- Calculate stage-by-stage dropoff to identify bottlenecks.
- Segment by: industry, company size, geo, source, persona.
- A/B test messaging, timing, and channel at each stage.

### Conversion Formula
\`Conversion Rate = (Deals entering next stage / Deals in current stage) × 100\`

### Improving Conversion Rates
- Qualify harder at top to reduce time wasted on bad-fit leads.
- Use intent data to prioritize warm accounts.
- Automate follow-ups to prevent leads going cold.
- Clear stage definitions — ambiguous stages kill conversion.

## 4. Deal Health Scoring

### BANT Framework (Classic)
- **Budget**: Do they have budget to buy?
- **Authority**: Who makes the buying decision?
- **Need**: Do they have a burning problem your solution solves?
- **Timeline**: When do they need to solve it?

### MEDDIC Framework (Enterprise)
- **Metrics**: What business metrics will improve?
- **Economic Buyer**: Who controls the budget?
- **Decision Criteria**: What are they using to evaluate?
- **Decision Process**: How does buying happen internally?
- **Identify Pain**: What specifically hurts?
- **Champion**: Who internally is pushing for this?

### Scorecard Approach
Rate each deal 1-10 on:
1. Need urgency (1-5): How pressing is the problem?
2. Budget clarity (1-5): Confirmed budget range?
3. Decision-maker access (1-5): Can you reach the decision-maker?
4. Timeline (1-5): Is there a defined purchasing window?
5. Champion strength (1-5): Do you have an internal advocate?

**Health Score = Sum. Red: <12, Yellow: 12-18, Green: 19-25**

### Deal Stalling Signals
- No response >5 business days.
- Meeting cancelled 2+ times.
- Champion goes silent or gets replaced.
- "We're still evaluating" without specific next steps.
- Competitor mentioned by name.
- No budget conversation after 3+ calls.

## 5. CRM Hygiene Automation

### Core Hygiene Rules
- **Deduplication**: Merge duplicate contacts/companies.
- **Data enrichment**: Auto-populate firmographics (headcount, revenue, industry).
- **Activity logging**: Every call, email, meeting logged automatically via integrations.
- **Stage progression**: Enforce stage movement rules (e.g., can't skip stages).
- **Stale deal flagging**: Auto-flag deals with no activity in 7/14/30 days.

### Automation Tools
- **Gong / Clari**: Conversation intelligence + deal прогнозирование.
- **Salesforce / HubSpot**: Workflow automation for stage updates.
- **Apollo / Outreach / Salesloft**: Cadence automation + engagement tracking.
- **Clearbit / ZoomInfo**: Auto-enrichment.
- **Chorus**: Call recording + coaching.

### CRM Fields Every SDR Must Fill
- Lead source
- Industry / Vertical
- Company size (employees + revenue)
- Current tool in use (competitive intel)
- Buying timeline
- Decision-maker name + title
- Last contact date (auto)
- Next action + date
- Lead score / Health score
- Stage

### Hygiene Cadence
| Task | Frequency |
|---|---|
| Update all open deals | Daily |
| Log all activities | Real-time |
| Purge stale leads | Weekly |
| Re-engage cold prospects | Bi-weekly |
| Enrich CRM data | Weekly |
| Audit pipeline stages | Monthly |

## 6. Sales Analytics Dashboards

### Must-Have Dashboard Metrics

#### Volume Metrics
- Leads received per day/week/month
- MQLs delivered
- SQLs created
- Opportunities created
- Meetings booked
- Demos completed

#### Conversion Metrics
- Stage-by-stage conversion rates
- Lead-to-close rate
- Response rate (% of outreach replied to)
- Meeting show rate

#### Velocity Metrics
- Avg time in stage
- Avg cycle length (contact → close)
- Days to first response
- Days to meeting booked

#### Activity Metrics
- Calls made / connects / conversations
- Emails sent / open rate / reply rate
- LinkedIn messages sent / response rate
- Meetings completed

#### Efficiency Metrics
- Revenue per rep
- Cost per lead / cost per MQL / cost per SQL
- Pipeline coverage ratio
- Win rate by segment

### Tools
- **Gong Analytics**: Conversation data, talk ratio, questions asked.
- **Salesforce Reports & Dashboards**: Pipeline, forecast, activity.
- **Looker / Tableau**: Custom visualization.
- **HubSpot Sales Hub**: Built-in dashboards.
- **Clari**: Pipeline + forecast management.
- **Outreach Analytics**: Engagement sequences.
- **Xactly / Inspima**: Commission tracking + quota attainment.

### Building a Weekly Review Framework
1. **Monday**: Pipeline review — stale deals, next actions, forecast update.
2. **Wednesday**: Mid-week check — are you on pace for activity targets?
3. **Friday**: Week close — log all activities, update CRM, plan next week.

## 7. SDR-Specific Pipeline Tips

### For SDRs
- Treat every lead as a mini-pipeline: qualify hard, advance fast.
- Focus on activities that drive velocity: calls, LinkedIn, personalized email.
- Don't let deals go dark — set automated reminders.
- Know your ICP cold: only pursue leads that match.
- Track your personal metrics: conversion rates, meeting rates, deal quality.
- Use intent signals: job postings, funding news, expansion signals.

### Common Pipeline Mistakes
- Chasing volume over quality.
- Not logging activities (kills forecasting).
- Skipping stages (demo before qualification).
- Letting stale deals sit too long.
- Not escalating to AE when qualified.

### Qualifying Questions for Pipeline Health
1. What happens if you don't solve this problem?
2. Who else is affected by this problem?
3. How are you solving it today?
4. What's your budget range for a solution?
5. When do you need this solved by?
6. Who else needs to be involved in the decision?
7. What does the evaluation process look like?
8. What would have to be true for you to move forward?

---

*Generated by SDR-2 Agent — Pipeline Management Research v3*
*Date: $(date +%Y-%m-%d)*

## 8. Advanced Pipeline Management Techniques

### Weighted Pipeline Formula
\`Weighted Pipeline = Σ(Deal Value × Stage Win Rate)\`

Example:
| Stage | Deal Value | Win Rate | Weighted Value |
|---|---|---|---|
| Demo Scheduled | $50,000 | 75% | $37,500 |
| Proposal | $50,000 | 50% | $25,000 |
| Negotiation | $50,000 | 85% | $42,500 |
| **Total Weighted Pipeline** | | | **$105,000** |

### Pipeline Coverage Ratios by Stage
- **3× coverage**: Conservative — good for high-conversion, small-deal sales.
- **4-5× coverage**: Standard SaaS — typical quota attainment.
- **6×+ coverage**: Aggressive — may indicate quality issues or long cycles.
- Monitor coverage ratio weekly, not monthly.

### Stages: Design vs. Reality
Most CRMs ship with terrible stage names. Customize to your process:
- Generic: Lead → Qualified → Demo → Proposal → Closed Won
- Better: Discovery → Technical Fit → Business Case → Negotiation → Contract

### Stage Definitions (Why They Matter)
Every stage needs:
1. **Entry criteria**: What must be true to enter this stage?
2. **Exit criteria**: What must be true to leave this stage?
3. **Owner**: Who moves the deal forward?
4. **Activities**: What happens at this stage?
5. **Average time**: How long should deals stay here?

### Pipeline Generation by ICP
Segment your pipeline by:
- **Ideal Customer Profile (ICP)**: Best-fit companies.
- **Tier 2 ICP**: Good fit, lower priority.
- **Out of ICP**: Bad fit, minimum engagement.

Track your conversion rates by ICP tier. You should see:
- Tier 1: Highest conversion, shortest cycle.
- Tier 2: Medium conversion, medium cycle.
- Out of ICP: Lowest conversion, longest cycle, most time wasted.

### CRM Architecture for SDRs
Key objects and fields to track:
```
CONTACT
├── First Name, Last Name, Title
├── Email, Phone, LinkedIn URL
├── Company (linked)
├── Lead Source
├── Initial Source
├── Buying Stage
├── Last Contact Date
└── Next Follow-up Date

COMPANY
├── Company Name, Domain
├── Industry, Employee Count
├── Annual Revenue
├── Country, State, City
├── Tech Stack (tools in use)
├── Funding Stage
├── Funding Amount
└── Company Notes

OPPORTUNITY
├── Opportunity Name
├── Account (linked)
├── Owner (SDR/AE)
├── Stage
├── Amount
├── Close Date
├── Probability (%)
├── Next Step
├── Next Step Date
├── Lead Source
├── ICP Tier
└── Competition

ACTIVITY (Task/Event)
├── Type (Call, Email, Meeting, LinkedIn)
├── Subject
├── Date
├── Duration
├── Outcome (Connected, No Answer, Voicemail, etc.)
├── Notes
└── Opportunity/Contact (linked)
```

## 9. Deal Velocity Deep Dive

### The Four Drivers of Deal Velocity
**V = D × C × P × A**

Where:
- **V** = Velocity (revenue per time unit)
- **D** = Deals (number of opportunities)
- **C** = Cycle Length (days from open to close)
- **P** = Price (average deal size)
- **A** = Win Rate

To increase velocity:
- **Increase deals**: More top-of-funnel, better qualification.
- **Shorten cycle**: Faster follow-up, reduce friction.
- **Raise price**: Better value prop, competitive differentiation.
- **Raise win rate**: Better qualification, stronger champion.

### Meeting Velocity Metrics
Track these specifically:
- **Avg days from first contact to demo booked**: Target <7 days.
- **Demo show rate**: Target >70%.
- **Meeting length**: Longer ≠ better. Measure outcomes.
- **Meetings per deal**: Fewer is better (more efficient).

### Speed-to-Lead Standards
| Lead Type | Target Response Time |
|---|---|
| Inbound (web form) | <5 minutes |
| Inbound (chat) | <30 seconds |
| Phone call (inbound) | Immediate |
| Demo request | <30 minutes (email), <2 hours (form) |
| Referred warm lead | <2 hours |
| Event lead | <24 hours |
| Cold outbound | Sequence start within 1 hour of list creation |

### Acceleration Tactics by Stage
**Stage 1: New Lead**
- Auto-dialer immediately on lead creation.
- Personal video email (Loom, Vidyard) for top prospects.
- LinkedIn connection + message same day.

**Stage 2: First Contact**
- 3-touch sequence in first 5 days (no more than 1/day).
- Offer a relevant resource (case study, ROI calculator).
- Social proof: "We work with [similar company] in your industry."

**Stage 3: Demo/Meeting**
- Book meeting within 2 calls max.
- Calendar link in first reply.
- Confirm 24 hours before + morning-of reminder.

**Stage 4: Post-Demo**
- Send personalized follow-up same day.
- Book next step before ending current meeting.
- Send relevant content based on what they asked about.

**Stage 5: Proposal/Negotiation**
- Weekly check-in cadence.
- Executive touchpoint every 2 weeks.
- Business case review call before close.

## 10. CRM Automation for SDRs

### Outreach/Salesloft/HubSpot Automation Ideas
1. **Lead scoring**: Auto-score based on engagement (opens, clicks, replies, page visits).
2. **Lead routing**: Auto-assign leads to rep based on geography, industry, or round-robin.
3. **Follow-up reminders**: Auto-create task when no activity for 3-5 days.
4. **Stage progression**: Move deal to next stage when meeting is logged.
5. **Hot lead alerts**: Notify rep via Slack/email when high-intent trigger fires.
6. **Auto-enrichment**: Pull firmographics from Clearbit/ZoomInfo on lead creation.
7. **Sequence pauses**: Pause sequence when meeting is booked.
8. **Step skip logic**: Skip steps when email bounces or phone is disconnected.

### Revenue Operations (RevOps) Alignment
SDRs should have a regular RevOps cadence:
- **Weekly**: Review pipeline accuracy with RevOps. Flag CRM issues.
- **Bi-weekly**: Align on sequence performance, cadence changes.
- **Monthly**: Review forecast accuracy, conversion rates, deal velocity.
- **Quarterly**: Pipeline review, territory planning, quota setting.

### Sales Analytics: Building Your Own Scorecard

Track these weekly metrics personally:
1. **Activities**: Calls, emails, LinkedIn touches, meetings booked.
2. **Meetings**: Demos scheduled, demos completed, meeting show rate.
3. **Conversion**: MQL → SQL → Opp conversion rates.
4. **Pipeline**: Total pipeline, weighted pipeline, pipeline coverage.
5. **Velocity**: Avg days to book, avg days in stage.
6. **Quality**: Win rate, deal size average, quota attainment.

---

*Generated by SDR-2 Agent — Pipeline Management Research v3*
*Date: $(date +%Y-%m-%d)*
