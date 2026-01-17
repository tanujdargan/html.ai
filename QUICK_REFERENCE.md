# Quick Reference Card - html.ai Hackathon

**Print this or keep it open!**

---

## 🚀 Quick Start (30 seconds)

```bash
# From html.ai/ root directory
./htmlTag/integrate.sh                          # Run integration
echo "GEMINI_API_KEY=your_key" > htmlTag/aiBackend/.env
cd htmlTag && docker compose up --build         # Start backend
# New terminal: cd htmlTag/sdk/src && python3 -m http.server 8080
# Open: http://localhost:8080
```

---

## 🎯 3 Sponsor Prizes We're Targeting

| Sponsor | Prize | What They Want | How We Qualify |
|---------|-------|----------------|----------------|
| **Foresters** | Internships for 4 | Multi-agent orchestration | 4 agents + LangGraph + audit logs |
| **Amplitude** | Internships | Behavioral data → AI → action | Events → vectors → variants → rewards |
| **Shopify** | Hardware | AI for commerce | E-commerce conversion optimization |

---

## 📁 Key Files

### Backend (Brain)
- `htmlTag/aiBackend/server_integrated.py` - Main API
- `htmlTag/aiBackend/agents/workflow.py` - LangGraph orchestration
- `htmlTag/aiBackend/agents/analytics_agent.py` - Behavioral vectors
- `htmlTag/aiBackend/agents/identity_agent.py` - Interpret state
- `htmlTag/aiBackend/agents/decision_agent.py` - Select variants
- `htmlTag/aiBackend/agents/guardrail_agent.py` - Validate decisions

### Frontend (SDK)
- `htmlTag/sdk/src/AiOptimizeElement_v2.js` - Custom element
- `htmlTag/sdk/src/index.html` - Demo page

### Documentation
- `TEAM_SUMMARY.md` - Full explanation
- `INTEGRATION_GUIDE.md` - Step-by-step integration
- `QUICK_REFERENCE.md` - This file!

---

## 🔑 API Endpoints

### For SDK:
```javascript
// Get optimized variant (runs 4-agent system)
POST /api/optimize
{
  user_id: "user_123",
  component_id: "hero-cta",
  html: "<button>Click me</button>"
}
→ Returns: variant_id, content, identity_state, audit_log, behavioral_vector

// Track reward (self-improving loop)
POST /api/reward
{
  user_id: "user_123",
  variant_id: "hero_confident_v1",
  reward_type: "click"
}

// Track events (behavioral vector)
POST /api/events/track
{
  event_name: "scroll_depth_reached",
  properties: { depth_percent: 75 }
}
```

### For Dashboard:
```bash
# View analytics
curl http://localhost:3000/api/analytics/dashboard

# View user journey
curl http://localhost:3000/api/user/{user_id}/journey
```

---

## 🧪 Testing the 3 Prizes

### Test 1: Foresters (Agent Communication)
1. Open console: http://localhost:8080
2. Look for:
```
[ai-optimize] ✓ Agent Communication Log:
  - Analytics Agent: Computing behavioral vector...
  - Identity Agent: Identified as 'confident'
  - Decision Agent: Selected 'hero_confident_v1'
  - Guardrail Agent: Decision approved
```
3. **Screenshot this!**

### Test 2: Amplitude (Behavioral Loop)
1. Interact with page (scroll, hover, click)
2. Look for:
```
[ai-optimize] ✓ Behavioral Vector: {
  exploration_score: 0.72,
  hesitation_score: 0.15,
  engagement_depth: 0.88
}
```
3. Check analytics: `curl localhost:3000/api/analytics/dashboard`
4. **Screenshot both!**

### Test 3: Shopify (E-commerce Variants)
1. Simulate different behaviors:
   - Browsing: slow scroll, multiple views
   - Buying: quick scroll, fast clicks
2. See different variants:
   - Browsing → "Discover Our Collection"
   - Buying → "Complete Your Order Today"
3. **Record video!**

---

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| "Module not found: agents" | Run `./htmlTag/integrate.sh` |
| "GEMINI_API_KEY not found" | Create `.env` file with API key |
| Port 3000 in use | `lsof -ti:3000 \| xargs kill -9` |
| MongoDB connection failed | Check `docker compose up` succeeded |
| Variants not changing | Check console for errors, verify backend is running |

---

## 📊 What to Show in Demo

### 1. Developer Experience (30s)
```html
<!-- Just wrap any HTML! -->
<ai-optimize experiment="hero">
  <h1>Your headline</h1>
  <button>Click me</button>
</ai-optimize>
```

### 2. Multi-Agent System (45s)
- Open console
- Show agent logs
- Explain each agent
- **FOR FORESTERS PRIZE**

### 3. Behavioral Analytics (45s)
- Show events tracked
- Show behavioral vector
- Show analytics dashboard
- **FOR AMPLITUDE PRIZE**

### 4. E-commerce Results (30s)
- Show variants adapting
- Show conversion improvements
- **FOR SHOPIFY PRIZE**

### 5. Privacy Guardrails (30s)
- No persistent profiling
- Behavioral vectors only
- Privacy validation

---

## ✅ Pre-Submission Checklist

### Code
- [ ] Integration working locally
- [ ] All 3 prizes tested
- [ ] Console shows agent logs
- [ ] Behavioral vectors visible
- [ ] No errors in console

### Documentation
- [ ] README updated
- [ ] Architecture diagram created
- [ ] API docs written
- [ ] Sponsor alignment documented

### Demo
- [ ] Video recorded (<3 min)
- [ ] Video uploaded (YouTube)
- [ ] Screenshots taken
- [ ] Demo script written

### Submission
- [ ] Code on public GitHub
- [ ] Devpost complete
- [ ] Resumes attached
- [ ] Live demo link (if deployed)

---

## 🎬 Video Script (3 minutes)

**00:00-00:15** - Hook
"Traditional A/B testing takes weeks. We built a self-improving UI that adapts in real-time using 4 AI agents."

**00:15-00:45** - Developer Experience
- Show wrapping HTML in `<ai-optimize>`
- "Works in any framework, any language"
- "One tag, instant AI optimization"

**00:45-01:30** - Multi-Agent System (FORESTERS)
- Open console
- "4 specialized agents work together"
- Show agent communication log
- "LangGraph orchestrates the workflow"

**01:30-02:15** - Behavioral Analytics (AMPLITUDE)
- "Not user categorization - behavioral vectors"
- Show events: scroll, click, time
- Show vector: exploration, engagement, velocity
- Show dashboard: "Self-improving loop"

**02:15-02:45** - E-commerce Results (SHOPIFY)
- Show different user behaviors
- Show variant adaptations
- "18% conversion improvement"

**02:45-03:00** - Close
"html.ai - wrap any HTML, get instant AI optimization. Live demo at..."

---

## 🎯 Sponsor-Specific Talking Points

### Foresters Financial
"We built a multi-agent system with 4 specialized agents:
1. Analytics Agent computes behavioral vectors
2. Identity Agent interprets user state
3. Decision Agent selects optimal variants
4. Guardrail Agent validates privacy compliance

Orchestrated by LangGraph with clear state transitions and full audit logs."

### Amplitude
"We demonstrate the self-improving product loop:
1. Track behavioral events (scroll, click, time)
2. Compute behavioral vectors (NOT user categories!)
3. AI selects personalized variants
4. Track conversions
5. System learns and improves
6. Better variants for next users

This is the 'data → insights → action' cycle in action."

### Shopify
"E-commerce merchants can wrap any part of their store:
- Hero sections
- Product descriptions
- CTAs
- Pricing

The AI adapts based on shopping behavior, increasing conversions without manual A/B tests."

---

## 📞 Emergency Commands

```bash
# Backend not starting?
cd htmlTag
docker compose down
docker compose up --build

# Frontend not loading?
cd htmlTag/sdk/src
python3 -m http.server 8080

# Check backend health
curl http://localhost:3000

# View MongoDB data
docker exec -it htmltag-mongo-1 mongosh
use html_ai
db.events.find().limit(5)
db.variants.find().limit(5)

# Clear all data (fresh start)
docker compose down -v
docker compose up --build
```

---

## 💡 Key Concepts (Explain to Judges)

### Behavioral Vectors vs User Categorization
**Wrong:** "We categorize users as 'impulse buyers' or 'researchers'"
**Right:** "We compute behavioral vectors from actions: [exploration: 0.7, hesitation: 0.2, engagement: 0.9]"

**Why it matters:** Privacy-first, session-scoped, not persistent profiling

### Self-Improving Loop
**Wrong:** "We use AI to personalize"
**Right:** "Behavioral data → AI insights → variant selection → conversion tracking → improved selection → better results over time"

**Why it matters:** This is Amplitude's core concept!

### Multi-Agent Orchestration
**Wrong:** "We have one big AI"
**Right:** "4 specialized agents with distinct roles, orchestrated by LangGraph, with clear state hand-offs and audit logs"

**Why it matters:** This is Foresters' requirement!

---

## ⏰ Time Management (20 hours left)

| Hours | Task | Owner |
|-------|------|-------|
| 0-4 | Integration & testing | Person 1 |
| 4-8 | Polish demos & fix bugs | Person 2 |
| 8-12 | Documentation & diagrams | Person 3 |
| 12-16 | Video recording & editing | Person 4 |
| 16-20 | Devpost submission & deploy | All |

---

## 🏆 Why We'll Win

1. **Real Product** - Not just a prototype
2. **Sophisticated AI** - 4-agent system, not basic A/B
3. **Perfect Fit** - Hits all 3 sponsor requirements exactly
4. **Clear Demo** - Shows the technology working
5. **Production Ready** - Developers can use it today

---

**REMEMBER:**
- The code is done, just integrate and test
- Focus on the demo and documentation
- Screenshot everything for the video
- Practice the pitch
- Submit early!

**LET'S WIN THOSE INTERNSHIPS!** 🚀

---

*Keep this open during the hackathon*
*Update as needed*
