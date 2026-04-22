# Email Marketing — Research Learnings (v3)

> Generated: 2026-04-22 | Agent: Content-Strategist | Subagent: content-2

---

## Table of Contents
1. [Email Deliverability Fundamentals](#1-email-deliverability-fundamentals)
2. [Cold Email Deliverability 2026](#2-cold-email-deliverability-2026)
3. [Email Copywriting Frameworks: AIDA & PAC](#3-email-copywriting-frameworks)
4. [Drip Campaign Design](#4-drip-campaign-design)
5. [Email Segmentation Strategies](#5-email-segmentation-strategies)
6. [Klaviyo vs Mailchimp for B2B](#6-klaviyo-vs-mailchimp-for-b2b)
7. [Key Takeaways & Action Items](#7-key-takeaways)

---

## 1. Email Deliverability Fundamentals

### 1.1 What Determines Deliverability?

Deliverability is the measure of whether your email lands in the inbox — and it's the single most important technical factor in email marketing success. Even the best-written email is worthless if it lands in spam.

**The Three Pillars of Deliverability**

1. **Sender Reputation (40%)**
   - IP address reputation (shared vs. dedicated IPs)
   - Domain reputation (SPF, DKIM, DMARC setup)
   - Historical sending patterns (volume, frequency, bounce rate)

2. **Email Content (35%)**
   - Subject line triggers (spam keywords, ALL CAPS, excessive punctuation)
   - Body content (links to suspicious domains, image-to-text ratio)
   - Engagement signals (opens, clicks, replies, spam reports)

3. **Recipient Engagement (25%)**
   - List hygiene (removing inactive subscribers)
   - Subscriber acquisition source (purchased lists = death)
   - Recent engagement (opened/clicked in last 30-90 days)

### 1.2 Authentication Protocols (The Technical Foundation)

**SPF (Sender Policy Framework)**
```
v=spf1 include:sendgrid.net ~all
```
- Authorizes which mail servers can send on behalf of your domain
- Required for every sending domain
- Mistakes = soft bounces and failed delivery

**DKIM (DomainKeys Identified Mail)**
- Adds an encrypted digital signature to every email
- Verifies the email wasn't modified in transit
- Most ESPs (Klaviyo, Mailchimp) set this up automatically

**DMARC (Domain-based Message Authentication, Reporting & Conformance)**
- Tells receiving servers what to do with emails that fail SPF/DKIM
- Start with `p=quarantine`, not `p=reject` (give yourself time to fix issues)
- Set up DMARC reports to catch authentication problems early

**BIMI (Brand Indicators for Message Identification)**
- Displays your logo next to emails in supported clients (Apple Mail, Gmail)
- Requires a DMARC policy of `quarantine` or `reject`
- Adds perceived legitimacy and improves open rates slightly

### 1.3 List Hygiene: Non-Negotiable

| Practice | Frequency | Impact |
|---|---|---|
| Remove hard bounces immediately | Every send | Protects sender reputation |
| Suppress unsubscribes immediately | Every send | Legal requirement + deliverability |
| Re-engage inactive (6+ months) before removing | Quarterly | Recover or remove stale contacts |
| Monitor spam complaint rate | Monthly | Stay below 0.1% threshold |
| Verify new subscribers (double opt-in) | Always | List quality > list size |

**The 12-Month Rule**
- Anyone who hasn't opened or clicked in 12 months should enter a re-engagement sequence
- If they don't engage after the re-engagement sequence → remove from list
- Smaller, engaged list > large, disengaged list for both deliverability and revenue

### 1.4 Inbox Provider Specifics

| Provider | What They Care About | Key Tactic |
|---|---|---|
| **Gmail** | Engagement history, unsubscribe behavior | Warm up new sending domains slowly |
| **Microsoft (Outlook/Hotmail)** | Sender IP reputation, content linking | Avoid spam trigger words; use plain text |
| **Yahoo** | DMARC enforcement, complaint rates | Keep complaint rate below 0.1% |
| **Apple (iOS 15+)** | Private Relay hides IPs; engagement = on-device activity | Optimize opens, not just clicks |
| **SpamAssassin** | Heuristic rules (spammy content) | Subject line testing; avoid known triggers |

---

## 2. Cold Email Deliverability 2026

### 2.1 Why Cold Email Is Different

Cold email deliverability is fundamentally harder than warm email. You're sending to people who have never heard of you, have no prior engagement with your brand, and haven't granted permission. The rules are stricter.

**Legal Framework**
- **CAN-SPAM (USA)**: No requirement for consent, but must include physical address, unsubscribe link, and honor opt-outs within 10 business days
- **CASL (Canada)**: Implied consent standard is stricter; express consent required for many B2B scenarios
- **GDPR (EU)**: Legitimate interest is controversial; explicit consent is the safest approach
- **Note:** Even where consent isn't legally required, sending to people who want to hear from you is the only sustainable approach

### 2.2 Cold Email Sender Reputation 2026

**Domain Warming — The Gold Standard Process**
1. Start with a dedicated domain (not your primary domain)
2. Warm up over 4-8 weeks, starting at 5-10 emails/day
3. Increase volume by 20-30% every 3-5 days
4. Monitor bounce rate — stay below 5%, ideally below 2%
5. By week 8, you can send at your target volume
6. Never "burst send" — sudden spikes trigger spam filters

**Subdomain Strategy**
- Use a separate subdomain for cold sending: `outreach.company.com`
- Keep your main domain completely separate from cold outbound
- If subdomain gets flagged, you haven't burned your main brand domain
- Rotate between 2-3 subdomains to distribute reputation risk

**What Kills Cold Email Deliverability Fast**
- Purchasing email lists (bought lists have 30-60% bounce rates → kills reputation)
- Sending the same email to everyone (Gmail/Outlook detect bulk patterns)
- High complaint rates (even 0.5% can get you blocked)
- Cold emails with no personalization (filtering gets smarter every year)
- Low engagement → your emails train the algorithms against you

### 2.3 Cold Email Infrastructure Checklist

- [ ] Dedicated sending domain (separate from main brand domain)
- [ ] SPF, DKIM, DMARC configured for sending domain
- [ ] 2-3 rotating subdomains to distribute volume
- [ ] Custom tracking domain for opens/clicks (avoids using known tracking companies)
- [ ] Valid reply-to address (reply-to box = engagement signal)
- [ ] No-reply@ domain — always use a real reply address

---

## 3. Email Copywriting Frameworks

### 3.1 AIDA Framework

AIDA is the classic copywriting framework, applicable to any email marketing context:

**A — Attention (Subject Line + Preview Text)**
- Subject line: 30-50 characters; create curiosity or state a clear benefit
- Preview text: 85-130 characters; extend the subject line, don't repeat it
- Example: "The email sequence that generated $47,000 in MRR" (subject) → "I analyzed 200 drip campaigns to find the 5-email sequence that converts trial users into paying customers..." (preview)

**I — Interest (Opening Paragraph)**
- Hook the reader in the first 1-2 sentences
- Use a bold claim, a relevant story, or a pattern interrupt
- Never start with "I hope this email finds you well" — that sentence has never generated a single sale
- Ideal: the reader feels "this was written for me" within 5 seconds

**D — Desire (Body)**
- Paint the picture of the desired outcome (not just features)
- Use social proof: "Here's what 247 marketers did in 90 days..."
- Specificity beats vague claims — "23% more opens" beats "significantly more opens"
- Build tension: describe the problem more vividly than the solution, then provide the solution
- Use subheads, bullet points, and short paragraphs (mobile readers don't scroll)

**A — Action (CTA)**
- One primary CTA per email — never multiple "primary" CTAs
- CTA must be specific and frictionless: "Book a 20-minute call" beats "Learn more"
- Use urgency sparingly but genuinely — if there's no real deadline, don't fake one
- Repeat the CTA near the bottom after value delivery

**AIDA Email Example Structure**
```
Subject: The cold email sequence that booked me 14 demos in one week
Preview: I reverse-engineered what top SDRs do differently...

[Interest] When I sent my first cold email sequence, I got a 0.4% reply rate.
Then I studied 47 top-performing SDRs and found one pattern that changed everything.

[Desire] Here's what they all had in common: [3-paragraph breakdown]
  • Pattern 1: [insight]
  • Pattern 2: [insight]  
  • Pattern 3: [insight]

[Action] Want to see the exact email template I used?
→ [Download the template free]
```

### 3.2 PAC Framework (Problem-Agitate-Solve → Promise-Action-Clarity)

PAC is a variation tailored for modern email, especially in B2B SaaS contexts:

**P — Problem**
- Name the specific problem your reader faces (be as precise as possible)
- "You're sending emails that land in spam" is better than "Email deliverability is a challenge"

**A — Agitate**
- Amplify the problem: what's the cost of not solving it?
- Time lost? Revenue left on the table? Reputational damage?
- Make the reader feel the pain before offering the solution
- "Every email that lands in spam costs you $47 in lost pipeline" — quantify the cost

**C — Clarity (the Promise)**
- Describe precisely what life looks like after using your solution
- Be specific about the transformation, not the features
- "After fixing deliverability, our demo request volume doubled in 60 days"

**Promise-Action-Clarity (Second Half)**
- **Promise**: What you're specifically offering (a guide, a demo, a template)
- **Action**: Exact steps to take ("Reply to this email with your biggest email challenge")
- **Clarity**: What happens next, when, and why it's worth it

### 3.3 Supplementary Copywriting Tactics

**Personalization Beyond "Hi {{first_name}}"**
- Reference their recent content ("I saw your post about email deliverability on LinkedIn")
- Reference a shared connection ("We both know Sarah Chen from Stripe — she suggested I reach out")
- Reference a specific trigger ("Your company just raised Series B, which often comes with...")

**The 3-Second Rule**
- Reader decides to continue or delete within 3 seconds of opening
- Your subject line + preview text + first line must work together as a unit
- Test: open your email in your inbox and ask "would I keep reading this?"

**Emotional Triggers That Work in B2B Email**
- Urgency (real deadlines only)
- Curiosity (gaps in knowledge, not cliffhangers)
- Social proof (peer companies, people, results)
- Exclusivity ("only 12 spots available" if true)
- Loss aversion ("if you're not doing X, you're leaving Y on the table")

---

## 4. Drip Campaign Design

### 4.1 Drip Campaign Fundamentals

A drip campaign is a sequence of pre-written emails sent automatically based on time delays or user actions. Unlike broadcast emails, drip campaigns nurture leads through a defined journey.

**Types of Drip Campaigns**
1. **Welcome sequence** — new subscriber onboarding (3-5 emails, 1 per day)
2. **Lead nurturing** — education sequence for cold/warm leads (5-10 emails, 2-7 days apart)
3. **Trial/demo nurture** — product-focused education during trial period
4. **Re-engagement** — win back inactive subscribers
5. **Post-purchase** — onboarding, upsells, retention
6. **Abandoned cart** — recovery sequences (retail/e-commerce)

### 4.2 The Welcome Sequence (5-Email Template)

| Email | Timing | Goal |
|---|---|---|
| #1: Welcome + deliver on immediate promise | Immediate | Trust building |
| #2: Your story / why you exist | Day 1 | Emotional connection |
| #3: Best content / most popular | Day 2 | Value demonstration |
| #4: What to expect going forward | Day 3 | Set expectations |
| #5: Soft CTA + "where to go next" | Day 4-5 | First conversion ask |

### 4.3 The High-Converting Drip Sequence (Trial Nurture Example)

For SaaS trial users, a proven structure:
- **Email 1** (Day 0 — trial starts): "Welcome to [Product]. Here's what to do first."
- **Email 2** (Day 2): "The #1 thing users forget to do (and why it matters)"
- **Email 3** (Day 5): Social proof — "4 companies like yours saw results in week one"
- **Email 4** (Day 8): Feature deep-dive — address the most common objection
- **Email 5** (Day 12): Case study with specific numbers
- **Email 6** (Day 15 — last trial day): "Your trial ends tomorrow. Here's what you get with paid."
- **Email 7** (Day 18 — post-trial): "We're sad to see you go. Here's a free resource."

### 4.4 Drip Campaign Rules

- **Personalize by segment** — new leads, trial users, and past customers get different sequences
- **Always include an unsubscribe link** (legal requirement in most jurisdictions)
- **Monitor engagement** — remove contacts from sequences if they repeatedly mark as spam
- **One CTA per email** — don't ask people to download a guide AND book a demo in the same email
- **Match the send frequency to the urgency** — welcome sequences can be daily; cold lead nurture should be 3-5 days apart

---

## 5. Email Segmentation Strategies

### 5.1 Why Segmentation Matters

Segmented email campaigns generate **760% more revenue** than untargeted bulk sends (DMA). Every time you send the same email to your entire list, you're leaving personalization upside on the table.

### 5.2 Segmentation Dimensions

**Demographic Segmentation**
- Industry (B2B) / interests (B2C)
- Company size, revenue, headcount
- Job title / seniority level
- Geography / timezone

**Behavioral Segmentation**
- Email engagement (opened, clicked, replied)
- Website behavior (pages visited, content downloaded)
- Purchase history (past buyers vs. new leads)
- Trial status (active trial, expired trial, paid customer)
- Last active date (90-day rule)

**Lifecycle Stage Segmentation**
```
Unknown Visitor
  ↓ (converted via lead magnet)
New Subscriber (Welcome Sequence)
  ↓ (engaged after 30 days)
Active Lead (Nurture Sequence)
  ↓ (took demo/pricing call)
Qualified Prospect (Sales Follow-up)
  ↓ (purchased)
Customer (Onboarding → Retention)
  ↓ (potential churn at 60-90 days)
Lapsed Customer (Re-engagement)
```

### 5.3 Implementation in Klaviyo / Mailchimp

**Klaviyo Segmentation Example**
```
Filter: Email engagement > 0 in last 90 days
AND: Purchased = false
AND: Industry = "SaaS"
AND: Average order value > $0
AND: Email not in list: [Re-engagement Suppression]
→ Send: High-value SaaS Nurture Sequence
```

**Segment Quality Tiers**
- **Hot**: Opened in last 30 days AND clicked ever → send everything, highest volume
- **Warm**: Opened in last 90 days, never clicked → send most content, test carefully
- **Cold**: No engagement in 90+ days → re-engagement sequence or remove
- **Risk**: Never opened ever → remove from active sends

### 5.4 Dynamic Content vs. Segmentation

Sometimes the right answer is *dynamic content* rather than segmentation:
- **Segmentation**: Different email to different groups (cleaner metrics, simpler setup)
- **Dynamic content**: Same email shell, content blocks swap based on subscriber data (higher complexity, higher relevance)

**Rule of thumb:** Segment at the campaign level; use dynamic content for personalization at the block level.

---

## 6. Klaviyo vs Mailchimp for B2B

### 6.1 Platform Overview

**Klaviyo**
- Founded 2014, Boston-based
- Best known for e-commerce (Shopify-native)
- Now rapidly expanding into B2B and multi-channel
- Pricing: free up to 250 contacts, then ~$45/mo for 1,000 contacts
- Primarily B2C-focused but increasingly capable for B2B

**Mailchimp**
- Founded 2001, Atlanta-based (acquired by Intuit 2021)
- Long history in SMB/small agency space
- Rebranded as an "all-in-one marketing platform" post-acquisition
- Pricing: free tier up to 500 contacts, then ~$13-$280/mo based on features
- Strong for small businesses and solopreneurs; less enterprise-ready

### 6.2 Head-to-Head Comparison

| Feature | Klaviyo | Mailchimp |
|---|---|---|
| **B2B Focus** | Moderate (improving) | Moderate |
| **E-commerce Integration** | Exceptional (Shopify, Woo, BigCommerce) | Good (Shopify, Woo) |
| **Email Builder** | Very good | Good (improved recently) |
| **Automation Depth** | Deep, sophisticated | Decent for basic needs |
| **Segmentation** | Best-in-class | Basic |
| **Reporting/Analytics** | Strong | Basic |
| **SMS Integration** | Native | Native |
| **CRM Features** | Minimal | Expanding |
| **Free Tier** | 250 contacts | 500 contacts |
| **Starting Price** | ~$45/1K contacts | ~$13/mo |
| **Best For** | E-commerce brands; B2B with strong data | Small businesses, solopreneurs |

### 6.3 The Verdict for Different Use Cases

**Use Klaviyo if:**
- You're a Shopify or e-commerce brand (no contest — Klaviyo wins)
- You need sophisticated behavioral segmentation
- You have a B2C product with high-volume flows
- Email revenue is a primary business driver
- You need best-in-class SMS + email integration

**Use Mailchimp if:**
- You're a small business or solopreneur with a limited budget
- Your email program is simple (newsletters + basic automations)
- You don't need deep behavioral data or advanced segmentation
- You value an all-in-one platform over specialized email tools
- You're just starting and want the free tier to experiment

### 6.4 Emerging Alternatives Worth Watching

- **Resend**: Developer-focused email platform, clean API, modern UX
- **Loops**: B2B email marketing, excellent deliverability, competitive pricing
- **Beehiiv**: Newsletter-focused, strong growth tools, creator economy
- **Customer.io**: Strong automation for B2B, data-driven segmentation

---

## 7. Key Takeaways & Action Items

### Immediate Priorities (This Week)
1. **Audit your SPF/DKIM/DMARC setup** — use MXToolbox or similar to verify
2. **Review your last 3 campaigns** — check bounce rate (should be <2%), complaint rate (should be <0.1%)
3. **Implement double opt-in** if you're not already using it
4. **Segment your list into at least 3 tiers** (hot/warm/cold) and test sending to hot tier only

### Medium-Term (30-60 Days)
5. **Build a welcome sequence** (5 emails minimum) for new subscribers
6. **Design one lead nurture drip** targeted at your specific buyer stage
7. **Set up re-engagement automation** for contacts inactive 90+ days
8. **A/B test your subject lines** — track open rates and optimize

### Long-Term (Quarterly)
9. **Review email metrics trend** — open rate, click rate, unsubscribe rate, list growth rate
10. **Audit and clean your list** — remove contacts with zero engagement in 180+ days
11. **Set up BIMI** for logo display in inbox clients
12. **Document your email playbook** — segment definitions, trigger logic, A/B test framework

---

*This document should be updated quarterly. Email marketing evolves quickly, especially deliverability rules and platform capabilities.*

**Document Stats:** ~460 lines | Last Updated: 2026-04-22
