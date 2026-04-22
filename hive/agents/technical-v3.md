# Technical Deep Dives Research Guide v3
*Research-Analyst — Subagent 2 | Technical Deep Dives*

---

## 1. Introduction: Why Technical Depth Matters

In a world where AI-generated summaries and surface-level takes dominate, the ability to deeply understand technical topics quickly is a strategic advantage. Whether evaluating an AI startup's technology claims, understanding a new framework, assessing a technical due diligence target, or making investment decisions — the ability to go deep quickly and accurately separates skilled analysts from the crowd.

This guide covers: how to deeply understand technical topics rapidly, navigating academic literature, doing technical due diligence, understanding AI benchmarks, and evaluating technical claims with rigor.

---

## 2. The Deep Dive Process: A Systematic Approach

### 2.1 The 5-Layer Understanding Model

**Layer 1 — Conceptual (What is it?)**
- Read 2-3 high-level explainers (Wikipedia, introductory blog posts)
- Watch a YouTube explainer or conference talk
- Build a one-paragraph mental model
- *Goal*: Can explain it to a smart non-technical person in plain English

**Layer 2 — Mechanics (How does it work?)**
- Read the primary documentation
- Follow a tutorial or build a demo
- Trace through a simple example step by step
- *Goal*: Can explain the mechanism to a technical colleague

**Layer 3 — Implementation (How is it built?)**
- Read source code (open source repos on GitHub)
- Study architecture diagrams and system design docs
- Examine data structures and algorithms used
- *Goal*: Can evaluate implementation quality and spot red flags

**Layer 4 — Limitations (Where does it break?)**
- Read failure modes, edge cases, known bugs
- Study benchmark limitations and methodology critiques
- Understand scaling behavior and resource requirements
- *Goal*: Can identify where the technology struggles and what it cannot do

**Layer 5 — Frontier (What is unknown?)**
- Read recent arXiv papers in the space
- Follow active researchers on Twitter/LinkedIn
- Attend conferences or watch recorded talks
- Understand open problems and active research areas
- *Goal*: Can speak intelligently about where the field is heading

### 2.2 Speed vs. Depth Triage

Not every topic requires all 5 layers. Apply the right depth:

| Decision Type | Required Depth |
|---------------|---------------|
| Investment thesis screening | Layer 1-2 |
| Partnership evaluation | Layer 2-3 |
| Acquisition / acquisition target | Layer 3-4 |
| Technical investment (VC/PE) | Layer 4-5 |
| Academic credibility check | Layer 5 |

### 2.3 Building a Topic Map

When approaching a new technical domain:
1. List the key concepts and their relationships
2. Identify the canonical papers or texts in the space
3. Map the "family tree" — who built on whose work
4. Find the key players (researchers, companies, open-source projects)
5. Identify the benchmark datasets and evaluation methods

---

## 3. Reading Academic Papers (ArXiv, Papers With Code, etc.)

### 3.1 Where to Find Academic Papers

**Primary Repositories**:
- **arXiv** (https://arxiv.org) — Preprint server for physics, math, CS, q-bio, stat, etc. The canonical source for cutting-edge AI/ML research.
- **Papers With Code** (https://paperswithcode.com) — Links papers to code implementations and benchmarks. Essential for AI research.
- **ACL Anthology** (https://aclanthology.org) — NLP/CL papers specifically
- **ICML / NeurIPS / ICLR / CVPR proceedings** — Conference proceedings (often on arXiv too)
- **Semantic Scholar** (https://semanticscholar.org) — Search engine for academic papers with citation graphs
- **Google Scholar** — General academic search
- **Z-Library / Sci-Hub** — For access to paywalled papers (use responsibly; some institutions provide free access)

**Secondary Sources**:
- Distill.pub — Beautiful interactive explanations of ML concepts
- The Gradient (thegradient.pub) — Accessible ML research summaries
- Towards Data Science (Medium) — Practitioner writeups
- Andrej Karpathy's blog — Deep learning insights
- Lilian Weng's blog — Technical deep dives on AI

### 3.2 How to Read a Paper Efficiently

**The 3-Pass Method** (S. Keshav, 2007):

**Pass 1 — The Shallow Read (5-10 minutes)**
1. Read the title
2. Read the abstract
3. Read the introduction
4. Read section headings
5. Read the conclusion
6. Glance at references, mark what you recognize
→ **Goal**: Understand the high-level contribution and why it matters

**Pass 2 — Grasp the Content (1-2 hours)**
1. Read the paper carefully, but ignore proofs/details
2. Read with pencil — mark unclear passages
3. Follow figures, diagrams, and charts carefully
4. Try to re-derive arguments mentally
5. Look up definitions of terms you don't know
→ **Goal**: Understand the methodology and results in detail

**Pass 3 — Deep Critique (3-5 hours)**
1. Strip out all auxiliary material, focus on core ideas
2. Challenge every assumption
3. Rethink the presentation from scratch
4. Identify weaknesses: overclaimed results, missing baselines, flawed methodology
5. Consider how you would present the work differently
6. Check if you can find counterexamples or alternative interpretations
→ **Goal**: Form an independent critical assessment

### 3.3 Evaluating AI/ML Papers

**Key Questions for AI Paper Evaluation**:
1. Is the problem well-defined and meaningful?
2. Are the baselines sufficient? (SOTA-chasing vs. genuine improvement)
3. Is the evaluation methodology appropriate?
4. Are the benchmark datasets the right proxy for real-world performance?
5. Are results statistically significant? Are error bars reported?
6. Does the paper claim more than the evidence supports?
7. Is the code available? Is it well-tested?
8. Are there potential harms or biases the paper doesn't discuss?
9. Would this work in production? (Paper ML ≠ Production ML)

### 3.4 The Leaderboard Problem

On Papers With Code, every ML paper promises to beat SOTA. Critically evaluate:

- **Did they compare against the right baselines?** (Often papers compare against weak or outdated methods)
- **Did they report statistical variance?** (Single-run results are unreliable)
- **Did they use the same hyperparameters?** (Cherry-picked settings for comparison)
- **Did they train fairly?** (Leakage between train/test sets)
- **Is the benchmark saturated?** (If everyone is at 99%+ accuracy, marginal gains are meaningless)

### 3.5 Citation Analysis

**Citation Count ≠ Quality**: High citation counts can mean "foundational" or "trendy," not necessarily "correct" or "high quality."

**Key Metrics**:
- Citation count over time (new vs. accumulating)
- Citation context (positive, negative, or neutral?)
- Self-citation ratio (concerning if >30%)
- H-index of authors

---

## 4. Technical Due Diligence (TDD)

Technical due diligence is the process of evaluating the technical substance, quality, and risks of a company — typically before investment, acquisition, or partnership.

### 4.1 What TDD Covers

| Area | What to Evaluate |
|------|-----------------|
| **Architecture** | System design, scalability, tech stack choices |
| **Code Quality** | Testing coverage, code debt, review practices |
| **IP & Technology** | Patents, trade secrets, open-source compliance |
| **Team** | Key technical talent, retention risk, hiring plan |
| **Product** | Technical differentiation, defensibility |
| **Security** | Security posture, vulnerability history, compliance |
| **Data** | Data quality, volume, competitive value of data assets |
| **Infrastructure** | Cloud costs, reliability, DR/BCP |

### 4.2 TDD Process

**Stage 1: Background Research (1-3 days)**
- Review public code (GitHub presence)
- Read engineering blog posts, job postings
- Analyze tech stack (Wappalyzer, LinkedIn, job descriptions)
- Search for CVE disclosures, breach history

**Stage 2: Technical Interviews (1-3 days)**
- Interview CTO/VP Engineering: architecture decisions, scaling story, technical risks
- Interview key engineers: code quality practices, technical challenges
- Ask about the engineering culture and process

**Stage 3: Code Review (1-5 days)**
- Request access to codebase (under NDA) or review public commits
- Use static analysis tools (SonarQube, CodeClimate)
- Look for: test coverage %, code complexity, security issues, technical debt

**Stage 4: Reference Checks**
- Talk to former employees, technical partners, customers
- Ask specifically about technical credibility, execution quality

### 4.3 Red Flags in Technical Due Diligence

- No automated testing, or testing is minimal
- Single points of failure in architecture (one engineer knows everything)
- Massive technical debt with no plan to address it
- Heavy dependence on a single cloud provider without mitigation
- No security audit history, especially for a data-sensitive product
- IP claims that don't match what's publicly visible
- Key engineers not committed post-acquisition
- Tech stack that is significantly outdated (Ruby on Rails 3.0 in 2026, etc.)
- No documented architecture or runbooks
- Inconsistent engineering investment vs. claimed maturity

### 4.4 Green Flags

- High test coverage (>80%)
- CI/CD pipeline with automated quality gates
- Security practices: SAST/DAST tools, dependency scanning
- Clear technical roadmap aligned with business goals
- Engineers who can clearly explain the "why" behind technical choices
- Strong engineering culture (blameless postmortems, code reviews, documentation)
- Open-source contributions (sign of technical confidence)
- Active monitoring and observability (Datadog, Grafana, etc.)

### 4.5 TDD for AI Companies Specifically

AI companies require additional scrutiny:

- **Data Assets**: Is the training data proprietary? Licensed? Scraped (legally risky)?
- **Model Documentation**: Can they explain how their model works? (Explainability vs. black box)
- **Benchmark Validation**: Independently verify their benchmark claims
- **Training Costs**: Can they afford to retrain as the market evolves?
- **Inference Costs**: Economics at scale — what does inference cost per query?
- **Regulatory Exposure**: Are there data privacy/GDPR/CCPA risks specific to their use case?
- **Compute Dependencies**: Heavy dependency on a single cloud provider (AWS, GCP) for GPU access?
- **Talent Concentration**: Is the entire model development team 2-3 people?
- **Foundation Model Risk**: Are they building on top of someone else's API? (vendor lock-in)

---

## 5. Understanding AI Benchmarks

### 5.1 What AI Benchmarks Measure

AI benchmarks are standardized evaluation datasets and tasks used to measure AI system performance. They serve as:
- **Progress tracking**: Is the field improving?
- **Comparison**: How does X perform vs. Y?
- **Debugging**: Where does a system fail?
- **Accountability**: Are claims substantiated?

### 5.2 Major AI Benchmark Categories

**Language Models**:
- **MMLU** (Massive Multitask Language Understanding): 57 subjects, multiple choice — widely used
- **GSM8K**: Grade school math word problems
- **HumanEval**: Code generation (Python)
- **BIG-Bench Hard**: Subset of BIG-Bench tasks that stump models
- **TruthfulQA**: Propensity to generate false statements
- **HellaSwag**: Commonsense reasoning
- **LLM Leaderboards** (LMSYS Chatbot Arena, Scale AI Leaderboard): Human preference rankings

**Image Models**:
- **ImageNet**: Object classification (1K categories)
- **COCO**: Object detection and segmentation
- **ADE20K**: Scene parsing
- **FID (Fréchet Inception Distance)**: Image quality comparison for generative models

**Multimodal**:
- **MMBench**: Multi-modal understanding
- **VQAv2**: Visual question answering
- **SEED-Bench**: Comprehensive multimodal evaluation

**Code**:
- **OpenAI HumanEval**: Python function completion
- **MBPP**: Mostly Basic Python Problems
- **SWE-Bench**: Real GitHub issue resolution

### 5.3 Critical Evaluation of Benchmarks

**Contamination**: The most serious issue in AI benchmarking. Models may have been trained on benchmark data itself, artificially inflating scores.
- Look for benchmark contamination indicators: "AI-generated benchmarks," data leakage from training corpora
- Check if the benchmark is in the training data (Pile, C4, The Pile)
- MMLU contamination is a well-known issue for models trained on large web corpora

**Benchmark Saturation**: As models improve, benchmarks become less discriminative. If all top models are at 90%+ on a benchmark, the benchmark is no longer useful for differentiation.

**Goodhart's Law**: "When a measure becomes a target, it ceases to be a good measure." Top models are increasingly over-optimized on popular benchmarks, making scores less meaningful.

**Evaluation Protocol**: Check:
- How many runs? (Mean ± std? Or single run?)
- Are results statistically significant?
- Is the evaluation setup the same as what was reported?
- Are there adversarial or hard examples that aren't in the main benchmark?

### 5.4 Benchmark Interpretation for Decision-Making

**For evaluating AI products**:
- Don't rely on a single benchmark number
- Ask for private, in-domain evaluation on the customer's actual use case
- Run your own red teaming / adversarial evaluation
- Check performance on edge cases, not just averages
- Validate benchmark performance in production-like conditions

**For evaluating companies making benchmark claims**:
- Verify the claim independently (look for third-party evaluations)
- Check if the benchmark is relevant to their stated use case
- Understand what the benchmark does and doesn't cover
- Ask about failure modes — can they articulate where their model breaks?

---

## 6. Evaluating Technical Claims

### 6.1 The Scientific Method Applied to Business Claims

**Claims → Evidence → Alternative Explanations → Conclusion**

1. **What is the claim?** (State it precisely, in writing)
2. **What evidence supports it?** (Citations, data, methodology)
3. **How strong is the evidence?** (Peer-reviewed? Reproducible? Single-source?)
4. **What are alternative explanations?** (Confirmation bias, survivorship bias, correlation ≠ causation)
5. **Who benefits from this claim?** (Incentive alignment check)
6. **What would it take to disprove it?** (Falsifiability test)

### 6.2 Common Technical Claim Red Flags

| Claim Pattern | What It Often Signals |
|---------------|----------------------|
| "10x better performance" (no data) | Marketing over engineering |
| "First/only/only AI that..." | Often verifiably false or misleadingly narrow |
| "Enterprise-grade security" (no specifics) | Vapor — no actual security investment |
| "Powered by advanced AI" | Often simple rules-based systems or wrappers |
| "SOC2 certified" (can't show report) | Certification in progress, not achieved |
| Benchmark results without methodology | Cherry-picked, unreproducible |
| Customer logos without permission | Permission not obtained, legal risk |
| "Built on blockchain" (no rationale) | Hype-driven, not solving a real problem |
| "Our model is better than GPT-4" (no eval) | Unsubstantiated marketing claim |

### 6.3 Claim Verification Checklist

- [ ] Can I verify the claim independently?
- [ ] Who did the measurement? (Self-reported? Third-party?)
- [ ] What were the conditions? (Same hardware? Same dataset? Same task?)
- [ ] Is the claim about a controlled test or real-world production?
- [ ] Can I reproduce it?
- [ ] What is the sample size? Is it statistically significant?
- [ ] Does the incentive structure encourage accurate reporting?
- [ ] Is there a conflict of interest? (Evaluator paid by the company?)
- [ ] Has this claim been independently replicated?
- [ ] Does the claim hold across diverse conditions, or only ideal ones?

### 6.4 Technical Due Diligence on Claims

When a company makes a technical claim:
1. Ask for the underlying data and methodology
2. Request a live demonstration on a representative task
3. Run your own test on a sample of their claimed capabilities
4. Call their reference customers and ask about real-world performance vs. claims
5. Check if their technical team has published or spoken publicly about the technology
6. Look at their GitHub or open-source presence for code quality signals

---

## 7. Technical Reading Resources by Domain

### 7.1 AI/ML

- **Distill.pub** — Interactive ML explanations
- **Hugging Face Blog** — Practitioner-focused
- **The Annotated Transformer** (http://nlp.seas.harvard.edu/transformer) — Walkthrough of the transformer architecture
- **Google ML Crash Course** — Foundational
- **fast.ai** — Practical deep learning
- **Andrej Karpathy's YouTube** — Neural networks from scratch

### 7.2 Software Engineering

- **Martin Fowler's Blog** — Architecture and patterns
- **Google Engineering Practices** — Code review standards
- **CNCF Landscape** — Cloud-native ecosystem map
- **System Design Primer** (GitHub) — Scalable systems design

### 7.3 Security

- **OWASP Top 10** — Web application security
- **CVE Database** (cve.mitre.org) — Vulnerability database
- **Krebs on Security** — Industry news
- **CISO's Guide to Cloud Security** — Enterprise security

---

## 8. Quick-Reference: Technical Deep Dive Cheat Sheet

1. **5-Layer Model**: Conceptual → Mechanics → Implementation → Limitations → Frontier
2. **3-Pass Paper Reading**: Shallow (5 min) → Grasp content (1-2 hrs) → Critique (3-5 hrs)
3. **Benchmark Validation**: Check contamination, saturation, evaluation protocol
4. **TDD Red Flags**: No tests, single point of failure, tech debt, security gaps, key person dependency
5. **AI TDD Extra**: Data ownership, inference costs, foundation model dependency, model explainability
6. **Claim Evaluation**: Precise claim → evidence strength → alternative explanations → independent verification
7. **Key Resources**: ArXiv + Papers With Code + Semantic Scholar for AI; GitHub + static analysis for code quality

---

*Document: technical-v3.md | Agent: research-analyst | Subagent: technical-deep-dives*
*Last Updated: 2026-04-22*
