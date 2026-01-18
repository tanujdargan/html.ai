# Dashboard Quick Test Guide

## What You Just Built

A **professional analytics dashboard** similar to Amplitude's with:
- User table showing all cookie-tracked users
- **Clickable rows** that open detailed modal
- Behavioral vector visualization
- Event timeline
- **Embedded HTML preview** (shows what user saw)
- Real-time stats and auto-refresh

---

## Test It Now (3 Steps)

### Step 1: Start Backend
```bash
cd /Users/takatoshilee/html.ai/htmlTag
docker compose up --build
```

**Wait for:**
```
adaptive_engine | INFO:     Uvicorn running on http://0.0.0.0:3000
```

### Step 2: Open Dashboard
```bash
# Option A: Direct open
open /Users/takatoshilee/html.ai/htmlTag/dashboard.html

# Option B: Serve it
cd /Users/takatoshilee/html.ai/htmlTag
python3 -m http.server 8080
# Then open: http://localhost:8080/dashboard.html
```

### Step 3: Generate Test Data
```bash
# In another terminal
curl -X POST http://localhost:3000/tagAi \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "changingHtml": "<button>Click Me</button>",
    "contextHtml": "<div>Test Page</div>"
  }'
```

**Refresh dashboard** - you should see the user appear!

---

## What You'll See

### Dashboard Shows:
```
┌─────────────────────────────────────────────┐
│ html.ai Dashboard                           │
│ Real-time user analytics & behavioral...    │
└─────────────────────────────────────────────┘

📊 Stats: [1 User] [1 Session] [0 Events] [0 Rewards]

┌─────────────────────────────────────────────┐
│ User Sessions & Behavioral Data            │
│ [Search box] [Refresh]                      │
├─────────────────────────────────────────────┤
│ User ID      │Sessions│Events│Variant│Status│
│ test_user_001│   1    │  0   │  A    │Active│ ← Click this!
└─────────────────────────────────────────────┘
```

### Click on Row → Modal Opens:
```
┌─────────────────────────────────────────────┐
│ User: test_user_001                    [×]  │
├─────────────────────────────────────────────┤
│ User ID: test_user_001                      │
│ Session ID: session_...                     │
│ Identity State: confident                   │
│ Confidence: 85.0%                          │
│                                             │
│ Behavioral Vector                          │
│ Exploration  ████████░░ 75%                │
│ Hesitation   ███░░░░░░░ 25%                │
│ Engagement   ████████░░ 80%                │
│                                             │
│ Event Timeline                             │
│ ┌─────────────────────────────────────────┐│
│ │ 2026-01-17 16:30:42                     ││
│ │ component_viewed                        ││
│ │ {experiment: "hero-cta"}                ││
│ └─────────────────────────────────────────┘│
│                                             │
│ Rendered HTML Preview (Amplitude-style)    │
│ ┌─────────────────────────────────────────┐│
│ │ [Button: Click Me]                      ││
│ └─────────────────────────────────────────┘│
└─────────────────────────────────────────────┘
```

---

## Generate More Realistic Data

### Create Multiple Users
```bash
# User 1 - Variant A
curl -X POST http://localhost:3000/tagAi \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice_123", "changingHtml": "<h1>Welcome</h1>", "contextHtml": ""}'

# User 2 - Variant B
curl -X POST http://localhost:3000/tagAi \
  -H "Content-Type: application/json" \
  -d '{"user_id": "bob_456", "changingHtml": "<h1>Welcome</h1>", "contextHtml": ""}'

# User 3 - Variant A
curl -X POST http://localhost:3000/tagAi \
  -H "Content-Type: application/json" \
  -d '{"user_id": "charlie_789", "changingHtml": "<h1>Welcome</h1>", "contextHtml": ""}'
```

### Add Rewards
```bash
curl -X POST http://localhost:3000/rewardTag \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice_123", "reward": 1.0}'

curl -X POST http://localhost:3000/rewardTag \
  -H "Content-Type: application/json" \
  -d '{"user_id": "bob_456", "reward": 1.0}'
```

**Refresh dashboard** - now you have multiple users!

---

## Test Features

### 1. Click on Different Users
- Each user has different data
- Modal shows their journey
- Preview shows their HTML

### 2. Search Functionality
- Type part of a user ID
- Table filters in real-time

### 3. Auto-Refresh
- Wait 10 seconds
- Dashboard updates automatically
- Or click "Refresh" button

### 4. Stats Update
- Total users increases
- Variant scores update based on rewards
- Events count increases with activity

---

## For Demo Video

### Perfect Flow:
1. **Start:** "Here's our real-time analytics dashboard"
2. **Show table:** "All users tracked by cookie ID"
3. **Click row:** "Let's see what this user did"
4. **Show modal:** "Session info, behavioral vector, event timeline"
5. **Scroll to preview:** "This is what they actually saw - Amplitude-style"
6. **Close modal, click another:** "Each user has their own journey"
7. **Show stats:** "Variant A winning with score of 4.3"

**Time: ~45 seconds for full demo**

---

## For Judges

### Amplitude Prize - Perfect Alignment:
✅ **Behavioral data:** Vector visualization
✅ **Event tracking:** Timeline shows all events
✅ **Self-improving:** Variant scores update
✅ **Data → Insights → Action:** Complete loop visible
✅ **Amplitude-style UI:** Embedded preview

### Show Them:
1. Click on a user
2. Point to behavioral vector: "NOT user categories - behavior patterns"
3. Point to events: "Every action tracked"
4. Point to preview: "Exactly what they saw"
5. Point to variant scores: "System learns which works better"

---

## Troubleshooting

### Dashboard shows "Cannot Connect"
```bash
# Check backend is running
curl http://localhost:3000/

# Should return:
{"status":"running","service":"html.ai - A/B Testing Engine",...}
```

### No users in table
```bash
# Check MongoDB
curl http://localhost:3000/api/users/all

# Should return JSON with users array
```

### Modal won't open
- Check browser console for errors
- Make sure API endpoints are working
- Try: `curl http://localhost:3000/api/user/test_user_001/journey`

### Preview not showing
- Preview only shows if user has `last_html` stored
- Generate more activity to populate this

---

## API Endpoints (For Testing)

```bash
# Health check
curl http://localhost:3000/

# Get all users
curl http://localhost:3000/api/users/all

# Get user journey
curl http://localhost:3000/api/user/alice_123/journey

# Get analytics
curl http://localhost:3000/api/analytics/dashboard
```

---

## Next Steps

1. ✅ Dashboard created
2. ✅ API endpoints added
3. ✅ Pushed to GitHub
4. 🔄 **Test it now!**
5. 📹 **Record demo video**
6. 🏆 **Show judges**

---

**This dashboard is your secret weapon for the Amplitude prize!** 🎯

It shows exactly what they want to see:
- Behavioral tracking ✅
- Event timeline ✅
- Self-improving loop ✅
- Professional UI ✅
- Amplitude-style preview ✅

**Test it, record it, win it!** 🚀
