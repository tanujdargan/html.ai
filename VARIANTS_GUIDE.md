# Identity States & Variants Guide

## Overview

The Adaptive Identity Engine classifies users into 7 distinct behavioral identity states based on real-time interaction patterns. Each identity state triggers a specific variant optimized for that user type.

---

## Identity States & Matching Variants

### 1. CONFIDENT
**Behavioral Profile:**
- High decision velocity (fast clicks, low hesitation)
- Low exploration (knows what they want)
- Minimal backtracking
- Direct path to conversion

**Variant:** `hero_confident_v1`
- **Headline:** "Complete Your Purchase Today"
- **Subheadline:** "Join thousands of satisfied customers"
- **CTA:** "Buy Now"
- **Urgency:** High
- **Visual Style:** Shopify green gradient background (#e8f5f2 to #d4ede6)
- **Conversion Rate:** 15%

---

### 2. EXPLORATORY
**Behavioral Profile:**
- High exploration score (browsing multiple products)
- Low conversion intent (not ready to buy yet)
- Medium engagement depth
- Wide browsing pattern

**Variant:** `hero_exploratory_v1`
- **Headline:** "Discover Our Collection"
- **Subheadline:** "Find the perfect fit for your needs"
- **CTA:** "Explore Products"
- **Urgency:** Low
- **Visual Style:** Blue gradient background (#e3f2fd to #bbdefb)
- **Conversion Rate:** 8%

---

### 3. OVERWHELMED
**Behavioral Profile:**
- Scattered attention (high backtracking)
- Low content focus ratio
- Hesitation signals (dwelling without action)
- Too many options causing paralysis

**Variant:** `hero_overwhelmed_v1`
- **Headline:** "We'll Help You Choose"
- **Subheadline:** "Answer 3 quick questions to find your match"
- **CTA:** "Get Started"
- **Urgency:** Medium
- **Visual Style:** Purple/lavender gradient (#f3e5f5 to #e1bee7)
- **Conversion Rate:** 12%

---

### 4. COMPARISON_FOCUSED
**Behavioral Profile:**
- High engagement depth (reading details)
- Multiple revisits to same products
- Careful consideration of options
- Feature-focused browsing

**Variant:** `hero_comparison_v1`
- **Headline:** "Compare Our Best Sellers"
- **Subheadline:** "Side-by-side feature breakdown"
- **CTA:** "See Comparison"
- **Urgency:** Low
- **Visual Style:** Orange gradient (#fff3e0 to #ffe0b2)
- **Conversion Rate:** 11%

---

### 5. READY_TO_DECIDE (Best Performer!)
**Behavioral Profile:**
- Very high decision velocity
- High conversion signals (add to cart, checkout views)
- Low exploration (focused intent)
- Strong purchase signals

**Variant:** `hero_ready_v1`
- **Headline:** "Ready to Check Out?"
- **Subheadline:** "Free shipping on orders over $50"
- **CTA:** "Proceed to Checkout"
- **Urgency:** High
- **Visual Style:** Dark gradient (#1a1a1a to #2d2d2d) with bright green accents
- **Conversion Rate:** 18% (HIGHEST)

---

### 6. CAUTIOUS
**Behavioral Profile:**
- High hesitation score
- Seeking trust signals
- Multiple page revisits
- Needs reassurance before purchase

**Variant:** `hero_cautious_v1`
- **Headline:** "Risk-Free Shopping Guarantee"
- **Subheadline:** "30-day returns, secure checkout, trusted by 10,000+ customers"
- **CTA:** "Shop with Confidence"
- **Urgency:** Medium
- **Trust Elements:** Shows trust badges (30-day returns, secure checkout, customer reviews)
- **Visual Style:** Pink/red gradient (#ffebee to #ffcdd2)
- **Conversion Rate:** 13%

---

### 7. IMPULSE_BUYER
**Behavioral Profile:**
- Very low hesitation
- High decision velocity
- Quick clicks without much browsing
- Responds to scarcity and urgency

**Variant:** `hero_impulse_v1`
- **Headline:** "FLASH SALE - 40% OFF!"
- **Subheadline:** "Only 3 hours left! Limited stock available"
- **CTA:** "Grab Deal Now"
- **Urgency:** Extreme
- **Special Effects:** Pulsing animation, countdown timer, flashing badge
- **Visual Style:** Bright red gradient (#ff1744 to #d50000) with yellow CTA
- **Conversion Rate:** 22% (HIGHEST for impulse scenarios)

---

## How to Trigger Each Variant (For Demo)

### CONFIDENT:
- Click directly on a product
- Add to cart quickly (within 5 seconds)
- Fast, decisive actions

### EXPLORATORY:
- Browse multiple product categories
- Scroll through all products
- Don't add anything to cart

### OVERWHELMED:
- Click on 4+ different products
- Backtrack (revisit products)
- Spend 10+ seconds on page without clicking CTAs

### COMPARISON_FOCUSED:
- Click on 2-3 products
- Revisit the same product multiple times
- Spend time reading (scroll depth 50%+)

### READY_TO_DECIDE:
- Add items to cart
- View cart multiple times
- High engagement with checkout-related elements

### CAUTIOUS:
- Hover over products without clicking
- Backtrack frequently
- Spend long time on page (15+ seconds) without converting

### IMPULSE_BUYER:
- Very fast clicking
- Add to cart within 2-3 seconds
- Multiple rapid interactions

---

## Behavioral Vector Metrics

The system computes 5 key metrics to determine identity state:

1. **exploration_score** (0.0-1.0): How much the user explores vs. stays focused
2. **hesitation_score** (0.0-1.0): Degree of indecision and backtracking
3. **engagement_depth** (0.0-1.0): Time spent vs. content consumed
4. **decision_velocity** (0.0-1.0): Speed of progression through funnel
5. **content_focus_ratio** (0.0-1.0): Focused browsing vs. scattered attention

---

## Visual Variant Differences (Quick Reference)

| Identity | Background Color | Top Border | Button Color | Animation |
|----------|-----------------|------------|--------------|-----------|
| CONFIDENT | Light Green | Shopify Green | Green | None |
| EXPLORATORY | Light Blue | Blue | Blue | None |
| OVERWHELMED | Light Purple | Purple | Purple | None |
| COMPARISON | Light Orange | Orange | Orange | None |
| READY_TO_DECIDE | Dark Gray | Bright Green | Bright Green | None |
| CAUTIOUS | Light Pink | Red | Red | None |
| IMPULSE_BUYER | Bright Red | Red/Orange | Yellow | Pulse + Flash |

---

## Analytics Dashboard

Access the analytics dashboard at `http://localhost:8080/dashboard.html` to see:

- Total sessions and conversions
- Conversion rate per variant
- Identity state distribution
- Engagement metrics
- Which variants work best for which user types

This lets you demonstrate how the AI learns which variants convert better for different user behaviors!
