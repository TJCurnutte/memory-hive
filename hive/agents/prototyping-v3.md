# Rapid Prototyping Mastery — Vibe Coder Learning
*Generated: $(date)*

## 1. The Prototyping Mindset

### What Makes a Prototype "Good"?

A prototype's value isn't measured by how polished it looks—it's measured by:
- **Speed of creation** — Can you get to a demo in hours, not weeks?
- **Learning generated** — Does it answer the right question?
- **Signal clarity** — Can stakeholders make decisions based on it?
- **Iteration cost** — How easy is it to change?

### The Prototype Spectrum

```
Paper Mockup → Wireframe → Clickable Prototype → Functional Prototype → MVP
   ↑                    ↑                         ↑
   Fastest, cheapest    Mid-fi, interaction        High-fi, real data
```

### Golden Rule
**Build the simplest thing that will answer your question.**

- If you're testing navigation → paper is fine
- If you're testing data flows → wireframe with annotations
- If you're testing UX → clickable prototype
- If you're testing technical feasibility → functional prototype
- If you're testing market fit → MVP

## 2. Design Sprints (Google Ventures Method)

### 5-Day Sprint Structure

**Monday: Map**
- Define the problem (HMW statements)
- Sketch user journey
- Identify target dates and outcomes
- Pick a sprint target question

**Tuesday: Sketch**
- Lightning demos (inspiration research)
- Four-step sketch (notes, ideas, roughs, solution)
- Solution sketch (detailed, annotated)

**Wednesday: Decide**
- Decide on the best solution
- Storyboard the prototype
- Plan the test script

**Thursday: Build**
- Fake it till you make it
- Build the prototype
- Role-play the testing

**Friday: Test**
- Conduct user interviews
- Debrief and synthesize learnings
- Document insights

### Sprint Cheats
- Limit team to 5-7 people
- Remove all distractions
- Decisions by "super-vote" when stuck
- Prototype for ONE user scenario, not all
- Avoid "we'll iterate later"—document decisions

## 3. No-Code Tools Deep Dive

### Webflow

**Best for:** High-fidelity websites, marketing sites, portfolios

**Key Features:**
- Visual CMS with relational databases
- CMS collections (dynamic content)
- Memberships and authentication
- E-commerce (Shopify integration or native)
- Interactions and animations
- Export to clean code

**Rapid Prototyping with Webflow:**
```
1. Choose a starting template or blank canvas
2. Set up a CMS collection for content
3. Build section by section (hero → features → pricing → footer)
4. Add interactions (scroll-triggered animations, hover states)
5. Connect forms to Webflow's built-in or Zapier/Make
6. Publish and share
```

**Complex Features:**
- Custom code embeds (HTML/CSS/JS)
- Memberstack for advanced auth
- Finsweet for utility components
- Relume for AI wireframes (integrated with Webflow)

### Bubble

**Best for:** Web apps, marketplaces, SaaS products

**Key Features:**
- Visual programming (no code)
- Database with relations
- Workflows (IF/THEN logic)
- Plugins for integrations
- Custom workflows with JavaScript
- Responsive design

**Bubble Limitations to Know:**
- Performance with large datasets (optimize with pagination)
- Mobile apps require wrapping (native iOS/Android not native)
- Complex logic can get messy (plugin ecosystem helps)

**Bubble Prototyping Speed:**
- Basic app: 2-4 hours
- Database-driven app: 1-3 days
- Full MVP: 2-4 weeks

**Speed Optimization:**
- Use plugins (don't build everything from scratch)
- Leverage templates (Appgyver, Briq, Zeroqode)
- Start with Bubble's responsive engine, don't fight it
- Test on mobile early (different from desktop preview)

### Framer

**Best for:** High-fidelity interactive prototypes, landing pages, portfolios

**Key Features:**
- Figma-like design + code
- CMS and collections
- Animations and interactions
- Auth and user management
- A/B testing built-in
- AI page generation

**Framer Power Moves:**
```javascript
// Custom code overrides
// Scroll effects
const scrollY = useScroll()
// Parallax effects
const translateY = useTransform(scrollY, [0, 500], [0, -100])

// State-based animations
const [hovered, setHovered] = useState(false)

// Conditional rendering with scroll
const opacity = useTransform(scrollY, [100, 200], [0, 1])
```

**Framer vs Webflow:**
- Framer: Better for highly interactive, animated sites
- Webflow: Better for content-heavy sites with CMS
- Both: Great for rapid prototyping

### Adalo

**Best for:** Simple apps, internal tools

**Pros:**
- Easy database setup
- Drag-and-drop components
- Native-feeling iOS/Android apps
- Good for simple CRUD apps

**Cons:**
- Limited customization
- Performance issues with complex apps
- Limited third-party integrations

### Softr + Airtable

**Quick app from existing data:**
```
1. Set up Airtable base (tables, fields, sample data)
2. Connect to Softr
3. Choose theme/template
4. Configure access (public, logged in, role-based)
5. Add pages (list, detail, form)
6. Customize styling
7. Publish
```

### Glide

**Best for:** Simple apps from Google Sheets

**Strengths:**
- Connects to Google Sheets
- Extremely fast setup
- Great for internal tools
- Mobile-first design

**Limitations:**
- Limited to spreadsheet-like data
- Can't handle complex business logic
- Smaller customization range

## 4. Low-Code Platforms

### Xano

**Best for:** Backend-first apps, complex API requirements

**Features:**
- Visual database builder
- API endpoints (auto-generated + custom)
- Function builder (Node.js)
- Authentication
- Real-time subscriptions
- External API integrations

**Speed:** Backend in hours, full stack in days

### Supabase

**Best for:** Developers who want code but less boilerplate

**Features:**
- PostgreSQL database
- Auth (email, OAuth, magic links)
- Real-time subscriptions
- Edge functions
- Storage
- Studio (database GUI)

**Stack example:**
```
Supabase (backend) + Flutter (iOS) = MVP in 1 week
Supabase (backend) + React (web) = MVP in 1 week
Supabase (backend) + No-code tool (bubble/softr) = MVP in 1-2 weeks
```

### n8n + Make (Integromat)

**For automation and integrations:**

```javascript
// n8n: Build integrations visually
Trigger (Webhook/API/Timer) → Transform data → Send to external service

// Common patterns:
1. Webhook → Parse → Insert into database → Send Slack notification
2. Schedule → Fetch from API → Transform → Update Airtable → Email report
3. Form submit → AI processing → Generate response → Send to user
```

### WeWeb + Xano

**Frontend (WeWeb) + Backend (Xano) = Full-stack MVP**

```
WeWeb: Visual builder, auth, CMS, complex interactions
Xano: Database, APIs, business logic, external integrations

Timeline: 1-2 weeks for functional MVP
```

## 5. MVP Strategies

### MVP Definition by Stage

**Demo MVP (For investors/demos):**
- Looks real, works enough for screenshot demos
- Fake data that looks real
- Core flows only
- May not scale

**Internal MVP (For team validation):**
- Real data, real logic
- Single user (you) in many cases
- Basic error handling
- Can iterate fast

**Launch MVP (For real users):**
- Production-ready (errors, edge cases handled)
- Security basics covered
- Performance acceptable
- Documentation for team

### The "Hello World" MVP Frame

Always start with the simplest version:

```python
# MVP v1: 1 feature, 1 user, 1 page
# If it's a SaaS:
- Landing page (with sign-up form)
- Authenticated dashboard (with "Coming soon" for most features)
- ONE core feature that actually works

# If it's an app:
- 1 screen that does 1 thing really well
- Minimal onboarding
- Core value delivered in < 2 minutes
```

### Features to Cut (That Founders Always Include)

❌ User profiles with avatars and settings
❌ Notifications and emails (at first)
❌ Analytics dashboard
❌ Admin panel
❌ Mobile app (start with web)
❌ Multi-tenancy
❌ Advanced search
❌ Export/import functionality
❌ Social features
❌ Payments (use manual at first)

### The "Manual First" Approach

Before building software:
1. **Do it manually** — Validate demand by doing the work yourself
2. **Charge money** — Get real payment, not just interest
3. **Automate later** — Once validated, build software to replace manual work

```
Example: Airbnb didn't start with a booking system.
They made a website, manually managed listings via email, and charged via PayPal.
Only when the volume was unsustainable did they build the platform.
```

### Build-Measure-Learn Loop

```
BUILD → MEASURE → LEARN
  ↑               |
  └───────────────┘
  
Tools:
- Build: Any of the no-code/low-code tools above
- Measure: Google Analytics, Mixpanel, Amplitude, or simple spreadsheets
- Learn: Customer interviews, session recordings (Hotjar), heatmaps
```

## 6. Getting to Demo Fast

### The Demo-Ready Checklist

```
Core flow works (start to finish, no dead ends)
├── User can log in/sign up
├── User can complete the primary action
├── User can see the result of their action
└── Error states are handled gracefully

Visuals are presentable
├── No placeholder text except intentional
├── No broken images
├── No layout glitches on main screen sizes
└── Navigation is discoverable

Performance is acceptable
├── Page loads in < 3 seconds
├── Interactions respond in < 1 second
└── No obvious bugs in happy path

Context is understood
├── Product is named
├── Value proposition is clear
└── User knows what to do next
```

### Quick Demo Setup

**For in-person demos:**
1. Use localhost or staging environment
2. Clear demo data before (reset database)
3. Have a script (don't improvise on first run)
4. Practice the demo 3+ times
5. Prepare for "what if it breaks" scenarios
6. Record a backup video

**For async demos (video/screen share):**
1. Record walking through the key flow
2. Show before/after (problem → solution)
3. Keep it under 2-3 minutes
3. Add narration
4. Upload to Loom, Vidly, or cloud storage

### Demo Environment Setup

```bash
# Separate demo database (never pollute production)
# Clear state before each demo
# Pre-populate realistic sample data
# Have "demo mode" flags for edge case simulation

# Quick reset script
npm run db:reset:demodata
npm run seed:demo
```

## 7. Handling Edge Cases in Prototypes

### The Edge Case Spectrum

```
Happy Path (80% of cases)
    ↓
Edge Cases You Can Ignore (10%)
    ↓
Edge Cases You Must Handle (10%)
```

### Which Edge Cases to Handle?

**Must handle:**
- Empty states (no data)
- Loading states (async operations)
- Error states (API failures, validation errors)
- Empty form submissions
- Very long inputs (names, descriptions)
- Network offline scenarios (if critical)

**Can ignore in prototype:**
- Race conditions
- Concurrent edit conflicts
- Extremely rare validation errors
- Mobile browsers other than Safari/Chrome
- Accessibility compliance (MVP stage)

### Quick Edge Case UI Patterns

```jsx
// Empty state component
const EmptyState = ({ message, action }) => (
  <div className="text-center py-12">
    <p className="text-gray-500 mb-4">{message}</p>
    {action && (
      <Button onClick={action.onClick}>{action.label}</Button>
    )}
  </div>
)

// Error state component
const ErrorState = ({ error, onRetry }) => (
  <div className="p-4 bg-red-50 border border-red-200 rounded">
    <p className="text-red-700">Something went wrong: {error.message}</p>
    <button onClick={onRetry} className="text-red-600 underline mt-2">
      Try again
    </button>
  </div>
)

// Loading skeleton
const LoadingSkeleton = () => (
  <div className="animate-pulse space-y-4">
    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
  </div>
)
```

### The "Graceful Degradation" Pattern

```javascript
// Try the ideal path, fall back gracefully
async function loadData() {
  try {
    const data = await api.getData() // ideal path
    setData(data)
  } catch (error) {
    // Fallback: show cached data, error message, or retry button
    if (cachedData) {
      setData(cachedData)
      toast.warn('Showing cached data')
    } else {
      setError('Unable to load data. Please try again.')
    }
  }
}
```

### Fake Data That's Believable

```javascript
// Company names: Use real-sounding names
const companies = ['Acme Corp', 'Globex Industries', 'Initech', 'Massive Dynamic']

// Emails: Use realistic formats
const email = (name) => `${name.toLowerCase().replace(' ', '.')}@company.com`

// Dates: Use relative times
const recent = '2 days ago'
const upcoming = 'in 3 weeks'

// Numbers: Use meaningful ranges
const userCount = Math.floor(Math.random() * 1000) + 100
const revenue = `$${(Math.random() * 100000).toFixed(2)}`
```

## 8. Figma to Production Speed

### The Figma-to-Code Handoff

**Setup:**
1. Use auto-layout (Figma's power feature)
2. Set up component variants systematically
3. Use consistent naming (btn-primary-md, input-default-lg)
4. Add annotations for developer notes
5. Export specs with DevOps plugin (Marketch, FigmaTokens)

**Rapid workflow:**
```
Figma → Export CSS → Tailwind conversion → Component code

Or:
Figma → Relume → Webflow/Framer
```

### Prompt-to-Page (AI-Assisted)

**Tools:**
- Relume (AI wireframes from sitemap)
- Framer AI (page from description)
- Builder.io (code from design)
- Locofy (Figma to React code)
- Anima (Figma to code)

**Workflow:**
```
1. Describe page in text
2. AI generates design/code
3. Iterate based on feedback
4. Export and refine
```

## 9. Testing & Validation

### MVP Testing Framework

**Question:** What do we need to learn?

| Question | Test Method | Prototype Required |
|----------|-------------|-------------------|
| Do users want this? | Landing page test (sign-ups) | Minimal |
| Can users use it? | Usability test | Functional prototype |
| Will users pay? | Pre-sale | Demo + payment link |
| Do developers trust it? | Code review/demo | Working prototype |

### Lean Testing Methods

**Smoke tests:**
- Can user complete primary action in under 60 seconds?
- Is the value proposition clear in under 10 seconds?
- Does the UI feel responsive (< 1s response)?

**Preference tests:**
- Show 2 options, ask which they'd use
- Don't ask "which is better" — ask "which would you use"

**Concierge test:**
- Do manually what you plan to automate
- Learn what automation needs to do
- Build for those specific needs

## 10. Rapid Iteration Frameworks

### Build-Learn Loop (Weekly)

```
Monday: Build (last week's learnings → code)
Tuesday: Build
Wednesday: Build + internal test
Thursday: External test with 1-3 users
Friday: Analyze feedback, write learnings
Weekend: Plan next week's build
```

### The 1-Page Sprint Retrospective

```markdown
## Sprint Retrospective [Date]

### What worked:
- [Bullet points]

### What didn't:
- [Bullet points]

### Next sprint changes:
- [Bullet points]

### Top 3 learnings:
1. [Learning]
2. [Learning]
3. [Learning]
```

### Version Naming for MVPs

```
v0.1: Proof of concept (might break)
v0.3: Demoable (stable demo flow)
v0.5: Alpha (first real users, watch closely)
v0.7: Beta (broader release, bug fixing)
v1.0: Launch (production-ready)
```

## 11. Tool Selection Guide

| Need | Tool | Why |
|------|------|-----|
| Landing page, fast | Webflow, Framer | Beautiful, quick |
| Web app, complex logic | Bubble, WeWeb | Full-stack |
| Mobile app, simple | Adalo, Glide | Native feel, easy |
| Backend, APIs | Xano, Supabase | Speed, scalability |
| Automation | Make, n8n | Visual, powerful |
| Landing page test | Carrd, Framer | $10-20/month |
| Interactive prototype | ProtoPie, Principle | Desktop native, advanced |
| Clickable prototype | Figma, Axure | Design-native, web |

## 12. Timeline Estimation

### By Complexity

| Project | No-code | Low-code | Custom |
|---------|---------|----------|--------|
| Landing page | 2-4 hours | N/A | 1-2 days |
| Simple form + DB | 1-2 days | 1 day | 3-5 days |
| Authenticated app | 3-7 days | 2-4 days | 1-2 weeks |
| Marketplace | 1-3 weeks | 1-2 weeks | 4-8 weeks |
| SaaS product | 2-4 weeks | 2-4 weeks | 8-16 weeks |
| Complex marketplace | 1-2 months | 1-2 months | 3-6 months |

### Buffer Multiplier

Always multiply estimates by 1.5x for:
- New tool learning curve
- Edge cases
- Testing and bug fixing
- Stakeholder revisions

## 13. Resources & References

### Documentation & Learning
- GV Sprint: https://sprintstudio.com/resources/
- No-code communities: Bubble forums, Webflow university
- ProtoPie: https://www.protopie.io/learn
- Xano: https://docs.xano.com

### Templates & Starters
- Bubble templates: Zeroqode, Briq
- Webflow templates: Finsweet, Flowbase
- Framer templates: Framer marketplace

### Communities
- Indie Hackers (validation strategies)
- Product Hunt (launch feedback)
- No-code Twitter community
- Maker communities on Discord (Ship Fast, etc.)

---

*End of Rapid Prototyping Mastery*
