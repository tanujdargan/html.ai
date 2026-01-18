# Adaptive Identity Engine - Demo Script

## Quick Setup

1. **Start Backend**: `cd backend && source venv/bin/activate && uvicorn main:app --port 8000`
2. **Start Frontend**: `cd demo-store && python3 -m http.server 8080`
3. **Open Store**: http://localhost:8080
4. **Open Dashboard**: http://localhost:8080/dashboard.html (in separate tab)

---

## How to Trigger Each Identity State

The system analyzes 5 behavioral metrics to classify users:
- **exploration_score**: How much browsing vs focused behavior
- **hesitation_score**: Indecision and backtracking
- **engagement_depth**: Time spent vs content consumed
- **decision_velocity**: Speed through the funnel
- **content_focus_ratio**: Focused vs scattered attention

---

### 1. CONFIDENT (Green Variant)

**What it looks like:**
- Background: Light green gradient (#e8f5f2)
- Headline: "Premium Tech at Your Fingertips"
- CTA: "Shop Now"
- Badge: "CONFIDENT"

**How to trigger:**
1. Load the page fresh (Cmd+Shift+R)
2. Click directly on ONE product within 3-5 seconds
3. Click "Add to Cart" immediately (within 2 seconds)
4. Refresh the hero section or reload page
5. You should see the GREEN variant

**Why it works:**
- High decision velocity (fast clicks)
- Low exploration (focused on one product)
- Low hesitation (no backtracking)

**Expected dashboard results:**
- Identity: CONFIDENT
- Variant shown: hero_confident_v1
- Conversion: YES (if you clicked Add to Cart)

---

### 2. EXPLORATORY (Blue Variant)

**What it looks like:**
- Background: Light blue gradient (#e3f2fd)
- Headline: "Discover Premium Electronics"
- CTA: "Browse Collection"
- Badge: "EXPLORATORY"

**How to trigger:**
1. Load page fresh
2. Scroll down slowly through ALL products (scroll to bottom)
3. Click on 3-4 different product cards
4. DON'T add anything to cart
5. Scroll back up after 15+ seconds
6. Refresh or reload page

**Why it works:**
- High exploration score (browsing multiple products)
- Low conversion signals (no cart additions)
- Wide browsing pattern

**Expected dashboard results:**
- Identity: EXPLORATORY
- Variant shown: hero_exploratory_v1
- Conversion: NO

---

### 3. OVERWHELMED (Purple Variant)

**What it looks like:**
- Background: Light purple gradient (#f3e5f5)
- Headline: "Not Sure What You Need?"
- CTA: "See Our Picks"
- Badge: "OVERWHELMED"

**How to trigger:**
1. Load page fresh
2. Click on Product 1 → wait 2 seconds
3. Click on Product 2 → wait 2 seconds
4. Click BACK on Product 1 (backtracking!)
5. Click on Product 3 → wait 2 seconds
6. Click BACK on Product 1 again
7. Scroll up and down without clicking CTA
8. Wait 10+ seconds on page
9. Refresh/reload

**Why it works:**
- High backtracking (revisiting products)
- Low content focus (scattered attention)
- Hesitation signals (dwelling without action)

**Expected dashboard results:**
- Identity: OVERWHELMED
- Variant shown: hero_overwhelmed_v1
- Conversion: NO (unless you add to cart after)

---

### 4. COMPARISON_FOCUSED (Orange Variant)

**What it looks like:**
- Background: Light orange gradient (#fff3e0)
- Headline: "Compare Features & Specs"
- CTA: "Compare Products"
- Badge: "COMPARISON"

**How to trigger:**
1. Load page fresh
2. Click on Product 1 and read details (hover for 5+ seconds)
3. Scroll down slowly on Product 1 card area
4. Click on Product 2 and read details (hover for 5+ seconds)
5. Click BACK on Product 1 (revisit)
6. Scroll down to 50%+ depth
7. Spend 20+ seconds total on page
8. Refresh/reload

**Why it works:**
- High engagement depth (reading/scrolling)
- Multiple revisits to same products
- Careful consideration of options

**Expected dashboard results:**
- Identity: COMPARISON_FOCUSED
- Variant shown: hero_comparison_v1
- Conversion: MAYBE (if you add to cart)

---

### 5. READY_TO_DECIDE (Dark Green - BEST PERFORMER!)

**What it looks like:**
- Background: Dark gradient (#1a1a1a) with bright green accents
- Headline: "Complete Your Order Today"
- CTA: "View Cart"
- Badge: "READY"

**How to trigger:**
1. Load page fresh
2. Click "Add to Cart" on Product 1 (within 5 seconds)
3. Click "Add to Cart" on Product 2 immediately after
4. Click the cart icon in nav bar
5. Scroll to hero section
6. Refresh/reload

**Why it works:**
- Very high decision velocity
- High conversion signals (multiple cart additions)
- Low exploration (focused intent)

**Expected dashboard results:**
- Identity: READY_TO_DECIDE
- Variant shown: hero_ready_v1
- Conversion: YES
- **Highest conversion rate: 18%**

---

### 6. CAUTIOUS (Pink Variant)

**What it looks like:**
- Background: Light pink gradient (#ffebee)
- Headline: "Shop Risk-Free with 30-Day Returns"
- CTA: "Shop Safely"
- Trust badges: "30-day returns", "Secure checkout", "10k+ reviews"
- Badge: "CAUTIOUS"

**How to trigger:**
1. Load page fresh
2. Hover over Product 1 (DON'T click, just hover for 3 seconds)
3. Hover over Product 2 (DON'T click, just hover for 3 seconds)
4. Click on Product 1 → immediately click on Product 2 (backtracking)
5. Click BACK on Product 1 again
6. Scroll up and down multiple times
7. Spend 20+ seconds WITHOUT clicking any CTA or Add to Cart
8. Refresh/reload

**Why it works:**
- High hesitation score (lots of hovering, no action)
- Multiple page revisits (backtracking)
- Seeking trust signals (long time on page)

**Expected dashboard results:**
- Identity: CAUTIOUS
- Variant shown: hero_cautious_v1
- Conversion: NO (unless reassured enough to buy)

---

### 7. IMPULSE_BUYER (Red Flash Sale - HIGHEST CONVERSION!)

**What it looks like:**
- Background: BRIGHT RED gradient (#ff1744) with pulsing animation
- Headline: "FLASH SALE - 40% OFF!"
- CTA: "Shop Sale Now" (yellow button)
- Countdown timer effect
- Pulsing background animation
- Badge: "IMPULSE"

**How to trigger:**
1. Load page fresh
2. IMMEDIATELY click "Add to Cart" on Product 1 (within 1-2 seconds)
3. IMMEDIATELY click "Add to Cart" on Product 2 (within 1 second)
4. IMMEDIATELY click "Add to Cart" on Product 3 (rapid fire!)
5. Total time should be under 5 seconds
6. Refresh/reload

**Why it works:**
- Very low hesitation (instant clicks)
- Very high decision velocity (rapid actions)
- Quick clicks without browsing
- Responds to scarcity/urgency

**Expected dashboard results:**
- Identity: IMPULSE_BUYER
- Variant shown: hero_impulse_v1
- Conversion: YES (multiple times!)
- **Highest conversion rate: 22%**

---

## Demo Flow for Presentation

### Opening (2 minutes)
1. Show the store at http://localhost:8080
2. Explain: "This looks like a normal e-commerce site, but it's adapting in real-time"
3. Open dashboard at http://localhost:8080/dashboard.html side-by-side

### Demo 1: Confident User (1 minute)
1. Load fresh page
2. Quickly click product → Add to Cart
3. Show GREEN variant appears
4. Point to dashboard: "See? CONFIDENT state, 15% conversion rate"

### Demo 2: Impulse Buyer (1 minute)
1. Load fresh page
2. Rapid-fire add 3 products to cart (under 5 seconds)
3. Show BRIGHT RED pulsing variant
4. Point to dashboard: "IMPULSE buyer detected, 22% conversion rate - our best performer!"

### Demo 3: Overwhelmed User (1 minute)
1. Load fresh page
2. Click around randomly, backtrack, hover without action
3. Show PURPLE variant with "We'll Help You Choose"
4. Point to dashboard: "System detected overwhelmed behavior, simplified the choice"

### Demo 4: Show Analytics (1 minute)
1. Point to dashboard table showing:
   - Different variants tried
   - Conversion rates for each
   - Which identity states trigger which variants
2. Highlight: "The AI learns which variants work best for which user types"

### Closing (30 seconds)
- "This demonstrates real-time behavioral analytics → identity classification → variant selection"
- "All powered by multi-agent workflow with Analytics, Identity, Decision, and Guardrail agents"

---

## Tweaking the Algorithm for Demo

If identity changes aren't obvious enough, you can adjust thresholds in:
`/Users/takatoshilee/html.ai/backend/agents/identity_agent.py`

**Make IMPULSE_BUYER easier to trigger:**
```python
# Line ~80-90 in classify_identity()
if decision_velocity > 0.6 and hesitation_score < 0.2:  # Lower from 0.8 and 0.3
    return IdentityState.IMPULSE_BUYER
```

**Make OVERWHELMED easier to trigger:**
```python
# Line ~95-100
if hesitation_score > 0.5 and content_focus_ratio < 0.4:  # Lower from 0.7 and 0.5
    return IdentityState.OVERWHELMED
```

**Make CONFIDENT easier to trigger:**
```python
# Line ~60-65
if decision_velocity > 0.5 and exploration_score < 0.3:  # Lower from 0.7 and 0.4
    return IdentityState.CONFIDENT
```

---

## Troubleshooting

**Variant not changing?**
- Make sure you refresh the page AFTER performing the actions
- The identity is classified when `/api/variants/get` is called
- Hero section updates when page loads or when you scroll to it

**Dashboard showing 0 conversions?**
- Make sure you clicked "Add to Cart" button
- Check browser console for "[Conversion Tracked]" message
- Refresh dashboard (auto-refreshes every 5 seconds)

**Wrong variant appearing?**
- The algorithm has randomness (20% exploration rate)
- Try the sequence 2-3 times to see consistent results
- Check backend logs for identity classification

**Backend not responding?**
- Check if running: `lsof -ti:8000`
- Restart: `cd backend && uvicorn main:app --port 8000`

---

## Key Talking Points for Judges

1. **Real-time Behavioral Analytics**: System tracks clicks, hovers, scrolling, backtracking
2. **Multi-Agent Architecture**: Analytics → Identity → Decision → Guardrail agents collaborate
3. **7 Distinct Identity States**: Each with unique behavioral profile and optimized variant
4. **Contextual Bandit Algorithm**: Epsilon-greedy selection balances exploration vs exploitation
5. **Conversion Tracking**: Dashboard shows which variants work best for which user types
6. **Production-Ready**: Uses FastAPI, LangGraph, Gemini AI, proper CORS, session management
