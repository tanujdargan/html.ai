# html.ai - Devpost Submission

## Inspiration

### The Identity Problem

Every user has an identity, but most products treat identity as static. Traditional A/B testing optimizes for the "average user," finding one winning design for everyone. But users aren't average. They're individuals with constantly shifting psychological states.

We asked ourselves: **What if identity wasn't a fixed label, but an adaptive experience that evolves in real time?**

Users reveal their psychological state through micro-behaviors: how fast they scroll, whether they rage-click, how long they hover. These signals are gold mines of intent that current systems ignore.

### The Business Problem

Only giants like Amazon have access to real-time personalization. Small sellers are stuck with generic, one-size-fits-all websites.

We built html.ai to give every entrepreneur the same AI-driven optimization that tech giants use. We're building it as an open source project with a B2B model that enables cross-business intelligence.

## What it does

**html.ai** is an adaptive identity engine that continuously learns a user's behavioral identity from their actions and serves personalized UI variants in real time using a coordinated AI system.

### The Core Innovation: Hyper-Personalization at the Session Level

Instead of showing everyone the same "winning" variant from an A/B test, html.ai maintains a dynamic profile for each user and adapts the experience based on their **current psychological state**:

- **Confident Buyer**: Sees minimal, high-trust UI with strong CTAs ("Buy Now")
- **Overwhelmed Explorer**: Gets simplified layouts, fewer choices, guided navigation
- **Ready to Decide**: Receives urgency signals, comparison tools, social proof
- **Cautious Researcher**: Sees detailed specs, reviews, trust badges

### How It Works (AI Pipeline)

1. **Behavioral Tracking**: Monitors user actions across websites (clicks, hovers, scroll patterns, time on page) and sends signals to the backend via our lightweight JavaScript SDK

2. **Identity Interpretation (Gemini 2.0 Flash)**: Analyzes behavioral signals (exploration patterns, hesitation, engagement depth, decision velocity) and classifies users into psychological states using AI reasoning

3. **Variant Optimization**: Maintains a MongoDB database of HTML variants, tracks performance metrics (conversion rates, engagement time), and continuously learns which variants work best

4. **Dynamic Rendering**: Serves the optimal variant in real-time by injecting personalized HTML directly into the page using our `<ai-optimize>` custom element

**📚 [Check out our developer documentation](https://github.com/tanujdargan/html.ai#readme)** for implementation guides, API reference, and code examples.

### Cross-Site Intelligence

When a user visits multiple sites in the network, html.ai syncs their identity and transfers learned behavioral patterns. If the system learns "Green Buttons" are performing poorly across all fashion sites, it stops suggesting them for new clients in that vertical.

## How we built it

**Frontend**: Lightweight JavaScript SDK with custom `<ai-optimize>` HTML elements. Framework-agnostic (works with React, Vue, plain HTML). First-party tracking pixel for cross-domain identity syncing.

**Backend**: Python FastAPI server with MongoDB Atlas for storing behavioral events and variant performance. Real-time event ingestion processing 100+ events/second.

**AI**: Google Gemini 2.0 Flash for behavioral analysis and psychological state classification. Sub-200ms inference for real-time personalization.

**Analytics**: Real-time dashboard with Shopify Polaris design. Carousel displaying live variant HTML previews, conversion metrics, and identity distribution.

**Demo**: Two e-commerce sites ("Shoopify" and "Amazoon") showing cross-site intelligence in action.

## Challenges we ran into

**Cross-Domain Identity Tracking**: Browsers block third-party cookies. We solved this with first-party tracking pixels and `localStorage` + server-side session tokens. Took 8+ hours debugging Safari's ITP and Chrome's SameSite policies.

**Variant Injection Flickering**: Waiting for AI classification caused 200-500ms blank screens. We implemented default variants that show instantly, then smoothly fade to AI-selected variants with CSS transitions.

**Gemini API Consistency**: Getting structured JSON was challenging. We used Pydantic models for strict validation, detailed prompt engineering, and retry logic with exponential backoff.

**Dashboard Performance**: Loading took 5+ seconds with client-side aggregation. We moved to MongoDB's aggregation pipeline and reduced load time to under 300ms.

**API Rate Limits**: Free tier Gemini has 15 req/min. We added caching for similar behavioral patterns, reducing API calls by 70%.

## Accomplishments that we're proud of

**Fully Functional System**: Most hackathon projects are demos. html.ai is production-ready with real-time personalization across two live websites, cross-domain tracking, and an analytics dashboard.

**Beautiful Carousel**: Live HTML variant previews rendered in iframes (not screenshots) with Framer Motion-inspired animations. Judges can see exactly what users see.

**Framework-Agnostic SDK**: Works with React, Vue, Angular, or plain HTML. Just drop in one `<script>` tag and you're live.

**Real Cross-Site Intelligence**: Built a network, not separate sites. When you browse Shoopify then Amazoon, the system syncs identity and applies learnings across sites.

**Sub-200ms Latency**: From user action to AI classification to variant served, the entire pipeline runs in under 200ms.

## What we learned

**Simplicity Wins**: Over-engineered systems fail. One well-crafted Gemini prompt beats complex multi-agent orchestration. Simpler code is faster code.

**Behavioral Signals > Demographics**: What someone does in the moment is more predictive than who they are. Scroll speed and hover time beat age and location.

**MongoDB Aggregation**: Writing aggregation queries directly in the database is way faster than doing it in Python.

**Cross-Domain Tracking is Hard**: Safari's ITP, Chrome's SameSite, and GDPR ate 30% of dev time. Privacy-first tracking requires first-party solutions.

**Prompt Engineering is an Art**: Getting structured JSON from Gemini took dozens of iterations. Always provide examples, use XML tags, specify edge cases.

**Fault Tolerance is Critical**: When Gemini API went down, our system crashed. We added fallback variants, exponential backoff, and health checks.

## What's next for html.ai

### 1. **Visual Validation Agent (Browser Automation)**

We want to add an agent with headless browser access (Playwright/Puppeteer) that:
- Renders generated variants
- Checks if components rendered correctly
- Validates accessibility (color contrast, ARIA labels)
- Screenshots the page for the analytics dashboard

This ensures the AI doesn't generate broken HTML that looks good in theory but breaks in practice.

### 2. **Multi-Framework SDK Support**

Expand beyond JavaScript to:
- **Swift SDK** for iOS apps
- **Kotlin SDK** for Android apps
- **Go SDK** for server-side rendering
- **React/Vue/Svelte components** for native framework integration

Goal: html.ai should work on ANY platform-web, mobile, desktop.

### 3. **Federated Learning Network**

Scale cross-site intelligence by:
- Allowing multiple businesses to opt into a shared learning network
- Anonymizing behavioral patterns across sites (no PII shared)
- Building a "marketplace of insights" where sites can see aggregated trends (e.g., "Green CTAs are down 15% this month in fashion vertical")

### 4. **Dynamic SERP Alignment**

Integrate with Google Search Console to:
- Detect which search query brought a user to the page
- Automatically rewrite H1, meta descriptions, and hero text to match search intent
- Track how SERP alignment affects bounce rate and conversion

### 5. **Emotion Detection via Behavioral Analysis**

Add ML models that infer emotional state from behavioral patterns:
- Rage clicking → frustration → trigger help chat
- Slow, deliberate scrolling → research mode → show detailed specs
- Rapid bouncing between pages → comparison shopping → show side-by-side tools

### 6. **GDPR/Privacy-First Mode**

Build a fully privacy-compliant version:
- No cross-site tracking (each site is isolated)
- No persistent user IDs (ephemeral session tokens only)
- Opt-in consent flows
- Anonymized behavioral clustering

### 7. **Open Source the SDK**

We want to open-source the core SDK so developers can:
- Self-host the backend
- Customize agent prompts
- Add new behavioral signals
- Build community-driven variants

### 8. **Enterprise Dashboard**

Build a SaaS platform with:
- Multi-tenant support (each business gets isolated data)
- Advanced analytics (cohort analysis, funnel visualization)
- A/B test comparison (traditional A/B vs. AI-driven adaptive testing)
- Variant editor (visual UI builder for non-technical users)

---

## Built With

- Python
- FastAPI
- Uvicorn
- Google Gemini 2.0 Flash API
- MongoDB Atlas
- JavaScript (Vanilla)
- HTML5/CSS3
- Git/GitHub

## Try It Out

- **GitHub**: https://github.com/tanujdargan/html.ai
- **Demo Video**: https://www.youtube.com/watch?v=mkKrlVUX3mE
- **Domain**: htmlai.tech

## Team

- University of Toronto
- Toronto Metropolitan University
- University of Victoria
- University of Calgary

---

**html.ai: Reinventing identity as an adaptive experience that evolves in real time through user action.**
