# html.ai Multi-Tenant B2B Platform

Self-improving UI optimization for e-commerce with cross-site user tracking.

## Quick Start

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| API | 3000 | Main backend API |
| Tracking | 3001 | Central sync service for cross-site tracking |
| SDK | 8080 | JavaScript SDK server |
| Dashboard | 8081 | Admin dashboard |
| Demo Store | 8082 | Example e-commerce site |
| MongoDB | 27017 | Database |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     html.ai Platform                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐    │
│  │  Business A  │     │  Business B  │     │  Business C  │    │
│  │  (shoes.com) │     │ (clothes.com)│     │  (bags.com)  │    │
│  │              │     │              │     │              │    │
│  │  <script>    │     │  <script>    │     │  <script>    │    │
│  │  SDK.js      │     │  SDK.js      │     │  SDK.js      │    │
│  │  apiKey=A    │     │  apiKey=B    │     │  apiKey=C    │    │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘    │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              Central Tracking Service                      │  │
│  │              (tracking.htmlai.com:3001)                   │  │
│  │                                                            │  │
│  │  - Issues global_uid cookie (1st party on tracking domain) │  │
│  │  - Sync iframe for cross-site identification              │  │
│  │  - Links business UIDs to global UID                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    Main API (port 3000)                    │  │
│  │                                                            │  │
│  │  - Business registration & API keys                       │  │
│  │  - Event tracking with business isolation                 │  │
│  │  - AI-powered content optimization                        │  │
│  │  - Data sharing agreements                                │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      MongoDB                               │  │
│  │                                                            │  │
│  │  Collections:                                             │  │
│  │  - businesses (API keys, tiers, partner lists)            │  │
│  │  - global_users (cross-site identity linking)             │  │
│  │  - events (behavioral tracking, isolated by business)     │  │
│  │  - users (sessions, per business)                         │  │
│  │  - variants (A/B test results)                            │  │
│  │  - data_sharing_agreements (partner permissions)          │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## API Endpoints

### Business Management

```bash
# Register a new business
POST /api/business/register
{
  "name": "My Store",
  "domain": "mystore.com",
  "email": "admin@mystore.com"
}
# Returns: api_key, api_secret, business_id

# Get business info
GET /api/business/me
Headers: X-API-Key: pk_xxxxx
```

### Data Sharing

```bash
# Request data sharing with partner
POST /api/sharing/request
Headers: X-API-Key: pk_xxxxx
{
  "partner_business_id": "biz_partner123",
  "sharing_level": "aggregate",  # or "full"
  "permissions": {
    "share_conversion_data": true
  }
}

# View pending requests
GET /api/sharing/pending

# Accept a request
POST /api/sharing/accept/{agreement_id}

# Revoke sharing
POST /api/sharing/revoke/{agreement_id}
```

### Event Tracking

```bash
# Track single event
POST /api/events/track
Headers: X-API-Key: pk_xxxxx
{
  "user_id": "user_123",
  "session_id": "sess_456",
  "event_name": "product_click",
  "component_id": "hero",
  "properties": { "product_id": "shoe-1" },
  "global_uid": "guid_xxxxx"  # Optional, from sync
}

# Track batch of events
POST /api/events/batch
```

### AI Optimization

```bash
# Optimize HTML component
POST /api/optimize
Headers: X-API-Key: pk_xxxxx
{
  "user_id": "user_123",
  "component_id": "hero-cta",
  "html": "<div>Original content</div>",
  "global_uid": "guid_xxxxx"
}
# Returns: optimized variant based on user behavior
```

## SDK Integration

```html
<!-- Add to your site -->
<script src="https://cdn.htmlai.com/sdk.js"
        data-api-key="pk_live_xxxxx"
        data-tracking-domain="https://tracking.htmlai.com"
        data-api-url="https://api.htmlai.com">
</script>

<!-- Wrap components for AI optimization -->
<ai-optimize component-id="hero">
  <h1 data-ai="headline">Welcome</h1>
  <p data-ai="subheadline">Check out our products</p>
  <button data-ai="cta">Shop Now</button>
</ai-optimize>
```

### Manual Tracking

```javascript
// Track custom events
HtmlAI.track('add_to_cart', 'product-123', {
  price: 99.99,
  quantity: 1
});

// Get user identity
const user = HtmlAI.getUser();
console.log(user.user_id, user.global_uid);

// Callback when cross-site sync completes
HtmlAI.onSync((globalUid) => {
  console.log('User synced across sites:', globalUid);
});
```

## Subscription Tiers

| Feature | Free | Starter | Growth | Enterprise |
|---------|------|---------|--------|------------|
| Events/month | 10K | 100K | 1M | Unlimited |
| Partners | 0 | 3 | 10 | Unlimited |
| Cross-site tracking | No | Yes | Yes | Yes |
| Data export | No | No | Yes | Yes |
| Price | $0 | $49 | $199 | Contact |

## Cross-Site Tracking Flow

1. User visits Business A (shoes.com)
2. SDK creates local `user_id` cookie
3. SDK loads sync iframe from tracking.htmlai.com
4. Tracking domain sets `global_uid` cookie (first-party)
5. SDK links `user_id` → `global_uid` via API

6. User visits Business B (clothes.com)
7. SDK creates NEW local `user_id` (different domain)
8. Sync iframe reads SAME `global_uid` (same tracking domain)
9. SDK links Business B's `user_id` → same `global_uid`

10. Now both businesses can:
    - See the same user visited both sites
    - Share behavioral data (if agreement exists)
    - Personalize based on cross-site behavior

## Data Sharing Permissions

When requesting data sharing, you can configure:

| Permission | Description |
|------------|-------------|
| `share_behavioral_vectors` | Share engagement scores, scroll patterns, etc. |
| `share_identity_states` | Share detected user states (confident, cautious, etc.) |
| `share_conversion_data` | Share which products users converted on |
| `share_raw_events` | Share individual event data (most detailed) |

## Demo

1. Start the stack: `docker-compose up -d`
2. Open Business A: http://localhost:8082/demo-business-a.html
3. Click around, scroll, interact
4. Open Business B: http://localhost:8082/demo-business-b.html
5. Notice the "Cross-Site" indicator shows you're recognized!
6. View admin dashboard: http://localhost:8081

## Environment Variables

```bash
# .env file
GEMINI_API_KEY=your_key_here  # For AI-powered optimization
MONGO_URI=mongodb://mongo:27017/  # MongoDB connection
```

## Development

```bash
# Run API locally (without Docker)
cd htmlTag/aiBackend
pip install -r requirements_multitenant.txt
uvicorn server_multitenant:app --reload --port 3000
```
