# MongoDB Atlas Integration Plan

## MLH Prize Track
**Best Use of MongoDB Atlas**
**Prize**: M5GO IoT Starter Kit

## Why MongoDB for This Project?

Perfect fit because we need to store:
- **User sessions** (behavioral data over time)
- **Events** (high-volume time-series data)
- **Variants** (UI variant performance metrics)
- **A/B test results** (aggregated analytics)

MongoDB is ideal for:
- ✅ Schema-less event data (different events have different properties)
- ✅ Time-series collections (perfect for behavioral events)
- ✅ Fast writes (event ingestion)
- ✅ Aggregation pipelines (compute behavioral vectors)

---

## Integration Points

### 1. Replace In-Memory Session Store
**Current**: `sessions: Dict[str, Dict[str, Any]] = {}`
**New**: MongoDB Atlas collection `sessions`

### 2. Event Storage
**Current**: Events stored in session object
**New**: MongoDB time-series collection `events`

### 3. Variant Performance Tracking
**Current**: Hardcoded in `DEMO_VARIANTS`
**New**: MongoDB collection `variants` with real-time performance updates

### 4. Analytics Queries
Use MongoDB aggregation pipelines to:
- Compute behavioral vectors from events
- Calculate conversion rates per variant
- Segment users by behavior patterns

---

## Quick Setup

### 1. Create MongoDB Atlas Account
- Go to mongodb.com/cloud/atlas
- Free tier (M0) is perfect for hackathon
- Create cluster (takes 3-5 minutes)

### 2. Get Connection String
```
mongodb+srv://username:password@cluster.mongodb.net/adaptive-identity?retryWrites=true&w=majority
```

### 3. Update Code
Add to `requirements.txt`:
```
pymongo[srv]==4.10.1
motor==3.6.0  # async MongoDB driver
```

### 4. Update `.env`
```
MONGODB_URI=mongodb+srv://...
```

---

## Implementation

I'll create:
- `backend/database.py` - MongoDB connection & schemas
- Update `backend/main.py` - Use MongoDB instead of in-memory
- Update agents to query from MongoDB

This adds:
- ✅ Persistent data across server restarts
- ✅ Real analytics (not just demo data)
- ✅ Scalability story for judges
- ✅ MongoDB prize eligibility!

Ready to implement?
