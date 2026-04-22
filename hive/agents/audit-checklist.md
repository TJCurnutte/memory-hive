# Security Audit Checklist — AI Agent Systems
*Generated: 2026-04-22*

## Pre-Engagement
- [ ] Define system boundaries (agent scope, tools, data flows)
- [ ] Identify threat model (adversarial vs. benign-only context)
- [ ] Confirm audit scope with stakeholder sign-off

---

## Prompt Injection Testing
- [ ] Test direct prompt injection (explicit override attempts)
- [ ] Test indirect injection via uploaded files (markdown, PDF, images)
- [ ] Test multi-turn conversation manipulation
- [ ] Test role-play / jailbreak attempts
- [ ] Verify instruction hierarchy — system prompt vs. user prompt boundary enforcement
- [ ] **Questions to ask**: Can user input alter system behavior? Are there meta-prompt guards?

---

## Data Security
- [ ] Audit context isolation between sessions
- [ ] Check for PII in training or logging pipelines
- [ ] Verify API keys / secrets not exposed in responses or logs
- [ ] Test data retention and cleanup policies
- [ ] **Questions to ask**: Where does data flow? Who has access? What's logged?

---

## Tool & Action Safety
- [ ] Enumerate all tools/actions the agent can invoke
- [ ] Test unauthorized tool invocation attempts
- [ ] Verify permission model (least privilege)
- [ ] Check for command injection in tool parameters
- [ ] Test rate limits and denial-of-service resistance
- [ ] **Questions to ask**: What's the blast radius of each tool? Is there confirmation before destructive actions?

---

## Multi-Agent / Orchestration Security
- [ ] Audit inter-agent communication channels
- [ ] Test compromised agent scenarios (malicious instructions in messages)
- [ ] Verify trust boundaries between agents
- [ ] Check for prompt leakage between agent messages
- [ ] **Questions to ask**: Can one agent manipulate another? Is there authentication between agents?

---

## Output & Behavior Safety
- [ ] Test for harmful or disallowed content generation
- [ ] Verify output filtering and content classification
- [ ] Test edge cases in system behavior under adversarial input
- [ ] **Questions to ask**: What happens with malformed/corrupted inputs? Is output validated?

---

## Access Control & Identity
- [ ] Verify agent identity and authentication model
- [ ] Audit RBAC / permission scopes
- [ ] Test session isolation and impersonation resistance
- [ ] **Questions to ask**: How does the system authenticate agents? Can one agent impersonate another?

---

## Logging & Monitoring
- [ ] Confirm security-relevant events are logged
- [ ] Verify log integrity (tamper-proof?)
- [ ] Check for log injection vulnerabilities
- [ ] Test alerting on anomalous behavior
- [ ] **Questions to ask**: Can logs be manipulated? What's the detection time for an attack?

---

## Compliance & Policy
- [ ] Align with OWASP LLM Top 10
- [ ] Check GDPR/CCPA compliance for data handling
- [ ] Verify model usage aligns with model provider policy
- [ ] Document risk posture and residual risks

---

## Severity Ratings
| Finding | Severity | Remediation Priority |
|---------|----------|---------------------|
| Prompt injection with system override | Critical | Immediate |
| Unauthorized code execution | Critical | Immediate |
| Cross-session data leakage | High | Urgent |
| Weak tool permission model | High | Urgent |
| Insufficient logging | Medium | Standard |
| Output content gaps | Medium | Standard |

---

*Use this checklist as a starting point. Customize per deployment context.*