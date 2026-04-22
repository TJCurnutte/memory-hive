# B2B Outbound Research — Modern Strategies for SDR-Alpha
*Last updated: 2026-04-22*

---

## 1. Personalization at Scale

### Token vs. Deep Personalization
| Level | What | Example | Use When |
|---|---|---|---|
| **Token** | First name, company name | "Hi {{first_name}}, congrats on {{company}}'s Series B" | Volume plays, top-of-funnel |
| **Surface** | Job title, industry, recent news | "I noticed you're VP of Sales at a SaaS company" | Mid-sequence touches |
| **Deep** | Recent blog post, LinkedIn post, funding event, tech stack | "Your post on Q4 pipeline challenges really resonated — we work with teams facing the same thing" | High-value targets, ABM |
| **Hyper** | Personal context, mutual connections, conversation threads | "Saw you and Sarah Chen both commented on the same RevOps thread — small world" | VIP prospecting, enterprise |

### Tools for Personalization at Scale
- **Clay** — AI-powered data enrichment, 100+ integrations to auto-personalize at row level. Gold standard for ICP-tier personalization.
- **Instantly** — Email warmup + sending at scale. Pairs well with Clay.
- **Apollo** — Prospect database + sequencing. Good for contact info at scale.
- **Reply.io** — Multi-channel sequencing with AI copy assist.
- **Smartlead / Mailshake** — Lower-cost alternatives for smaller teams.
- **Lemlist** — Email + LinkedIn combined, with personalized images (e.g., dynamically generated company screenshots).
- **Phantombuster** — LinkedIn scraping for research signals (use responsibly).

### Rule of Thumb
- First 2 touches: token personalization (volume)
- Touches 3-5: surface-level research signals
- Re-engagement / VIP: deep personalization

---

## 2. Multi-Channel Outreach

### Channel Hierarchy for B2B SaaS
1. **Email** — Primary channel. Highest volume, lowest cost.
2. **LinkedIn** — Social proof, relationship building, discovery.
3. **Cold Call** — Highest conversion rate per conversation, lowest volume.
4. **SMS** — Great for mid-sequence re-engagement (post-GDPR compliance required).
5. **Video / Loom** — Personalized async video can 3-4x reply rates. Use for high-priority accounts.

### Optimal Sequence Architecture
**Recommended 7-touch multi-channel sequence:**

| Touch | Channel | Day | Purpose |
|---|---|---|---|
| 1 | Email | Day 0 | Initial value prop |
| 2 | LinkedIn | Day 1 | Social connection + light comment |
| 3 | Email | Day 3 | Different angle / social proof |
| 4 | LinkedIn | Day 5 | Follow up + send content |
| 5 | Email | Day 7 | Breakup / last attempt |
| 6 | LinkedIn | Day 10 | Re-engagement |
| 7 | Email | Day 14 | Final exit + calendar link |

### Channel-Specific Notes
- **Email before LinkedIn first:** Don't open with "I tried to connect on LinkedIn" before sending email. Send email Day 0, LinkedIn Day 1 to avoid looking pushy.
- **LinkedIn:** Connect with a personalized note (always include one, under 300 chars). Comment on a post of theirs for visibility.
- **Cold calling:** Best paired with email Day 0. Leave a voicemail — they're 4x more likely to reply to your follow-up email. Voicemail: 22 seconds max. Hook → why you called → callback number. Never read a script.
- **SMS:** Best Day 4-5 for re-engagement. "Hey {{first_name}}, quick follow-up on the note I sent — curious if timing's off?"

---

## 3. Response Rate Optimization

### Subject Lines
- **Top performers:** Questions (15% higher open rate), curiosity gaps, personalized with company/name, brevity (3-5 words).
- **Avoid:** "Quick question," "Intro," all-caps, excessive punctuation, "Free."
- **A/B test priorities:** Subject line → preview text → CTA placement.
- **Examples that work:**
  - "Quick question about [Company]'s Q2 pipeline"
  - "[First name] — one thing about [Company]'s go-to-market"
  - "Saw you mentioned [their LinkedIn post topic]"

### Preview Text (Often More Important Than Subject Line)
- Shows in inbox under subject line. Second thing people read.
- Keep 40-80 characters. Never leave blank — shows first 80 chars of body.
- Complementary to subject line, not redundant.

### Email Copy Principles
- **Lead with a hook**, not your intro. "I noticed..." outperforms "I'm reaching out from [Company]..."
- **Body: 50-100 words.** No one reads 300-word emails cold.
- **Short paragraphs (1-2 sentences max).** White space = readability.
- **CTA: singular and low-commitment.** "Worth a quick chat?" beats "Book a demo."
- **Signature:** Name + title + phone. Clean. No logos — triggers spam filters.

### Timing
- **Best open rates:** Tuesday–Thursday, 8–10am and 3–5pm (recipient's timezone).
- **Best reply rates:** Wednesday 9–11am.
- **Worst:** Monday mornings, Friday afternoons, post-holiday weeks.
- Send 30-50/day per email account initially to avoid throttling.

---

## 4. Email Deliverability

### Warmup Protocol (Non-Negotiable)
- **New domain:** Warm up 2-3 weeks minimum before sending cold at volume.
- Start at 5-10 emails/day, increase by 5/day.
- Tools: **Instantly, Lemwarm (Lemlist), Socialplug.**
- During warmup: inbox = important, mark as important, reply to every email.

### Technical Foundations
| Element | What to Do |
|---|---|
| **SPF** | Add sending domain to SPF record |
| **DKIM** | Enable domain-key signing |
| **DMARC** | Set to "p=quarantine" minimum |
| **MX setup** | Ensure receiving domain has proper MX records |
| **Custom tracking domain** | Never use free email domains for cold outreach |
| **Reply-to vs. From** | Keep Reply-to matching From to build sender reputation |

### Sending Practices
- **Throttle:** Max 30-50 emails/day per sending domain initially. Scale up over 4-6 weeks.
- **Seed list:** 5 test accounts at Gmail, Outlook, Hotmail. Track delivery rates.
- **Hard bounce rate:** Must stay below 3%. Pause at 5%.
- **Spam complaint rate:** Must stay below 0.1%.
- **Unsubscribe:** Honor immediately. One-click unsubscribe (RFC 8058) required by law in many regions.

---

## 5. Sequence Design

### Sequence Length
- **Minimum:** 5 touches. Most replies come on touch 3-5.
- **Optimal:** 7-10 touches over 30-45 days.
- **Don't stop at 1.** 60% of positive responses come after the 3rd touch.
- **Breakup email:** Touch 5 or 7 — "closing the loop" message. Removes guilt, can generate replies.

### Touch Intervals
| Style | Intervals |
|---|---|
| **Aggressive** | Day 0, 1, 3, 5, 7, 10, 14 |
| **Standard** | Day 0, 2, 5, 8, 12, 18, 25, 35 |
| **Nurture** | Day 0, 5, 10, 20, 30, 45, 60 |

### Exit Criteria — When to Stop a Sequence
**Stop if:**
- Responded "not interested" → remove from sequence immediately
- Responded with anything → move to sales / booked meeting
- No reply after 8-10 touches → pause 90 days, re-engage with new angle

**Never:**
- Keep emailing someone who said no
- Keep emailing after a hard bounce
- Keep emailing if domain no longer exists

### Re-Engagement
- Wait 60-90 days minimum.
- Lead with new value: new case study, new use case, new angle.
- Reference previous outreach briefly: "I know I reached out a few months ago..."

---

## 6. Tools Stack

| Function | Top Tools |
|---|---|
| **Email Finder/Verifier** | Apollo, Hunter.io, Snov.io, ZeroBounce |
| **Email Warmup** | Instantly, Lemwarm (Lemlist), Warmbox |
| **Email Sequencing** | Instantly, Smartlead, Mailshake, Outreach, Salesloft |
| **Multi-Channel Sequencing** | Reply.io, Instantly (multi-channel), LaGrowthMachine |
| **LinkedIn Automation** | Phantombuster, Dux-Soup, Expandi, MeetAlfred |
| **CRM** | HubSpot, Salesforce, Pipedrive, GoHighLevel |
| **Enrichment/Personalization** | Clay (top-tier), Apollo, Clearbit, People.ai |
| **Video Outreach** | Loom (personalized), Vidyard, Bonjoro |
| **Intent Signals** | Bombora, G2 reviews, Crunchbase |
| **Cold Calling Dialer** | Kixie, Aircall, Dialpad, CallTools |

---

## Key Takeaways

1. **Personalization drives reply rates.** Token = 5-10% reply. Deep personalization = 15-25%.
2. **Multi-channel > single channel.** Adding LinkedIn to email sequences can increase reply rates 2-3x.
3. **Subject line and preview text are your highest-leverage copy.** Test obsessively.
4. **Deliverability is foundational.** A perfect email in spam = 0% reply rate.
5. **5-10 touches minimum.** Most SDRs give up too early. Touch 6-10 reply rates are often 2-4x higher than touch 1.
6. **Use the breakup email to your advantage.** Frame as "closing the loop" — reduces guilt, can generate replies.
7. **Warmup your domains.** Non-negotiable before scaling volume.
8. **Time emails in recipient's timezone.** Use tools with timezone awareness.
