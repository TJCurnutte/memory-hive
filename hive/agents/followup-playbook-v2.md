# SDR-2 Follow-Up Playbook v2
**Session:** sdr-2 | **Date:** 2026-04-22 | **Agent:** SDR-Beta subagent  
**Sources:** GitHub repos, Salesforce, Sales Process Engineering literature, CRO science

---

## SKILL 1: FOLLOW-UP CADENCE

### The Optimal Multi-Touch Sequence
**Structure:** 5–7 touches across 3+ channels in 21 days

| Touch | Channel | Timing | Message Goal |
|-------|---------|--------|-------------|
| 1 | Email | Day 0 | Value-driven intro + CTA |
| 2 | Email | Day 2 | Social proof / case study |
| 3 | LinkedIn | Day 4 | Mutual connection or insight |
| 4 | Email | Day 7 | Different angle / new pain point |
| 5 | Voicemail | Day 10 | Short, specific reference |
| 6 | Email | Day 14 | Break-up email / final offer |
| 7 | LinkedIn DM | Day 18 | Direct ask |

### Cadence Rules
- **Never follow up more than once per channel per 48 hours**
- **Pause 5–7 days between touches** — don't spam
- **Use "reply" vs "new" email threading** for higher open rate
- **Send emails Tue–Thu, 8–10am or 2–4pm local time**
- **Log every touch in CRM** — track the sequence for pattern analysis

### GitHub Auto-Cadence Tools
- `mohamedhanyerp-byte/google-sheets-follow-up-automation` — Google Sheets-based sequence tracker with auto-reminders
- `bdevz/meeting-follow-up-automation` — Slack + email auto-follow-up
- `taylorshelp22/lead-capture-follow-up-automation` — real-time trigger-based follow-up

---

## SKILL 2: CHANNEL SWITCHING

### When to Switch Channels
| Signal | Channel to Switch To |
|--------|---------------------|
| No email reply (2x) | LinkedIn connection request |
| LinkedIn ignored | Cold call / voicemail |
| Voicemail no return | SMS (mobile number found) |
| Stalled >14 days | Re-engagement email with new angle |
| Budget quarter-end | Urgency-tied outreach |

### Channel Hierarchy (response rates)
1. **LinkedIn DM** → 3–5x response rate vs. cold email
2. **SMS** → highest open rate (~98%) but use sparingly
3. **Email** → baseline; best for long-form value
4. **Voicemail** → high effort but signals persistence

### Multi-Channel Setup (from b2b-sdr-agent-template)
- WhatsApp + Telegram + Email = 3-channel parallel SDR
- Use CRM to log all channel interactions in one timeline
- Tag each touch with: channel, message type, sentiment, response status

---

## SKILL 3: URGENCY CREATION

### Urgency Triggers That Actually Work
1. **Budget cycle** — "Quarter-end allocation"
2. **Organizational change** — "New initiative starting Q2"
3. **Competitive threat** — "Your competitor just announced X"
4. **Limited availability** — "Only 2 spots left this cohort"
5. **Price change** — "Pricing increases after [date]"
6. **Mutual connection** — "I saw you connected with [mutual]"

### Urgency Language Templates
- "Most teams in your situation see ROI within 30 days — if we start now"
- "We're opening only 5 spots for this implementation wave"
- "Our Q2 calendar fills 2 weeks ahead — booking now locks current pricing"
- "Before your fiscal planning cycle closes, can we schedule 20 minutes?"

### Rules
- **Never manufacture false urgency** — it destroys trust
- **Tie urgency to real events** — budget cycles, fiscal years, product launches
- **Use sparingly** — 1 urgency trigger per sequence max

---

## SKILL 4: SOCIAL PROOF TACTICS

### Social Proof Stack (by effectiveness)
1. **Named case study** — "Acme Corp (500 employees, FinTech) saw 40% reduction in churn"
2. **Named testimonial** — Direct quote with name, title, company
3. **ROI statistic** — "Customers average $X ROI in 90 days"
4. **Logo wall** — Company logos (without quote)
5. **Analyst mention** — "Recognized by Gartner as a Cool Vendor"
6. **News/PR mention** — "As covered in TechCrunch"

### How to Use Social Proof in Sequences
- Touch 2 email: Include 1-sentence case study
- LinkedIn connection note: "We work with [industry] leaders like [Company]"
- Proposal stage: Full case study PDF with similar prospect profile
- Objection response: "Similar company [X] faced this — here's how they solved it"

---

## SKILL 5: OBJECTION REBUTTAL

### Top 5 B2B Objections + Rebuttals

**1. "Not a priority right now"**
→ "Totally understand. What's driving the timing for the decision later this year? I want to make sure we connect when it's most useful."
*(Find the real timeline, add value in the meantime)*

**2. "Too expensive"**
→ "Fair concern. Let's look at it differently — compared to the cost of [problem they're solving], what's the ROI threshold that would make this a yes?" 
*(Reframe from cost to value)*

**3. "Need to talk to my team"**
→ "Absolutely. Can I ask — what would you need to present to make this a confident recommendation? I'll put together a one-pager that makes that easier."
*(Empower them to sell internally)*

**4. "We're already working with [competitor]"**
→ "Makes sense — most teams do at some point. I'd love to show you one thing [competitor] doesn't do — would 10 minutes give you enough to evaluate?" 
*(Differential hook, low-commitment ask)*

**5. "Send me an email"**
→ "Happy to. Quick question — what's the single most important thing you'd want to know before considering a change?" 
*(Qualify + deliver targeted value)*

---

## SKILL 6: CLOSING TECHNIQUES

### The 4 High-Probability Closes

**1. Assumptive Close** (when momentum is high)
> "Great — looks like we're aligned on the scope. I'll get the SOW drafted. Who needs to sign off?"

**2.微Commit + Expand Close** (when they're hesitating)
> "On a scale of 1–10, how interested are you right now? [If 6+] What would it take to get you to an 8 or 9?"

**3. Timeline Close** (when budget/quarter is relevant)
> "If we can get this signed by [date], we can deliver it before your fiscal year ends — which means you capture [benefit] this cycle."

**4. Next Step Close** (when stuck at "maybe")
> "I'd love to get 20 minutes on [date] to walk through the implementation plan. Should I send a calendar invite?"

### Close Signals to Watch For
- "What would it take to get started?"
- "How soon can you implement?"
- "Who else needs to be involved?"
- Budget or timeline mentioned in conversation
- Repeated "yes" responses to value questions
- Specific questions about pricing/contract terms

---

## SKILL 7: PIPELINE HYGIENE

### Daily CRM Habits
- **Log every touch** within 24 hours — no exceptions
- **Update deal stage** when criteria are met
- **Add notes** with key conversation points (use buyer keywords for future AI analysis)
- **Score each lead** 1–100 on every interaction

### Weekly Pipeline Review (30 min)
1. **Stale deal audit** — Any deal >21 days without activity? Re-engage or archive
2. **Stage conversion check** — Are deals moving? Where's the bottleneck?
3. **Forecast accuracy** — Did last week's predictions hold?
4. **Gap analysis** — What's missing to hit quota? What needs more pipeline?
5. **Activity ratio check** — Do deals have 5–7 touches in active stages?

### Pipeline Coverage Rules
- **Maintain 3–4x quota in pipeline** at all times
- **Stage-weighted pipeline** — later-stage deals weighted higher
- **Leads without activity for 7 days** → trigger re-engagement sequence
- **Deals stuck >30 days** → escalate or archive — don't let them rot

### GitHub Pipeline Tools
- `nash-md/meow` — Free pipeline manager with auto-forecast
- `staff0rd/salesforce-pipeline` — Salesforce pipeline visualization
- `RichM1216/react-native-crm` — Mobile CRM for iOS/Android
- `KlementMultiverse/ai-crm-agents` — AI agent–driven pipeline management

---

## SKILL 8: AI-DRIVEN SALES OPTIMIZATION (Practical Stack)

### Immediate Actions
1. **Set up lead scoring** — Weight: authority (25pts) + need (25pts) + budget (25pts) + timeline (25pts)
2. **Auto-tag email responses** — Positive/negative/neutral sentiment for next action routing
3. **Trigger sequences on behavior** — Page visit, email open, LinkedIn view = automated touch
4. **Use AI to draft** — Let AI generate first draft of emails, then personalize manually

### AI Tools for SDRs
| Task | GitHub Tool | Purpose |
|------|-----------|---------|
| Lead scoring | `VishalKumar-S/Sales_Conversion_Optimization_MLOps_Project` | H2O AutoML scoring model |
| Email sequences | `csg09/AI-Sales-Automation-Agent` | OpenAI agentic multi-email |
| Follow-up automation | `noman-ai-workflows/AI-Lead-Qualification__Follow-Up-Automation` | AI + auto-follow-up |
| CRM agent | `KlementMultiverse/ai-crm-agents` | 6-agent autonomous CRM |
| Pipeline analytics | `sotirisspyrou-uk/growth-experiment-framework` | A/B testing + CRO |

---

## SKILL 9: DEAL VELOCITY OPTIMIZATION

### Velocity Formula
```
Pipeline Velocity = (Deals in Stage × Win Rate × Avg Deal Size) / Length of Sales Cycle
```

### 5 Levers to Increase Velocity
1. **Shorten time-to-response** — Reply within 5 minutes of inbound inquiry
2. **Accelerate qualification** — Use BANT aggressively; disqualify fast
3. **Add channel pressure** — Use 3 channels simultaneously on stalled deals
4. **Escalate authority contact** — Ask for 15-min "alignment call" with decision-maker
5. **Use urgency anchors** — Tether every ask to a real deadline

### Quick Wins
- Respond to every inbound lead within 5 minutes
- Send intro video Loom with first email (increases reply rate 3x)
- Include calendar link in every email (reduces back-and-forth by 2+ touches)
- Personalize subject lines with company name or contact's name

---

## SKILL 10: SOCIAL LISTENING & TRIGGER-BASED OUTREACH

### Real-Time Signals That Trigger Action
| Signal | Action |
|--------|--------|
| Prospect posted on LinkedIn about a problem | Immediate DM with relevant insight |
| Company announced funding | Congrats message + "ready to help scale" |
| New hire in their team | Intro email referencing org change |
| Job posting for relevant role | "I see you're building a [role] team — happy to share how others solved that" |
| Conference attendance | Connect with relevant session insight |
| Company press release | Reference it in follow-up (shows you did your homework) |

### Tools for Signal Detection
- Google Alerts (company + industry keywords)
- LinkedIn Sales Navigator (trigger alerts)
- Crunchbase (funding events)
- Crunchbase company updates
- Twitter/X monitoring for industry keywords

---

## SKILL 11: EMAIL WRITING FOR SDRs

### High-Performance Email Anatomy
1. **Subject Line** — Personalized, under 50 chars, creates curiosity or urgency
2. **Opener** — Reference them specifically (company, post, mutual, pain)
3. **Hook** — 1–2 sentences on their likely challenge
4. **Proof** — Social proof or data point (credibility)
5. **Soft CTA** — Low-commitment next step
6. **Signature** — Name + title + company + calendar link

### Subject Line Formulas That Work
- "[Company] + [outcome]" — e.g., "How [Company] cut churn 30%"
- Question format — "Is [problem] still slowing [Company] down?"
- Peer reference — "Quick question from a [Company] neighbor"
- Curiosity gap — "The 1 thing most [role]s miss about [topic]"
- Calendar ask — "25 min to show you what we built for [Company]?"

---

## SKILL 12: LINKEDIN OUTREACH

### Connection Request Templates
**For cold (no prior contact):**
> "Hi [Name] — I help [industry] teams solve [problem]. Would love to connect."

**For warm (common connection/content):**
> "Hi [Name] — I noticed your post on [topic]. Strong take. Would love to connect and share what's working for [similar companies]."

### InMail Formula
1. Reference something specific about them (post, update, role)
2. State the insight or value you'll share
3. Make 1 specific, low-commitment ask
4. Include calendar link

---

## SKILL 13: OBJECTION PREVENTION (Proactive Framing)

Prevent objections before they happen by addressing them proactively:

| Likely Objection | Pre-emptive Move |
|-----------------|-----------------|
| "We don't have budget" | Mention flexible pricing/payment options in initial email |
| "Need to talk to team" | Offer to join their team meeting as a resource |
| "Not a priority" | Connect solution to their stated Q1/Q2 goals in intro |
| "Too busy" | Offer 15-min "quick pulse call" instead of full demo |
| "Already have a solution" | Ask what they like about current solution before comparing |

---

## SKILL 14: CRM DATA ENRICHMENT

### Enrichment Sources (Free/Paid)
- **Clearbit Connect** (Gmail plugin) — company + contact data
- **Hunter.io** — email finder + domain search
- **Apollo.io** — full B2B database + enrichment
- **LinkedIn Sales Navigator** — org charts, contact data
- **ZoomInfo** — detailed firmographic data
- **Crunchbase** — funding, growth stage, headcount trends

### Enrich Before Every Sequence
1. Verify job title, company, funding stage
2. Confirm email format (hunter.io pattern)
3. Check LinkedIn for recent activity
4. Look for trigger events in past 90 days
5. Verify tech stack if relevant (for competitive intel)

---

## SKILL 15: METRICS-DRIVEN SDR MANAGEMENT

### Weekly Scorecard
| KPI | This Week | Target | Delta |
|-----|-----------|--------|-------|
| Leads Contacted | | | |
| Replies Received | | | |
| Calls Booked | | | |
| Show Rate (%) | | | |
| Meetings Held | | | |
| Opps Created | | | |
| Pipeline Generated | | | |

### Conversion Funnel Math
- 100 cold emails → 4% reply rate → 4 replies
- 4 replies → 50% qualify rate → 2 qualified leads
- 2 qualified → 50% demo rate → 1 demo booked
- 1 demo → 30% close rate → 0.3 deals
- **Required:** 334 emails/week to close 1 deal (adjust for your industry benchmarks)

### Activity Benchmarks
- Cold emails/day: 50–100 (depending on tooling/sequence)
- Calls made/day: 20–40
- LinkedIn touches/day: 10–20
- Book 3–5 demos/week to hit quota (varies by ACV)

---

*End of Follow-Up Playbook v2 — compiled 2026-04-22*
*15 skills built. Ready for operational use.*
