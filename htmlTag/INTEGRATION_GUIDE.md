# Integration Guide: Merging htmlTag + Root Project

## What We Did

We merged the best of both projects:

**htmlTag (Developer UX)** + **Root Backend (AI Brain)** = **Complete Product**

### Before:
- ❌ htmlTag: Good UX, but simple backend with stubs
- ❌ Root: Sophisticated AI, but no simple integration

### After:
- ✅ Simple dev experience: `<ai-optimize experiment="hero">...</ai-optimize>`
- ✅ 4-agent multi-agent system under the hood
- ✅ Wins all 3 sponsor prizes

---

## Architecture

```
Developer Wraps HTML
   <ai-optimize experiment="hero">
      <button>Click me</button>
   </ai-optimize>
            ↓
      SDK (JavaScript)
            ↓
   FastAPI Backend (port 3000)
            ↓
   4-Agent System (LangGraph)
   ├─ Analytics Agent → Behavioral Vector
   ├─ Identity Agent → Interpret State
   ├─ Decision Agent → Select Variant
   └─ Guardrail Agent → Validate
            ↓
   MongoDB (Store events & variants)
            ↓
   Optimized Variant Returned
            ↓
   DOM Updates Automatically
            ↓
   User Clicks → Reward Signal
            ↓
   System Learns & Improves
```

---

## Sponsor Prize Alignment

### 1. Foresters Financial - Multi-Agent Mind ✅
**Prize:** Paid summer internships for all 4 team members

**How we qualify:**
- ✅ 4 specialized agents (Analytics, Identity, Decision, Guardrail)
- ✅ LangGraph orchestration framework
- ✅ Clear state management and hand-offs
- ✅ Agent communication logs in API response

**Demo:** Show the `audit_log` in console:
```javascript
[ai-optimize] ✓ Agent Communication Log:
  - Analytics Agent: Computing behavioral vector from 8 events
  - Analytics Agent: Behavioral vector computed
  - Identity Agent: Interpreting identity state
  - Identity Agent: Identified as 'confident' with confidence 0.85
  - Decision Agent: Selecting variant for identity=confident
  - Decision Agent: Selected 'hero_confident_v1' - target matches identity
  - Guardrail Agent: Validating decision
  - Guardrail Agent: Decision approved
```

### 2. Amplitude - Self-Improving Products ✅
**Prize:** Paid internships at Amplitude

**How we qualify:**
- ✅ Behavioral event tracking (scroll_depth, time_on_component, click, etc.)
- ✅ AI analyzes patterns → behavioral vector (NOT user categorization!)
- ✅ Data → Insights → Action loop
- ✅ Product adapts based on behavior

**Demo:** Show the behavioral vector:
```javascript
[ai-optimize] ✓ Behavioral Vector: {
  exploration_score: 0.72,
  hesitation_score: 0.15,
  engagement_depth: 0.88,
  decision_velocity: 0.65,
  content_focus_ratio: 0.91
}
```

### 3. Shopify - Hack Shopping with AI ✅
**Prize:** Shopify Keyboard + Meta Ray-Bans per person

**How we qualify:**
- ✅ AI optimizes e-commerce conversions
- ✅ Dynamically adapts product pages based on shopping behavior
- ✅ Works with any e-commerce platform (including Shopify)

**Demo:** Show conversion rate improvements in dashboard

---

## File Structure

```
htmlTag/
├── aiBackend/
│   ├── server_integrated.py    ← NEW: Integrated backend
│   ├── server.py               ← OLD: Keep as backup
│   ├── requirements.txt        ← UPDATE: Add backend deps
│   └── Dockerfile              ← UPDATE: Copy backend agents
│
├── sdk/src/
│   ├── AiOptimizeElement_v2.js ← NEW: Updated SDK
│   ├── AiOptimizeElement.js    ← OLD: Keep as backup
│   ├── index.js                ← UPDATE: Load v2
│   └── index.html              ← Keep as demo
│
└── Docker-compose.yml          ← Keep as-is

backend/                         ← Copy agents to htmlTag
├── agents/
│   ├── workflow.py
│   ├── analytics_agent.py
│   ├── identity_agent.py
│   ├── decision_agent.py
│   └── guardrail_agent.py
└── models/
    ├── events.py
    └── variants.py
```

---

## Step-by-Step Integration

### Step 1: Copy Backend Agents

```bash
# From html.ai/ root
cd htmlTag/aiBackend
mkdir -p agents models

# Copy agent files
cp ../../backend/agents/*.py agents/
cp ../../backend/models/*.py models/
```

### Step 2: Update Requirements

Add to `htmlTag/aiBackend/requirements.txt`:

```txt
fastapi
uvicorn
pymongo
pydantic
python-dotenv

# Multi-agent system dependencies
langgraph>=0.0.20
langchain>=0.1.0
google-generativeai>=0.3.0
```

### Step 3: Update Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy all backend code
COPY requirements.txt .
COPY server_integrated.py .
COPY agents/ agents/
COPY models/ models/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3000

CMD ["python", "server_integrated.py"]
```

### Step 4: Update SDK

In `htmlTag/sdk/src/index.js`:

```javascript
// Load the v2 SDK
import './AiOptimizeElement_v2.js';
```

### Step 5: Environment Variables

Create `.env` in `htmlTag/aiBackend/`:

```bash
GEMINI_API_KEY=your_key_here
```

**IMPORTANT:** Add `.env` to `.gitignore`!

### Step 6: Test Locally

```bash
# Terminal 1: Start backend + MongoDB
cd htmlTag
docker compose up --build

# Terminal 2: Start frontend demo
cd sdk/src
python3 -m http.server 8080

# Open browser
open http://localhost:8080
```

Check console for:
- ✅ "Multi-agent workflow execution"
- ✅ "Agent Communication Log"
- ✅ "Behavioral Vector"

---

## Testing the 3 Sponsor Prizes

### Test 1: Foresters (Multi-Agent)

1. Open browser console
2. Refresh page
3. Look for agent communication log:

```
[ai-optimize] ✓ Agent Communication Log:
  - Analytics Agent: Computing behavioral vector...
  - Identity Agent: Identified as 'exploratory'
  - Decision Agent: Selected 'hero_exploratory_v1'
  - Guardrail Agent: Decision approved
```

**Screenshot this for demo!**

### Test 2: Amplitude (Behavioral Data → AI → Action)

1. Open browser console
2. Scroll the page
3. Click buttons
4. Watch events being tracked:

```
[ai-optimize] Event: scroll_depth_reached (75%)
[ai-optimize] Event: time_on_component (12.3s)
[ai-optimize] Event: component_hover
[ai-optimize] 🎯 CONVERSION: Button clicked
```

5. Visit analytics dashboard:

```bash
curl http://localhost:3000/api/analytics/dashboard
```

Shows:
- Variant performance by identity state
- Conversion rates
- Behavioral patterns

**This demonstrates the self-improving loop!**

### Test 3: Shopify (E-commerce Optimization)

1. Simulate different user behaviors:
   - **Browsing:** Slow scrolling, multiple page views
   - **Comparing:** Back and forth navigation
   - **Ready to buy:** Quick scrolling, add to cart

2. Each behavior gets different variants:
   - Browsing → "Discover Our Collection"
   - Comparing → "Compare Features & Specs"
   - Ready → "Complete Your Order Today"

3. Show conversion rate improvements in dashboard

---

## Demo Video Script

**1. Introduction (15 seconds)**
"We built html.ai - a self-improving UI engine that uses 4 AI agents to personalize websites based on user behavior"

**2. Developer Experience (30 seconds)**
- Show code: Just wrap HTML in `<ai-optimize>`
- Show it works in any framework
- Show simple integration

**3. Multi-Agent System (45 seconds) - FOR FORESTERS**
- Open console
- Show agent communication log
- Explain each agent's role
- Show LangGraph orchestration

**4. Behavioral Analytics (45 seconds) - FOR AMPLITUDE**
- Show events being tracked
- Show behavioral vector (NOT categorization!)
- Show how variants adapt
- Show analytics dashboard

**5. E-commerce Results (45 seconds) - FOR SHOPIFY**
- Show different user journeys
- Show variant adaptations
- Show conversion rate improvements

**Total: 3 minutes**

---

## Common Issues & Solutions

### Issue: "Multi-agent system unavailable"
**Solution:** Check GEMINI_API_KEY is set in `.env`

### Issue: "Module not found: agents"
**Solution:** Make sure you copied agents/ and models/ folders

### Issue: Port 3000 already in use
**Solution:** Kill existing process:
```bash
lsof -ti:3000 | xargs kill -9
```

### Issue: MongoDB connection failed
**Solution:** Make sure Docker is running and `docker compose up` succeeded

---

## What Makes This Win

### For Judges:
1. **Real product** - developers can actually use this
2. **Sophisticated AI** - not just simple A/B testing
3. **Complete solution** - frontend + backend + database
4. **Sponsor alignment** - hits all 3 prizes perfectly

### For Developers:
1. **Simple integration** - one HTML tag
2. **Framework agnostic** - works everywhere
3. **No complex setup** - just Docker
4. **Privacy-first** - behavioral vectors, not user profiling

### Technical Excellence:
1. **4-agent system** with LangGraph
2. **Behavioral vectors** not user categorization
3. **Contextual bandits** for variant selection
4. **Self-improving loop** with reward signals
5. **Privacy guardrails** built in

---

## Next Steps (Final 20 Hours)

### Priority 1: Integration (4 hours)
- [ ] Copy backend agents to htmlTag
- [ ] Update requirements.txt
- [ ] Update Dockerfile
- [ ] Test end-to-end locally
- [ ] Fix any bugs

### Priority 2: Demo & Testing (4 hours)
- [ ] Create 2-3 demo pages showing different use cases
- [ ] Test all 3 sponsor prize scenarios
- [ ] Screenshot agent logs
- [ ] Record analytics dashboard
- [ ] Test on different browsers

### Priority 3: Documentation (4 hours)
- [ ] Update README with integration guide
- [ ] Create architecture diagram
- [ ] Document API endpoints
- [ ] Write sponsor alignment doc
- [ ] Prepare demo script

### Priority 4: Video & Devpost (4 hours)
- [ ] Record demo video (<3 min)
- [ ] Edit with captions/highlights
- [ ] Upload to YouTube
- [ ] Write Devpost submission
- [ ] Add screenshots/diagrams
- [ ] Attach resumes (for internships!)

### Priority 5: Deployment (4 hours)
- [ ] Deploy backend to Railway/Render
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Test deployed version
- [ ] Update README with live links
- [ ] Final testing

---

## You Got This!

The hard part (architecture) is done. Now:
1. Integrate the code
2. Test the demos
3. Record the video
4. Submit!

**Let's win those internships!** 🚀
