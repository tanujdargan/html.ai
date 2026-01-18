# 📊 html.ai Analytics Dashboard

Beautiful real-time dashboard for monitoring your multi-agent AI system.

## Features

### Real-Time Metrics
- **Total Sessions** - Unique user sessions tracked
- **Total Events** - Behavioral events captured
- **Variants Tested** - A/B test variations
- **System Status** - Multi-agent or stub mode

### Variant Performance
- Conversion rates by variant
- Identity state targeting
- Real-time performance tracking
- Visual progress indicators

### Identity Distribution
- User behavior patterns
- Identity state breakdown
- Session distribution

### Behavioral Vectors
- Exploration score
- Hesitation patterns
- Engagement depth
- Decision velocity
- Content focus ratio

### Agent Communication Log
- Live agent activity
- Multi-agent orchestration flow
- Decision-making transparency

## Quick Start

### 1. Start Backend
```bash
cd /Users/takatoshilee/html.ai/htmlTag
docker compose up --build
```

### 2. Open Dashboard
```
http://localhost:8080/dashboard.html
```

The dashboard auto-refreshes every 5 seconds!

## API Endpoints Used

```javascript
// Main analytics endpoint
GET /api/analytics/dashboard
Returns: {
  total_users: number,
  total_events: number,
  total_variants: number,
  multi_agent_enabled: boolean,
  variant_stats: [...],
  identity_distribution: {...}
}

// Recent agent logs
GET /api/analytics/recent-logs
Returns: [
  {
    timestamp: "2026-01-17T...",
    agent: "Analytics Agent",
    message: "Computing behavioral vector..."
  },
  ...
]
```

## Sponsor Prize Demos

### Foresters Financial (Multi-Agent)
**What to show:**
1. Open dashboard
2. Point to "Agent Communication Log"
3. Show 4 agents working together:
   - Analytics Agent → Behavioral vector
   - Identity Agent → State interpretation
   - Decision Agent → Variant selection
   - Guardrail Agent → Validation

**Screenshot:** Agent log showing all 4 agents

### Amplitude (Behavioral Analytics)
**What to show:**
1. Point to "Behavioral Vector" section
2. Explain each metric:
   - **Exploration:** How much user is browsing
   - **Hesitation:** Decision uncertainty
   - **Engagement:** Depth of interaction
   - **Velocity:** Speed of decisions
   - **Focus:** Attention patterns

**Key point:** "NOT user categorization - behavioral vectors!"

**Screenshot:** Behavioral vector bars

### Shopify (E-commerce)
**What to show:**
1. Point to "Variant Performance"
2. Show conversion rates by identity
3. Examples:
   - `hero_confident_v1` → 15% conversion (for confident buyers)
   - `hero_exploratory_v1` → 8% conversion (for browsers)
   - `hero_ready_v1` → 18% conversion (for ready-to-buy)

**Key point:** "AI adapts UI based on shopping behavior"

**Screenshot:** Variant performance table

## Dashboard Features

### Auto-Refresh
- Updates every 5 seconds automatically
- No manual refresh needed
- Real-time monitoring

### Responsive Design
- Works on desktop and mobile
- Beautiful gradient design
- Smooth animations

### Empty States
- Helpful messages when no data
- Clear calls to action
- User-friendly

### Color Coding
- **Green** - High performance (>15% conversion)
- **Yellow** - Medium performance (10-15%)
- **Red** - Low performance (<10%)

## Customization

### Change Refresh Rate
Edit line 620 in `dashboard.html`:
```javascript
// Change from 5000ms (5 seconds) to your preference
setInterval(loadDashboard, 5000);
```

### Add More Metrics
Add new cards to the grid:
```html
<div class="card">
    <div class="card-title">Your Metric</div>
    <div class="card-value" id="yourMetric">0</div>
    <div class="card-subtitle">Description</div>
</div>
```

### Styling
All styles are in the `<style>` tag at the top. Key CSS variables:
- Primary color: `#667eea`
- Secondary: `#764ba2`
- Background: Linear gradient

## Troubleshooting

### Dashboard shows all zeros
**Check:**
1. Is backend running? `curl http://localhost:3000/`
2. Have you generated any traffic? Visit `http://localhost:8080/`
3. Check browser console for errors (F12)

### "Failed to fetch" error
**Solution:**
```bash
# Make sure backend is running on port 3000
cd htmlTag && docker compose up

# Check backend health
curl http://localhost:3000/api/analytics/dashboard
```

### Logs not showing
**Possible reasons:**
1. No users have visited yet (visit index.html first)
2. Multi-agent system not enabled (check .env file)
3. Agents not loaded (check Docker logs)

## Screenshots for Demo Video

**Must capture:**
1. Full dashboard with all metrics populated
2. Variant performance showing different conversion rates
3. Agent communication log with 4 agents visible
4. Behavioral vector with all 5 metrics
5. Identity distribution showing different user types

**Tips:**
- Generate test traffic first (visit index.html multiple times)
- Click buttons to generate conversion events
- Scroll and interact to generate behavioral data
- Take screenshots after 5-10 test sessions

## Integration with Demo

### Flow for demo video:
1. Show main page (`index.html`) with `<ai-optimize>` tags
2. Interact with page (click, scroll, hover)
3. Switch to dashboard
4. Point out: "See? Multi-agent system is working!"
5. Show agent logs
6. Show behavioral vectors
7. Show variant performance

### Talking points:
- "Real-time monitoring of our AI system"
- "4 agents working together"
- "Behavioral vectors, not user categorization"
- "Self-improving based on conversions"
- "Transparent decision-making"

## Export Data

To export analytics data:
```bash
# Get full dashboard data
curl http://localhost:3000/api/analytics/dashboard > analytics.json

# Get recent logs
curl http://localhost:3000/api/analytics/recent-logs > logs.json
```

## Production Considerations

For production deployment:
1. Add authentication
2. Implement rate limiting
3. Add data export features
4. Connect to analytics platform (Amplitude, Mixpanel)
5. Add alerting for low conversion rates

## File Location

```
htmlTag/sdk/src/dashboard.html
```

**Access:** http://localhost:8080/dashboard.html

---

**This dashboard proves all 3 sponsor prize requirements!** 🏆🏆🏆
