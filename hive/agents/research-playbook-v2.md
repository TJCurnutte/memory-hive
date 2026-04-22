# Research Analyst — Research Playbook v2
**Session:** research-analyst | **Date:** 2026-04-22  
**Purpose:** Complete operational playbook for the Research Analyst agent

---

## 15+ Research Skills — Operational Definitions

### SKILL 1: Source Discovery
**Goal:** Find all relevant sources on a topic, not just the obvious ones.

**Methods:**
- Boolean search strings: `("X" OR "Y") AND ("Z" -excluded)` for precision
- Google Scholar: use "cited by" forward chaining + bibliography backward chaining
- Semantic Scholar: AI-assisted relevance ranking
- arXiv: for cutting-edge ML/AI/tech research
- Twitter/X: search by expert accounts + hashtag chains
- Substack / beehiiv: search newsletter archives
- Reddit: r/SideProject, r/entrepreneur, r/startups for real pain points
- Listen Notes: podcast search for audio interviews with experts
- Product Hunt: track new entrants in any space
- AlternativeTo: competitive landscape + user reviews

**Output:** A source list with tiers (primary/secondary/tertiary) and credibility tags.

---

### SKILL 2: Credibility Evaluation
**Goal:** Know before you trust. Rate every source before using it.

**Methods:**
- **CRAAP Test:** Currency (how recent?) → Relevance → Authority (who wrote it?) → Accuracy (can you verify?) → Purpose (what's the agenda?)
- **SIFT Method:** Stop → Investigate the source → Find other coverage → Trace claims back
- **Lateral Reading:** Check what other reputable sources say about the source (Stanford Credibility Lab method — gold standard)
- **Author track record:** h-index, publication history, past predictions
- **Publication venue:** Peer-reviewed > established outlet > self-published > unknown
- **Conflict of interest disclosure:** Check funding, affiliations, commercial interest
- **Source hierarchy tags:**
  - 🟢 Tier 1: Primary sources (original papers, patents, raw data)
  - 🟡 Tier 2: Expert peer-reviewed / original reporting
  - 🟡 Tier 3: Secondary analysis by credible experts
  - 🟠 Tier 4: Curated synthesis / reviews
  - 🔴 Tier 5: General media / summaries
  - ⚫ Tier 6: UGC (user-generated content — caveat emptor)

**Output:** Credibility tag on every source used in a brief.

---

### SKILL 3: Cross-Referencing
**Goal:** Verify accuracy and find the full picture.

**Methods:**
- Backward citation chain: follow bibliography to source papers
- Forward citation chain: "cited by" on Google Scholar
- Snowball sampling: recursively apply both chains
- Domain overlap validation: does source A confirm source B independently?
- Conflicting data point tracking: log contradictions, don't resolve prematurely
- Wikipedia method: read Talk pages to see contested claims

**Output:** Cross-reference log with source links and confirmation status.

---

### SKILL 4: Synthesis
**Goal:** Turn many sources into a coherent, decision-ready understanding.

**Methods:**
- **Progressive Summarization:**
  - L1: Save raw highlights
  - L2: Bold key passages
  - L3: Highlight most important bolded text
  - L4: Write executive summary at top
- **MECE Framework:** Mutually Exclusive, Collectively Exhaustive breakdown
- **First-Principles Breakdown:** Identify axioms, rebuild from there
- **Thesis-Antithesis-Synthesis:** Argued position → counterargument → reconciled position
- **Argument Mapping:** Visual nodes showing claim → evidence → assumption

**Output:** A synthesis document with clear thesis, supporting evidence, and acknowledged gaps.

---

### SKILL 5: Briefing Formats
**Goal:** Deliver the right format for the decision context.

| Brief Type | When to Use | Structure |
|-----------|-------------|-----------|
| **Intelligence Brief** | Fast decision, time-limited reader | 1 page: Situation → Signal → Recommendation |
| **Deep Dive Memo** | Major decision, full analysis needed | Context → Evidence → Analysis → Recommendation → Risk |
| **Competitive Brief** | Landscape assessment | Players → Positioning → Gaps → Moats |
| **Market Brief** | Sizing + trends | TAM/SAM/SOM → Segments → Trends → Trajectory |
| **Thesis Brief** | Invest in a view | Thesis → Evidence → Counter-evidence → Conviction level |
| **FAQ Brief** | Fast reference | Q → A → Confidence level per answer |

**Output:** Formatted brief matching the requester's decision context.

---

### SKILL 6: Data Visualization
**Goal:** Make patterns visible, not just describable.

**Methods:**
- **Comparison matrices:** feature × competitor grid, color-coded gaps
- **2x2 positioning maps:** x-axis vs y-axis (e.g., quality vs price, simplicity vs power)
- **Timeline / roadmap:** market evolution, technology adoption S-curves
- **Market landscape maps:** cluster map of players by category + size
- **Funnel / conversion visualizations:** pipeline analysis
- **Network graphs:** co-citation networks, relationship maps
- **Stacked bar / bubble chart:** market share + growth rate combined

**Tools:** Markdown tables for simple, Mermaid diagrams for flowcharts, or direct image generation.

---

### SKILL 7: Competitive Analysis
**Goal:** Understand the full competitive landscape and where moats exist.

**Steps:**
1. Identify direct competitors (same job-to-be-done)
2. Identify indirect competitors (alternative solutions)
3. Build feature comparison matrix
4. Run pricing benchmarking
5. Synthesize user reviews (G2, Capterra, AppStore reviews)
6. Write competitive positioning statement per competitor
7. Identify moat candidates: network effects, switching costs, brand, IP, distribution, data

**Output:** Competitive landscape brief with positioning map and moat analysis.

---

### SKILL 8: Market Research
**Goal:** Size the opportunity and understand market dynamics.

**Methods:**
- **TAM/SAM/SOM:** Top-down (market reports) + bottom-up (segment × segment)
- **Market trend analysis:** 5-year arc, CAGR, adoption S-curves
- **Customer segmentation:** demographic, psychographic, behavioral, firmographic
- **Win/loss interviews:** structured questions for past customers
- **Survey design:** avoid leading questions, triangulate with behavioral data
- **Trend extrapolation:** look for the meta-trend under the trend

**Output:** Market sizing brief with segmentation and trajectory.

---

### SKILL 9: Interview & Expert Research
**Goal:** Get proprietary qualitative insights from experts.

**Methods:**
- Cold outreach: LinkedIn InMail with specific, valuable framing
- Expert databases: Clarity.fm, Intro.co, Catalant
- Interview question frameworks: STAR (Situation, Task, Action, Result)
- Async audio: TunedIn, Yac, Coschedule for async expert interviews
- Transcription: Whisper API or Temi for audio → text
- Theme extraction: manual coding or LLM-assisted theme clustering

**Output:** Interview notes with key themes and attributed quotes.

---

### SKILL 10: Deep Work Batching
**Goal:** Maximize research quality by batching similar cognitive tasks.

**Methods:**
- **Research sprints:** 2-hour focused blocks, no interruption
- **Morning intelligence:** 20-min daily scan of key topics (feeds, alerts)
- **Synthesis sessions:** separate from gathering, no new sources mid-session
- **Pomodoro research:** 25-min gather → 5-min distill cycle
- **Weekly research review:** update key briefs, retire stale sources

**Output:** Structured research calendar with batched session blocks.

---

### SKILL 11: AI-Assisted Research
**Goal:** Use AI to amplify speed without sacrificing quality.

**Tools:**
- **Perplexity.ai** — rapid sourcing and fact-check
- **Claude/GPT** — synthesis drafting, outline generation, translation
- **Elicit.org** — literature review, abstract extraction
- **Scispace** — paper understanding, Q&A on papers
- **Zotero / Paperpile** — citation management
- **RAG pipelines** — private corpus search for long-term research memory
- **gpt-researcher** — autonomous multi-agent research agent

**Note:** AI is a force multiplier for synthesis, not a replacement for source judgment.

---

### SKILL 12: Document Intelligence
**Goal:** Extract structured data from unstructured documents.

**Methods:**
- **PDF parsing:** pdfminer, PyMuPDF, pdfplumber
- **Web scraping:** BeautifulSoup, Playwright for dynamic pages
- **Table extraction:** tabula-py for PDFs with tables
- **LLM extraction:** prompt-based extraction from PDFs, docs, web pages
- **OCR:** pytesseract for scanned documents

**Output:** Structured data from raw documents, ready for analysis.

---

### SKILL 13: Information Architecture
**Goal:** Build a research memory system that compounds over time.

**Methods:**
- **Taxonomy design:** folders (projects) + tags (concepts) + links (relationships)
- **Zettelkasten atomic notes:** one idea per note, unique ID, bidirectional links
- **Progressive disclosure:** short summary → expandable detail
- **Search + browse hybrid:** index by keyword, navigate by relationship
- **Version control:** Git-based research notes for changelog and rollback

**Recommended tools:** Obsidian, Logseq, SiYuan, or plain Markdown with git.

---

### SKILL 14: Alert & Monitoring Systems
**Goal:** Stay current on a topic without active searching.

**Methods:**
- **Google Alerts:** keyword monitoring, daily/weekly digest
- **Talkwalker / Brandwatch:** social listening for brands and trends
- **Product Hunt:** track new launches in category
- **Competitor site monitoring:** ChangeTower or visualping for site changes
- **Newsletter digest:** Substack/beehiiv curation of research topics
- **Twitter lists:** curated expert lists for passive intelligence
- **RSS feeds:** Feedly or Inoreader for blog/Podcast monitoring

**Output:** Dashboard of active alerts with last-check timestamps.

---

### SKILL 15: Research Storytelling
**Goal:** Make research compelling and actionable, not just accurate.

**Methods:**
- **Problem → Tension → Resolution arc:** create narrative momentum
- **Data narrative integration:** let data drive the story, not the reverse
- **Visual-first storytelling:** lead with the image/chart, explain in text
- **Audience-specific tailoring:** executive version vs. analyst version vs. technical version
- **Confidence calibration:** label every claim with evidence strength
  - 🔵 High confidence: verified by multiple Tier 1-2 sources
  - 🟡 Medium: single source or Tier 3+, needs validation
  - 🔴 Low: inference or extrapolation, note as hypothesis

**Output:** Research that informs and moves a decision forward.

---

### SKILL 16: Ethical Research Practices
**Goal:** Maintain integrity and avoid common research pitfalls.

**Methods:**
- Source attribution: cite at point of claim, not just at end
- Plagiarism avoidance: paraphrase with link to original
- Perspective diversity: actively seek disconfirming evidence
- Uncertainty acknowledgment: flag where evidence is thin
- Privacy: never include PII in research notes without consent
- Conflicts of interest: disclose any relevant affiliations

---

## Master Research Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: DEFINE THE QUESTION                                │
│  - Specific, constrained research question                  │
│  - Audience and decision context                            │
│  - Output format required                                    │
│  - Deadline                                                 │
├─────────────────────────────────────────────────────────────┤
│  STEP 2: PARALLEL SOURCE DISCOVERY (this is where you spawn)│
│  - Web search (Perplexity, Google)                          │
│  - Academic (Scholar, arXiv, Semantic Scholar)              │
│  - Social (Twitter/X, Reddit, newsletters)                  │
│  - GitHub (tools, code, datasets)                           │
│  - Expert (interviews, outreach)                            │
├─────────────────────────────────────────────────────────────┤
│  STEP 3: CREDIBILITY EVALUATION                             │
│  - Rate each source (Tier 1-6)                             │
│  - Apply CRAAP test or SIFT method                          │
│  - Flag conflicts and gaps                                  │
├─────────────────────────────────────────────────────────────┤
│  STEP 4: CROSS-REFERENCING                                  │
│  - Forward + backward citation chains                      │
│  - Triangulation across 3+ independent sources             │
│  - Track contradictions explicitly                          │
├─────────────────────────────────────────────────────────────┤
│  STEP 5: SYNTHESIS                                          │
│  - Progressive summarization                               │
│  - First-principles breakdown if needed                    │
│  - Thesis statement + supporting evidence                  │
│  - Acknowledged gaps and risks                             │
├─────────────────────────────────────────────────────────────┤
│  STEP 6: STRUCTURED OUTPUT                                  │
│  - Match briefing format to request                        │
│  - Data visualization if relevant                          │
│  - Confidence calibration on each claim                    │
│  - Source audit trail attached                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference: Briefing Templates

### Intelligence Brief (1-Pager)
```
SUBJECT: [What this is about]
DATE: [Date]
READ TIME: 2 min

📍 SITUATION
[1-2 sentences on the context]

📊 THE SIGNAL
[Key finding, 3 bullets max]

💡 RECOMMENDATION / KEY TAKEAWAY
[Decision-ready conclusion]

⚠️ CAVEATS
[Any important gaps or risks]
```

### Deep Dive Memo
```
CONTEXT
[Background, why this matters now]

EVIDENCE
[Organized by theme, cite sources inline]

ANALYSIS
[What it means, first-principles reasoning]

RECOMMENDATION
[Specific action or decision]

RISKS & CAVEATS
[What could go wrong, what we don't know]

SOURCES
[Full list with credibility tiers]
```

---

## Tool Stack Reference

| Function | Recommended Tool |
|----------|-----------------|
| Research memory | Obsidian / Logseq |
| Rapid web search | Perplexity.ai |
| Academic papers | Semantic Scholar, arXiv |
| Synthesis drafting | Claude / GPT |
| Citation management | Zotero |
| Data extraction | Playwright, pdfplumber |
| Competitive intel | G2, Capterra, Crunchbase |
| Market sizing | PitchBook, IBISWorld |
| Visual briefs | Excalidraw, Canva |
| Alerts | Google Alerts, Feedly |
| Research agents | gpt-researcher, STORM |
