# 🚀 Quick Start Guide

## Setup (5 minutes)

### 1. Backend Setup

```bash
cd backend

# Run setup script (creates venv and installs dependencies)
chmod +x setup.sh
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Create .env file
cp .env.example .env

# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=your_key_here" >> .env

# Run the server
python main.py
```

**Note:** Always activate venv first: `source venv/bin/activate`

Server will be running on `http://localhost:8000`

### 2. Test the Multi-Agent System

```bash
# In backend/ directory
python agents/workflow.py
```

This will run a demo showing the 4 agents processing a user session.

You should see output like:
```
AGENT COMMUNICATION LOG
========================
[timestamp] Analytics Agent: Computing behavioral vector from 6 events
[timestamp] Analytics Agent: Vector computed - exploration=0.33, hesitation=0.17, engagement=0.25
[timestamp] Identity Interpretation Agent: Interpreting behavioral vector
[timestamp] Identity Interpretation Agent: Identified as exploratory (confidence=0.82)
[timestamp] Decision Agent: Selecting variant for identity=exploratory
[timestamp] Decision Agent: Selected 'hero_exploratory_v1'
[timestamp] Guardrail Agent: Validating decision against guardrails
[timestamp] Guardrail Agent: ✓ All guardrails passed
```

### 3. Run Demo Store

```bash
# Open demo-store/index.html in your browser
open demo-store/index.html

# Or use a simple HTTP server
cd demo-store
python -m http.server 8080
# Then visit http://localhost:8080
```

### 4. Watch the Magic ✨

1. **Open demo store** - You'll see a purple hero section
2. **Look bottom right** - Debug panel shows live agent communication
3. **Browse around** - Click products, scroll, navigate
4. **Watch the hero adapt** - The headline/CTA will change based on your behavior!

Identity states you might see:
- **Exploratory** → "Discover Our Collection" (browsing mode)
- **Confident** → "Complete Your Purchase Today" (ready to buy)
- **Overwhelmed** → "We'll Help You Choose" (needs guidance)
- **Comparison Focused** → "Compare Our Best Sellers" (researching)
- **Ready to Decide** → "Ready to Check Out?" (high intent)

---

## API Testing

### Create a session
```bash
curl -X POST http://localhost:8000/api/session/create
```

### Track an event
```bash
curl -X POST http://localhost:8000/api/events/track \
  -H "Content-Type: application/json" \
  -d '{
    "event_name": "component_viewed",
    "session_id": "your_session_id",
    "component_id": "hero",
    "properties": {}
  }'
```

### Get a variant (triggers multi-agent workflow)
```bash
curl -X POST http://localhost:8000/api/variants/get \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your_session_id",
    "component_id": "hero"
  }'
```

---

## For Hackathon Judges

### What Makes This Special?

**1. Foresters Challenge (Multi-Agent Mind) ✅**
- 4 specialized agents with clear roles
- LangGraph orchestration framework
- Explicit state hand-offs between agents
- Full communication logs showing agent reasoning

**2. Amplitude Challenge (Self-Improving Products) ✅**
- Behavioral event tracking (product analytics style)
- AI-powered personalization based on events
- "data → insights → action" loop
- Events drive real-time UI adaptation

**3. Shopify Challenge (Hack Shopping with AI) ✅**
- AI optimizes e-commerce conversions
- Dynamic product page personalization
- Merchant-focused (increase sales automatically)

### Demo Script (30 seconds)

1. **Show the demo store** - "This looks like a normal e-commerce site"
2. **Point to debug panel** - "But watch the AI agents analyzing behavior in real-time"
3. **Browse products** - "As I explore, the Analytics Agent computes behavioral signals"
4. **Show variant change** - "The hero section just adapted! The Identity Agent detected I was 'exploratory' and the Decision Agent changed the CTA"
5. **Show audit log** - "Every decision flows through 4 specialized agents with full transparency"
6. **Revenue impact** - "This 18% conversion rate variant was automatically selected for my behavior pattern"

---

## Architecture Overview

```
User browsing store
   ↓
identity.js SDK tracks events
   ↓
FastAPI backend receives events
   ↓
Multi-Agent Workflow (LangGraph)
   ├─ Analytics Agent (computes behavioral vector)
   ├─ Identity Agent (interprets user state)
   ├─ Decision Agent (selects optimal variant)
   └─ Guardrail Agent (validates ethics/privacy)
   ↓
Variant returned to SDK
   ↓
Page updates dynamically
   ↓
Conversion increases 📈
```

---

## Common Issues

**"ModuleNotFoundError: No module named 'langgraph'"**
→ Run `pip install -r requirements.txt`

**"OpenAI API key not found"**
→ Make sure `.env` file exists with `OPENAI_API_KEY=...`

**"CORS error in browser"**
→ Make sure backend is running on port 8000

**"Variants not showing"**
→ Check browser console and backend logs for errors

---

## Next Steps

- [ ] Deploy backend to Railway/Render
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Record demo video
- [ ] Write Devpost submission
- [ ] Add team bios and resumes

Good luck! 🚀
