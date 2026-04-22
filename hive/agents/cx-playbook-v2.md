# CX/CCaaS Specialist Playbook — 15 Core Skills

> Built from: GitHub research, vendor documentation, industry frameworks. April 2026.

---

## SKILL 1: CCaaS Vendor Evaluation Framework

### Description
A structured framework for evaluating CCaaS vendors against your organization's specific needs. Vendor demos and sales pitches are misleading — use this framework to systematically compare platforms.

### Evaluation Criteria (Weighted Scoring)

**Category A: Technical Fit (40% total)**
| Criterion | Weight | Questions to Ask |
|---|---|---|
| AI/Analytics capabilities | 15% | Does it have real-time agent assist? Post-call summarization? Sentiment analysis? |
| Omnichannel breadth | 10% | Voice, chat, email, WhatsApp, SMS, social — what's native vs. third-party? |
| CRM integration | 10% | Native Salesforce/HubSpot? API depth? Real-time context passing? |
| Customization/API depth | 5% | Can you build custom workflows? Webhook support? Low-code builders? |

**Category B: Operational Fit (35% total)**
| Criterion | Weight | Questions to Ask |
|---|---|---|
| WFM + QM | 15% | Is WFM included? AI-powered forecasting? QM automated scoring? |
| Security & Compliance | 12% | PCI-DSS Level 1? HIPAA BAA available? SOC 2 Type II? GDPR? |
| Scalability & SLA | 8% | Uptime SLA?geo-redundancy? Max concurrent contacts? |

**Category C: Commercial Fit (25% total)**
| Criterion | Weight | Questions to Ask |
|---|---|---|
| Pricing model | 10% | Per-seat? Per-minute? Hybrid? Hidden fees (API, recordings, data)? |
| Vendor stability | 8% | Financial health? Customer base size? Longevity (acquisition risk)? |
| Migration complexity | 7% | How long to migrate from legacy? What does migration support include? |

### Steps
1. **Create a weighted scorecard** using the table above, customized for your org's priorities
2. **Score each vendor 1–5** on each criterion
3. **Weight × Score = Weighted Score** for each criterion
4. **Sum weighted scores** → overall vendor ranking
5. **Run a proof-of-concept** (2–4 weeks) with the top 2 vendors before committing
6. **Negotiate**: Most vendors have 20–30% pricing flexibility, especially for 3-year commits

---

## SKILL 2: AWS Connect Deep Dive

### Description
End-to-end AWS Connect setup, configuration, and integration for production deployments.

### Steps

**Step 1: Core Infrastructure Setup**
```
1. Create AWS account → Enable Connect in us-east-1 or preferred region
2. Claim a phone number (DID) via Connect → provision inbound numbers
3. Create a routing profile: set queue hierarchy, routing criteria
4. Create queues: define priority, max contacts, service level thresholds
5. Create routing rules: hours of operation, holiday schedules, IVR logic
```

**Step 2: IVR / Contact Flow Design**
```
1. Go to Connect → Create contact flow (drag-and-drop builder)
2. Build basic flow: Entry → Play prompt → Get customer input (Lex) → Branch
3. Connect to queue → Transfer to agent
4. Advanced: Lambda invocation for CRM lookup → pass data to agent desktop
5. Use Contact Flow samples from AWS re:Post as starting templates
```

**Step 3: Agent Setup**
- Create agent hierarchy → assign routing profiles
- Set up softphone (Connect uses browser-based CCP — Contact Control Panel)
- Assign security profiles (permissions: transfer, conference, conference out)
- Configure quick connects (transfer targets: queues, external numbers, other agents)

**Step 4: CRM Integration (Salesforce example)**
```
1. Install "Connect CTI Adapter" from Salesforce AppExchange
2. Configure softphone layout in Salesforce (screen pop configuration)
3. Connect → Settings → Integrations → Salesforce → OAuth
4. Map Connect queue to Salesforce case/status
5. Test: inbound call → CRM screen pop with caller context
```

**Step 5: Contact Lens (AI) Setup**
```
1. Enable Contact Lens in Connect: Settings → Contact Lens
2. Configure real-time and post-call analysis rules
3. Set up data storage: S3 bucket + KMS encryption
4. Create IAM roles for analytics access
5. Connect to Kinesis for real-time streaming to custom dashboards
```

**Step 6: Real-World Configuration Template**
```python
# Example: Lambda for CRM lookup on inbound call (Python)
import boto3

def lambda_handler(event, context):
    # Extract phone number from Connect contact event
    phone = event['Details']['ContactData']['CustomerEndpoint']['Address']
    
    # Query Salesforce (or your CRM) for customer record
    sf_client = boto3.client('sfc')  # Simple CRM client
    
    customer = sf_client.find_customer(phone=phone)
    
    return {
        'CustomerName': customer['Name'],
        'AccountId': customer['AccountId'],
        'OpenCases': customer['OpenCases'],
        'Tier': customer['Tier']
    }
    # This result gets passed to the agent's CCP screen pop
```

### Key AWS Connect Gotchas
- Contact Lens requires S3 + KMS setup — don't skip encryption configuration
- Lex bot versions: use Lex V2 API, V1 is being deprecated
- Contact flows time out at 20 minutes — watch for long wait times
- Hour of operation defaults to 24/7 — configure actual business hours

---

## SKILL 3: Genesys Cloud Capabilities

### Description
Full platform walkthrough — routing, AI, agent desktop, analytics, WFM, QM.

### Core Architecture

**Genesys Cloud = Architect (flow builder) + ACD + PureCloud (unified communications) + AI layer**

### Key Capabilities

**1. Architect (Flow Builder)**
- Drag-and-drop flow builder for all interaction types
- Supports webhooks, REST calls, data actions, custom integrations
- Built-in NLU for intent detection in digital flows
- Version control for flows (promote from dev → staging → prod)

**2. Routing & Orchestration**
- Skill-based routing: agents tagged with skills → interactions routed by matching
- Predictive routing: ML model → routes to agent with highest probability of positive outcome
- Priority queuing: SLA-based, patience-based, value-based
- Overflow rules: peak handling, cross-queue backup routing

**3. AI Layer (Genesys AI + Pineal)**
- Real-time agent assist: knowledge articles suggested in-context
- Post-contact summarization: auto-generated wrap-up notes
- Intent detection: categorizes inbound intents automatically
- Sentiment analysis: real-time scoring, trend dashboards
- Bot Foundry: no-code bot builder for voice + digital

**4. Workforce Management (WFM)**
- AI-powered forecasting: uses historical data + event-based adjustments
- Scheduling optimizer: builds schedules meeting FTE requirements
- Real-time adherence: agent adherence tracking vs. schedule
- Intraday management: real-time adjustments for volume variances

**5. Quality Management (QM)**
- Automated call scoring: AI evaluates calls against criteria (gentle, accurate, compliant)
- Manual QA reviews: supervisor evaluation with standardized forms
- Calibration: supervisor calibration reports to ensure consistent scoring
- Speech analytics: keyword spotting, silence detection, talking speed

**6. Analytics**
- Forecite (real-time): real-time dashboard for queues, agents, SL
- Explore: historical analytics, custom report builder
- Predictive engagement: identifies opportunities to proactively engage visitors

### Implementation Steps
1. **Foundation**: Import users → create sites → create queues → create routing profiles
2. **Routing**: Build Architect flows for each interaction type
3. **AI**: Configure Genesys AI → enable agent assist → configure summarization
4. **WFM**: Import historical data → run forecasting → create schedules → enable adherence
5. **QM**: Create evaluation forms → configure auto-scoring → calibrate supervisors

---

## SKILL 4: Journey Mapping Methodology

### Description
A repeatable, data-driven approach to mapping customer journeys and identifying AI/intervention opportunities.

### The 6-Phase Journey Mapping Process

**Phase 1: Define Scope**
- Pick 3–5 key journeys (e.g., new customer, tech support, billing inquiry)
- Set boundaries: where does the journey start and end?
- Identify stakeholders: CX team, operations, agents, IT

**Phase 2: Data Collection**
```
1. Quantitative: CCaaS analytics → top 10 reasons for contact
2. Qualitative: Agent interviews (30 min each, 5–10 agents)
3. VOC: Survey data, NPS verbatims, chat transcripts
4. Operational: AHT, FCR, CSAT by journey stage
```

**Phase 3: Map the AS-IS Journey**
- Use canvas with columns: Touchpoint → Channel → Action → Emotion → Friction → KPI
- Map from customer perspective, not internal org chart
- Mark emotional highs (delight) and lows (frustration) with emoji

**Phase 4: Analyze Friction**
- Score friction points: Effort (1–5) × Frequency × Business Impact
- Use ICE scoring: Impact × Confidence × Ease → prioritize
- Identify root causes: is it process? Technology? Policy? Training?

**Phase 5: Design TO-BE Journey**
- Brainstorm AI interventions (bot, agent assist, proactive notification)
- Map new touchpoints and expected outcomes
- Set target KPIs for each stage (AHT reduction, CSAT improvement, FCR improvement)

**Phase 6: Implementation & Measurement**
- Build a roadmap: Q1 (quick wins), Q2 (AI pilots), Q3+ (full rollout)
- Implement in CCaaS as contact flows
- Measure against baseline — 90-day post-launch review

### Journey Map Template

| Touchpoint | Channel | Customer Action | Emotion | Friction | AI Opportunity | KPI Target |
|---|---|---|---|---|---|---|
| Product not working | Email | Customer sends email | 😤 | Long wait for response | AI respond with fix steps | < 2hr response |
| Call in | Voice | Waits 8 min in queue | 😤 | Long hold | AI callback scheduler | < 2 min wait |
| Agent answers | Voice | Explains issue | 😐 | Repeat info 3x | Screen pop with context | CSAT > 4.5 |
| Resolution | Chat | Confirm fix | 😊 | None | Self-serve knowledge | FCR > 75% |

---

## SKILL 5: Voice of Customer (VoC) Program Design

### Description
Build a VOC program that captures, analyzes, and acts on customer feedback at scale.

### The 4-Layer VOC Framework

**Layer 1: Feedback Collection**
- **Post-contact surveys**: CSAT (1–5), CES (1–7), NPS (0–10) — triggered automatically by CCaaS
- **In-interaction feedback**: "Was this helpful?" thumbs up/down during chat
- **Agent-initiated feedback**: agents can flag issues in QM system
- **Social/listening**: monitor Twitter, Reddit, review sites for brand mentions
- **Verbatims**: auto-capture text responses in all surveys

**Layer 2: Analytics & Classification**
- **Text analytics**: NLP to classify feedback into categories (billing, support, product)
- **Sentiment scoring**: positive/negative/neutral across all feedback
- **Theme detection**: AI identifies emerging themes before they become trends
- **Root cause linking**: tie CSAT scores to specific agent/interaction/flow

**Layer 3: Routing & Action**
- **Negative feedback → escalation**: CSAT ≤ 2 triggers immediate supervisor alert
- **Positive feedback → agent recognition**: CSAT ≥ 5 triggers agent kudos
- **Trend → operational change**: themes over threshold → create Jira ticket for CX team
- **NPS detractor → retention**: NPS ≤ 6 triggers proactive outreach workflow

**Layer 4: Closed-Loop Reporting**
- **Daily dashboard**: CSAT trend, response rate, top categories
- **Weekly review**: agent-level CSAT, coaching opportunities
- **Monthly executive report**: NPS trend, cost to serve, journey-level CSAT

### VOC Program KPI Targets
| KPI | Target | Measure |
|---|---|---|
| Survey response rate | > 20% | responses / contacts |
| CSAT average | > 85% | (4+5 ratings) / total |
| NPS | > 40 | 0–10 score |
| First-contact resolution | > 70% | resolved in 1 interaction |
| Verbatim capture rate | > 50% | non-null text responses |
| Action closure rate | > 80% | themes acted on / themes identified |

---

## SKILL 6: AI-Powered Routing and Queuing

### Description
Design and implement intelligent routing that uses AI to match customers with the best available agent.

### Routing Architecture Layers

**Layer 1: Priority Rules (deterministic)**
- Skills-based routing: match customer need → agent skill
- Language matching: preferred language → agent language capability
- VIP routing: high-value customers → senior agents
- Time-based routing: business hours → correct queue

**Layer 2: ML-Based Optimization**
- Predictive routing: ML model scores agents by probability of positive outcome for this customer
- Wait time optimization: route to queue with shortest projected wait
- Agent workload balancing: prevent agent overload / underload

**Layer 3: AI Intervention**
- Callback offers: if wait time > threshold → offer callback (AI schedules)
- Virtual queue: customer enters virtual queue → gets position → AI calls when agent available
- Proactive outreach: AI identifies customers likely to need support → contacts first

### Implementation: Predictive Routing

```
Step 1: Define the outcome to optimize
        → Resolution in first contact? Customer satisfaction? Speed to answer?

Step 2: Pull historical data
        → Past interactions: customer attributes + agent attributes → outcome
        → Include: customer tenure, product tier, issue type, agent experience, skill score

Step 3: Train ML model (use vendor's built-in or AWS SageMaker)
        → Outcome: FCR (binary) or CSAT (1–5)
        → Model: Gradient boosted trees (XGBoost) or logistic regression

Step 4: Deploy scoring in routing layer
        → At time of incoming contact: score each available agent
        → Route to agent with highest predicted score
        → Log prediction + actual outcome for model retraining

Step 5: Monitor and retrain
        → Track prediction accuracy vs. actual
        → Retrain monthly or when concept drift detected (performance degrades)
```

### Routing Templates by Use Case

**E-commerce support**:
```
High value (>$500 order) → VIP queue → senior agent → < 30 sec SLA
Low value + simple question → IVA bot → self-serve → resolve without agent
Low value + complex question → standard queue → any available agent
```

**Financial services**:
```
Urgent (fraud alert) → immediate agent (no queue)
Account management → IVA → 80% self-serve, 20% escalate
New application → routing to sales queue → skilled agent
```

---

## SKILL 7: Workforce Management (WFM) Setup

### Description
End-to-end WFM implementation: forecasting, scheduling, adherence, real-time management.

### The WFM Cycle

```
1. Historical Data Analysis (Inputs)
2. Forecasting (demand prediction)  
3. Capacity Planning (FTE calculation)
4. Scheduling (shift creation)
5. Intraday Management (real-time adjustments)
6. Adherence & Coaching (performance vs. plan)
7. Analysis & Optimization (back to step 1)
```

### Step-by-Step: WFM Setup in CCaaS

**Step 1: Data Preparation**
```
Gather 12 months of: contact volume, AHT, handle time by interval (30 min)
Add: agent headcount, shrinkage (vacation, sick, training), seasonal patterns
Clean: remove anomalies (system outages, marketing campaigns) from baseline data
```

**Step 2: Forecasting**
```
Use CCaaS WFM tool (or implement in Python/R):
  - Erlang C or machine learning for volume forecasting
  - Adjust for: seasonality, day-of-week, marketing events, product launches
  - Output: forecast contact volume by 30-min interval for next 13 weeks
```

**Step 3: Staffing Calculation**
```
Formula: Required Agents = (Forecasted Contacts × AHT) / Target SL / Available Time

Example:
  - 100 calls/hour × 5 min AHT = 500 min/hour demand
  - 480 min/agent/hour (20% shrinkage)
  - At 80/20 SLA target: ~15 agents needed for 100 calls/hour
```

**Step 4: Schedule Creation**
```
- Create shift patterns: morning, afternoon, evening, part-time options
- Build schedules meeting FTE requirements while minimizing overtime
- Publish schedules 2–4 weeks in advance
- Build in flexibility: allow shift swaps via self-service portal
```

**Step 5: Real-Time Adherence**
```
- Track agent adherence: are they in Available state when scheduled?
- Alert supervisors when adherence < 85%
- Use real-time queue dashboards to adjust break schedules dynamically
```

**Step 6: Intraday Management**
```
- Compare actual vs. forecast every 2 hours
- If volume +10% above forecast: call in overtime, adjust breaks
- If volume -10% below forecast: send agents home early, adjust training
- Document all intraday changes for next forecast cycle
```

### AI in WFM
- **AI Forecasting**: Vendor WFM tools (Genesys WFM, AWS + third party, NICE) use ML to improve forecast accuracy
- **Smart Scheduling**: AI suggests schedule optimizations to reduce overtime and improve agent preferences
- **Real-Time Adherence Alerts**: AI detects patterns before they become adherence issues

---

## SKILL 8: Quality Management (QM) Scoring

### Description
Build a QM program that combines AI-powered automated scoring with human calibration for continuous agent improvement.

### QM Framework

**Step 1: Define Quality Criteria**
| Category | Criteria | Weight |
|---|---|---|
| Customer Experience | Greeting, empathy, resolution, hold handling | 40% |
| Process Compliance | Script adherence, data capture, transfers, documentation | 30% |
| Sales Effectiveness | Cross-sell, upsell, compliance (where applicable) | 20% |
| Operational | AHT, hold time, post-contact work | 10% |

**Step 2: Automated Scoring (AI)**
```
Most CCaaS vendors offer auto-scoring:
- Genesys: QM with AI auto-evaluation (50–80% of calls auto-scored)
- NICE: Nexidia automated QA with speech analytics
- AWS Connect: Contact Lens analytics → export to QM system
- Five9: Smart QA automated scoring

Auto-scoring outputs:
  ✓ Sentiment score (positive/negative)
  ✓ Compliance violations (keywords, silence, interruption)
  ✓ Hold time vs. standard
  ✓ Script adherence (keyword matching)
  ✓ Transfer count vs. expected
```

**Step 3: Manual QA Sampling**
- Sample size: 3–5% of all interactions
- Ensure balanced sample: every agent, every queue, every shift
- Use standardized evaluation form in QM system

**Step 4: Calibration**
- Monthly: supervisor calibration session (review 5 calls as a group)
- Goal: ensure consistent scoring across supervisors (calibration score > 85%)
- Use disagreements to refine scoring guidelines

**Step 5: Coaching Loop**
```
QA Review Complete → 
  Score < threshold → Coaching alert to supervisor (within 24hrs)
  Supervisor reviews with agent → creates coaching plan
  Re-evaluate after 30 days → measure improvement
  Top performers → recognition/program (don't ignore high performers!)
```

### QM Dashboard KPIs
| KPI | Target |
|---|---|
| Calls evaluated per agent/month | 3–5 |
| Average quality score | > 85% |
| Calibration consistency | > 85% |
| Coaching completion rate | > 90% |
| Improvement trend (post-coaching) | > 10% improvement on next QA |

---

## SKILL 9: CRM Integration Patterns

### Description
Patterns for connecting CCaaS platforms with CRM systems to deliver context-rich, personalized customer interactions.

### Pattern 1: Screen Pop (Inbound)

```
[Inbound Call] → [CCaaS Platform] → [CRM Lookup] → [Agent Desktop]
                                    ↓
                          Customer Name, Account, 
                          Open Cases, Last 3 Tickets
                          
Implementation:
- AWS Connect: Lambda + Salesforce CTI Adapter
- Genesys: Data actions → Salesforce REST API
- Twilio Flex: Segment → custom webhook
- Five9: Pre-built Salesforce connector
```

### Pattern 2: Activity Logging (Outbound)

```
[Agent interaction ends] → [CCaaS] → [Log to CRM]
                          
Log: interaction type, duration, agent notes, 
     disposition code, next follow-up task
     
Implementation:
- Use CRM REST API to POST interaction record
- Or use vendor's native CRM connector (faster, less flexible)
```

### Pattern 3: Click-to-Dial from CRM

```
[CRM Record] → [Click Phone Number] → [CCaaS dials out] → [Customer answers]
                                                 ↓
                                    Agent desktop shows CRM record

Implementation:
- Twilio Flex: Twilio Client SDK embedded in CRM
- Genesys: embedded softphone in Salesforce
- AWS Connect: Connect CTI + Salesforce Lightning
```

### Pattern 4: 360° Customer Context Panel

```
[Agent receives contact] → [CCaaS sends event to CRM/Segment] 
                          → [Agent sees unified panel:]

  - Customer profile (from CRM)
  - Recent interactions (from CCaaS + CRM)
  - Current sentiment (from Contact Lens/AI)
  - Next best action (from AI model)
```

### Implementation Checklist

```
□ Auth method: OAuth 2.0 (preferred) vs. API key
□ Data fields: define what customer data to pass (account ID, tier, history)
□ Real-time vs. batch: real-time for screen pops, batch for activity logging
□ Field mapping: CRM fields ↔ CCaaS data model
□ Error handling: what happens if CRM is down? (queue interaction, retry)
□ Testing: test with 10% of agents → full rollout
□ Security: OAuth tokens, IP allowlisting, PII handling
```

---

## SKILL 10: Omnichannel Orchestration

### Description
Design and implement a seamless omnichannel experience where customers can move between channels without repeating themselves.

### Omnichannel Architecture

**Channel List** (in priority order of complexity):
1. Voice (phone)
2. Chat (web/mobile)
3. Email
4. WhatsApp / SMS / Messaging (Apple Business Chat, Google Messages)
5. Social (Twitter/X, Facebook Messenger)
6. Video (for complex service scenarios)
7. Self-serve (knowledge base, community)

### The Omnichannel Flow Design

```
[Customer initiates on Channel A]
        ↓
[AI routes to queue] → [Agent picks up on Channel A]
        ↓
[Customer requests move to Channel B]
        ↓
[Agent transfers with context preserved]
        ↓
[Customer continues on Channel B — no need to repeat info]
        ↓
[Single interaction record in CRM, regardless of channels]
```

### Key Omnichannel Principles

1. **Single Customer ID**: each customer has one profile, visible across all channels
2. **Context preservation**: customer never repeats info across channel transitions
3. **Consistent routing logic**: same skills/priority rules apply regardless of channel
4. **Channel preference learning**: AI tracks customer channel preferences over time
5. **Unified reporting**: all channels reported in one dashboard — not siloed

### Implementation Steps

```
1. Map all customer touchpoints and current channel silos
2. Create unified customer profile strategy (use CRM or CDP as master)
3. Configure routing profiles per channel (chat vs. voice have different SL targets)
4. Build channel transition flows (transfer from chat to voice with context)
5. Enable "callback" as an option across all channels (wait time management)
6. Deploy AI deflection: bot first for digital channels (70%+ of contacts)
7. Implement unified analytics: cross-channel KPI dashboard
```

### Channel Deflection Targets (AI/Bot)
| Channel | Bot Resolution Target | Escalation Threshold |
|---|---|---|
| Chat | 70%+ | Intent not recognized after 2 turns |
| WhatsApp | 75%+ | Complex transaction required |
| Email | 60%+ | Sentiment negative or intent complex |
| Voice (IVA) | 40–60% | Caller requests agent or intent complex |

---

## SKILL 11: Real-Time Analytics and Dashboards

### Description
Design, build, and use real-time operational dashboards that drive daily contact center management decisions.

### Dashboard Architecture

**Level 1: Real-Time Operations (updated every 30 sec)**
- Agents available vs. in queue vs. on call
- Current wait time by queue
- Longest wait caller
- SLA status (% of calls answered within target)
- Agents on break vs. wrap-up

**Level 2: Near-Real-Time Performance (updated every 5 min)**
- Current period AHT vs. target
- Agent productivity leaderboard
- Service level trend (last 2 hours)
- Channel mix (voice vs. chat vs. digital)

**Level 3: Daily/Weekly Trend (updated hourly)**
- Daily volume vs. forecast
- CSAT trend
- FCR rate
- Agent occupancy trend

**Level 4: Executive Reporting (daily/weekly)**
- Cost per contact
- NPS trend
- Queue performance vs. target
- Staffing efficiency

### Key Metrics Definition

| Metric | Formula | Target |
|---|---|---|
| Service Level | % calls answered within X seconds (target: 80/20) | > 80% in 20 sec |
| ASA (Avg Speed to Answer) | Total wait time / calls answered | < 30 sec |
| AHT (Avg Handle Time) | (Talk + Hold + Wrap) / contacts | varies by industry |
| Occupancy | (Talk + Hold time) / (Total logged time) | 75–85% |
| FCR (First Contact Resolution) | % contacts resolved without follow-up | > 75% |
| CSAT | % responses ≥ 4 (of 1–5 scale) | > 85% |
| Shrinkage | (Non-productive time) / Scheduled time | 30–35% |

### Building Custom Dashboards

**AWS Connect + QuickSight**:
```
1. Enable Connect data streaming to Kinesis
2. Kinesis → Lambda → S3 (or Redshift for querying)
3. QuickSight → connect to Redshift → build real-time dashboard
4. Publish to supervisors via QuickSight dashboard links
```

**Genesys Cloud**:
```
1. Use built-in Genesys Explore (analytics)
2. Create custom dashboards in Explore
3. Schedule daily email with dashboard snapshot
4. Use Genesys Forecasting for intraday variance analysis
```

**Twilio Flex + Segment**:
```
1. Segment sources → data warehouse (BigQuery/Snowflake/Redshift)
2. Looker/Metabase/Grafana → connect to warehouse
3. Build custom dashboards for real-time operations
```

---

## SKILL 12: Agent Assist and Coaching AI

### Description
Deploy AI-powered agent assist tools that help agents resolve contacts faster, more accurately, and with higher customer satisfaction.

### Agent Assist Architecture

**Real-Time Agent Assist Layer**:
```
[Customer speaks] → [Speech-to-text (real-time)] → [Intent detection] 
                  → [Knowledge base retrieval] → [Suggested response pushed to agent screen]
                      
[Agent sees: suggested response, next-best-action, relevant knowledge article]
[Agent accepts or ignores suggestion] → [outcome logged for model retraining]
```

### Types of Agent Assist

**1. Knowledge Assist**
- AI surfaces relevant KB articles based on what customer is describing
- Agent clicks "Use This" → KB article sent to customer
- Reduces AHT: 20–45 seconds per interaction

**2. Suggested Responses (Chat/Digital)**
- AI generates response suggestions in real-time
- Agent approves/edits → sends to customer
- Reduces AHT: 15–30 seconds per message

**3. Next Best Action**
- AI recommends next action (transfer, offer, upsell) based on customer context
- Based on business rules + ML model
- Increases upsell/retention: 5–15% improvement in conversion

**4. Real-Time Coaching**
- Supervisor sees real-time dashboard of agent performance
- AI flags when agent needs help (sentiment goes negative, customer on hold too long)
- Supervisor can whisper coach to agent without customer hearing

**5. Post-Call Summary**
- AI generates wrap-up notes automatically
- Agent reviews/edits → saved to CRM record
- Reduces after-call work time: 30–60 seconds per interaction

### Implementation Steps

```
1. Audit knowledge base: is it comprehensive, searchable, up-to-date?
   → If KB is poor, agent assist will be poor
2. Choose vendor: Genesys Agent Assist, AWS Q in Connect, Five9 Agent Assist, custom (Twilio + OpenAI)
3. Integration: connect to your CRM → pull customer context
4. Train the model: labeled interactions + agent feedback
5. Roll out: pilot with 10 agents → measure AHT reduction, CSAT impact
6. Iterate: weekly review of assist accuracy → tune KB + model
```

### AI Coaching Loop

```
[Daily] → Supervisor reviews AI flags: negative sentiment, long hold, escalation risk
            ↓
[Weekly] → 1-on-1 coaching session using real call recordings + AI insights
            ↓
[Monthly] → Calibration: supervisor QA scores vs. AI scores
            ↓
[Quarterly] → Update training program based on top failure patterns
```

---

## SKILL 13: Security and Compliance (PCI, HIPAA)

### Description
Ensure your CCaaS deployment meets the security and compliance requirements for handling sensitive customer data, especially payment card data (PCI-DSS) and protected health information (PHI/HIPAA).

### PCI-DSS Compliance for CCaaS

**Scope Definition**:
- Cardholder Data Environment (CDE) = systems that store, process, or transmit card data
- Agent desktops that display card data are in scope
- CCaaS platform must be PCI-DSS compliant (most major vendors are)

**Key Requirements**:
| Requirement | CCaaS Implementation |
|---|---|
| R3 — Protect stored cardholder data | Use DTMF masking (customer enters card # via phone keypad, never exposed to agent) |
| R7 — Restrict access to cardholder data | Role-based access control, no agents see full card number |
| R12 — Maintain security policies | CCaaS platform must provide compliance documentation (SOC 2, PCI Attestation of Compliance) |

**DTMF Suppression (Critical)**:
```
Most modern CCaaS: enable "Suppress digits" in IVR design
  → Customer enters card number via phone keypad
  → Digits never logged, never displayed, never accessible to agents
  → Only tokenized value stored (for refund/reconciliation)
  
NICE Nexidia: PCI suppression (redacts audio segments where card numbers are spoken)
```

### HIPAA Compliance for CCaaS

**PHI Scope**:
- Healthcare organizations, insurance, any org handling medical information
- Audio recordings of calls = PHI (if medical info discussed)
- Chat transcripts = PHI

**Required Controls**:
| Control | Implementation |
|---|---|
| Business Associate Agreement (BAA) | Must be signed with CCaaS vendor (not all vendors offer this) |
| Encryption at rest + in transit | TLS 1.2+, AES-256 |
| Access control | RBAC, audit logging of who accessed PHI |
| Data retention/deletion | Define how long call recordings are kept; automatic deletion |
| Incident response | Define breach notification process with vendor |

**CCaaS Vendor HIPAA Readiness**:
- **Genesys**: BAA available for healthcare customers
- **AWS Connect**: BAA available, covered by AWS HIPAA compliance program
- **Five9**: BAA available (verify with their compliance team)
- **Twilio Flex**: BAA available for Flex + Segment (verify scope)
- **NICE CXone**: BAA available for enterprise healthcare

### Compliance Implementation Checklist

```
□ Get SOC 2 Type II report from vendor (annual publication)
□ Get PCI DSS AOC (Attestation of Compliance) from vendor
□ Sign BAA with vendor (HIPAA only)
□ Enable DTMF suppression for all payment interactions
□ Configure data retention policy (auto-delete recordings after X days)
□ Set up audit logging for admin access to CCaaS
□ Implement RBAC: minimum necessary access for agents
□ Encrypt all call recordings in S3 (or equivalent) with KMS
□ Conduct annual security review with vendor account team
□ Document incident response plan with vendor contacts
```

---

## SKILL 14: ROI Calculation Framework

### Description
Build a rigorous business case for CCaaS investment with defensible ROI projections.

### The Full ROI Model

**Step 1: Define the Scope**
```
Project name: [e.g., "Genesys Cloud Migration + AI Implementation"]
Scope: 250 agents, 3 locations, voice + digital channels
Current state: legacy Avaya, no WFM, manual QM
Timeline: 12-month implementation, 36-month ROI analysis
```

**Step 2: Quantify Current Costs**
| Cost Category | Current State | Source |
|---|---|---|
| Agent headcount | $12M/year | Payroll data |
| Platform license | $800K/year | Avaya invoices |
| Hardware (PBX, servers) | $200K/year | CapEx amortized |
| Telecom (DIDs, DID costs) | $150K/year | Telecom invoices |
| Agent turnover cost | $500K/year | HR data (attrition × replacement cost) |
| Escalation cost (repeat calls) | $300K/year | Analytics |
| Total Current Cost | ~$14M/year | |

**Step 3: Project Implementation Costs**
| Cost | Year 1 | Year 2 | Year 3 |
|---|---|---|---|
| Implementation (vendor + SI) | $1.2M | $0 | $0 |
| Hardware (if any) | $200K | $0 | $0 |
| Training | $300K | $100K | $100K |
| Internal resource (FTE) | $400K | $200K | $200K |
| Migration/parallel run | $100K | $0 | $0 |
| **Year Total** | **$2.2M** | **$300K** | **$300K** |

**Step 4: Project Annual Savings (Year 2+ when fully live)**
| Benefit | Calculation | Annual Value |
|---|---|---|
| Agent attrition reduction | 250 agents × 25% attrition → 20% reduction × $10K replacement cost | $125K |
| AHT reduction | 250 agents × 5 min × 1M calls/year = 2.5M min @ $0.35/min | $875K |
| FCR improvement (avoided escalations) | 10% FCR improvement × 1M calls × $5 cost/escalation | $500K |
| Reduced IVR failures (AI bot handles) | 30% of calls → AI bot resolves → agent time saved | $600K |
| WFM optimization (reduce overtime) | 10% overtime reduction | $200K |
| Hardware elimination (PBX) | Eliminate legacy hardware + maintenance | $200K |
| Telecom savings | Switch to VoIP (CCaaS included) | $80K |
| **Total Annual Savings** | | **$3.58M/year** |

**Step 5: Calculate ROI**
```
3-Year Net Benefit = (Annual Savings × 3) - Total Implementation Cost
                   = ($3.58M × 3) - $2.8M = $10.74M - $2.8M = $7.94M net

3-Year ROI = $7.94M / $2.8M = 284%

Payback Period = $2.8M / $3.58M = 9.4 months
```

**Step 6: Build Sensitivity Analysis**
```
Scenario A (Conservative): savings 70% of projection → payback = 13 months
Scenario B (Base case):     savings 100% of projection → payback = 9.4 months
Scenario C (Aggressive):    savings 130% of projection → payback = 7 months
```

### ROI Confidence Factors
- **High confidence**: attrition reduction, hardware elimination, telecom savings
- **Medium confidence**: AHT reduction, WFM optimization
- **Lower confidence**: bot resolution rates, FCR improvement (depends on implementation quality)

---

## SKILL 15: Migration Planning from Legacy to CCaaS

### Description
A proven methodology for migrating from legacy on-premise contact center platforms (Avaya, Cisco, Genesys Enterprise, NICE) to modern CCaaS with minimal disruption and maximum data preservation.

### Migration Phases

**Phase 0: Discovery (Weeks 1–4)**
```
□ Inventory all current contact flows (IVR, routing, queues)
□ Document all integrations (CRM, WFM, recording, telephony)
□ Map agent workflows and agent desktop configurations
□ Capture current KPIs (AHT, SL, FCR, CSAT) as baseline
□ Identify "not-to-migrate" flows (edge cases that will stay on legacy)
□ Assess change management readiness
```

**Phase 1: Planning (Weeks 5–8)**
```
□ Choose migration strategy:
  - "Big Bang": migrate all at once (low risk of migration confusion, high cutover risk)
  - "Phased by queue": migrate queue by queue (most common, lower risk)
  - "Parallel run": run both platforms for 60–90 days (safest, most expensive)
  
□ Select CCaaS platform → sign contract → get implementation team assigned
□ Design target state: map legacy flows → CCaaS contact flows
□ Build integration architecture (CRM, WFM, recording connections)
□ Plan pilot: select 1 queue (50–100 agents) for pilot
□ Define go/no-go criteria for pilot
```

**Phase 2: Build (Weeks 9–20)**
```
□ Build CCaaS tenant: configure queues, routing, IVR, agent profiles
□ Build contact flows in new platform (map from legacy flows)
□ Configure integrations: CRM screen pop, WFM, recording, SIP trunking
□ Build agent desktop: softphone, CRM integration, knowledge base access
□ UAT: test all flows with IT team, then business users (test accounts)
□ Resolve all UAT issues before pilot launch

Step-by-step CCaaS build:
1. Core config: queues, agents, routing profiles
2. IVR/Contact flows: import legacy flow logic
3. Integrations: CRM, WFM, recording
4. AI features: agent assist, Contact Lens/analytics
5. Training: run parallel training for agents
6. Pilot: 50–100 agents, 1–2 queues, 4-week run
```

**Phase 3: Pilot (Weeks 21–24)**
```
□ Run pilot: selected queue runs on CCaaS, others on legacy
□ Monitor daily: AHT, SL, CSAT, FCR vs. baseline
□ Collect agent feedback: UX issues, integration gaps, knowledge gaps
□ Run agent satisfaction survey: is new platform better or worse?
□ Weekly steering committee: review metrics, decide on go/no-go
□ At 4 weeks: if metrics are at or above baseline → proceed to rollout
□ If metrics below baseline → extend pilot, fix issues, re-test
```

**Phase 4: Rollout (Weeks 25–40)**
```
□ Queue-by-queue migration (most common approach)
□ Migrate 2–3 queues per week
□ Run parallel for 2 weeks per queue: both platforms handle same queue
□ After parallel period: deprecate legacy queue config
□ Weekly migration review: issues, lessons learned, pace adjustment

Rollout sequence:
1. Week 1: Low-complexity queues (billing, general inquiries)
2. Week 3: Moderate-complexity queues (sales, support tier 1)
3. Week 5: Complex queues (technical support, VIP)
4. Week 7+: Legacy routing → CCaaS routing (100% complete)
```

**Phase 5: Optimization (Post-Launch, Weeks 40+)**
```
□ Run 30/60/90 day reviews against baseline KPIs
□ Optimize contact flows: reduce transfers, improve self-serve rate
□ Tune AI: improve bot resolution rate with real-world data
□ Expand WFM/QM: enable full WFM now that platform is stable
□ Review and close integration gaps identified during pilot
□ Annual review: 12-month ROI validation against business case
```

### Legacy Data Migration

```
Customer data: migrate from legacy CRM → current CRM (existing system)
  → No change to CRM required, just new CCaaS integration
  
Call recordings: 
  → Option A: migrate historical recordings (expensive, limited value)
  → Option B: archive on legacy system, access via link in CRM
  → Recommended: Option B for recordings > 12 months old
  
Agent history/performance data:
  → Migrate last 12 months of performance data to new WFM
  → Older data: archive, accessible via legacy system
  
IVR flows:
  → Map legacy flow logic to CCaaS contact flow builder
  → Document edge cases with legacy team
  → Test with real customer data in test environment
```

### Migration Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Agent adoption failure | Medium | High | Parallel training, agent ambassadors, early UX feedback loop |
| Integration failures (CRM) | High | High | Build and test all integrations in pilot phase |
| Call quality issues (VoIP) | Medium | High | Quality gates: test VoIP MOS score before cutover; run parallel 2 weeks |
| AHT spike during migration | High | Medium | Extended coaching period, mentor support, 1-on-1 check-ins |
| Scope creep (AI features) | Medium | Medium | Lock scope 8 weeks before pilot; no scope changes during pilot |
| Vendor delivery delays | Medium | High | Weekly vendor steering meeting; escalation path defined upfront |

### Migration Success Criteria
| Criteria | Target |
|---|---|
| Pilot SL (Service Level) | ≥ 80% within 4 weeks |
| Agent satisfaction | ≥ 3.5/5 vs. legacy ≥ 3.0/5 |
| AHT deviation from baseline | < 10% increase during pilot |
| CRM integration success rate | ≥ 99% screen pop success |
| Go/No-Go decision | Week 24 |

---

*Built: April 2026 — CX/CCaaS Specialist Agent v2*
*Sources: GitHub research, vendor documentation, industry frameworks, analyst reports*