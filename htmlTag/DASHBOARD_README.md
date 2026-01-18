# html.ai Dashboard

**Real-time user analytics and behavioral tracking dashboard**

## Features

### 1. User Table with Cookie-Based Tracking
- View all users by their persistent cookie ID
- See session count, event count, current variant (A/B)
- Status indicators (Active/Inactive)
- Last seen timestamps
- **Click any row** to see detailed user journey

### 2. User Detail Modal (Amplitude-Style)
When you click on a user, you get:

**Session Information:**
- User ID (cookie)
- Session ID
- Identity state
- Confidence score
- Total events
- Last variant shown

**Behavioral Vector:**
- Visual bars showing behavioral metrics
- Exploration, hesitation, engagement, decision velocity, focus
- **NOT user categorization** - just behavior patterns

**Event Timeline:**
- Last 10 events in reverse chronological order
- Event names and properties
- Timestamps
- Shows complete user journey

**HTML Preview (Amplitude-style):**
- Embedded iframe showing the actual HTML rendered for the user
- See exactly what they saw
- Perfect for debugging and demos

### 3. Real-Time Stats
- Total users
- Active sessions
- Total events tracked
- Total rewards (conversions)
- Variant A vs B scores

### 4. Search Functionality
- Search users by cookie ID
- Real-time filtering

### 5. Auto-Refresh
- Dashboard updates every 10 seconds
- Manual refresh button available

---

## How to Use

### 1. Start Backend
```bash
cd htmlTag
docker compose up --build
```

### 2. Open Dashboard
```bash
# Simple way - just open the file
open dashboard.html

# Or serve it
python3 -m http.server 8080
# Then open: http://localhost:8080/dashboard.html
```

### 3. Generate Some Data
- Open your app (e.g., `index.html`)
- Interact with `<ai-optimize>` elements
- Click buttons, scroll, etc.
- Refresh dashboard to see updates

---

## API Endpoints (Used by Dashboard)

### GET /api/users/all
Returns all users with their session data, events, and rewards.

**Response:**
```json
{
  "users": [...],
  "events": [...],
  "rewards": [...],
  "total_users": 5,
  "total_events": 42,
  "total_rewards": 8
}
```

### GET /api/user/{user_id}/journey
Returns detailed journey for a specific user.

**Response:**
```json
{
  "user_id": "user_123",
  "user": {...},
  "session": {...},
  "events": [...],
  "rewards": [...],
  "behavioral_vector": {
    "exploration_score": 0.72,
    "hesitation_score": 0.15,
    ...
  }
}
```

### GET /api/analytics/dashboard
Returns aggregated analytics.

**Response:**
```json
{
  "total_users": 10,
  "active_sessions": 5,
  "variant_a": {
    "users": 6,
    "avg_score": 4.3
  },
  "variant_b": {
    "users": 4,
    "avg_score": 3.8
  },
  "winner": "A"
}
```

---

## Perfect for Demos

### For Judges:
1. **Show the user table** - "Here are all our users tracked by cookie ID"
2. **Click on a user** - "Let's see exactly what this user did"
3. **Point to behavioral vector** - "These are NOT user categories - just behavioral patterns"
4. **Show event timeline** - "Every action tracked in real-time"
5. **Show HTML preview** - "This is what they actually saw - just like Amplitude"

### For Amplitude Prize:
- **Behavioral vectors** clearly visible
- **Event timeline** shows the data collection
- **Self-improving loop** - variant scores update based on rewards
- **Data → Insights → Action** - complete loop demonstrated

### For Foresters Prize:
- If using integrated backend, agent logs appear in events
- Shows multi-agent decision making
- Tracks identity state and confidence

---

## Customization

### Change API URL
Edit line 552 in `dashboard.html`:
```javascript
const API_BASE = 'http://localhost:3000';  // Change this
```

### Change Auto-Refresh Interval
Edit line 712 in `dashboard.html`:
```javascript
setInterval(loadDashboard, 10000);  // 10 seconds
```

### Add More Metrics
Add to the stats grid in HTML and update `updateStats()` function.

---

## Troubleshooting

### Dashboard shows "Cannot Connect to Backend"
**Solution:** Make sure backend is running on port 3000
```bash
cd htmlTag && docker compose up --build
```

### No users showing
**Solution:** Generate some activity first
1. Open `index.html` or your app
2. Interact with elements
3. Refresh dashboard

### Modal not opening
**Solution:** Check browser console for errors. Make sure API endpoint `/api/user/{id}/journey` is working.

### Preview iframe not showing
**Solution:** User might not have `last_html` stored. This is populated when they interact with the app.

---

## MongoDB Structure

The dashboard expects this data structure:

```javascript
// users collection
{
  user_id: "user_123",
  last_session: {
    session_id: "session_456",
    identity_state: "confident",
    identity_confidence: 0.85,
    behavioral_vector: {
      exploration_score: 0.72,
      ...
    }
  },
  variants: {
    A: { current_html: "...", current_score: 4.3 },
    B: { current_html: "...", current_score: 3.0 }
  },
  created_at: "2026-01-17T...",
  last_updated: "2026-01-17T..."
}

// events collection (optional)
{
  user_id: "user_123",
  event_name: "component_viewed",
  timestamp: "2026-01-17T...",
  properties: {...}
}

// rewards collection (optional)
{
  user_id: "user_123",
  variant: "A",
  reward: 1.0,
  timestamp: "2026-01-17T..."
}
```

---

## Tech Stack

- **Frontend:** Vanilla JavaScript + CSS
- **Backend:** FastAPI (Python)
- **Database:** MongoDB
- **Styling:** Inter font, Shopify-inspired design
- **Real-time:** Auto-refresh every 10 seconds

---

## Features Comparison: Root vs htmlTag Dashboard

| Feature | Root Dashboard | htmlTag Dashboard |
|---------|---------------|-------------------|
| Variant performance | ✅ | ✅ |
| Identity distribution | ✅ | Behavioral vector |
| Conversion rates | ✅ | Reward scores |
| **User table** | ❌ | ✅ **NEW** |
| **Cookie tracking** | ❌ | ✅ **NEW** |
| **Clickable rows** | ❌ | ✅ **NEW** |
| **Event timeline** | ❌ | ✅ **NEW** |
| **HTML preview** | ❌ | ✅ **NEW** |
| **Amplitude-style** | Partial | ✅ **FULL** |

---

## Perfect for Hackathon

This dashboard is designed to:
1. **Impress judges** - Visual, interactive, professional
2. **Show data flow** - Clear data → insights → action loop
3. **Demonstrate tracking** - Cookie-based user tracking
4. **Amplitude alignment** - Behavioral vectors, event timelines
5. **Easy to demo** - Click and show, no complex setup

---

**Ready to use! Just start the backend and open `dashboard.html`** 🎉

**Pro tip:** Record a video walking through the dashboard clicking on users and showing their journeys - judges will love it!
