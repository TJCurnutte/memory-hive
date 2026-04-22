# Industry Analysis Research — v3
> Autonomous research run | Research-Analyst agent | ra-b1 subagent

---

## SECTION 1 — PORTER'S FIVE FORCES (2025–2026 Deep Dive)

### 1.1 Threat of New Entrants

**Barriers to Entry (High):**
- Capital intensity: Deep-tech & AI-adjacent sectors require $50M–$500M seed rounds to compete
- Network effects: Winner-take-all dynamics in SaaS, marketplaces, and AI platforms lock out newcomers
- Regulatory moats: Healthcare (HIPAA), FinTech (SOC2, PCI-DSS), and defense require costly compliance certs
- Talent wars: ML/AI engineers command 2–4x salary premiums vs. traditional SWE; talent scarcity is structural

**Low Barriers in:**
- Low-code/no-code tooling democratizing SaaS creation
- Open-source AI models (LLaMA, Mistral, Gemma) enabling near-zero-cost entrants in AI applications
- Agentic AI reducing the cost of software development by 60–80% (McKinsey, 2025)

**Score: 4/5 — Threat is HIGH** (AI lowering barriers at the app layer, but incumbents hold data + distribution)

---

### 1.2 Bargaining Power of Suppliers

**Concentration:**
- Cloud infrastructure: AWS, Azure, GCP hold ~67% combined market share (Synergy Group, Q4 2025)
- GPU supply: NVIDIA controls ~80% of AI training GPU market; H100/B100 allocation a strategic constraint
- Enterprise software: SAP, Salesforce, Oracle dominate with embedded switching costs

**Countervailing Forces:**
- Multi-cloud adoption: 78% of enterprises now use 2+ cloud providers (Flexera 2025)
- Open-source AI: Reduced dependency on proprietary model vendors
- Sovereign clouds: Government/military clouds in EU, India, China creating alternative supplier ecosystems

**Score: 3.5/5 — Supplier power is SIGNIFICANT but fragmenting**

---

### 1.3 Bargaining Power of Buyers

**Shifts:**
- SaaS consolidation: Buyers using 120+ SaaS tools on average; vendor fatigue drives buying power up
- AI transparency demands: Buyers now require model cards, bias audits, data lineage
- Procurement automation: eProcurement platforms auto-screening vendors, compressing margins

**Enterprise vs. SMB Split:**
- Enterprise buyers: High switching costs, relationship leverage
- SMB: Self-serve, price-sensitive, churn-driven

**Score: 4/5 — Buyers have HIGH power, especially for commoditized tools**

---

### 1.4 Threat of Substitutes

**Top Substitution Vectors (2026):**
1. AI agents replacing professional services (legal, accounting, consulting)
2. Open-source software replacing commercial licenses
3. No-code tools replacing custom development
4. Embedded finance replacing traditional banking
5. Decentralized protocols replacing centralized intermediaries

**Uncertainty:** Regulation of AI (EU AI Act 2025, US executive orders) may slow substitution in regulated sectors

**Score: 4.5/5 — Threat of substitutes is VERY HIGH; AI is the great substitute machine**

---

### 1.5 Industry Rivalry

**Key Trends (2025–2026):**
- AI infrastructure wars: NVIDIA vs. AMD vs. custom silicon (Google TPU, AWS Trainium, Meta MTIA)
- Model commoditization: API pricing wars; GPT-4o mini, Claude Haiku, Gemini Flash all sub-$1/M tokens
- Vertical SaaS: Incumbents being displaced by purpose-built AI-native vertical solutions
- Consolidation: M&A wave in cybersecurity, DevOps, and martech (PE and strategic buyers)

**Profit Pools:**
- Highest: AI inference infrastructure, enterprise AI integration
- Medium: Vertical SaaS, data platforms
- Compressing: Horizontal SaaS, generic automation tools

---

## SECTION 2 — REGULATORY ENVIRONMENT (2025–2026)

### 2.1 United States
- **AI Executive Order (2023 → 2025 updates):** Mandatory safety tests for frontier AI models (>10^26 FLOP); voluntary commitments → potential mandatory reporting
- **State-level AI laws:** Colorado AI Act (2024, effective 2026), Illinois AI video interview law, NYC automated employment decision tool law
- **Sector-specific:** FDA AI/ML-based Software as Medical Device (SaMD); FTC guidelines on AI-generated reviews and endorsements
- **Antitrust:** DOJ/FTC scrutiny of AI partnerships (Microsoft/OpenAI, Amazon/Anthropic) under 2023 merger guidelines

### 2.2 European Union
- **EU AI Act (2024, phased implementation 2025–2026):** Risk-based classification; GPAI systemic risk tier (>10^25 FLOP); conformity assessments; black-box prohibition in high-risk applications
- **Digital Markets Act (DMA):** Designating tech gatekeepers (Google, Meta, Apple, Amazon); interoperability mandates
- **Data Act (2024):** B2B data sharing rights; IoT device data portability

### 2.3 Other Jurisdictions
- **UK:** Pro-innovation AI governance; no AI Act (post-Brexit divergence); ICO AI guidance
- **China:** Generative AI Regulations (2023); generative content watermarking; algorithm recommendation rules
- **India:** Digital India AI Mission ($1.2B); upcoming AI regulation framework (2025–2026)
- **Brazil:** AI legal framework bill (PL 2338/2023); LGPD (data protection) enforcement

### 2.4 Regulatory Risk Matrix

| Jurisdiction | AI-Specific Law | Data Privacy | Sector Reg | Compliance Burden |
|---|---|---|---|---|
| USA | Medium (sector/state) | Moderate (CCPA/CPRA) | High (health/finance) | Medium |
| EU | HIGH (AI Act) | HIGH (GDPR) | HIGH | Very High |
| UK | Low | HIGH | Medium | Medium |
| China | HIGH | HIGH | HIGH | Very High |
| India | Medium (emerging) | Medium | Low | Low-Medium |
| Brazil | Medium | HIGH (LGPD) | Medium | Medium |

---

## SECTION 3 — MARKET SIZE & GROWTH (2025–2026)

### 3.1 AI Market
- Total AI market: $184B (2024) → $327B (2025) → $438B (2026 est.) — Gartner
- Generative AI: $36B (2024) → $100B+ (2026 est.)
- AI chips: $78B (2025) → $117B (2027 est.) — McKinsey

### 3.2 SaaS
- Global SaaS market: $272B (2025) → $335B (2027)
- AI-integrated SaaS growing at 28% CAGR vs. traditional SaaS at 12%

### 3.3 Cybersecurity
- Global cybersecurity market: $212B (2025) → $298B (2028)
- AI-driven security tools capturing 40% of new enterprise security budget

---

## SECTION 4 — COMPETITIVE DYNAMICS & KEY PLAYERS

### 4.1 AI Infrastructure Layer
| Player | Strength | Weakness |
|---|---|---|
| NVIDIA | GPU dominance, CUDA ecosystem | Supply constraints, geopolitical risk |
| AWS | Distribution, breadth | Complexity, cost |
| Azure | Enterprise + OpenAI integration | Open source ambivalence |
| Google Cloud | TPUs, Search moat | Organizational friction |
| Anthropic | Safety brand, Claude quality | Revenue scale vs. OpenAI |

### 4.2 AI Application Layer (Emerging Winners)
- **Perplexity, Arc Search:** Challenging Google search monopoly
- **Harvey, Casetext:** Legal AI taking share from BigLaw
- **Glean, Writer:** Enterprise knowledge + AI writing
- **Cognition, SWE-agent:** Autonomous coding agents

---

## SECTION 5 — INDUSTRY TRENDS & THEMES (2026)

1. **Agentic AI going mainstream:** 2026 = "Year of the AI Agent"; every SaaS embedding agents
2. **Model commoditization + inference wars:** Price per token dropping 10x YoY
3. **AI Regulation materializing:** EU AI Act enforcement begins; US Congress debate active
4. **Sovereign AI:** Nations building domestic AI infrastructure (Saudi Arabia, UAE, India, France)
5. **AI + robotics convergence:** Physical AI emerging (Figure, Tesla Optimus, 1X)
6. **Synthetic data:** Solving training data scarcity for niche domains
7. **Multimodal proliferation:** Video generation reaching parity with image (Sora, Veo, Runway Gen-3)
8. **Enterprise AI governance:** Board-level AI risk mandates; CIO/CISO accountability

---

## SECTION 6 — RESEARCH METHODOLOGY NOTES

- **Sources consulted:** Gartner, McKinsey, Forrester, Synergy Research, IDC, Flexera, CB Insights, Crunchbase, EU AI Act official text, US EO 14110 updates, NIST AI Risk Management Framework
- **Web search strategy:** Cross-referenced analyst firm forecasts vs. primary regulatory documents; triangulated with startup funding data (PitchBook, Crunchbase)
- **Confidence levels:** Market size estimates = Medium (high analyst variance); regulatory = High (primary sources); competitive dynamics = Medium (rapidly evolving)

---

*ra-b1 | Industry Analysis | Research-Analyst agent | 2026-04-22*
