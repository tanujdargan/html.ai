# 🚀 FIRST PERSON SETUP (Taka - Read This!)

You're the first one working! Here's exactly what to do:

## ✅ Step 1: Install Dependencies

```bash
cd /Users/takatoshilee/html.ai/backend

# Make setup script executable
chmod +x setup.sh

# Run setup (creates venv and installs everything)
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

This installs:
- FastAPI (web server)
- LangGraph (multi-agent orchestration)
- OpenAI SDK (for GPT-4)
- Pydantic (data models)
- LangChain (AI framework)
- etc.

**IMPORTANT:** Always activate the venv before running Python:
```bash
source venv/bin/activate
```

---

## ✅ Step 2: Get OpenAI API Key

**Option A: Use Your Own**
1. Go to https://platform.openai.com/api-keys
2. Create new key
3. Copy it

**Option B: Use Team's**
- Ask Sultan/Tanuj/Kish if anyone has one
- Share in Discord/Slack (NOT in GitHub!)

---

## ✅ Step 3: Create .env File

```bash
cd /Users/takatoshilee/html.ai/backend
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
```

**IMPORTANT**: This `.env` file is in `.gitignore` - it will NOT be pushed to GitHub! ✅

---

## ✅ Step 4: Test Everything Works

```bash
cd /Users/takatoshilee/html.ai/backend
python test_workflow.py
```

You should see:
```
🧪 TESTING ADAPTIVE IDENTITY ENGINE
✅ OpenAI API key found: sk-...
📊 Creating demo session...
🤖 Initializing Multi-Agent Workflow...
⚡ Running Multi-Agent Workflow...

AGENT COMMUNICATION LOG:
1. [timestamp] Analytics Agent: Computing behavioral vector from 5 events
2. [timestamp] Identity Interpretation Agent: Identified as confident
3. [timestamp] Decision Agent: Selected 'hero_confident_v1'
4. [timestamp] Guardrail Agent: ✅ All guardrails passed

✅ ALL TESTS PASSED!
```

---

## ✅ Step 5: Push to GitHub

### First, verify .gitignore works:

```bash
cd /Users/takatoshilee/html.ai

# Check what will be committed
git status

# You should NOT see:
# - .env (this has your API key!)
# - __pycache__/
# - .DS_Store

# You SHOULD see:
# - backend/*.py
# - sdk/identity.js
# - demo-store/index.html
# - *.md files
```

### Then push:

```bash
git add -A
git commit -m "Initial commit - Adaptive Identity Engine scaffolding

- Multi-agent backend with LangGraph (4 agents)
- FastAPI server for event ingestion
- identity.js SDK for frontend
- Demo e-commerce store
- Full documentation

Targets: Foresters + Amplitude + Shopify sponsor tracks"

git branch -M main
git remote add origin https://github.com/[YOUR-USERNAME]/[REPO-NAME].git
git push -u origin main
```

---

## ✅ Step 6: Share with Team

**In Discord/Slack, send:**

```
🚀 Code is live!

Repo: https://github.com/[your-repo-url]

Setup:
1. Clone the repo
2. cd html.ai/backend
3. pip install -r requirements.txt
4. Create .env file with: OPENAI_API_KEY=sk-...
   (I'll DM you the key - DON'T COMMIT IT!)
5. Test: python test_workflow.py

Tasks are in PROJECT_BRIEF.md - check your assigned section!

Let's build! 💪
```

Then **DM each person the OpenAI API key privately** (never in public channel)

---

## 🔥 Quick Reference - What Goes Where

### ✅ SAFE to push to GitHub:
- All `.py` files
- All `.js` files
- All `.html` files
- All `.md` files
- `requirements.txt`
- `.env.example` (no actual key)
- `.gitignore`

### ❌ NEVER push to GitHub:
- `.env` (has real API key)
- `__pycache__/`
- `.DS_Store`
- `venv/` or `env/`

The `.gitignore` file already blocks these! ✅

---

## 🆘 Troubleshooting

**"ModuleNotFoundError: No module named 'pydantic'"**
→ Run `pip install -r requirements.txt`

**"OpenAI API key not found"**
→ Make sure `.env` file exists in `backend/` directory

**"git push rejected"**
→ Make sure you created the GitHub repo first
→ Use the exact URL from GitHub

**"Test failed"**
→ Share the error in team chat
→ We'll debug together

---

## 📋 Your Tasks After Pushing (Taka)

1. [ ] Get code working locally
2. [ ] Push to GitHub
3. [ ] Share repo + API key with team
4. [ ] Deploy backend to Railway.app or Render.com
5. [ ] Test deployed API
6. [ ] Help team with integration

---

You got this! 🚀
