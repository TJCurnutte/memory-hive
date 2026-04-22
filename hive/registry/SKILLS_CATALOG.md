# Skills Catalog

Matrix of what each agent can do. Used for routing decisions.

## Skill Categories

### 🔧 Technical / Development

| Skill | Agents |
|---|---|
| Architecture & system design | coder, vibe-coder, api-expert |
| Frontend development | web-dev, coder, vibe-coder |
| Backend development | coder, api-expert, web-dev |
| Debugging | coder, security-auditor, api-expert |
| Code review | coder, security-auditor |
| API design | api-expert, coder |
| Security auditing | security-auditor |
| Testing & QA | coder, web-dev |

### 📊 Research & Data

| Skill | Agents |
|---|---|
| Deep research (Karpathy-style) | research-analyst |
| Data analysis & queries | data-analyst |
| Market research | research-analyst, cxaas-specialist |
| Competitive analysis | research-analyst, cxaas-specialist |
| Report generation | data-analyst, content-strategist |

### 📢 Marketing & Content

| Skill | Agents |
|---|---|
| Social media strategy | social-media-mgr |
| Content calendar planning | content-strategist, social-media-mgr |
| Long-form content writing | content-strategist |
| LinkedIn posts | social-media-mgr, content-strategist |
| Email sequences | content-strategist |
| Brand growth | social-media-mgr, content-strategist |

### 🤝 Sales & Outreach

| Skill | Agents |
|---|---|
| Outbound prospecting | sdr-1, sdr-2 |
| Lead qualification | sdr-1 |
| Appointment setting | sdr-1 |
| Follow-up campaigns | sdr-2 |
| Pipeline hygiene | sdr-2 |

### ☁️ Domain Expertise

| Skill | Agents |
|---|---|
| CCaaS platforms | cxaas-specialist |
| CX technology | cxaas-specialist |
| AWS Connect | cxaas-specialist |
| Genesys, Five9, Twilio Flex | cxaas-specialist |
| Telecom / SIP | cxaas-specialist, api-expert |
| UCaaS | cxaas-specialist |

### 🗂️ Coordination

| Skill | Agents |
|---|---|
| Task triage & delegation | main (Chief of Staff) |
| Memory curation | main (Chief of Staff) |
| Project coordination | main (Chief of Staff) |
| Multi-agent orchestration | main (Chief of Staff) |

---

## Routing Guide

When a task comes in, route to the agent with the matching primary skill:

- **Build something** → coder, web-dev, vibe-coder
- **Secure/audit something** → security-auditor
- **Research something thoroughly** → research-analyst
- **Numbers/reports** → data-analyst
- **API/integration** → api-expert
- **Social content** → social-media-mgr
- **Long-form writing** → content-strategist
- **Outbound sales** → sdr-1
- **Pipeline/foll0w-ups** → sdr-2
- **CCaaS questions** → cxaas-specialist
- **Anything unclear / everything** → main (Chief of Staff)

---

**Last updated:** 2026-04-22