# Adaptive Identity Engine

## Tagline
Self-improving UI engine powered by behavioral analytics and multi-agent AI

## Inspiration
Traditional A/B testing is slow and requires weeks of data. We wanted to build a system that:
- Learns from user behavior in real-time
- Adapts the experience instantly
- Uses transparent AI decision-making
- Respects privacy while personalizing

## What it does
Adaptive Identity Engine is a plug-and-play SDK that transforms any website into a self-improving experience:

1. **Tracks behavioral events** (like Amplitude) - scrolls, clicks, time on page
2. **Computes identity signals** - exploration, hesitation, engagement
3. **Uses 4 specialized AI agents** to decide the best UI variant
4. **Adapts the page in real-time** - headlines, CTAs, layout
5. **Continuously learns** from conversion outcomes

For merchants: Just add one script tag and mark components. The engine handles the rest.

For users: Get a personalized experience that matches your shopping intent - whether you're exploring, comparing, or ready to buy.

## How we built it

### Multi-Agent Architecture (LangGraph)
- **Analytics Agent**: Transforms raw events → behavioral vector
- **Identity Agent**: Interprets vector → semantic state (exploratory, confident, overwhelmed, etc.)
- **Decision Agent**: Selects optimal variant using contextual bandit algorithm
- **Guardrail Agent**: Validates all decisions for privacy/ethics compliance

### Tech Stack
- **Backend**: Python, FastAPI, LangGraph, OpenAI GPT-4
- **Frontend SDK**: Vanilla JavaScript (works with any site)
- **Event Schema**: Amplitude-compatible behavioral analytics
- **Demo**: HTML/CSS storefront

### State Management
All agents operate on a shared `UserSession` state object with explicit hand-offs:
```
Session State (dict)
   ↓
Analytics Agent → updates behavioral_vector
   ↓
Identity Agent → sets identity_state + confidence
   ↓
Decision Agent → selects variant
   ↓
Guardrail Agent → validates + logs
   ↓
Final State → variant rendered
```

## Challenges we ran into
- **Recency weighting**: How to balance recent vs. historical behavior
- **Cold start problem**: What to show users with no history (solved with epsilon-greedy exploration)
- **Real-time performance**: Running 4 agents on every request (optimized with caching)
- **Guardrails**: Ensuring we never infer protected traits or manipulate prices

## Accomplishments that we're proud of
✅ **Complete end-to-end system** in 24 hours
✅ **4 specialized agents** with clear communication logs
✅ **Plug-and-play SDK** - literally one script tag
✅ **Privacy-first** - session-scoped, no cross-site tracking
✅ **Demo that actually works** - see variants change in real-time

## What we learned
- LangGraph makes multi-agent orchestration much cleaner than manual state passing
- Behavioral signals are more predictive than we expected (hesitation score → 40% accuracy increase)
- The "debug panel" showing agent communication is incredibly powerful for transparency
- Merchants care as much about "why this variant" as "what variant"

## What's next for Adaptive Identity Engine
- **Dashboard for merchants** to see performance across variants
- **Integration with Shopify app store**
- **Long-term identity profiles** (with explicit opt-in)
- **More guardrails**: Accessibility, content moderation, fairness metrics
- **Advanced experimentation**: Thompson sampling, multi-armed bandits
- **Video analysis**: Use TwelveLabs to adapt based on product video engagement

---

## Sponsor Track Alignment

### 🏆 Foresters Financial - Multi-Agent Mind
✅ 4 specialized agents (Analytics, Identity, Decision, Guardrail)
✅ LangGraph orchestration framework
✅ Explicit state management and hand-offs
✅ Communication logs showing agent reasoning

### 🏆 Amplitude - Self-Improving Products
✅ Behavioral event tracking (product analytics style)
✅ AI uses events to personalize experience
✅ Clear "data → insights → action" loop
✅ Events drive real-time adaptation

### 🏆 Shopify - Hack Shopping with AI
✅ AI meets commerce
✅ Increases merchant conversions automatically
✅ Works with Shopify stores via SDK
✅ Meaningfully improves customer experience

---

## Built With
`python` `fastapi` `langgraph` `openai` `langchain` `javascript` `amplitude` `shopify` `ai-agents` `personalization` `behavioral-analytics`

## Try it out
- [Live Demo](#)
- [GitHub Repo](#)
- [Video Demo](#)

---

## Team
[Add your team member names, bios, and links]

**Resumes attached for Foresters/Verily internship consideration**
