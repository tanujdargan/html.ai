"""
Integrated AI Backend - Merges htmlTag UX with Multi-Agent Brain

This combines:
- htmlTag's simple developer experience (wrap any HTML)
- Root project's sophisticated 4-agent system (Analytics → Identity → Decision → Guardrail)

Sponsor Prize Alignment:
- Foresters: 4 agents + LangGraph + audit logs
- Amplitude: Behavioral vectors (not user categorization!) + self-improving loop
- Shopify: E-commerce conversion optimization
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import os

# Import the multi-agent system from root project
import sys
sys.path.append('../../backend')  # Add root backend to path
from agents.workflow import AdaptiveIdentityWorkflow
from models.events import Event, UserSession, EventType

# ----------------------------------------
# FastAPI App + CORS
# ----------------------------------------
app = FastAPI(
    title="html.ai - Self-Improving UI Engine",
    description="Wrap any HTML in <ai-optimize> for instant AI-powered A/B testing",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# MongoDB
# ----------------------------------------
client = MongoClient("mongodb://mongo:27017/")
mongodb = client["html_ai"]

users_collection = mongodb["users"]
events_collection = mongodb["events"]
variants_collection = mongodb["variants"]

# ----------------------------------------
# Multi-Agent Workflow (THE BRAIN)
# ----------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    print("WARNING: No GEMINI_API_KEY - using mock mode")

workflow = AdaptiveIdentityWorkflow(gemini_api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# ----------------------------------------
# Request Models
# ----------------------------------------
class HtmlOptimizeRequest(BaseModel):
    """Request to optimize HTML content"""
    user_id: str  # Cookie-based persistent ID
    component_id: str  # e.g. "hero-cta", "pricing-block"
    html: str  # The original HTML wrapped in <ai-optimize>
    context_html: Optional[str] = ""  # Optional: surrounding page context

class RewardRequest(BaseModel):
    """Reward signal when user clicks goal button"""
    user_id: str
    component_id: str
    variant_id: str
    reward_type: str = "click"  # "click", "conversion", "engagement"
    properties: Dict[str, Any] = {}

class EventTrackingRequest(BaseModel):
    """Track behavioral events (Amplitude-style)"""
    user_id: str
    session_id: str
    event_name: str
    component_id: Optional[str] = None
    properties: Dict[str, Any] = {}

# ----------------------------------------
# Core Logic: AI Tag Optimization
# ----------------------------------------
@app.post("/api/optimize")
async def optimize_html(request: HtmlOptimizeRequest):
    """
    Main endpoint: Receives HTML, runs multi-agent system, returns optimized variant
    
    Flow:
    1. Get or create user session
    2. Add event: "component_viewed"
    3. Run 4-agent workflow:
       - Analytics Agent: Compute behavioral vector from user history
       - Identity Agent: Interpret identity state (exploratory, confident, etc.)
       - Decision Agent: Select best variant using contextual bandit
       - Guardrail Agent: Validate decision for privacy/ethics
    4. Return optimized HTML + audit log
    """
    try:
        # Get or create session
        session = get_or_create_session(request.user_id)
        
        # Track component view event
        view_event = Event(
            event_name=EventType.COMPONENT_VIEWED,
            session_id=session["session_id"],
            user_id=request.user_id,
            component_id=request.component_id,
            timestamp=datetime.utcnow(),
            properties={"original_html": request.html}
        )
        
        # Add to session history
        session["event_history"].append(view_event.model_dump())
        
        # Save to MongoDB
        events_collection.insert_one({
            **view_event.model_dump(),
            "timestamp": datetime.utcnow()
        })
        
        # Run multi-agent workflow (THE MAGIC)
        if workflow:
            final_state = workflow.process_session(session)
            
            # Extract decision
            variant_decision = final_state.get("outcome_metrics", {}).get("variant_decision")
            audit_log = final_state.get("audit_log", [])
            
            if variant_decision:
                selected_variant = variant_decision["selected_variant"]
                
                # Update session in MongoDB
                users_collection.update_one(
                    {"user_id": request.user_id},
                    {"$set": {
                        "last_session": final_state,
                        "last_updated": datetime.utcnow()
                    }}
                )
                
                # Log variant shown
                variants_collection.insert_one({
                    "user_id": request.user_id,
                    "session_id": session["session_id"],
                    "component_id": request.component_id,
                    "variant_id": selected_variant["variant_id"],
                    "identity_state": final_state.get("identity_state"),
                    "confidence": final_state.get("identity_confidence", 0.0),
                    "timestamp": datetime.utcnow(),
                    "converted": False  # Will be updated on reward
                })
                
                return {
                    "status": "optimized",
                    "variant_id": selected_variant["variant_id"],
                    "content": selected_variant["content"],
                    "identity_state": final_state.get("identity_state"),
                    "confidence": final_state.get("identity_confidence", 0.0),
                    "audit_log": audit_log,  # For Foresters prize demo
                    "behavioral_vector": final_state.get("behavioral_vector")  # For Amplitude prize
                }
        
        # Fallback: return original HTML if workflow fails
        return {
            "status": "original",
            "content": {"html": request.html},
            "message": "Multi-agent system unavailable, showing original"
        }
        
    except Exception as e:
        print(f"Error in optimize_html: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reward")
async def track_reward(request: RewardRequest):
    """
    Track reward signals (button clicks, conversions)
    
    This creates the feedback loop for the self-improving system:
    - Track which variants led to conversions
    - Update variant performance metrics
    - Agents learn which variants work best for each identity state
    """
    try:
        # Log reward event
        reward_event = {
            "user_id": request.user_id,
            "component_id": request.component_id,
            "variant_id": request.variant_id,
            "reward_type": request.reward_type,
            "properties": request.properties,
            "timestamp": datetime.utcnow()
        }
        
        events_collection.insert_one(reward_event)
        
        # Update variant performance
        variants_collection.update_one(
            {
                "user_id": request.user_id,
                "variant_id": request.variant_id,
                "converted": False
            },
            {
                "$set": {
                    "converted": True,
                    "conversion_timestamp": datetime.utcnow()
                }
            }
        )
        
        print(f"[REWARD] {request.reward_type.upper()} tracked for variant {request.variant_id}")
        
        return {
            "status": "reward_tracked",
            "variant_id": request.variant_id,
            "reward_type": request.reward_type
        }
        
    except Exception as e:
        print(f"Error in track_reward: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/events/track")
async def track_event(request: EventTrackingRequest):
    """
    Track behavioral events (Amplitude-style)
    
    Events create the behavioral vector:
    - scroll_depth
    - time_on_component
    - click
    - backtrack
    - etc.
    
    This is NOT user categorization - it's behavioral vectors!
    """
    try:
        event = {
            "user_id": request.user_id,
            "session_id": request.session_id,
            "event_name": request.event_name,
            "component_id": request.component_id,
            "properties": request.properties,
            "timestamp": datetime.utcnow()
        }
        
        events_collection.insert_one(event)
        
        # Update session with new event
        session = get_or_create_session(request.user_id)
        session["event_history"].append(event)
        
        users_collection.update_one(
            {"user_id": request.user_id},
            {"$set": {"last_session": session}}
        )
        
        return {"status": "tracked", "event_name": request.event_name}
        
    except Exception as e:
        print(f"Error in track_event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------
# Analytics Dashboard (For Demo)
# ----------------------------------------
@app.get("/api/analytics/dashboard")
def get_dashboard():
    """
    Analytics dashboard showing:
    - Variant performance by identity state
    - Conversion rates
    - Behavioral patterns
    
    This demonstrates the self-improving loop for Amplitude prize
    """
    try:
        # Aggregate variant performance
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "variant_id": "$variant_id",
                        "identity_state": "$identity_state"
                    },
                    "total_shown": {"$sum": 1},
                    "conversions": {
                        "$sum": {"$cond": ["$converted", 1, 0]}
                    },
                    "avg_confidence": {"$avg": "$confidence"}
                }
            }
        ]
        
        results = list(variants_collection.aggregate(pipeline))
        
        # Calculate conversion rates
        for result in results:
            total = result["total_shown"]
            result["conversion_rate"] = result["conversions"] / total if total > 0 else 0.0
        
        return {
            "variant_performance": results,
            "total_events": events_collection.count_documents({}),
            "total_users": users_collection.count_documents({})
        }
        
    except Exception as e:
        print(f"Error in dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{user_id}/journey")
def get_user_journey(user_id: str):
    """
    Get a user's complete journey (for debugging/demo)
    Shows behavioral vector evolution over time
    """
    try:
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        events = list(events_collection.find({"user_id": user_id}).sort("timestamp", 1))
        
        return {
            "user_id": user_id,
            "session": user.get("last_session", {}),
            "events": [serialize_mongo_doc(e) for e in events],
            "identity_evolution": user.get("last_session", {}).get("identity_state")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_user_journey: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ----------------------------------------
# Helper Functions
# ----------------------------------------
def get_or_create_session(user_id: str) -> Dict[str, Any]:
    """Get existing session or create new one"""
    user = users_collection.find_one({"user_id": user_id})
    
    if user and "last_session" in user:
        return user["last_session"]
    
    # Create new session
    session = UserSession(
        session_id=f"session_{uuid.uuid4().hex[:12]}",
        user_id=user_id,
        language="en"
    ).model_dump()
    
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"last_session": session, "created_at": datetime.utcnow()}},
        upsert=True
    )
    
    return session


def serialize_mongo_doc(doc):
    """Convert MongoDB document to JSON-serializable format"""
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    if "timestamp" in doc:
        doc["timestamp"] = doc["timestamp"].isoformat()
    return doc


# ----------------------------------------
# Health Check
# ----------------------------------------
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "html.ai - Self-Improving UI Engine",
        "version": "2.0.0",
        "agents": ["Analytics", "Identity", "Decision", "Guardrail"],
        "sponsors": ["Foresters", "Amplitude", "Shopify"]
    }


# ----------------------------------------
# Run Server
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
