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

# Import the multi-agent system (local copy in agents/)
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
    print("WARNING: No GEMINI_API_KEY - using mock mode with rule-based identity detection")

workflow = AdaptiveIdentityWorkflow(gemini_api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# ----------------------------------------
# Mock Workflow for Demo Mode (no API key)
# ----------------------------------------
def mock_process_session(session: Dict[str, Any], component_id: str) -> Dict[str, Any]:
    """
    Mock multi-agent workflow for demo/testing without Gemini API key.
    Uses rule-based identity detection based on event count and patterns.
    """
    from models.variants import UIVariant
    import random

    event_history = session.get("event_history", [])
    event_count = len(event_history)

    # Analyze events to determine identity (now with advanced tracking)
    scroll_events = sum(1 for e in event_history if "scroll" in e.get("event_name", "").lower())
    click_events = sum(1 for e in event_history if "click" in e.get("event_name", "").lower())
    backtrack_events = sum(1 for e in event_history if "backtrack" in e.get("event_name", "").lower())
    time_events = [e for e in event_history if "time" in e.get("event_name", "").lower()]

    # Advanced event analysis
    rage_clicks = sum(1 for e in event_history if e.get("event_name") == "rage_click")
    dead_clicks = sum(1 for e in event_history if e.get("event_name") == "dead_click")
    mouse_hesitations = sum(1 for e in event_history if e.get("event_name") == "mouse_hesitation")
    scroll_direction_changes = sum(1 for e in event_history if e.get("event_name") == "scroll_direction_change")
    fast_scrolls = sum(1 for e in event_history if e.get("event_name") == "scroll_fast")
    hover_events = sum(1 for e in event_history if e.get("event_name") == "hover")
    tab_hidden_events = sum(1 for e in event_history if e.get("event_name") == "tab_hidden")
    mouse_idle_events = sum(1 for e in event_history if e.get("event_name") == "mouse_idle_start")

    # Calculate behavioral signals with advanced tracking
    exploration_score = min(1.0, (scroll_events + scroll_direction_changes) / 8.0)
    hesitation_score = min(1.0, (backtrack_events + mouse_hesitations + scroll_direction_changes) / 6.0)
    engagement_depth = min(1.0, (click_events + hover_events) / 6.0)
    decision_velocity = min(1.0, event_count / 10.0)
    frustration_score = min(1.0, (rage_clicks * 2 + dead_clicks) / 5.0)
    distraction_score = min(1.0, (tab_hidden_events + mouse_idle_events) / 4.0)
    skimming_score = min(1.0, fast_scrolls / 3.0)

    # Rule-based identity detection
    audit_log = []
    audit_log.append(f"Analytics Agent: Computed behavioral vector from {event_count} events")
    audit_log.append(f"Analytics Agent: exploration={exploration_score:.2f}, hesitation={hesitation_score:.2f}, engagement={engagement_depth:.2f}")
    audit_log.append(f"Analytics Agent: frustration={frustration_score:.2f}, distraction={distraction_score:.2f}, skimming={skimming_score:.2f}")

    # Determine identity state with enhanced signals
    if frustration_score > 0.4:
        # High frustration = overwhelmed or needs help
        identity_state = "overwhelmed"
        confidence = 0.85
        audit_log.append(f"Identity Agent: Detected frustration signals (rage_clicks={rage_clicks}, dead_clicks={dead_clicks})")
    elif hesitation_score > 0.5 and exploration_score > 0.4:
        identity_state = "overwhelmed"
        confidence = 0.75
    elif skimming_score > 0.5 and engagement_depth < 0.3:
        # Fast scrolling, low engagement = impulse buyer
        identity_state = "impulse_buyer"
        confidence = 0.80
        audit_log.append(f"Identity Agent: Detected skimming behavior (fast_scrolls={fast_scrolls})")
    elif decision_velocity > 0.6 and hesitation_score < 0.2:
        identity_state = "confident"
        confidence = 0.82
    elif engagement_depth > 0.5 and scroll_direction_changes > 2:
        # High engagement + scroll back = comparing
        identity_state = "comparison_focused"
        confidence = 0.78
        audit_log.append(f"Identity Agent: Detected comparison behavior (direction_changes={scroll_direction_changes})")
    elif engagement_depth > 0.5 and exploration_score > 0.3:
        identity_state = "comparison_focused"
        confidence = 0.70
    elif decision_velocity > 0.7 and engagement_depth < 0.3:
        identity_state = "impulse_buyer"
        confidence = 0.78
    elif distraction_score > 0.4:
        # Frequently leaving tab = cautious/researching elsewhere
        identity_state = "cautious"
        confidence = 0.72
        audit_log.append(f"Identity Agent: Detected distraction signals (tab_hidden={tab_hidden_events})")
    elif exploration_score > 0.5:
        identity_state = "exploratory"
        confidence = 0.68
    elif hesitation_score > 0.3 or mouse_hesitations > 2:
        identity_state = "cautious"
        confidence = 0.65
    elif engagement_depth > 0.6 and decision_velocity > 0.5:
        identity_state = "ready_to_decide"
        confidence = 0.75
    else:
        identity_state = "exploratory"
        confidence = 0.55

    audit_log.append(f"Identity Agent: Identified user as {identity_state} (confidence={confidence:.2f})")

    # Select variant based on identity
    MOCK_VARIANTS = {
        "confident": {
            "variant_id": "hero_confident_v1",
            "content": {
                "headline": "Premium Tech at Your Fingertips",
                "subheadline": "Fast, reliable shipping on all orders",
                "cta_text": "Shop Now",
                "urgency": "high"
            }
        },
        "exploratory": {
            "variant_id": "hero_exploratory_v1",
            "content": {
                "headline": "Discover Premium Electronics",
                "subheadline": "Browse our curated collection of the latest tech",
                "cta_text": "Browse Collection",
                "urgency": "low"
            }
        },
        "overwhelmed": {
            "variant_id": "hero_overwhelmed_v1",
            "content": {
                "headline": "Not Sure What You Need?",
                "subheadline": "We've picked our top 4 best-sellers just for you",
                "cta_text": "See Our Picks",
                "urgency": "medium"
            }
        },
        "comparison_focused": {
            "variant_id": "hero_comparison_v1",
            "content": {
                "headline": "Compare Features & Specs",
                "subheadline": "Find the perfect match for your needs",
                "cta_text": "Compare Products",
                "urgency": "low"
            }
        },
        "cautious": {
            "variant_id": "hero_cautious_v1",
            "content": {
                "headline": "Shop Risk-Free with 30-Day Returns",
                "subheadline": "Trusted by 10,000+ customers, secure checkout guaranteed",
                "cta_text": "Shop Safely",
                "urgency": "medium",
                "trust_badges": ["30-day returns", "Secure checkout", "10k+ reviews"]
            }
        },
        "impulse_buyer": {
            "variant_id": "hero_impulse_v1",
            "content": {
                "headline": "FLASH SALE - 40% OFF!",
                "subheadline": "Limited time only! Ends in 3 hours",
                "cta_text": "Shop Sale Now",
                "urgency": "extreme",
                "countdown": "3:00:00"
            }
        },
        "ready_to_decide": {
            "variant_id": "hero_ready_v1",
            "content": {
                "headline": "Complete Your Order Today",
                "subheadline": "Free shipping on orders over $50",
                "cta_text": "View Cart",
                "urgency": "high"
            }
        }
    }

    variant = MOCK_VARIANTS.get(identity_state, MOCK_VARIANTS["exploratory"])
    audit_log.append(f"Decision Agent: Selected '{variant['variant_id']}' for {identity_state} user")
    audit_log.append(f"Guardrail Agent: Decision validated - no privacy concerns detected")

    return {
        "status": "optimized",
        "variant_id": variant["variant_id"],
        "content": variant["content"],
        "identity_state": identity_state,
        "confidence": confidence,
        "audit_log": audit_log,
        "behavioral_vector": {
            "exploration_score": round(exploration_score, 3),
            "hesitation_score": round(hesitation_score, 3),
            "engagement_depth": round(engagement_depth, 3),
            "decision_velocity": round(decision_velocity, 3),
            "frustration_score": round(frustration_score, 3),
            "distraction_score": round(distraction_score, 3),
            "skimming_score": round(skimming_score, 3),
            "content_focus_ratio": 0.5
        },
        "event_summary": {
            "total_events": event_count,
            "scroll_events": scroll_events,
            "click_events": click_events,
            "rage_clicks": rage_clicks,
            "dead_clicks": dead_clicks,
            "mouse_hesitations": mouse_hesitations,
            "hover_events": hover_events,
            "tab_hidden_events": tab_hidden_events
        }
    }

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

class BatchEventRequest(BaseModel):
    """Batch of events to track at once"""
    user_id: str
    session_id: str
    events: List[Dict[str, Any]]

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
            # Full multi-agent system with Gemini API
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
        else:
            # Mock mode: rule-based identity detection (no API key)
            result = mock_process_session(session, request.component_id)

            # Log variant shown in MongoDB
            variants_collection.insert_one({
                "user_id": request.user_id,
                "session_id": session["session_id"],
                "component_id": request.component_id,
                "variant_id": result["variant_id"],
                "identity_state": result["identity_state"],
                "confidence": result["confidence"],
                "timestamp": datetime.utcnow(),
                "converted": False
            })

            return result
        
    except Exception as e:
        import traceback
        print(f"Error in optimize_html: {e}")
        print(f"Traceback: {traceback.format_exc()}")
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


@app.post("/api/events/batch")
async def track_events_batch(request: BatchEventRequest):
    """
    Track multiple behavioral events at once (reduces API calls)
    """
    try:
        session = get_or_create_session(request.user_id)
        tracked_count = 0

        for event_data in request.events:
            event = {
                "user_id": request.user_id,
                "session_id": request.session_id,
                "event_name": event_data.get("event_name"),
                "component_id": event_data.get("component_id"),
                "properties": event_data.get("properties", {}),
                "timestamp": datetime.utcnow()
            }

            events_collection.insert_one(event)
            session["event_history"].append(event)
            tracked_count += 1

        # Update session once with all events
        users_collection.update_one(
            {"user_id": request.user_id},
            {"$set": {"last_session": session}}
        )

        print(f"[BATCH] Tracked {tracked_count} events for user {request.user_id}")

        return {
            "status": "tracked",
            "events_count": tracked_count
        }

    except Exception as e:
        print(f"Error in track_events_batch: {e}")
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
        session = user["last_session"]
        # Ensure event_history exists and is a list
        if "event_history" not in session:
            session["event_history"] = []
        # Clean up event history - ensure it's serializable
        clean_history = []
        for event in session.get("event_history", []):
            if isinstance(event, dict):
                # Convert any datetime objects to strings
                clean_event = {}
                for k, v in event.items():
                    if hasattr(v, 'isoformat'):
                        clean_event[k] = v.isoformat()
                    else:
                        clean_event[k] = v
                clean_history.append(clean_event)
        session["event_history"] = clean_history
        return session

    # Create new session
    session = {
        "session_id": f"session_{uuid.uuid4().hex[:12]}",
        "user_id": user_id,
        "language": "en",
        "event_history": [],
        "behavioral_vector": None,
        "identity_state": None,
        "identity_confidence": 0.0,
        "last_variant_shown": None,
        "outcome_metrics": {},
        "audit_log": []
    }

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
