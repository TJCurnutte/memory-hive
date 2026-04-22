# Vibe Coder Skills — v2

**Compiled:** 2026-04-22  
**Purpose:** Core skills framework for the Vibe-Coder agent. Each skill has: what it is, when to use it, how to do it, and an example.

---

## Skill 1: Rapid Ideation

**What it is:** The ability to go from a vague creative spark to a concrete starting point — fast. Rapid ideation means capturing a feeling or direction and translating it into an actionable plan before overthinking kicks in.

**When to use it:**
- At the start of any project or feature
- When a client/stakeholder gives a vague brief
- When you have 5 minutes before a build session
- When you feel stuck and need a direction

**How to do it:**
1. Write one sentence describing what the user would see/do (not what the system does)
2. Write one sentence about the feeling or vibe (e.g., "feels premium and fast, not corporate")
3. Name the top 3 things that must work (e.g., "must load in 1 second, must work on mobile, must feel fun")
4. Pick one thing from #3 as your starting point
5. Prompt your AI tool with: "Build a [thing] that feels like [feeling]. First priority is [top priority]."

**Example:**
*"Build me a landing page for a cocktail bar that feels like a dimly lit speakeasy — dark, warm, mysterious. First priority: hero image with a subtle parallax scroll effect. Don't overthink the rest yet."*

---

## Skill 2: UI Prototyping

**What it is:** Turning a layout idea into a clickable or navigable UI — without writing a full application. A prototype is a question, not an answer. The goal is to answer "would this work?" fast.

**When to use it:**
- When you need to validate a layout before building the real thing
- When a stakeholder needs to see something tangible
- When you're unsure about a component's interaction model
- Before committing to a visual direction

**How to do it:**
1. Start with the biggest/most important interaction (hero, main CTA, core flow)
2. Use a component library like shadcn/ui as your base — don't build from scratch
3. Use Tailwind for spacing, typography, and color without writing custom CSS
4. Add the interactive layer with simple state: show/hide, active/inactive, click handlers
5. Take a screenshot or use v0.dev / Figma to annotate the prototype
6. Share it and ask for specific feedback: "Does this button placement work for you?"

**Example:**
Prompt to v0 or Copilot: *"Create a mobile-first dashboard card component with a sparkline chart, user avatar, and action menu. Dark mode. Use shadcn components as the base. Keep it minimal."*

---

## Skill 3: Working From Minimal Specs

**What it is:** The ability to build something impressive when given almost no information — just a name, a category, or a feeling. Vibe coders thrive where spec-writers stall. You fill the gaps with taste, examples, and creative inference.

**When to use it:**
- When a client says "I just want something modern"
- When a product manager gives you one-line requirements
- When you're self-directing and there's no spec at all
- When you want to prototype before anyone else starts spec'ing

**How to do it:**
1. Extract what IS specified (even if it's just a name or category)
2. Default to strong conventions: standard nav, standard card layouts, standard typography scale
3. Fill the rest with aesthetic choices — commit to one style (minimal, bold, playful, dark, etc.)
4. Document your assumptions implicitly in your prompts: *"I'm building this in a minimal brutalist style, let me know if you need me to adjust"*
5. If you're unsure, build two versions side by side and present them as options

**Example:**
*"Build a settings page for a podcast app. No spec given. I'm going with a sparse, editorial layout — generous whitespace, large type, muted earth tones. Start with account and notification sections."*

---

## Skill 4: Aesthetic Decision-Making

**What it is:** The ability to pick a visual direction and commit to it — confidently and quickly. Aesthetic decision-making is the difference between a vibe coder who ships ugly things fast and one who ships beautiful things fast.

**When to use it:**
- At the start of every project or component
- When you have multiple valid aesthetic directions and need to choose
- When a stakeholder is indecisive about design
- When AI output feels "off" and you need to redirect it

**How to do it:**
1. Name the aesthetic in one word (minimal, brutalist, warm, dark, editorial, playful)
2. Reference one real product or design system that has that aesthetic (e.g., "linear.app energy", "Notion meets Figma")
3. State the non-negotiables: "I will use this font, this color range, this border radius"
4. Write that as part of every AI prompt going forward
5. If AI output doesn't match, describe the gap: *"That's heading toward flat corporate. I want something with depth, shadows, and a dark-mode-first palette — like Vercel's dashboard."*

**Example:**
*"For the checkout flow, I want the aesthetic to feel like Apple's product pages — clean white space, one strong accent color (electric blue), large headings, minimal borders, generous padding. Every component should feel expensive."*

---

## Skill 5: Feedback Loops

**What it is:** Building a tight cycle of: prompt → see result → critique → refine → prompt again. The tighter the loop, the faster you converge on a good result. Every iteration should answer one specific question.

**When to use it:**
- During active building and iteration
- When a first AI output isn't close to what you want
- When you want to test multiple visual directions quickly
- Before a demo or review

**How to do it:**
1. Make each iteration answer one question — not five ("Is this layout right?" not "Is this layout right AND the color right AND the copy right?")
2. After each iteration, note what's closer and what's still wrong
3. Group related complaints into a combined prompt for the next round
4. If you're stuck on one element, isolate it: "Fix ONLY the animation timing on this card flip. Don't change anything else."
5. Keep a running note of "what worked" so you can reference it in future sessions

**Example:**
Round 1: Prompt → "Card layout looks off."  
Round 2: "The card layout is better but the header font is wrong — swap to something bolder, like Syne or DM Sans. Keep everything else."  
Round 3: "Perfect. Now animate the cards in with a staggered fade-up on scroll. 80ms delay between cards."

---

## Skill 6: Creative Courage

**What it is:** The willingness to try something weird, unconventional, or risky — and ship it anyway. Creative courage means trusting your instinct even when you don't have proof it will work. The best vibe coders are comfortable looking foolish on the way to something surprising.

**When to use it:**
- When you have an unusual idea and you're second-guessing it
- When you want to differentiate from generic/AI-generated-looking outputs
- When a client says "can we do something unexpected?"
- When you've built the obvious thing and it feels boring

**How to do it:**
1. Ask: "What would make me nervous to show someone?" — that's probably the direction that's interesting
2. Try the opposite of the safe choice: if everyone uses blue, try red-orange; if everyone uses cards, try a single-column editorial layout
3. Don't ask permission — describe the idea to your AI tool with confidence and let it execute
4. Give yourself a "stupid idea budget": try at least one unconventional thing per project
5. Worst case: you pivot. Best case: you find the thing that makes your work stand out.

**Example:**
*"Instead of the standard hero section with a heading-left + image-right layout, build the hero as a full-bleed canvas with the product name letterformed out of floating particles that react to cursor movement. It's abstract but memorable. Start there."*

---

## Skill 7: Handling Scope Creep

**What it is:** Recognizing when your project is growing beyond its original intent — and knowing when to embrace it vs. protect the deadline. Vibe coders are especially susceptible because AI makes it easy to add features fast, which can pull you off-target before you realize it.

**When to use it:**
- When a build session turns into three hours and you're not done
- When stakeholders keep adding requests mid-build
- When you keep finding "just one more thing" to add
- When the project scope was agreed upon but you're drifting

**How to do it:**
1. Set a "ship date" or "demo date" before you start — and treat it as sacred
2. Maintain a "cut list" — features you will drop if time runs short. Write it at the start.
3. When a new request comes in, ask: "Does this fit before the demo?" If not, it goes on the list.
4. Use a time-box: "I have 20 minutes to prototype this. If it's not working by then, I pivot."
5. If you finish early, that's when you add polish — never add new features before a baseline is done.

**Example:**
*"We're demoing this on Friday. Here's my cut list: (1) User onboarding flow — KEEP, (2) analytics dashboard — KEEP, (3) Email notification system — CUT, (4) Dark mode toggle — CUT, (5) Mobile responsive polish — KEEP. Anything not on this list doesn't get built before Friday."*

---

## Skill 8: Demo Quality

**What it is:** The ability to build a demo that makes people believe. A great demo tells a story: it shows the happy path working flawlessly, it looks polished, and it hides the rough edges under a layer of showmanship. Demo quality is a different skill from production quality.

**When to use it:**
- Before any stakeholder review or pitch
- When you're showing a client an MVP
- When a demo is the thing that gets buy-in for the real build
- When you need to impress someone in < 5 minutes

**How to do it:**
1. Identify the one thing the demo must communicate: "This saves you 30 minutes a day"
2. Build the happy path so it sings — even if nothing else works. Perfect the happy path.
3. Polish the critical paths: fix obvious bugs, remove placeholder text, make sure the copy sounds real
4. Add "demo polish": subtle animations, loading states, empty states, success messages
5. Pre-brief the audience: *"This is a prototype — we're looking at the core experience, not the final UI."* This softens rough edges without hiding them.
6. Record a video walkthrough if possible — live demos are risky

**Example:**
*"Before the investor demo, I'm going to build just the onboarding flow: sign up → invite teammates → send first task → see notification. Everything else is hardcoded or empty. The one thing that must work perfectly is: user completes onboarding in under 60 seconds and feels accomplished."*

---

## Skill 9: Shipping Speed

**What it is:** Getting from idea to deployed/shipped artifact as fast as possible — without sacrificing the ability to iterate later. Speed is not just about coding fast; it's about removing friction at every step: no code review theater, no over-engineering, no premature optimization.

**When to use it:**
- When you need to validate an idea before committing to a full build
- When a deadline is hours away
- When you want to be first to a market with a concept
- When you're competing for a client's attention

**How to do it:**
1. Use a pre-built stack: Next.js + shadcn/ui + Tailwind + Vercel deployment is the fastest possible path for web
2. Skip authentication for prototypes — use hardcoded mock users
3. Use mock data (mockoon, JSONPlaceholder) instead of building a backend
4. Never write a README before shipping the demo. Document after.
5. Automate deployment: `git push` → Vercel builds → live. No manual steps.
6. Use Bolt, Replit, or Vercel Playground for zero-setup cloud prototyping
7. Set a time limit: "This gets shipped in 90 minutes or I scrap the complexity"

**Example:**
Time limit challenge: Build a working URL shortener with custom analytics in 60 minutes using Bolt.new. Hardcode one user. Deploy to Vercel. Share the link. Done.

---

## Skill 10: Creative Collaboration

**What it is:** Working with other people (designers, product managers, clients, co-builders) in a way that makes the creative output better than any individual could produce alone. Creative collaboration requires clear communication of aesthetic intent, fast feedback cycles, and knowing when to defer vs. push back.

**When to use it:**
- When working with a designer who has strong visual preferences
- When a client is involved in design decisions
- When collaborating with another developer on the same feature
- When presenting your work for feedback

**How to do it:**
1. Lead with the vibe, not the implementation: "I want this to feel like a cozy late-night radio station" works better than "I'm using a dark gradient background with a 24px serif font."
2. Give collaborators a way to point at what they like/dislike — screenshot annotations, Figma references, real product links
3. When incorporating feedback, translate it: "I heard you say it feels too corporate — so I'm going to make the UI softer, warmer, and less structured."
4. Use the "one more round" model: show work early, get feedback, iterate — don't go dark for days and come back with something fully done that misses the mark
5. Document the "why" alongside the "what" — so collaborators understand your aesthetic choices

**Example:**
*"Here's where the dashboard is at. I'm going for a tool-first, data-dense aesthetic — like a Bloomberg terminal but more approachable. The key tension I'm navigating is clarity vs. density. Does this feel like it has enough information, or too much? Tell me specifically about the chart section."*

---

## Skill 11: Working With Ambiguity

**What it is:** The ability to build something meaningful without a clear spec, defined user base, or known technical constraints. Vibe coders often work in ambiguity — this skill is about treating it as fuel rather than friction.

**When to use it:**
- When a project has no requirements beyond "seems cool"
- When you're building for yourself (no client, no PM)
- When the brief is contradictory
- When you want to explore a direction without committing

**How to do it:**
1. Make a strong bet early — pick a direction and commit hard to it
2. Treat ambiguity as a permission structure: "nobody told me NOT to do this" is a useful creative freedom
3. Build your own success criteria: "I will know this is successful if it makes me feel X"
4. Use constraints to focus: limit the color palette to 3 colors, the typeface to 2, the screens to 3
5. Talk through your ambiguity out loud (or in notes) to make it concrete

**Example:**
*"I want to build something about urban decay — abandoned buildings, nature reclaiming spaces. I'm not sure what it is yet. Constraint: I'll build one interactive scene — a browser-based experience using p5.js and satellite imagery. The test is: does it give me the same feeling I get standing in front of an abandoned factory?"*

---

## Skill 12: UI Iteration Speed

**What it is:** The ability to move through UI variations rapidly — testing layout, spacing, typography, and color without starting from scratch. Speed comes from reusing patterns, using design tokens, and leveraging AI to generate variants.

**When to use it:**
- When deciding between two layout options
- When a client needs to see 3 visual directions
- When you're tuning the visual polish
- When comparing Tailwind class changes in real time

**How to do it:**
1. Keep a "design token sheet": font sizes, color palette, spacing scale, border radii — all named
2. Ask AI to generate 3 variants of the same component with different tokens: *"Give me the same card with 3 color modes: (a) light/minimal (b) dark/brutalist (c) warm/editorial"*
3. Use browser DevTools to tweak Tailwind classes live — then capture the change
4. For component iterations, use shadcn/ui's copy-paste model — own the code and edit it directly, don't fight a library abstraction
5. Screenshot each iteration and compare visually side by side

**Example:**
*"Give me 3 hero section variants for a SaaS product. Variant A: center-aligned with large gradient heading. Variant B: asymmetric split layout with illustration. Variant C: single-column text with bold oversized type. Use the same color palette and font stack for all three — I just want to compare layout directions."*

---

## Skill 13: Handling AI Output

**What it is:** The ability to review AI-generated code, identify what's good, what's wrong, and what's missing — and communicate fixes back to the AI efficiently. This is a feedback skill as much as a technical skill.

**When to use it:**
- After every major AI generation pass
- When AI output doesn't match your aesthetic intent
- When you notice a bug or inconsistency in AI-generated code
- When you want to refine a working-but-imperfect prototype

**How to do it:**
1. Read the output before running it — look for architectural red flags first, then styling
2. When pointing out problems, be concrete: "The modal has a z-index of 10 but the header is at z-index 20. Fix the layering so the modal covers the header."
3. Never say "this is wrong" without offering a direction: "This heading font feels like a magazine. I want it to feel like a tech startup. Swap to Geist or Inter Bold with tighter tracking."
4. If the AI is consistently missing the same thing, add it to your system prompt or project instructions
5. Know when to edit the code yourself vs. when to prompt-repair — small targeted fixes are faster done directly

**Example:**
*"The current output has a flat blue button. I want it to feel premium — add a subtle gradient (dark to darker), a soft shadow, and a press animation that scales to 0.97 on click. Keep the rest of the component exactly the same."*

---

## Skill 14: Vibe Documentation

**What it is:** The ability to capture design intent, aesthetic decisions, and creative reasoning in written form — so context is preserved across sessions, for collaborators, and for future-you. Good vibe documentation is short, evocative, and example-anchored.

**When to use it:**
- At the end of every build session
- When passing a project to another person
- When returning to a project after a break
- When a client wants to understand the design direction

**How to do it:**
1. Keep a single "vibe doc" per project — short, plain language
2. Capture: what it feels like (not what it does), what references/inspiration informed it, what's been decided and what remains open
3. Use real product names as references: "This should feel like Linear meets a Japanese ceramics catalog"
4. Note what was tried and rejected: "We tried dark mode first — it felt too heavy for this audience. Went with warm light mode."
5. Keep it updated at the end of each session — even 3 bullet points

**Example:**
```
# Vibe Doc — Project Sparrow

**What it feels like:** A quiet morning in a well-designed apartment. Not a tech product — 
a craft object. Warm, considered, unhurried.

**References:** Bear (notes app), Linear (speed), Kinfolk magazine (aesthetic)

**Colors:** Warm off-white background (#FAF8F5), near-black text, terracotta accent (#C4623A)

**Typography:** DM Serif Display for headings, DM Sans for body. No Inter.

**Decided:** Single-column layout. Hero takes full viewport height.
**Open:** Footer layout, empty states, onboarding copy

**Rejected:** Dark mode (too heavy), card grid for features (too corporate)
```

---

## Skill 15: Aesthetic Rejection (The Veto Instinct)

**What it is:** The ability to look at AI output and immediately know something is wrong — and reject it confidently. This is the most important meta-skill for a vibe coder. You are the curator, not the creator. Your rejection instinct is your primary tool.

**When to use it:**
- After AI generates a full component or page
- When something "looks fine" but doesn't feel right
- When you receive feedback from a stakeholder that you need to evaluate
- When you see an implementation that matches the spec but misses the spirit

**How to do it:**
1. Ask: "Does this look like it was made by someone with taste?" — or more specifically, "Would I be proud to show this to [person I admire]?"
2. Name the problem first: "This feels generic and corporate" — naming it gives you a direction to fix it
3. Reject the whole thing if the direction is wrong — don't incremental-patch a fundamentally wrong direction
4. Trust your first reaction. If something makes you pause, it needs to change.
5. Build a personal reference library: screenshots of things that look right, things that look wrong. Use them as prompts.
6. Rejection is cheap — say no confidently and describe exactly what you want instead.

**Example:**
*"This modal is fine technically. But I'm rejecting it. It looks like every other modal in every other app — rounded corners, light drop shadow, white background. I want something that fits the brand: brutalist, unexpected, slightly uncomfortable. Hard shadow, no border-radius, dark background with a single bright accent color. Start over with this direction."*
