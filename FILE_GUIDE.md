# 📁 File Structure Guide - What's What?

## 📖 Documentation Files (Read These First!)

| File | Who Reads It | What's In It |
|------|--------------|--------------|
| `PROJECT_BRIEF.md` | **EVERYONE** | Team coordination, task assignments, pitch |
| `SETUP_FIRST.md` | **TAKA** | How to install & push to GitHub |
| `QUICKSTART.md` | **SULTAN/TANUJ/KISH** | How to run the project after pulling |
| `DEVPOST_TEMPLATE.md` | **KISH** | Template for Devpost submission |
| `TEAM_TASKS.md` | **EVERYONE** | Detailed task breakdown |
| `README.md` | **JUDGES** | Main project overview |

---

## 🐍 Backend Files (Python)

### `/backend/models/` - Data Models

**`events.py`** - Defines all event types
```python
# What events do we track?
- page_viewed
- component_viewed
- click
- add_to_cart
- etc.

# What's a behavioral vector?
- exploration_score
- hesitation_score
- engagement_depth
- decision_velocity
- content_focus_ratio
```

**`variants.py`** - Defines UI variants
```python
# What's a variant?
{
  "variant_id": "hero_confident_v1",
  "content": {
    "headline": "Complete Your Purchase Today",
    "cta_text": "Buy Now"
  },
  "target_identity": "confident"
}
```

---

### `/backend/agents/` - The 4 AI Agents

**`analytics_agent.py`** - Agent #1
- Takes: Event history
- Does: Computes behavioral vector
- Returns: Updated state with vector

**`identity_agent.py`** - Agent #2
- Takes: Behavioral vector
- Does: Interprets it using GPT-4
- Returns: Identity state (exploratory/confident/overwhelmed/etc.)

**`decision_agent.py`** - Agent #3
- Takes: Identity state
- Does: Selects best UI variant (contextual bandit algorithm)
- Returns: Selected variant + rationale

**`guardrail_agent.py`** - Agent #4
- Takes: Variant decision
- Does: Checks for privacy violations, price manipulation, etc.
- Returns: Approved or rejected + reason

**`workflow.py`** - LangGraph Orchestration
- Connects all 4 agents in sequence
- Manages state hand-offs
- Returns audit log showing agent communication

---

### `/backend/` - API Server

**`main.py`** - FastAPI Server
```python
# Key endpoints:
POST /api/session/create - Create new session
POST /api/events/track   - Track behavioral event
POST /api/variants/get   - Get personalized variant (runs agents!)
GET  /api/session/{id}   - Get session state
```

**`requirements.txt`** - Python dependencies
```
fastapi - Web framework
langgraph - Multi-agent orchestration
langchain-openai - GPT-4 integration
pydantic - Data validation
uvicorn - ASGI server
supabase - Database (optional)
```

**`.env.example`** - Template for secrets
```
OPENAI_API_KEY=your_key_here
```

**`.env`** - Actual secrets (NOT in GitHub!)
```
OPENAI_API_KEY=sk-actual-key...
```

**`test_workflow.py`** - Test script
- Simulates user behavior
- Runs all 4 agents
- Shows output

---

## 🎨 Frontend Files

### `/sdk/identity.js` - Client SDK

**What it does:**
1. Tracks user events (clicks, scrolls, time on page)
2. Sends events to backend API
3. Requests personalized variants
4. Updates the page with new content
5. Shows debug panel (for demo)

**How to use:**
```html
<script src="identity.js"></script>
<div data-identity-component="hero">
  <!-- This will auto-adapt! -->
</div>
```

---

### `/demo-store/index.html` - Demo E-Commerce Site

**Sections:**
- Hero (adapts based on behavior!)
- Product grid (tracks clicks)
- Features section

**What's special:**
- Marked components with `data-identity-component="hero"`
- Includes debug panel showing live agent logs
- Simulates different user behaviors

---

## 🗂️ Config Files

**`.gitignore`** - What NOT to push
```
.env          ← Your API keys
__pycache__   ← Python cache
.DS_Store     ← Mac files
.claude/      ← AI assistant files
```

---

## 🎯 How Everything Connects

```
User browses demo-store/index.html
   ↓
identity.js tracks events
   ↓
POST /api/events/track
   ↓
Backend stores in session
   ↓
identity.js requests variant
   ↓
POST /api/variants/get
   ↓
workflow.py runs 4 agents:
   1. Analytics → computes vector
   2. Identity → interprets state
   3. Decision → selects variant
   4. Guardrail → validates
   ↓
Variant returned to frontend
   ↓
identity.js updates the hero section
   ↓
User sees personalized content! 🎉
```

---

## 🔧 Files You'll Edit Most

**Taka (Backend):**
- `backend/agents/*.py` - Tweak agent logic
- `backend/main.py` - Add endpoints
- `backend/test_workflow.py` - Debug

**Sultan (Frontend):**
- `sdk/identity.js` - Improve SDK
- `demo-store/index.html` - Better demo
- CSS styling

**Tanuj (Docs):**
- `README.md` - Better explanations
- New `docs/` folder - Architecture diagrams
- `QUICKSTART.md` - Clearer setup

**Kish (Video):**
- `DEVPOST_TEMPLATE.md` - Write submission
- Screen recording tools
- `video/` folder - Store recordings

---

## 🆘 Quick Find

**Need to change the variants?**
→ `backend/agents/decision_agent.py` (bottom of file, `DEMO_VARIANTS`)

**Need to add a new event type?**
→ `backend/models/events.py` (`EventType` enum)

**Need to change what the agents say?**
→ Each agent's `.py` file (`add_audit_entry` lines)

**Need to change debug panel?**
→ `sdk/identity.js` (`showDebugPanel` function)

**Need to test locally?**
→ `backend/test_workflow.py`

---

Got questions? Ask in team chat! 💬
