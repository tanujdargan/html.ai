# TEST GUIDE - What You Have Right Now

## Current Situation

You have **TWO versions** ready to test:

### Version 1: Original htmlTag (Simple, Working Now)
- **Backend:** `server.py` (simple stub)
- **SDK:** `AiOptimizeElement.js` (current index.js)
- **Status:** ✅ Ready to test immediately
- **Features:** Basic HTML wrapping, polling for updates
- **Limitations:** No AI agents, just stubs

### Version 2: Integrated (Needs Setup)
- **Backend:** `server_integrated.py` (4-agent system)
- **SDK:** `AiOptimizeElement_v2.js` (not loaded yet)
- **Status:** ⚠️ Needs integration script + API key
- **Features:** Full multi-agent system, wins all 3 prizes
- **Limitations:** Requires setup first

---

## OPTION A: Test Original Version (5 minutes)

**Use this to verify Docker/MongoDB work, then upgrade to integrated version**

### 1. Start Backend
```bash
cd /Users/takatoshilee/html.ai/htmlTag
docker compose up --build
```

**Expected output:**
```
adaptive_mongo     | MongoDB started
adaptive_engine    | Uvicorn running on http://0.0.0.0:3000
```

### 2. Start Frontend (New Terminal)
```bash
cd /Users/takatoshilee/html.ai/htmlTag/sdk/src
python3 -m http.server 8080
```

### 3. Test It
Open browser: http://localhost:8080

**What you should see:**
- Page loads with two `<ai-optimize>` blocks
- Console shows: `[ai-optimize] SDK loaded`
- Console shows: `[ai-optimize] Mounted: hero-cta`

**What it does:**
- Wraps HTML in custom tag
- Polls backend every 5 seconds
- Backend returns original HTML (no AI yet)

**Limitations:**
- No multi-agent system
- No behavioral tracking
- Won't win prizes (just a demo)

---

## OPTION B: Test Integrated Version (30 minutes)

**This is what you want for the hackathon - full AI system**

### Step 1: Run Integration Script
```bash
cd /Users/takatoshilee/html.ai
./htmlTag/integrate.sh
```

**What this does:**
- Copies backend agents to htmlTag
- Copies models to htmlTag
- Updates requirements.txt
- Updates SDK to v2

**Expected output:**
```
[1/6] Creating directories...
[2/6] Copying agent files...
  ✓ Copied 5 agent files
[3/6] Copying model files...
  ✓ Copied 2 model files
...
✓ Integration Complete!
```

### Step 2: Add API Key
```bash
cd /Users/takatoshilee/html.ai/htmlTag/aiBackend
nano .env
```

Add this line:
```
GEMINI_API_KEY=your_actual_key_here
```

Save and exit (Ctrl+X, Y, Enter)

### Step 3: Update Dockerfile
```bash
cd /Users/takatoshilee/html.ai/htmlTag/aiBackend
nano Dockerfile
```

Change the last line from:
```dockerfile
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000"]
```

To:
```dockerfile
CMD ["python", "server_integrated.py"]
```

### Step 4: Update SDK Loader
```bash
cd /Users/takatoshilee/html.ai/htmlTag/sdk/src
nano index.js
```

Replace everything with:
```javascript
// Load the v2 SDK with multi-agent backend
import './AiOptimizeElement_v2.js';
```

### Step 5: Update index.html API URL
```bash
nano index.html
```

Find the script tag and change API_URL from 8000 to 3000:
```javascript
// At the top of the file, if there's an API_URL, change it to:
const API_URL = "http://localhost:3000";
```

### Step 6: Start Everything
```bash
# Terminal 1: Backend
cd /Users/takatoshilee/html.ai/htmlTag
docker compose down  # Stop old version
docker compose up --build

# Terminal 2: Frontend
cd /Users/takatoshilee/html.ai/htmlTag/sdk/src
python3 -m http.server 8080
```

### Step 7: Test Multi-Agent System
Open browser: http://localhost:8080
Open console (F12)

**What you should see:**
```
[ai-optimize] SDK loaded - wrap any HTML in <ai-optimize experiment="name">
[ai-optimize] Mounted: hero-cta
[ai-optimize] User ID: user_1234567890_abc123
[ai-optimize] Requesting optimized variant from multi-agent system...
[ai-optimize] ✓ Variant: hero_confident_v1
[ai-optimize] ✓ Identity: confident (confidence: 0.85)
[ai-optimize] ✓ Agent Communication Log:
  - Analytics Agent: Computing behavioral vector from 8 events
  - Identity Agent: Identified as 'confident' with confidence 0.85
  - Decision Agent: Selected 'hero_confident_v1'
  - Guardrail Agent: Decision approved
[ai-optimize] ✓ Behavioral Vector: {exploration_score: 0.72, ...}
```

**If you see this, you're ready for the hackathon!** 🎉

---

## Quick Comparison

| Feature | Original | Integrated |
|---------|----------|------------|
| Setup time | 5 min | 30 min |
| Docker works? | ✅ Test this | ✅ Same |
| MongoDB works? | ✅ Test this | ✅ Same |
| Multi-agent system | ❌ No | ✅ Yes |
| Behavioral tracking | ❌ No | ✅ Yes |
| Agent logs | ❌ No | ✅ Yes |
| Wins Foresters | ❌ No | ✅ Yes |
| Wins Amplitude | ❌ No | ✅ Yes |
| Wins Shopify | ❌ No | ✅ Yes |

---

## My Recommendation

### For Right Now (Next 10 minutes):
**Test OPTION A** to verify:
- Docker works
- MongoDB connects
- Frontend loads
- Basic integration works

### After That Works (Next 30 minutes):
**Switch to OPTION B** to get:
- Full multi-agent system
- All 3 sponsor prizes
- Real hackathon project

---

## Troubleshooting

### Docker Issues
```bash
# If port 3000 in use:
lsof -ti:3000 | xargs kill -9

# If Docker won't start:
docker compose down
docker system prune -f
docker compose up --build
```

### Integration Script Issues
```bash
# If integrate.sh fails:
cd /Users/takatoshilee/html.ai

# Manual copy:
mkdir -p htmlTag/aiBackend/agents
mkdir -p htmlTag/aiBackend/models
cp backend/agents/*.py htmlTag/aiBackend/agents/
cp backend/models/*.py htmlTag/aiBackend/models/
```

### API Key Issues
```bash
# Check if .env exists:
cat htmlTag/aiBackend/.env

# Should show:
# GEMINI_API_KEY=your_key_here
```

---

## What to Test

### Test 1: Basic Functionality
- [ ] Page loads without errors
- [ ] Console shows SDK loaded
- [ ] Custom elements mount
- [ ] No red errors in console

### Test 2: Backend Connection
- [ ] Backend responds to requests
- [ ] MongoDB stores data
- [ ] API endpoints work

### Test 3: Multi-Agent System (After Integration)
- [ ] Agent communication logs appear
- [ ] Behavioral vectors computed
- [ ] Variants change based on behavior
- [ ] Reward signals tracked

---

## Files You'll Edit

### Must Edit (For Integration):
1. `htmlTag/aiBackend/Dockerfile` - Change CMD to use server_integrated.py
2. `htmlTag/aiBackend/.env` - Add GEMINI_API_KEY
3. `htmlTag/sdk/src/index.js` - Load AiOptimizeElement_v2.js

### Optional (For Better Demo):
4. `htmlTag/sdk/src/index.html` - Add more demo components
5. `htmlTag/aiBackend/server_integrated.py` - Customize variants

---

## Next Steps After Testing

Once you confirm it works:

1. **Screenshot everything** - Agent logs, behavioral vectors, variants
2. **Test all 3 prizes** - Foresters, Amplitude, Shopify scenarios
3. **Create demo video** - Show the multi-agent system working
4. **Write Devpost** - Use screenshots and video
5. **Deploy** - Railway for backend, Vercel for frontend
6. **Push to GitHub** - Make repo public
7. **Submit!**

---

## Summary

**Right now:** Test OPTION A (5 min) to verify Docker/MongoDB work

**After that:** Run integration script and test OPTION B (30 min) for full system

**Then:** You're ready to win! 🚀

Let me know which option you want to test first!
