# AI Research Methods — v3
> Autonomous research run | Research-Analyst agent | ra-b3 subagent

---

## SECTION 1 — EVALUATING AI CLAIMS

### 1.1 The AI Hype Cycle & Claim Categories

**Gartner Hype Cycle Application to AI:**
- **Technology Trigger:** Breakthrough paper or demo
- **Peak of Inflated Expectations:** Viral demos, maximal claims, venture hype
- **Trough of Disillusionment:** Real-world failures, retraction of claims
- **Slope of Enlightenment:** Narrowed, realistic use cases crystallize
- **Plateau of Productivity:** Mature products serving real jobs

**Key Question:** Where on the hype cycle is this specific claim?

### 1.2 Claim Taxonomy

| Claim Type | Example | Evidence Standard |
|---|---|---|
| Performance benchmark | "Best-in-class on MMLU" | Reproducible benchmark, peer review |
| User outcome | "Saves 10 hours/week" | User study, longitudinal data |
| Business impact | "2x revenue growth" | Controlled study, attribution model |
| Capability claim | "Reasons across 1M token context" | Technical demo, third-party audit |
| Safety claim | "Aligned, no harmful outputs" | Red-teaming, policy evaluation |
| Cost claim | "10x cheaper than human" | Total cost of ownership analysis |

### 1.3 Evaluating Performance Claims

**Benchmark Literacy Questions:**
1. **What benchmark?** (MMLU, HumanEval, BIG-Bench, TruthfulQA — each measures different things)
2. **Who runs it?** (Self-reported, independent, peer-reviewed?)
3. **Prompting conditions:** Zero-shot? Few-shot? Chain-of-thought? Temperature? These drastically change results
4. **Saturated?** (Are top models all scoring 90%+? Then the benchmark is saturated; need new benchmarks)
5. **Leakage?** (Did training data include benchmark test data?)
6. **Subset analysis:** Is the "best-in-class" claim cherry-picked on one subset?

**Benchmark Reference Card:**
| Benchmark | What It Measures | Limitations |
|---|---|---|
| MMLU | 57 subjects, multiple choice | Saturated; training data contamination |
| HumanEval | Python coding, pass@k | Contamination; single language |
| BIG-Bench | 200+ tasks, diverse reasoning | No single score; hard to compare |
| TruthfulQA | Propensity to repeat false beliefs | Proxy for real truthfulness |
| HELM | Holistic evaluation across scenarios | Complex; not user-friendly |
| GSM8K | Grade school math reasoning | Saturated for frontier models |
| GPQA | Expert-level graduate questions | Good for PhD-level science |
| Arena (LMSYS) | Human preference rankings | Subjective; crowdsourced |

### 1.4 Evaluating Business/ROI Claims

**Questions to Ask:**
1. **Study design:** A/B test? Before-after? Observational?
2. **Sample size:** Is it statistically powered?
3. **Selection bias:** Did users self-select into the "AI treatment" group?
4. **Hawthorne effect:** Did the act of being studied change behavior?
5. **Attribution:** Is the AI claim taking credit for other changes?
6. **Baseline:** Compared to what?
7. **Time horizon:** Short-term efficiency vs. long-term capability development?

**Common AI ROI Claim Errors:**
- Counting time saved on AI-assisted tasks without subtracting human review time
- Claiming accuracy improvement vs. human baseline when human baseline is mis-specified
- Measuring AI output speed vs. workflow speed (workflow still has human bottlenecks)

---

## SECTION 2 — BENCHMARK FRAMEWORKS & EVALUATION

### 2.1 AI Evaluation Ecosystem

**Academic Benchmarks:**
- **Stanford HELM:** Holistic Evaluation of Language Models — 42 scenarios, multiple metrics
- **BIG-Bench:** Google's Beyond the Imitation Game — 200+ tasks
- **LLMLeaderboard (HuggingFace):** Community-run benchmark aggregator
- **LiveBench:** Contamination-resistant benchmarks

**Industry Benchmarks:**
- **MLPerf:** Training and inference speed (hardware-focused)
- **OpenCompass:** Chinese open-source benchmark platform
- **SEAL:** Source-contamination detection

**Domain-Specific:**
- **MedQA, MedMCQA:** Medical knowledge
- **LegalBench:** Legal reasoning
- **BirdSQL, Spider:** SQL generation
- **DAIGT, TOEFL:** Academic writing detection

### 2.2 Red-Teaming & Safety Evaluation

**Red-Teaming Methods:**
- **Adversarial attacks:** Targeted prompts designed to elicit harmful outputs
- **Policy evaluation:** Structured evaluation against defined safety policies
- **Constitutional AI feedback:** AI-as-critic models evaluating outputs
- **Human red-teaming:** Expert adversarial testers

**Key Frameworks:**
- **NIST AI RMF:** Govern, Map, Measure, Control
- **Anthropic's Responsible Scaling Policy:** Identifies safety-critical capabilities; requires safeguards before scaling
- **Microsoft AIRAF:** AI Risk and Impact Assessment Framework
- **MITRE ATLAS:** Adversarial threat landscape for AI systems

### 2.3 Evaluating AI Agents

**Agentic AI Evaluation Challenges:**
- Benchmarks designed for static tasks don't capture multi-step planning
- Success is path-dependent (2 ways to solve, many ways to fail)
- Real-world agent success depends on integration with external tools

**Agent Evaluation Frameworks:**
- **WebArena, MiniWoB++:** Web-based agent tasks
- **AgentBench:** Multi-dimensional agent evaluation
- **GAIA:** General AI Assistants benchmark (real-world web tasks)
- **BFCL:** Berkeley Function Call Leaderboard (tool use)
- **MINT-Bench:** Multi-step tool use evaluation

### 2.4 Human Preference Evaluation

**Elo/LMSYS Arena:**
- Crowdsourced pairwise comparison
- Format: "Which response do you prefer?"
- **Strength:** Real user preferences in the wild
- **Weakness:** Subjective, noisy, prompt-sensitive, gaming possible

**Best Practices for Human Evaluation:**
- Blind evaluation (label-free)
- Diverse evaluator pool (not just AI researchers)
- Standardized prompts with calibrated scale
- Statistical significance testing

---

## SECTION 3 — AI NEWS LITERACY

### 3.1 AI Media Landscape (2025–2026)

**Major Outlets:**
- **Tech/AI-Press:** TechCrunch, VentureBeat AI, The Verge AI, Ars Technica
- **AI-Specialist:** The Gradient, Import AI (by Jack Clark), The Batch (by Andrew Ng), AI News
- **Research:** arXiv cs.AI, cs.CL, cs.LG; Papers With Code; Hugging Face blog
- **Business:** Bloomberg AI, Reuters AI, Financial Times AI coverage
- **Critical/Advocacy:** AI Now, Partnership on AI, Future of Life Institute, AI Ethics Lab

### 3.2 Source Credibility Tiers

| Tier | Source Type | Examples | Read With |
|---|---|---|---|
| T1 | Primary research | arXiv papers, conference proceedings (NeurIPS, ICML, ACL) | Critical evaluation |
| T2 | Peer-reviewed analysis | Nature, Science, JMLR, PNAS | Methodology awareness |
| T3 | Expert journalism | Verge, Ars Technica, Wired AI coverage | Source verification |
| T4 | Industry analysis | Gartner, McKinsey, Forrester | Disclosure awareness |
| T5 | Vendor communications | Press releases, model cards, website claims | Heavy skepticism |
| T6 | Social media | X/Twitter, Reddit AI communities | Very high skepticism |

### 3.3 Claim Verification Checklist

1. **Primary source?** Can I find the original paper, study, or data?
2. **Peer reviewed?** Has this been through independent expert review?
3. **Independent replication?** Has anyone else confirmed this?
4. **Out-of-context claim?** Is a narrow result being promoted as general?
5. **Demo vs. product?** Is a curated demo being sold as production reality?
6. **Self-reported vs. audited?** Is this vendor self-reported data?
7. **Context window?** Is this one study or a consistent body of evidence?
8. **Sample size?** Does the study have enough data to support the claim?
9. **Conflict of interest?** Does the source have a financial interest in the outcome?
10. **Publication date?** Is this a recent finding or outdated?

### 3.4 Common AI Misinformation Patterns

**Pattern 1: Demo-Real Gap**
- "We showed it can do X in a demo" → "We do X in production" → "You should buy this for X"
- *Mitigation: Always ask for production deployment evidence, not demo footage*

**Pattern 2: Benchmark Theater**
- Trained on test set → Score jumps → Claim "state of the art" → Test set leaks
- *Mitigation: Ask about data contamination methodology, request unseen benchmark*

**Pattern 3: Capability Stacking**
- "Uses GPT-4 class model" + "integrates with Slack" + "provides analytics" = "AI-powered platform"
- *Mitigation: Deconstruct into component capabilities and evaluate each*

**Pattern 4: Automation Fallacy**
- "AI automates X" when actually "AI assists with X + humans still required for Y"
- *Mitigation: Ask for the full workflow, not just the AI portion*

**Pattern 5: Benchmark Saturation Cherry-Pick**
- 10 benchmarks run, 1 shows improvement → "Best-in-class on benchmark X"
- *Mitigation: Request full benchmark suite results or use third-party evaluation*

**Pattern 6: Impressive-Words**
- "Revolutionary," "breakthrough," "100x faster" without quantitation
- *Mitigation: Demand the number and the methodology behind it*

---

## SECTION 4 — AI RESEARCH METHODS

### 4.1 Experimental Design for AI Systems

**Key Variables:**
- **Independent:** Model type, prompt strategy, context, temperature, RAG retrieval strategy
- **Dependent:** Output quality (human-rated or automated), latency, cost, task completion rate
- **Controlled:** Task type, difficulty level, evaluator

**Evaluation Design Patterns:**
- **Within-subjects:** Same evaluator judges all models → less noise but order effects
- **Between-subjects:** Different evaluators per model → less bias but more noise
- **Blind vs. non-blind:** Evaluators know which model → potential bias but realistic

### 4.2 Human-in-the-Loop Evaluation

**SOTA Approaches:**
- **G-Eval:** Framework using LLMs as evaluators (Cohere)
- **alpaca_eval:** LLM-as-judge with reference annotations
- **MT-Bench:** Multi-turn conversation evaluation
- **Chatbot Arena:** Crowdsourced human preference

**Human Rating Scales:**
- **Likert scales:** 1–5 or 1–7 for specific dimensions (accuracy, helpfulness, safety)
- **Comparative:** A vs. B preference with confidence level
- **Task success:** Binary or threshold-based completion check
- **Error taxonomy:** Classified error types for root cause analysis

### 4.3 Technical Evaluation Stack

```
Prompt Engineering Layer
  └── Chain-of-thought, few-shot, system prompts
  
Model Execution Layer
  └── Temperature, top-p, max_tokens, seed

RAG/Infrastructure Layer
  └── Retrieval quality, latency, API reliability

Output Evaluation Layer
  └── Automated metrics → Human evaluation → Production feedback
```

---

## SECTION 5 — AI NEWS LITERACY CASE STUDIES

### Case 1: "AI Diagnoses Cancer Better Than Radiologists"
- *Claim type:* Performance benchmark + business impact
- *Reality:* AI outperforms on narrow dataset tasks; radiologists use AI as second reader, not replacement
- *Lesson:* Narrow benchmark ≠ real-world performance; human-AI collaboration is the deployment pattern

### Case 2: "LLaMA 3 Beats GPT-4"
- *Claim type:* Benchmark performance
- *Reality:* On specific benchmarks yes; overall capability and safety alignment still lags
- *Lesson:* One benchmark ≠ global superiority; model is a bundle of trade-offs

### Case 3: "Autonomous AI Agent Automates Software Development"
- *Claim type:* Capability claim
- *Reality:* Works in sandboxed demos; real codebases with business logic require constant human oversight
- *Lesson:* Demo environment ≠ production environment; agent success rate drops significantly in real-world conditions

### Case 4: "AI Will Replace 40% of Jobs by 2030"
- *Claim type:* Macro business impact
- *Reality:* McKinsey, Goldman, and others publish different numbers (20% to 60% range); all are modeling estimates, not empirical studies
- *Lesson:* Macro predictions are model-dependent; the range of expert estimates reveals the uncertainty

---

## SECTION 6 — RESEARCH QUALITY FRAMEWORK (AI-FOCUSED)

### 6.1 AI Claim Audit Checklist

- [ ] Does the source have direct access to the model/system?
- [ ] Are evaluations independent or self-reported?
- [ ] Was the benchmark run on current-version model or outdated checkpoint?
- [ ] Is the claim about AI capability or AI-enabled human productivity?
- [ ] Has the study been pre-registered (reduces p-hacking)?
- [ ] Are error bars/confidence intervals reported?
- [ ] Does the evaluation reflect real-world deployment conditions?
- [ ] Are there potential conflicts of interest (investor, vendor, grant funder)?

### 6.2 Reading an AI Paper

1. **Abstract:** What did they claim? (Write it down before reading)
2. **Intro:** What problem does this solve? Is the problem real?
3. **Related work:** How does this fit in the literature?
4. **Methods:** Is the experimental design sound?
5. **Results:** Do the numbers support the claims? Check all tables, not just highlights
6. **Limitations:** Do they acknowledge what they can't do?
7. **Ethics:** Do they discuss safety, bias, misuse risks?
8. **Replicability:** Is code/data available?

---

*ra-b3 | AI Research Methods | Research-Analyst agent | 2026-04-22*
