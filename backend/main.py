"""
FastAPI Server for Adaptive Identity Engine

Exposes endpoints for:
- Event ingestion from SDK
- Variant retrieval
- Session management
- Real-time agent communication logs
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

from models.events import Event, UserSession, EventType
from agents.workflow import AdaptiveIdentityWorkflow

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Adaptive Identity Engine API",
    description="Self-improving UI engine with multi-agent behavioral analytics",
    version="1.0.0"
)

# CORS middleware for SDK integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize workflow
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
workflow = AdaptiveIdentityWorkflow(gemini_api_key=GEMINI_API_KEY)

# In-memory session store (in production, use Redis/Supabase)
sessions: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# Request/Response Models
# ============================================================================

class EventRequest(BaseModel):
    """Request to track an event"""
    event_name: str
    session_id: str
    user_id: Optional[str] = None
    component_id: Optional[str] = None
    properties: Dict[str, Any] = {}


class VariantRequest(BaseModel):
    """Request to get a variant for a component"""
    session_id: str
    component_id: str
    user_id: Optional[str] = None


class SessionCreateRequest(BaseModel):
    """Request to create a new session"""
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    language: str = "en"


class VariantResponse(BaseModel):
    """Response with selected variant"""
    variant_id: str
    content: Dict[str, Any]
    identity_state: Optional[str] = None
    confidence: float = 0.0
    audit_log: List[str] = []


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
def root():
    """Health check"""
    return {
        "status": "running",
        "service": "Adaptive Identity Engine",
        "version": "1.0.0",
        "agents": ["Analytics", "Identity", "Decision", "Guardrail"]
    }


@app.post("/api/session/create")
def create_session(request: SessionCreateRequest = None) -> Dict[str, str]:
    """
    Create a new user session

    Accepts:
        session_id: Optional client-provided session ID
        user_id: Optional persistent user ID from cookie
        language: Language preference (default: "en")

    Returns:
        session_id and user_id for tracking
    """
    # Use provided session_id or generate new one
    session_id = request.session_id if request and request.session_id else str(uuid.uuid4())
    user_id = request.user_id if request else None
    language = request.language if request else "en"

    session = UserSession(
        session_id=session_id,
        user_id=user_id,
        language=language
    )

    sessions[session_id] = session.model_dump()

    return {
        "session_id": session_id,
        "user_id": user_id,
        "created_at": datetime.utcnow().isoformat()
    }


@app.post("/api/events/track")
def track_event(event_request: EventRequest) -> Dict[str, str]:
    """
    Track a behavioral event (Amplitude-style)

    This endpoint receives events from the identity.js SDK
    and stores them in the session history.
    """
    session_id = event_request.session_id

    # Get or create session
    if session_id not in sessions:
        session = UserSession(
            session_id=session_id,
            user_id=event_request.user_id
        )
        sessions[session_id] = session.model_dump()

    session_data = sessions[session_id]
    session = UserSession(**session_data)

    # Create event
    event = Event(
        event_name=EventType(event_request.event_name),
        session_id=session_id,
        user_id=event_request.user_id,
        component_id=event_request.component_id,
        properties=event_request.properties,
        timestamp=datetime.utcnow()
    )

    # Add to session
    session.add_event(event)

    # Update session store
    sessions[session_id] = session.model_dump()

    return {
        "status": "tracked",
        "event_name": event.event_name.value,
        "session_id": session_id
    }


@app.post("/api/variants/get", response_model=VariantResponse)
def get_variant(request: VariantRequest):
    """
    Get personalized variant using multi-agent system

    This is the core endpoint that:
    1. Retrieves session event history
    2. Runs multi-agent workflow (Analytics → Identity → Decision → Guardrail)
    3. Returns the selected variant

    This demonstrates the full "data → insights → action" loop
    required for the Amplitude challenge.
    """
    session_id = request.session_id

    # Get session
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = sessions[session_id]

    # Run multi-agent workflow
    final_state = workflow.process_session(session_data)

    # Update session
    sessions[session_id] = final_state

    final_session = UserSession(**final_state)

    # Extract variant decision
    variant_decision = final_session.outcome_metrics.get("variant_decision")

    if not variant_decision:
        raise HTTPException(status_code=500, detail="No variant decision made")

    selected_variant = variant_decision["selected_variant"]

    # Get agent communication log
    audit_log = workflow.get_agent_communication_log(final_state)

    return VariantResponse(
        variant_id=selected_variant["variant_id"],
        content=selected_variant["content"],
        identity_state=final_session.identity_state.value if final_session.identity_state else None,
        confidence=final_session.identity_confidence,
        audit_log=audit_log
    )


@app.get("/api/session/{session_id}")
def get_session(session_id: str):
    """
    Get full session state including behavioral vector and audit log

    Useful for debugging and visualization dashboard
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_data = sessions[session_id]
    session = UserSession(**session_data)

    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "identity_state": session.identity_state.value if session.identity_state else None,
        "confidence": session.identity_confidence,
        "behavioral_vector": session.behavioral_vector.to_dict() if session.behavioral_vector else None,
        "events_count": len(session.event_history),
        "last_variant": session.last_variant_shown,
        "audit_log": session.audit_log
    }


@app.get("/api/user/{user_id}/sessions")
def get_user_sessions(user_id: str):
    """
    Get all sessions for a specific user ID (from cookie)

    Useful for tracking user behavior across multiple sessions
    """
    user_sessions = []
    for session_id, session_data in sessions.items():
        if session_data.get("user_id") == user_id:
            session = UserSession(**session_data)
            user_sessions.append({
                "session_id": session.session_id,
                "identity_state": session.identity_state.value if session.identity_state else None,
                "confidence": session.identity_confidence,
                "events_count": len(session.event_history),
                "last_variant": session.last_variant_shown
            })

    return {
        "user_id": user_id,
        "session_count": len(user_sessions),
        "sessions": user_sessions
    }


@app.get("/api/demo/variants")
def list_demo_variants():
    """
    List all available demo variants

    Useful for testing and visualization
    """
    from agents.decision_agent import DEMO_VARIANTS

    variants_list = []
    for component_id, variants in DEMO_VARIANTS.items():
        for variant in variants:
            variants_list.append({
                "variant_id": variant.variant_id,
                "component_id": variant.component_id,
                "target_identity": variant.target_identity,
                "content": variant.content,
                "performance": variant.performance_metrics
            })

    return {"variants": variants_list}


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
