# Competitive Intelligence Research Guide v3
*Research-Analyst — Subagent 1 | Competitive Intelligence*

---

## 1. Introduction: What Is Competitive Intelligence?

Competitive Intelligence (CI) is the systematic process of gathering, analyzing, and acting on information about competitors, market dynamics, and external forces that affect an organization's strategic position. Unlike corporate espionage—which is illegal and unethical—CI is a legitimate discipline that uses **publicly available information** to support decision-making. CI is foundational for sales teams, product managers, executives, and investors who need to understand what their competitors are doing, why, and how to respond.

---

## 2. Competitive Analysis Frameworks

### 2.1 Porter's Five Forces
Michael Porter's framework remains a cornerstone of competitive analysis. It examines five forces that shape industry competition:
1. **Threat of New Entrants** — How easy is it for new players to enter the market?
2. **Bargaining Power of Buyers** — How much leverage do customers have?
3. **Bargaining Power of Suppliers** — How much leverage do suppliers have?
4. **Threat of Substitute Products** — What alternatives exist?
5. **Rivalry Among Existing Competitors** — How intense is direct competition?

**Application**: Use this to assess industry attractiveness and identify where competitive pressure is highest.

### 2.2 SWOT Analysis
Strengths, Weaknesses, Opportunities, Threats. Classic but powerful:
- **Strengths/Weaknesses** are internal (your company vs. competitors)
- **Opportunities/Threats** are external (market shifts, regulatory changes)

**Application**: Build a 2×2 matrix. Map competitors against each quadrant to spot where they are vulnerable and where you have advantage.

### 2.3 Value Chain Analysis
Introduced by Porter (1985), this decomposes a company's activities into primary and support activities to identify sources of competitive advantage:
- **Primary**: inbound logistics, operations, outbound logistics, marketing/sales, service
- **Support**: firm infrastructure, human resources, technology development, procurement

**Application**: Compare your value chain against competitors to spot cost advantages or differentiation opportunities.

### 2.4 Strategic Group Mapping
Plot competitors on two dimensions (e.g., price vs. geographic scope) to identify clusters of similar competitors. This reveals which players truly compete with each other and which operate in different niches.

### 2.5 Blue Ocean Strategy
Instead of competing in "red oceans" (血腥竞争), create uncontested market space. Key tools:
- **Eliminate-Reduce-Raise-Create Grid**: systematically evaluate which factors to eliminate, which to reduce below industry standard, which to raise above standard, and which to create that the industry has never offered.
- **The Four Actions Framework**: Ask what factors should be eliminated, reduced, raised, and created.

### 2.6 BCG Matrix (Growth-Share Matrix)
Classify products/business units as Stars, Cash Cows, Question Marks, or Dogs based on market growth rate and relative market share. Useful for portfolio-level competitive analysis.

### 2.7 The 3C Analysis (Company-Customers-Competitors)
A Japanese framework (also called the "Strategic Triangle") that analyzes the balance between what your company can do, what customers want, and what competitors are doing. Popular in Japanese strategy consulting.

---

## 3. Reading SEC Filings for Competitive Intelligence

SEC filings are a goldmine of public competitive intelligence, especially for public companies.

### 3.1 Key SEC Documents to Monitor

| Filing | What It Reveals |
|--------|----------------|
| **10-K (Annual Report)** | Business overview, risk factors, competition sections, legal proceedings, financial statements |
| **10-Q (Quarterly Report)** | Quarterly performance, recent developments |
| **8-K (Current Reports)** | Material events, earnings announcements, leadership changes, acquisitions |
| **DEF 14A (Proxy Statement)** | Executive compensation, governance, insider holdings |
| **S-1 / S-11 (IPO Prospectus)** | Business model, market sizing, competitor disclosures, use of proceeds |
| **13F (Quarterly Holdings)** | Institutional investor holdings — shows what smart money is betting on |
| **Form 4 (Insider Trading)** | Executive and director trades — can signal confidence or lack thereof |
| **424B (Prospectus Filings)** | Pricing of new offerings, often with competitive context |
| **Form SC 13D/G** | Beneficial ownership reports (5%+ holders) |

### 3.2 How to Extract Competitive Intel from 10-Ks

**Step 1: The "Competition" Section**
Most 10-Ks have a "Business" section with a dedicated competition paragraph. Look for:
- Who they name as competitors
- How they describe their competitive advantages
- What they consider barriers to entry

**Step 2: Risk Factors (Item 1A)**
The risk factor section is gold. Companies are legally required to disclose material risks. Look for:
- Competitors they mention as threats
- Market trends threatening their position
- Regulatory risks that could shift competitive dynamics

**Step 3: MD&A (Management's Discussion & Analysis)**
Look for:
- Revenue breakdowns by segment → who are their most important customer groups
- Geographic mix → where are they winning vs. losing
- Pricing dynamics → are they gaining or losing pricing power
- Acquisition strategy → how are they building moats

**Step 4: Financial Statements & Notes**
- Revenue concentration (are they dependent on one customer/segment?)
- Gross margin trends → competitive pricing pressure
- R&D spending → innovation investment levels
- Segment profitability → which business lines are driving value

### 3.3 EDGAR Search Tips

- Use SEC EDGAR (https://www.sec.gov/cgi-bin/browse-edgar): Search by company name, CIK, or form type
- Set up RSS feeds or alerts for companies in your competitive set
- Compare 10-K competition sections year-over-year — language changes reveal shifts in strategy
- Cross-reference 8-K announcements with news to understand context
- Use `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany` to pull all filings for a specific company

### 3.4 Advanced SEC Analysis

**Word Frequency Analysis**: Compare risk factor language between competitors. Frequent mention of a specific threat (e.g., "cloud-native competitors," "open-source alternatives") signals it's a real concern.

**Competitive Moat Scoring**: From 10-K text, score mentions of: switching costs, network effects, brand, regulatory licenses, IP, scale economics. Track these over quarters/years.

**Management Quality Signals**: Read proxy statements for compensation structure — are executives incentivized on long-term value creation or short-term metrics?

---

## 4. Patent Analysis for Competitive Intelligence

Patents are public documents that reveal where a company is investing in innovation and where it is building legal moats.

### 4.1 Key Patent Databases

- **Google Patents** (https://patents.google.com): Free, comprehensive, with citation mapping
- **USPTO** (https://patents.uspto.gov): Official US patent database
- **WIPO** (https://patentscope.wipo.int): International PCT applications
- **Espacenet** (https://worldwide.espacenet.com): European Patent Office — global coverage
- **Lens.org**: Clean interface, good for citation networks
- **PatSnap / Questel**: Commercial platforms with advanced analytics (enterprise-level)

### 4.2 What to Look For in Patents

**Filing Trends**: A sudden spike in patent filings in a technology area signals heavy investment. Compare filing volumes between competitors.

**Claim Analysis**: The "claims" section defines the legal scope of protection. Read claims broadly — not just the title/abstract.

**Citation Networks**: Who is citing whose patents? This reveals:
- Who is building on a competitor's IP (potential licensing relationships)
- Who is designing around competitor patents
- Key inventors and their movement between companies

**International Filings (PCT)**: A company filing internationally via PCT is signaling global ambitions in that technology.

**Maintenance Fees**: Patents require maintenance fees. A patent going abandoned can signal the technology is no longer strategic.

**Re-exam and IPR (Inter Partes Review)**: Challenges to patents can signal active competitive disputes.

### 4.3 Patent Analysis Workflow

1. Define technology space of interest
2. Search by keyword, IPC/CPC classification codes, or inventor name
3. Filter by assignee (company)
4. Map filing trends over time
5. Analyze claim language for breadth and specificity
6. Build a citation network map
7. Identify key inventors — watch for their movements between companies
8. Flag patents expiring soon (can signal freedom-to-operate opportunities)

### 4.4 Legal Considerations

- **Patent Thickets**: Dense overlapping patent portfolios can create barriers to entry
- **FTO (Freedom to Operate)**: Does your product or service potentially infringe on competitor patents?
- **Patent Trolls**: NPEs (Non-Practicing Entities) that acquire patents for litigation — watch for competitors with portfolios that might be sold to NPEs

---

## 5. War-Gaming Competitor Moves

War-gaming is a structured scenario-planning exercise to anticipate and prepare for competitor moves.

### 5.1 Setting Up a War-Game

**Participants**: Mix of sales, product, strategy, and executive team. Sometimes bring in external advisors for fresh perspective.

**The 3 Horizons Framework**: Consider moves across three time horizons:
- **Horizon 1** (0-12 months): Competitive responses to current moves
- **Horizon 2** (1-3 years): Product/technology shifts
- **Horizon 3** (3-10 years): Market structure changes, new entrants, regulatory shifts

### 5.2 Classic War-Game Formats

**Two-Team War-Game**:
- Team A plays the defender (your company)
- Team B plays the competitor
- Each team proposes moves, the other team responds
- Facilitator judges plausible outcomes

**Multi-Player War-Game**:
- Each competitor gets a team
- Add a "market forces" neutral player
- More realistic for complex markets with 3+ significant players

**Red Team / Blue Team**:
- Blue = your company (defensive, opportunity-finding)
- Red = adversarial (attack-minded, critic)
- Red team specifically tries to find your vulnerabilities
- Classic military exercise adapted for business

### 5.3 The Competitor Move Library

Build a library of potential moves by competitor category:

**Product Moves**:
- New product launches (timing, features, pricing)
- Feature parity or differentiation
- Bundling / unbundling
- Platform plays

**Pricing Moves**:
- Discounting, promotions, freemium tiers
- Subscription changes
- Volume-based pricing shifts

**Go-to-Market Moves**:
- New channel partnerships
- Geographic expansion
- Sales team scaling
- Marketing campaign launches

**M&A / Strategic Moves**:
- Acquisitions
- Joint ventures
- IP licensing deals
- Capital raises (funding rounds, debt)

**Narrative / Perception Moves**:
- Messaging pivots
- Rebranding
- Awards and PR campaigns
- Thought leadership pushes

### 5.4 Red Team Methodology (Advanced)

1. **Assume the Competitor is Rational and Well-Informed**: Give them credit for intelligence
2. **Map Their Constraints**: Budget, technology, talent, regulatory
3. **Find Their Incentives**: What are they optimizing for? (Revenue? Users? Exit?)
4. **Pressure-Test Your Assumptions**: Ask "What if we're wrong about why they did that?"
5. **Identify the Move You Least Expect**: Often the most impactful competitor moves are surprises

### 5.5 War-Game Output

Document:
- **Move Library**: All plausible competitor moves across horizons
- **Impact Assessment**: How badly does each move hurt us?
- **Response Options**: What can we do in response?
- **Early Warning Indicators**: What signals would tell us the competitor is about to make a move?
- **Trigger Criteria**: At what point do we escalate from monitoring to active response?

---

## 6. Building Competitive Battlecards

A battlecard is a structured, actionable intelligence document used by sales teams to win deals against specific competitors.

### 6.1 Battlecard Structure

A battlecard is typically a one-page reference document per competitor. Standard sections:

```
## Competitor: [Name]
## Company Profile
## Product Overview
## Pricing Model
## Key Strengths (what they claim / where they win)
## Key Weaknesses (objections they can't answer)
## Win/Loss Patterns
## Competitive Positioning (our response)
## Talk Tracks (objection handling)
## Proof Points / Case Studies
## Last Updated
```

### 6.2 How to Build Battlecards

**Step 1: Source Collection**
- Win/loss data from CRM (what language did buyers use?)
- Sales team debrief calls and call recordings
- G2 / Capterra / Gartner peer reviews
- Analyst reports
- Direct customer interviews
- Competitive intelligence monitoring

**Step 2: Identify Patterns**
- Look for repeated objections ("They kept mentioning X")
- Note where deals were lost and won
- Identify the "magic moment" — what closed deals

**Step 3: Validate with Customers**
- When you lose a deal, call the prospect. Ask: "What sealed it? What would have changed your mind?"
- Be genuinely curious, not defensive

**Step 4: Write Sharp, Actionable Content**
- Use customer language, not internal jargon
- Make it scannable — sales teams read in 30 seconds between calls
- Update quarterly (at minimum)

### 6.3 Win/Loss Analysis Framework

**Win Analysis**:
- What did we do exceptionally well?
- What did the competitor do poorly?
- What specific capabilities mattered most?
- Who was the economic buyer vs. technical buyer?

**Loss Analysis**:
- What objection did we fail to overcome?
- Was it price, product, relationship, timing?
- What did the winner do that was better?
- Could we have won with different messaging?

### 6.4 Competitive Positioning Matrix

| Criteria | Us | Competitor A | Competitor B |
|----------|-----|-------------|-------------|
| Feature X | ★★★ | ★★ | ★ |
| Feature Y | ★★ | ★★★ | ★★ |
| Pricing | ★★ | ★ | ★★★ |
| Support | ★★★ | ★★ | ★★ |
| Integration | ★★★ | ★ | ★★ |

Use this to guide win/loss analysis and identify white space.

---

## 7. Monitoring and Alerting

### 7.1 Competitive Intelligence Monitoring Stack

**News & Media Monitoring**:
- Google Alerts (keyword + competitor names)
- Mention (brand monitoring)
- Meltwater / Cision (enterprise PR monitoring)
- LinkedIn company updates (follow competitors)
- Crunchbase company updates
- TechCrunch / FierceCN / industry trade press RSS feeds

**Funding & M&A Tracking**:
- Crunchbase Pro alerts
- PitchBook (if available)
- SEC EDGAR RSS feeds
- Dealroom / CB Insights

**Employee & Talent Tracking**:
- LinkedIn hiring trends (spike in hiring in specific area = product investment)
- Glassdoor reviews (weakness signals)
- GitHub activity (for tech companies)

**Patent Monitoring**:
- Google Patents alerts (by assignee)
- Patent Alert services

### 7.2 CI Report Cadence

- **Weekly**: News monitoring digest (15 min scan)
- **Monthly**: Win/loss review, competitor news summary, alert review
- **Quarterly**: Full battlecard refresh, war-game, competitive landscape update
- **Annual**: Strategic planning input, 5-force review, market structure analysis

---

## 8. Ethical and Legal Boundaries

**Do**:
- Use publicly available information
- Interview industry experts (with their consent)
- Analyze public filings, job postings, conference presentations
- Benchmark against public performance data

**Don't**:
- Recruit employees to steal trade secrets
- Intercept confidential communications
- Breach NDAs or confidentiality agreements
- Engage in any activity that violates computer fraud laws

**The CI Professional Code** (SICCI): CI professionals should act within legal, ethical, and moral boundaries, protecting confidential information and not misrepresenting themselves.

---

## 9. CI Tools and Platforms

| Tool | Use Case |
|------|---------|
| **Crunchbase** | Funding, acquisitions, founder history |
| **PitchBook** | Private market data, M&A tracking |
| **Gartner / Forrester** | Analyst research, market context |
| **Owler** | Real-time competitor news, revenue estimates |
| **SimilarTech / BuiltWith** | Technology stack analysis (what tech competitors use) |
| **LinkedIn Sales Navigator** | Track competitor employee growth, org changes |
| **Crayon** | AI-powered competitive intelligence platform |
| **Kompyte** | Automated competitor monitoring |
| **TrustAtlas** | Buyer intent data |

---

## 10. Quick-Reference: Competitive Intelligence Cheat Sheet

1. **Know the 5 frameworks**: Five Forces, SWOT, Value Chain, Strategic Groups, Blue Ocean
2. **Read SEC filings**: 10-K first (competition section, risk factors, MD&A), then 8-K for breaking news
3. **Patent analysis = innovation tracking**: Use Google Patents; track filing trends, citations, inventors
4. **War-game quarterly**: Build move library, red team your assumptions, update early warning indicators
5. **Battlecards are sales tools**: One page per competitor, customer language, update quarterly
6. **Monitor continuously**: News + funding + hiring + patents = full competitive picture
7. **Stay ethical**: Public information only; never misrepresent or steal

---

*Document: competitive-v3.md | Agent: research-analyst | Subagent: competitive-intelligence*
*Last Updated: 2026-04-22*
