# 🧪 Testing Guide - Do This Now!

## ✅ What We Just Fixed

1. **Debug panel** - SDK path fixed (copied to demo-store/)
2. **MongoDB** - Added for prize track eligibility
3. **Dependencies** - All installed and working

---

## 🚀 Test 1: Backend Only (No API Key Needed)

```bash
cd /Users/takatoshilee/html.ai/backend
source venv/bin/activate

# Test imports
python -c "from models.events import Event; from database import MongoDB; print('✅ All imports work!')"
```

**Expected**: `✅ All imports work!`

---

## 🚀 Test 2: Multi-Agent Workflow

**WITHOUT real API key** (uses fallback):
```bash
cd /Users/takatoshilee/html.ai/backend
source venv/bin/activate
python test_workflow.py
```

**Expected output**:
```
✅ Workflow initialized
⚡ Running Multi-Agent Workflow
✅ Workflow completed successfully!
```

You'll see "LLM error, using rule-based fallback" - that's OK! It means agents work, just need real API key.

---

## 🚀 Test 3: Start Backend Server

```bash
cd /Users/takatoshilee/html.ai/backend
source venv/bin/activate
python main.py
```

**Expected**:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this running!**

---

## 🚀 Test 4: Demo Store (MOST IMPORTANT!)

**In a NEW terminal:**
```bash
cd /Users/takatoshilee/html.ai/demo-store
python3 -m http.server 8080
```

Then open: **http://localhost:8080**

### What You Should See:

1. ✅ Purple hero section with "Discover Amazing Products"
2. ✅ **Debug panel in bottom right** (black box)
3. ✅ When you click around, debug panel updates
4. ✅ Browser console shows: `[Adaptive Identity] Initializing...`

### If Debug Panel Doesn't Show:

Open browser console (F12) and check for errors. Most likely:
- Backend not running on port 8000
- CORS error
- JavaScript error

---

## 🐛 Debug Panel Not Showing? Try This:

1. **Check backend is running**:
   ```bash
   curl http://localhost:8000/
   # Should return: {"status": "running", ...}
   ```

2. **Check browser console** (F12 → Console tab)
   - Look for error messages
   - Should see: `[Adaptive Identity] Initializing...`

3. **Check Network tab** (F12 → Network)
   - Should see requests to `http://localhost:8000/api/...`
   - If 404 or CORS error, backend isn't running

---

## 🎉 Success Criteria

You know it works when:
- [x] Backend starts without errors
- [x] Demo page loads
- [x] Debug panel appears bottom right
- [x] Clicking products shows events in debug panel
- [x] Agent communication logs appear

---

## 🆘 Common Issues

**"Connection refused"**
→ Backend not running. Start it in another terminal.

**"CORS error"**
→ Backend is running but blocking requests. Check CORS middleware in main.py.

**"Debug panel empty"**
→ Events are tracking but not getting variants. Check API key.

**"Nothing happens"**
→ Check browser console for JavaScript errors.

---

## 📸 Screenshot This for Your Team!

When debug panel works, take a screenshot showing:
1. The demo store
2. Debug panel with agent logs
3. Browser console showing no errors

This proves the multi-agent system works! 🎉

---

**Ready? Start with Test 1 and work your way through!**
