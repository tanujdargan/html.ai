# Adaptive Identity Engine

**Self-improving UI engine powered by behavioral analytics and multi-agent AI**

## 🎯 Hackathon Sponsor Tracks

- ✅ **Foresters Financial** - Multi-Agent Mind (4 specialized agents + LangGraph orchestration)
- ✅ **Amplitude** - Self-Improving Products (behavioral data → AI insights → action loop)
- ✅ **Shopify** - Hack Shopping with AI (optimize e-commerce conversions)

## 🏗️ Architecture

```
User Actions on Shopify Store
   ↓
identity.js SDK (event capture)
   ↓
FastAPI Backend
   ↓
Multi-Agent System (LangGraph)
   ├─ Analytics Agent (compute behavioral vector)
   ├─ Identity Agent (interpret user state)
   ├─ Decision Agent (select UI variant)
   └─ Guardrail Agent (validate ethics/privacy)
   ↓
Variant Rendered + Events Logged
   ↓
Continuous Learning Loop
```

## 🚀 Quick Start

### Backend (Python + LangGraph)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend SDK
```html
<script src="https://your-cdn.com/identity.js"></script>
<div data-identity-component="hero" data-goal="conversion" data-variants="3">
  Your content here
</div>
```

### Demo Store
```bash
cd demo-store
# Open index.html in browser
```

## 📊 Event Schema (Amplitude-Style)

Events tracked:
- `page_viewed`
- `component_viewed`
- `scroll_depth_reached`
- `time_on_component`
- `click`
- `add_to_cart`
- `conversion_completed`

Each event includes:
```json
{
  "event_name": "component_viewed",
  "timestamp": "2026-01-17T12:00:00Z",
  "session_id": "abc123",
  "user_id": "user_456",
  "properties": {
    "component_id": "hero",
    "variant_shown": "confident_v2"
  }
}
```

## 🤖 Multi-Agent System

### Agent 1: Analytics Agent
Transforms raw events → behavioral identity vector

### Agent 2: Identity Interpretation Agent
Interprets vector → semantic state (exploratory, confident, overwhelmed, etc.)

### Agent 3: Decision Agent
Selects optimal UI variant using contextual bandit algorithm

### Agent 4: Guardrail Agent
Validates all decisions for privacy/ethics compliance

## 🛡️ Privacy & Ethics

- Session-scoped identity (no persistent tracking)
- No inference of protected characteristics
- No price manipulation
- Full decision audit logs
- Only adapts pre-approved components

## 👥 Team

- [Your names here]

## 📦 Tech Stack

- **Backend**: Python, FastAPI, LangGraph, OpenAI
- **Database**: Supabase (PostgreSQL + Realtime)
- **Frontend SDK**: Vanilla JavaScript
- **Demo**: Shopify Liquid theme
- **Analytics**: Amplitude-compatible event schema

## 🏆 Demo

[Link to demo video]
[Link to live Shopify store]

---

Built for UofTHacks 2026 🎓
