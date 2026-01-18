"""
Multi-Tenant AI Backend for B2B SaaS

This extends the integrated server with:
- Business registration and API key management
- Multi-tenant data isolation
- Cross-site user tracking via global UIDs
- Data sharing agreements between businesses
- Central tracking sync for cross-domain identification
"""
from fastapi import FastAPI, HTTPException, Header, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from pymongo import MongoClient
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import os
import hashlib
import secrets

# Import models
from models.events import Event, UserSession, EventType
from models.business import (
    Business, DataSharingAgreement, GlobalUser,
    DataSharingLevel, BusinessTier, TIER_LIMITS,
    generate_api_key, generate_api_secret, generate_business_id,
    generate_agreement_id, generate_global_uid
)

# Import the multi-agent system
from agents.workflow import AdaptiveIdentityWorkflow

# ----------------------------------------
# FastAPI App + CORS
# ----------------------------------------
app = FastAPI(
    title="html.ai - Multi-Tenant B2B Platform",
    description="Self-improving UI optimization for e-commerce with cross-site tracking",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# MongoDB Collections
# ----------------------------------------
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
client = MongoClient(MONGO_URI)
db = client["html_ai"]

# Existing collections (now with business_id)
users_collection = db["users"]
events_collection = db["events"]
variants_collection = db["variants"]

# New multi-tenant collections
businesses_collection = db["businesses"]
agreements_collection = db["data_sharing_agreements"]
global_users_collection = db["global_users"]

# Create indexes for performance (with error handling for existing indexes)
def safe_create_index(collection, keys, **kwargs):
    """Create index, ignoring if it already exists with different options"""
    try:
        collection.create_index(keys, **kwargs)
    except Exception as e:
        print(f"Index creation note: {e}")

safe_create_index(businesses_collection, "api_key", unique=True)
safe_create_index(businesses_collection, "business_id", unique=True)
safe_create_index(global_users_collection, "global_uid", unique=True)
safe_create_index(events_collection, [("business_id", 1), ("user_id", 1)])
safe_create_index(users_collection, [("business_id", 1), ("user_id", 1)])

# ----------------------------------------
# Multi-Agent Workflow
# ----------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
workflow = AdaptiveIdentityWorkflow(gemini_api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# ----------------------------------------
# Authentication Middleware
# ----------------------------------------
async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> Business:
    """Verify API key and return business"""
    business = businesses_collection.find_one({"api_key": x_api_key, "is_active": True})
    if not business:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    # Check usage limits
    tier_limits = TIER_LIMITS.get(BusinessTier(business["tier"]), TIER_LIMITS[BusinessTier.FREE])
    if tier_limits["monthly_events"] != -1:  # Not unlimited
        if business.get("monthly_events_used", 0) >= tier_limits["monthly_events"]:
            raise HTTPException(status_code=429, detail="Monthly event limit exceeded")

    return Business(**business)


async def optional_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> Optional[Business]:
    """Optional API key verification for public endpoints"""
    if not x_api_key:
        return None
    business = businesses_collection.find_one({"api_key": x_api_key, "is_active": True})
    return Business(**business) if business else None


# ----------------------------------------
# Request Models
# ----------------------------------------
class BusinessRegistrationRequest(BaseModel):
    """Register a new business"""
    name: str
    domain: str
    email: str
    allowed_domains: List[str] = []


class DataSharingRequest(BaseModel):
    """Request to share data with another business"""
    partner_business_id: str
    sharing_level: DataSharingLevel = DataSharingLevel.AGGREGATE
    permissions: Dict[str, bool] = {}


class HtmlOptimizeRequest(BaseModel):
    """Request to optimize HTML content"""
    user_id: str
    component_id: str
    html: str
    context_html: Optional[str] = ""
    global_uid: Optional[str] = None  # From central tracking


class EventTrackingRequest(BaseModel):
    """Track behavioral events"""
    user_id: str
    session_id: str
    event_name: str
    component_id: Optional[str] = None
    properties: Dict[str, Any] = {}
    global_uid: Optional[str] = None


class BatchEventRequest(BaseModel):
    """Batch of events to track"""
    user_id: str
    session_id: str
    events: List[Dict[str, Any]]
    global_uid: Optional[str] = None


class RewardRequest(BaseModel):
    """Reward signal"""
    user_id: str
    component_id: str
    variant_id: str
    reward_type: str = "click"
    properties: Dict[str, Any] = {}


class SyncRequest(BaseModel):
    """Cross-site sync request"""
    business_id: str
    local_uid: str


# ----------------------------------------
# Business Management API
# ----------------------------------------
@app.post("/api/business/register")
async def register_business(request: BusinessRegistrationRequest):
    """
    Register a new business and get API credentials

    Returns:
    - api_key: Public key for SDK (safe to expose in frontend)
    - api_secret: Secret key for server-to-server (keep private!)
    """
    # Check if domain already registered
    existing = businesses_collection.find_one({"domain": request.domain})
    if existing:
        raise HTTPException(status_code=400, detail="Domain already registered")

    # Generate credentials
    business_id = generate_business_id()
    api_key = generate_api_key()
    api_secret, api_secret_hash = generate_api_secret()

    business = Business(
        business_id=business_id,
        name=request.name,
        domain=request.domain,
        allowed_domains=request.allowed_domains + [request.domain],
        api_key=api_key,
        api_secret_hash=api_secret_hash,
        tier=BusinessTier.FREE,
        monthly_event_limit=TIER_LIMITS[BusinessTier.FREE]["monthly_events"]
    )

    businesses_collection.insert_one(business.model_dump())

    return {
        "status": "registered",
        "business_id": business_id,
        "api_key": api_key,
        "api_secret": api_secret,  # Only returned once!
        "tier": "free",
        "message": "Save your api_secret - it won't be shown again!"
    }


@app.get("/api/business/me")
async def get_business_info(business: Business = Depends(verify_api_key)):
    """Get current business info"""
    tier_limits = TIER_LIMITS.get(business.tier, TIER_LIMITS[BusinessTier.FREE])

    return {
        "business_id": business.business_id,
        "name": business.name,
        "domain": business.domain,
        "tier": business.tier,
        "usage": {
            "events_used": business.monthly_events_used,
            "events_limit": tier_limits["monthly_events"],
            "partners_count": len(business.partner_ids),
            "partners_limit": tier_limits["max_partners"]
        },
        "features": {
            "cross_site_tracking": tier_limits["cross_site_tracking"],
            "data_export": tier_limits["data_export"]
        }
    }


@app.put("/api/business/upgrade")
async def upgrade_tier(
    new_tier: BusinessTier,
    business: Business = Depends(verify_api_key)
):
    """Upgrade business tier (in production, this would involve payment)"""
    tier_limits = TIER_LIMITS[new_tier]

    businesses_collection.update_one(
        {"business_id": business.business_id},
        {
            "$set": {
                "tier": new_tier.value,
                "monthly_event_limit": tier_limits["monthly_events"],
                "updated_at": datetime.utcnow()
            }
        }
    )

    return {
        "status": "upgraded",
        "new_tier": new_tier,
        "new_limits": tier_limits
    }


# ----------------------------------------
# Data Sharing API
# ----------------------------------------
@app.post("/api/sharing/request")
async def request_data_sharing(
    request: DataSharingRequest,
    business: Business = Depends(verify_api_key)
):
    """Request to share data with another business"""
    # Check tier allows cross-site
    tier_limits = TIER_LIMITS.get(business.tier, TIER_LIMITS[BusinessTier.FREE])
    if not tier_limits["cross_site_tracking"]:
        raise HTTPException(status_code=403, detail="Upgrade to enable cross-site tracking")

    # Check partner limit
    if tier_limits["max_partners"] != -1:
        if len(business.partner_ids) >= tier_limits["max_partners"]:
            raise HTTPException(status_code=403, detail="Partner limit reached")

    # Verify partner exists
    partner = businesses_collection.find_one({"business_id": request.partner_business_id})
    if not partner:
        raise HTTPException(status_code=404, detail="Partner business not found")

    # Check if agreement already exists
    existing = agreements_collection.find_one({
        "from_business_id": business.business_id,
        "to_business_id": request.partner_business_id,
        "status": {"$in": ["pending", "active"]}
    })
    if existing:
        raise HTTPException(status_code=400, detail="Agreement already exists")

    # Create agreement
    agreement = DataSharingAgreement(
        agreement_id=generate_agreement_id(),
        from_business_id=business.business_id,
        to_business_id=request.partner_business_id,
        sharing_level=request.sharing_level,
        permissions={
            "share_behavioral_vectors": True,
            "share_identity_states": True,
            "share_conversion_data": request.permissions.get("share_conversion_data", False),
            "share_raw_events": request.permissions.get("share_raw_events", False)
        },
        status="pending"
    )

    agreements_collection.insert_one(agreement.model_dump())

    return {
        "status": "pending",
        "agreement_id": agreement.agreement_id,
        "message": f"Request sent to {partner['name']}. They must accept to activate sharing."
    }


@app.get("/api/sharing/pending")
async def get_pending_requests(business: Business = Depends(verify_api_key)):
    """Get pending data sharing requests"""
    # Requests TO this business
    incoming = list(agreements_collection.find({
        "to_business_id": business.business_id,
        "status": "pending"
    }))

    # Requests FROM this business
    outgoing = list(agreements_collection.find({
        "from_business_id": business.business_id,
        "status": "pending"
    }))

    return {
        "incoming": [serialize_doc(a) for a in incoming],
        "outgoing": [serialize_doc(a) for a in outgoing]
    }


@app.post("/api/sharing/accept/{agreement_id}")
async def accept_sharing_request(
    agreement_id: str,
    business: Business = Depends(verify_api_key)
):
    """Accept a data sharing request"""
    agreement = agreements_collection.find_one({
        "agreement_id": agreement_id,
        "to_business_id": business.business_id,
        "status": "pending"
    })

    if not agreement:
        raise HTTPException(status_code=404, detail="Agreement not found or not pending")

    # Activate agreement
    agreements_collection.update_one(
        {"agreement_id": agreement_id},
        {
            "$set": {
                "status": "active",
                "accepted_at": datetime.utcnow()
            }
        }
    )

    # Add each other as partners
    businesses_collection.update_one(
        {"business_id": business.business_id},
        {"$addToSet": {"partner_ids": agreement["from_business_id"]}}
    )
    businesses_collection.update_one(
        {"business_id": agreement["from_business_id"]},
        {"$addToSet": {"partner_ids": business.business_id}}
    )

    return {"status": "active", "agreement_id": agreement_id}


@app.post("/api/sharing/revoke/{agreement_id}")
async def revoke_sharing(
    agreement_id: str,
    business: Business = Depends(verify_api_key)
):
    """Revoke a data sharing agreement"""
    agreement = agreements_collection.find_one({
        "agreement_id": agreement_id,
        "$or": [
            {"from_business_id": business.business_id},
            {"to_business_id": business.business_id}
        ],
        "status": "active"
    })

    if not agreement:
        raise HTTPException(status_code=404, detail="Active agreement not found")

    # Revoke
    agreements_collection.update_one(
        {"agreement_id": agreement_id},
        {
            "$set": {
                "status": "revoked",
                "revoked_at": datetime.utcnow()
            }
        }
    )

    # Remove from partner lists
    other_id = agreement["to_business_id"] if agreement["from_business_id"] == business.business_id else agreement["from_business_id"]
    businesses_collection.update_one(
        {"business_id": business.business_id},
        {"$pull": {"partner_ids": other_id}}
    )
    businesses_collection.update_one(
        {"business_id": other_id},
        {"$pull": {"partner_ids": business.business_id}}
    )

    return {"status": "revoked", "agreement_id": agreement_id}


# ----------------------------------------
# Central Tracking Sync (Cross-Site Identity)
# ----------------------------------------
@app.get("/sync/pixel.gif")
async def tracking_pixel(
    business_id: str,
    local_uid: str,
    response: Response
):
    """
    1x1 tracking pixel for cross-site sync
    Sets first-party cookie on tracking domain
    """
    # Get or create global UID
    global_uid = get_or_create_global_uid(business_id, local_uid)

    # Set cookie on tracking domain (1 year)
    response.set_cookie(
        key="htmlai_guid",
        value=global_uid,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        samesite="none",
        secure=True
    )

    # Return 1x1 transparent GIF
    gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return Response(content=gif_bytes, media_type="image/gif")


@app.get("/sync/iframe", response_class=HTMLResponse)
async def sync_iframe(request: Request):
    """
    Sync iframe that runs on tracking domain
    Reads global UID cookie and posts to parent
    """
    # Get global UID from cookie if exists
    global_uid = request.cookies.get("htmlai_guid", "")

    html = f"""
<!DOCTYPE html>
<html>
<head><title>Sync</title></head>
<body>
<script>
(function() {{
    var globalUid = "{global_uid}";

    // If no global UID, generate one
    if (!globalUid) {{
        globalUid = 'guid_' + Math.random().toString(36).substr(2, 16) + Date.now().toString(36);
        // Set cookie via API
        fetch('/sync/set-cookie?guid=' + globalUid, {{ credentials: 'include' }});
    }}

    // Post message to parent with global UID
    if (window.parent !== window) {{
        window.parent.postMessage({{
            type: 'htmlai_sync',
            global_uid: globalUid
        }}, '*');
    }}
}})();
</script>
</body>
</html>
"""
    return HTMLResponse(content=html)


@app.get("/sync/set-cookie")
async def set_sync_cookie(guid: str, response: Response):
    """Set the global UID cookie"""
    response.set_cookie(
        key="htmlai_guid",
        value=guid,
        max_age=365 * 24 * 60 * 60,
        httponly=False,  # Needs to be readable by JS
        samesite="none",
        secure=True
    )
    return {"status": "ok"}


@app.post("/sync/link")
async def link_user(
    request: SyncRequest,
    global_uid: Optional[str] = Header(None, alias="X-Global-UID")
):
    """
    Link a business's local UID to the global UID
    Called by SDK after sync iframe returns global UID
    """
    try:
        if not global_uid:
            global_uid = generate_global_uid()

        # Check if user already exists
        existing = global_users_collection.find_one({"global_uid": global_uid})

        if existing:
            # Update existing user
            global_users_collection.update_one(
                {"global_uid": global_uid},
                {
                    "$set": {
                        f"business_uids.{request.business_id}": request.local_uid,
                        "last_seen": datetime.utcnow(),
                        "last_business_id": request.business_id
                    },
                    "$inc": {
                        "aggregated_profile.cross_site_visits": 1
                    }
                }
            )
        else:
            # Create new user
            global_users_collection.insert_one({
                "global_uid": global_uid,
                "business_uids": {request.business_id: request.local_uid},
                "first_seen": datetime.utcnow(),
                "last_seen": datetime.utcnow(),
                "last_business_id": request.business_id,
                "aggregated_profile": {
                    "behavioral_tendency": None,
                    "engagement_level": None,
                    "cross_site_visits": 1,
                    "total_conversions": 0
                }
            })

        return {"global_uid": global_uid, "linked": True}
    except Exception as e:
        print(f"Error in sync/link: {e}")
        return {"global_uid": global_uid, "linked": False, "error": str(e)}


# ----------------------------------------
# Event Tracking (Multi-Tenant)
# ----------------------------------------
@app.post("/api/events/track")
async def track_event(
    request: EventTrackingRequest,
    business: Business = Depends(verify_api_key)
):
    """Track behavioral event with business isolation"""
    event = {
        "business_id": business.business_id,
        "user_id": request.user_id,
        "session_id": request.session_id,
        "event_name": request.event_name,
        "component_id": request.component_id,
        "properties": request.properties,
        "global_uid": request.global_uid,
        "timestamp": datetime.utcnow()
    }

    events_collection.insert_one(event)

    # Update session
    session = get_or_create_session(business.business_id, request.user_id)
    session["event_history"].append(event)

    users_collection.update_one(
        {"business_id": business.business_id, "user_id": request.user_id},
        {"$set": {"last_session": session}}
    )

    # Increment usage
    businesses_collection.update_one(
        {"business_id": business.business_id},
        {"$inc": {"monthly_events_used": 1}}
    )

    return {"status": "tracked", "event_name": request.event_name}


@app.post("/api/events/batch")
async def track_events_batch(
    request: BatchEventRequest,
    business: Business = Depends(verify_api_key)
):
    """Track multiple events with business isolation"""
    session = get_or_create_session(business.business_id, request.user_id)
    tracked_count = 0

    for event_data in request.events:
        event = {
            "business_id": business.business_id,
            "user_id": request.user_id,
            "session_id": request.session_id,
            "event_name": event_data.get("event_name"),
            "component_id": event_data.get("component_id"),
            "properties": event_data.get("properties", {}),
            "global_uid": request.global_uid,
            "timestamp": datetime.utcnow()
        }

        events_collection.insert_one(event)
        session["event_history"].append(event)
        tracked_count += 1

    users_collection.update_one(
        {"business_id": business.business_id, "user_id": request.user_id},
        {"$set": {"last_session": session}}
    )

    # Increment usage
    businesses_collection.update_one(
        {"business_id": business.business_id},
        {"$inc": {"monthly_events_used": tracked_count}}
    )

    return {"status": "tracked", "events_count": tracked_count}


# ----------------------------------------
# HTML Optimization (Multi-Tenant)
# ----------------------------------------
@app.post("/api/optimize")
async def optimize_html(
    request: HtmlOptimizeRequest,
    business: Business = Depends(verify_api_key)
):
    """Optimize HTML with business isolation and cross-site data"""
    try:
        # Get session for this business
        session = get_or_create_session(business.business_id, request.user_id)

        # If we have global_uid and partners, enrich with cross-site data
        cross_site_profile = None
        if request.global_uid and business.partner_ids:
            cross_site_profile = get_cross_site_profile(
                request.global_uid,
                business.business_id,
                business.partner_ids
            )

        # Track component view
        view_event = {
            "business_id": business.business_id,
            "event_name": "component_viewed",
            "session_id": session["session_id"],
            "user_id": request.user_id,
            "component_id": request.component_id,
            "global_uid": request.global_uid,
            "timestamp": datetime.utcnow(),
            "properties": {"original_html": request.html[:500]}  # Truncate
        }

        session["event_history"].append(view_event)
        events_collection.insert_one(view_event)

        # Run optimization (mock for now)
        result = mock_process_session(session, request.component_id, cross_site_profile)

        # Log variant shown
        variants_collection.insert_one({
            "business_id": business.business_id,
            "user_id": request.user_id,
            "session_id": session["session_id"],
            "component_id": request.component_id,
            "variant_id": result["variant_id"],
            "identity_state": result["identity_state"],
            "confidence": result["confidence"],
            "global_uid": request.global_uid,
            "timestamp": datetime.utcnow(),
            "converted": False
        })

        # Update session
        users_collection.update_one(
            {"business_id": business.business_id, "user_id": request.user_id},
            {"$set": {"last_session": session, "last_updated": datetime.utcnow()}}
        )

        return result

    except Exception as e:
        import traceback
        print(f"Error in optimize_html: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reward")
async def track_reward(
    request: RewardRequest,
    business: Business = Depends(verify_api_key)
):
    """Track reward with business isolation"""
    reward_event = {
        "business_id": business.business_id,
        "user_id": request.user_id,
        "component_id": request.component_id,
        "variant_id": request.variant_id,
        "reward_type": request.reward_type,
        "properties": request.properties,
        "timestamp": datetime.utcnow()
    }

    events_collection.insert_one(reward_event)

    # Update variant conversion
    variants_collection.update_one(
        {
            "business_id": business.business_id,
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

    return {"status": "reward_tracked", "variant_id": request.variant_id}


# ----------------------------------------
# Analytics Dashboard (Multi-Tenant)
# ----------------------------------------
@app.get("/api/analytics/dashboard")
async def get_dashboard(business: Business = Depends(verify_api_key)):
    """Business-specific analytics dashboard"""
    pipeline = [
        {"$match": {"business_id": business.business_id}},
        {
            "$group": {
                "_id": {
                    "variant_id": "$variant_id",
                    "identity_state": "$identity_state"
                },
                "total_shown": {"$sum": 1},
                "conversions": {"$sum": {"$cond": ["$converted", 1, 0]}},
                "avg_confidence": {"$avg": "$confidence"}
            }
        }
    ]

    results = list(variants_collection.aggregate(pipeline))

    for result in results:
        total = result["total_shown"]
        result["conversion_rate"] = result["conversions"] / total if total > 0 else 0.0

    return {
        "variant_performance": [serialize_doc(r) for r in results],
        "total_events": events_collection.count_documents({"business_id": business.business_id}),
        "total_users": users_collection.count_documents({"business_id": business.business_id})
    }


@app.get("/api/analytics/cross-site")
async def get_cross_site_analytics(business: Business = Depends(verify_api_key)):
    """Cross-site analytics for partners"""
    if not business.partner_ids:
        return {"message": "No partners configured", "data": []}

    # Get users that appear across multiple partners
    pipeline = [
        {
            "$match": {
                "global_uid": {"$exists": True, "$ne": None}
            }
        },
        {
            "$group": {
                "_id": "$global_uid",
                "businesses": {"$addToSet": "$business_id"},
                "total_events": {"$sum": 1}
            }
        },
        {
            "$match": {
                "businesses": {"$all": [business.business_id] + business.partner_ids[:2]}  # At least 2 partners
            }
        },
        {"$limit": 100}
    ]

    cross_site_users = list(events_collection.aggregate(pipeline))

    return {
        "cross_site_users": len(cross_site_users),
        "partner_count": len(business.partner_ids),
        "sample_journeys": cross_site_users[:10]
    }


@app.get("/api/users")
async def list_users(
    business: Business = Depends(verify_api_key),
    limit: int = 50
):
    """List all users for this business"""
    try:
        users = list(users_collection.find(
            {"business_id": business.business_id},
            {"user_id": 1, "created_at": 1, "_id": 0}
        ).limit(limit))

        # Also get unique users from events
        event_users = events_collection.distinct(
            "user_id",
            {"business_id": business.business_id}
        )

        return {
            "business_id": business.business_id,
            "users_from_collection": users,
            "users_from_events": event_users[:limit],
            "total_in_events": len(event_users)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{user_id}/journey")
async def get_user_journey(
    user_id: str,
    business: Business = Depends(verify_api_key)
):
    """Get user journey for this business"""
    try:
        user = users_collection.find_one({
            "business_id": business.business_id,
            "user_id": user_id
        })

        if not user:
            # Try to find in events even if no user record
            event_count = events_collection.count_documents({
                "business_id": business.business_id,
                "user_id": user_id
            })
            if event_count == 0:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found for business {business.business_id}")

        events = list(events_collection.find({
            "business_id": business.business_id,
            "user_id": user_id
        }).sort("timestamp", 1).limit(100))

        session_data = {}
        if user:
            session_data = user.get("last_session", {})

        return {
            "user_id": user_id,
            "business_id": business.business_id,
            "session": serialize_doc(session_data),
            "events": [serialize_doc(e) for e in events],
            "event_count": len(events)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in get_user_journey: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/{user_id}/cross-site-profile")
async def get_user_cross_site_profile(
    user_id: str,
    business: Business = Depends(verify_api_key)
):
    """Get cross-site profile if user has global UID and partners allow"""
    # Find user's global UID
    user = users_collection.find_one({
        "business_id": business.business_id,
        "user_id": user_id
    })

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Find recent event with global_uid
    recent_event = events_collection.find_one(
        {"business_id": business.business_id, "user_id": user_id, "global_uid": {"$exists": True}},
        sort=[("timestamp", -1)]
    )

    if not recent_event or not recent_event.get("global_uid"):
        return {"message": "No cross-site identity linked"}

    global_uid = recent_event["global_uid"]

    # Get cross-site profile
    profile = get_cross_site_profile(global_uid, business.business_id, business.partner_ids)

    return {
        "global_uid": global_uid,
        "cross_site_profile": profile
    }


# ----------------------------------------
# Helper Functions
# ----------------------------------------
def get_or_create_session(business_id: str, user_id: str) -> Dict[str, Any]:
    """Get or create session with business isolation"""
    user = users_collection.find_one({
        "business_id": business_id,
        "user_id": user_id
    })

    if user and "last_session" in user:
        session = user["last_session"]
        if "event_history" not in session:
            session["event_history"] = []
        # Clean up event history
        clean_history = []
        for event in session.get("event_history", [])[-50:]:  # Keep last 50
            if isinstance(event, dict):
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
        "business_id": business_id,
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
        {"business_id": business_id, "user_id": user_id},
        {
            "$set": {"last_session": session, "created_at": datetime.utcnow()},
            "$setOnInsert": {"business_id": business_id, "user_id": user_id}
        },
        upsert=True
    )

    return session


def get_or_create_global_uid(business_id: str, local_uid: str) -> str:
    """Get existing global UID or create new one"""
    # Check if this local UID is already linked
    global_user = global_users_collection.find_one({
        f"business_uids.{business_id}": local_uid
    })

    if global_user:
        return global_user["global_uid"]

    # Create new global user
    global_uid = generate_global_uid()
    global_users_collection.insert_one({
        "global_uid": global_uid,
        "business_uids": {business_id: local_uid},
        "first_seen": datetime.utcnow(),
        "last_seen": datetime.utcnow(),
        "last_business_id": business_id,
        "aggregated_profile": {
            "behavioral_tendency": None,
            "engagement_level": None,
            "cross_site_visits": 1,
            "total_conversions": 0
        }
    })

    return global_uid


def get_cross_site_profile(
    global_uid: str,
    business_id: str,
    partner_ids: List[str]
) -> Optional[Dict[str, Any]]:
    """Get aggregated cross-site profile based on data sharing agreements"""
    if not partner_ids:
        return None

    # Get active agreements
    active_agreements = list(agreements_collection.find({
        "$or": [
            {"from_business_id": business_id, "to_business_id": {"$in": partner_ids}},
            {"to_business_id": business_id, "from_business_id": {"$in": partner_ids}}
        ],
        "status": "active"
    }))

    if not active_agreements:
        return None

    # Aggregate data from partners based on permissions
    profile = {
        "cross_site_visits": 0,
        "behavioral_signals": [],
        "identity_states_seen": [],
        "partner_data": []
    }

    for agreement in active_agreements:
        partner_id = agreement["to_business_id"] if agreement["from_business_id"] == business_id else agreement["from_business_id"]
        permissions = agreement.get("permissions", {})

        # Get partner's data for this global user
        partner_events = list(events_collection.find({
            "business_id": partner_id,
            "global_uid": global_uid
        }).sort("timestamp", -1).limit(20))

        if not partner_events:
            continue

        profile["cross_site_visits"] += 1

        if permissions.get("share_behavioral_vectors", False):
            # Get behavioral summary
            for event in partner_events:
                if event.get("event_name") in ["scroll_fast", "rage_click", "hover"]:
                    profile["behavioral_signals"].append(event["event_name"])

        if permissions.get("share_identity_states", False):
            # Get identity states
            partner_variants = variants_collection.find_one({
                "business_id": partner_id,
                "global_uid": global_uid
            }, sort=[("timestamp", -1)])
            if partner_variants:
                profile["identity_states_seen"].append(partner_variants.get("identity_state"))

    return profile


def mock_process_session(
    session: Dict[str, Any],
    component_id: str,
    cross_site_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Mock multi-agent workflow with cross-site data enhancement"""
    event_history = session.get("event_history", [])
    event_count = len(event_history)

    # Analyze events
    scroll_events = sum(1 for e in event_history if "scroll" in str(e.get("event_name", "")).lower())
    click_events = sum(1 for e in event_history if "click" in str(e.get("event_name", "")).lower())
    rage_clicks = sum(1 for e in event_history if e.get("event_name") == "rage_click")
    dead_clicks = sum(1 for e in event_history if e.get("event_name") == "dead_click")
    mouse_hesitations = sum(1 for e in event_history if e.get("event_name") == "mouse_hesitation")
    fast_scrolls = sum(1 for e in event_history if e.get("event_name") == "scroll_fast")
    hover_events = sum(1 for e in event_history if e.get("event_name") == "hover")

    # Calculate scores
    exploration_score = min(1.0, scroll_events / 8.0)
    hesitation_score = min(1.0, (mouse_hesitations + rage_clicks) / 6.0)
    engagement_depth = min(1.0, (click_events + hover_events) / 6.0)
    decision_velocity = min(1.0, event_count / 10.0)
    frustration_score = min(1.0, (rage_clicks * 2 + dead_clicks) / 5.0)

    # Enhance with cross-site data
    cross_site_boost = 0
    if cross_site_profile:
        if "impulse_buyer" in cross_site_profile.get("identity_states_seen", []):
            cross_site_boost = 0.2
        if cross_site_profile.get("cross_site_visits", 0) > 2:
            decision_velocity = min(1.0, decision_velocity + 0.15)

    # Determine identity state
    if frustration_score > 0.4:
        identity_state = "overwhelmed"
        confidence = 0.85
    elif fast_scrolls > 3 and engagement_depth < 0.3:
        identity_state = "impulse_buyer"
        confidence = 0.80 + cross_site_boost
    elif decision_velocity > 0.6 and hesitation_score < 0.2:
        identity_state = "confident"
        confidence = 0.82
    elif engagement_depth > 0.5:
        identity_state = "comparison_focused"
        confidence = 0.70
    elif hesitation_score > 0.3:
        identity_state = "cautious"
        confidence = 0.65
    else:
        identity_state = "exploratory"
        confidence = 0.55

    # Select variant
    VARIANTS = {
        "confident": {"variant_id": "confident_v1", "content": {"headline": "Premium Quality", "cta": "Buy Now", "urgency": "high"}},
        "exploratory": {"variant_id": "exploratory_v1", "content": {"headline": "Discover More", "cta": "Browse", "urgency": "low"}},
        "overwhelmed": {"variant_id": "overwhelmed_v1", "content": {"headline": "Our Top Picks", "cta": "See Picks", "urgency": "medium"}},
        "comparison_focused": {"variant_id": "comparison_v1", "content": {"headline": "Compare Options", "cta": "Compare", "urgency": "low"}},
        "cautious": {"variant_id": "cautious_v1", "content": {"headline": "Risk-Free Shopping", "cta": "Learn More", "urgency": "medium"}},
        "impulse_buyer": {"variant_id": "impulse_v1", "content": {"headline": "Flash Sale!", "cta": "Shop Now", "urgency": "extreme"}}
    }

    variant = VARIANTS.get(identity_state, VARIANTS["exploratory"])

    return {
        "status": "optimized",
        "variant_id": variant["variant_id"],
        "content": variant["content"],
        "identity_state": identity_state,
        "confidence": min(1.0, confidence),
        "behavioral_vector": {
            "exploration_score": round(exploration_score, 3),
            "hesitation_score": round(hesitation_score, 3),
            "engagement_depth": round(engagement_depth, 3),
            "decision_velocity": round(decision_velocity, 3),
            "frustration_score": round(frustration_score, 3)
        },
        "cross_site_enhanced": cross_site_profile is not None
    }


def serialize_doc(doc: Dict) -> Dict:
    """Serialize MongoDB document - handles nested objects and datetime"""
    if doc is None:
        return {}

    result = {}
    for key, value in doc.items():
        if key == "_id":
            result[key] = str(value)
        elif hasattr(value, 'isoformat'):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)
        elif isinstance(value, list):
            result[key] = [serialize_doc(item) if isinstance(item, dict) else
                          (item.isoformat() if hasattr(item, 'isoformat') else item)
                          for item in value]
        else:
            result[key] = value
    return result


# ----------------------------------------
# Scoring System - A/B Testing with Weighted Interactions
# ----------------------------------------
from models.scoring import (
    DEFAULT_WEIGHTS, DEFAULT_SCORE_THRESHOLD,
    calculate_score_delta, should_trigger_regeneration
)

# Collections for scoring
scores_collection = db["user_scores"]
weights_collection = db["scoring_weights"]

# Create indexes for scoring
safe_create_index(scores_collection, [("business_id", 1), ("user_id", 1), ("component_id", 1)])


def get_business_weights(business_id: str) -> Dict[str, Any]:
    """Get scoring weights for a business (or defaults)"""
    weights_doc = weights_collection.find_one({"business_id": business_id})
    if weights_doc:
        return {
            "weights": weights_doc.get("weights", DEFAULT_WEIGHTS),
            "score_threshold": weights_doc.get("score_threshold", DEFAULT_SCORE_THRESHOLD)
        }
    return {
        "weights": DEFAULT_WEIGHTS.copy(),
        "score_threshold": DEFAULT_SCORE_THRESHOLD
    }


def get_or_create_user_scores(business_id: str, user_id: str, component_id: str) -> Dict:
    """Get or create score tracking for a user/component"""
    scores = scores_collection.find_one({
        "business_id": business_id,
        "user_id": user_id,
        "component_id": component_id
    })

    if not scores:
        scores = {
            "business_id": business_id,
            "user_id": user_id,
            "component_id": component_id,
            "variant_a": {
                "current_score": 0.0,
                "interaction_count": 0,
                "last_interaction": None
            },
            "variant_b": {
                "current_score": 0.0,
                "interaction_count": 0,
                "last_interaction": None
            },
            "active_variant": "A",
            "regeneration_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        scores_collection.insert_one(scores)

    return scores


class ScoreInteractionRequest(BaseModel):
    """Request to score an interaction"""
    user_id: str
    component_id: str
    interaction_type: str  # e.g., "click", "cta_click", "purchase"
    variant: str  # "A" or "B"
    properties: Dict[str, Any] = {}


class UpdateWeightsRequest(BaseModel):
    """Request to update scoring weights"""
    weights: Dict[str, float]
    score_threshold: Optional[float] = None


@app.get("/api/scoring/weights")
async def get_scoring_weights(business: Business = Depends(verify_api_key)):
    """Get current scoring weights for this business"""
    config = get_business_weights(business.business_id)
    return {
        "business_id": business.business_id,
        "weights": config["weights"],
        "score_threshold": config["score_threshold"],
        "available_interactions": list(DEFAULT_WEIGHTS.keys())
    }


@app.put("/api/scoring/weights")
async def update_scoring_weights(
    request: UpdateWeightsRequest,
    business: Business = Depends(verify_api_key)
):
    """Update scoring weights for this business"""
    update_data = {
        "business_id": business.business_id,
        "weights": request.weights,
        "updated_at": datetime.utcnow()
    }

    if request.score_threshold is not None:
        update_data["score_threshold"] = request.score_threshold

    weights_collection.update_one(
        {"business_id": business.business_id},
        {"$set": update_data},
        upsert=True
    )

    return {
        "status": "updated",
        "business_id": business.business_id,
        "weights": request.weights,
        "score_threshold": request.score_threshold or DEFAULT_SCORE_THRESHOLD
    }


@app.post("/api/scoring/interaction")
async def score_interaction(
    request: ScoreInteractionRequest,
    business: Business = Depends(verify_api_key)
):
    """
    Score an interaction for A/B testing.
    If score difference exceeds threshold, triggers component regeneration.
    """
    # Get weights and scores
    config = get_business_weights(business.business_id)
    weights = config["weights"]
    threshold = config["score_threshold"]

    scores = get_or_create_user_scores(
        business.business_id,
        request.user_id,
        request.component_id
    )

    # Calculate score delta
    score_delta = calculate_score_delta(request.interaction_type, weights)
    variant_key = f"variant_{request.variant.lower()}"

    # Update the variant's score
    current_score = scores.get(variant_key, {}).get("current_score", 0.0)
    new_score = current_score + score_delta
    interaction_count = scores.get(variant_key, {}).get("interaction_count", 0) + 1

    scores_collection.update_one(
        {
            "business_id": business.business_id,
            "user_id": request.user_id,
            "component_id": request.component_id
        },
        {
            "$set": {
                f"{variant_key}.current_score": new_score,
                f"{variant_key}.interaction_count": interaction_count,
                f"{variant_key}.last_interaction": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    # Get updated scores
    updated_scores = scores_collection.find_one({
        "business_id": business.business_id,
        "user_id": request.user_id,
        "component_id": request.component_id
    })

    score_a = updated_scores.get("variant_a", {}).get("current_score", 0.0)
    score_b = updated_scores.get("variant_b", {}).get("current_score", 0.0)

    # Check if regeneration needed
    should_regen, regen_variant = should_trigger_regeneration(score_a, score_b, threshold)

    result = {
        "status": "scored",
        "user_id": request.user_id,
        "component_id": request.component_id,
        "variant": request.variant,
        "interaction_type": request.interaction_type,
        "weight_applied": score_delta,
        "new_score": new_score,
        "variant_a_score": score_a,
        "variant_b_score": score_b,
        "score_difference": abs(score_a - score_b),
        "threshold": threshold,
        "should_regenerate": should_regen,
        "regenerate_variant": regen_variant
    }

    # If regeneration needed, trigger it via the main server's rewardTag
    if should_regen:
        result["regeneration_triggered"] = True
        result["regeneration_message"] = f"Variant {regen_variant} will be regenerated (losing by {abs(score_a - score_b):.2f} points)"

        # Increment regeneration count
        scores_collection.update_one(
            {
                "business_id": business.business_id,
                "user_id": request.user_id,
                "component_id": request.component_id
            },
            {"$inc": {"regeneration_count": 1}}
        )

        # Sync with main server.py user collection for regeneration
        # The main server uses user_id with variants.A/B.current_score
        winning_variant = "A" if score_a > score_b else "B"
        sync_score_to_main_users(
            request.user_id,
            request.component_id,
            score_a,
            score_b,
            winning_variant,
            request.properties.get("context_html", "")
        )

    return result


def sync_score_to_main_users(user_id: str, component_id: str, score_a: float, score_b: float, winning_variant: str, context_html: str = ""):
    """
    Sync scores to the main users collection used by server.py
    This enables the reRender/AIRags regeneration flow
    """
    # Create composite user_id for the main users collection
    composite_user_id = f"{user_id}_{component_id}"

    existing = users_collection.find_one({"user_id": composite_user_id})

    if not existing:
        # Create user entry matching server.py structure
        users_collection.insert_one({
            "user_id": composite_user_id,
            "variants": {
                "A": {
                    "current_html": "<div>Variant A</div>",
                    "current_score": score_a,
                    "number_of_trials": 1,
                    "history": []
                },
                "B": {
                    "current_html": "<div>Variant B</div>",
                    "current_score": score_b,
                    "number_of_trials": 1,
                    "history": []
                }
            }
        })
    else:
        # Update existing scores
        users_collection.update_one(
            {"user_id": composite_user_id},
            {
                "$set": {
                    "variants.A.current_score": score_a,
                    "variants.B.current_score": score_b
                }
            }
        )


@app.get("/api/scoring/user/{user_id}")
async def get_user_scores(
    user_id: str,
    component_id: Optional[str] = None,
    business: Business = Depends(verify_api_key)
):
    """Get scores for a user, optionally filtered by component_id"""
    query = {
        "business_id": business.business_id,
        "user_id": user_id
    }

    # If component_id specified, get that specific component's scores
    if component_id:
        query["component_id"] = component_id
        score_doc = scores_collection.find_one(query)

        if score_doc:
            return {
                "user_id": user_id,
                "business_id": business.business_id,
                "component_id": component_id,
                "scores": serialize_doc(score_doc)
            }
        else:
            # Return empty scores structure
            return {
                "user_id": user_id,
                "business_id": business.business_id,
                "component_id": component_id,
                "scores": {
                    "variant_a": {"current_score": 0.0, "interaction_count": 0},
                    "variant_b": {"current_score": 0.0, "interaction_count": 0},
                    "active_variant": "A",
                    "regeneration_count": 0
                }
            }

    # Otherwise return all components
    scores = list(scores_collection.find(query))

    return {
        "user_id": user_id,
        "business_id": business.business_id,
        "components": [serialize_doc(s) for s in scores],
        "total_components": len(scores)
    }


@app.get("/api/scoring/component/{component_id}")
async def get_component_scores(
    component_id: str,
    business: Business = Depends(verify_api_key)
):
    """Get aggregated scores for a component across all users"""
    pipeline = [
        {"$match": {"business_id": business.business_id, "component_id": component_id}},
        {
            "$group": {
                "_id": "$component_id",
                "total_users": {"$sum": 1},
                "avg_score_a": {"$avg": "$variant_a.current_score"},
                "avg_score_b": {"$avg": "$variant_b.current_score"},
                "total_interactions_a": {"$sum": "$variant_a.interaction_count"},
                "total_interactions_b": {"$sum": "$variant_b.interaction_count"},
                "total_regenerations": {"$sum": "$regeneration_count"}
            }
        }
    ]

    results = list(scores_collection.aggregate(pipeline))

    if not results:
        return {
            "component_id": component_id,
            "message": "No data for this component"
        }

    result = results[0]
    avg_a = result.get("avg_score_a", 0) or 0
    avg_b = result.get("avg_score_b", 0) or 0

    return {
        "component_id": component_id,
        "business_id": business.business_id,
        "total_users": result.get("total_users", 0),
        "variant_a": {
            "avg_score": round(avg_a, 2),
            "total_interactions": result.get("total_interactions_a", 0)
        },
        "variant_b": {
            "avg_score": round(avg_b, 2),
            "total_interactions": result.get("total_interactions_b", 0)
        },
        "winning_variant": "A" if avg_a > avg_b else "B" if avg_b > avg_a else "Tie",
        "score_difference": round(abs(avg_a - avg_b), 2),
        "total_regenerations": result.get("total_regenerations", 0)
    }


@app.get("/api/scoring/leaderboard")
async def get_scoring_leaderboard(
    business: Business = Depends(verify_api_key),
    limit: int = 10
):
    """Get top components by score difference (most decisive A/B tests)"""
    pipeline = [
        {"$match": {"business_id": business.business_id}},
        {
            "$group": {
                "_id": "$component_id",
                "total_users": {"$sum": 1},
                "avg_score_a": {"$avg": "$variant_a.current_score"},
                "avg_score_b": {"$avg": "$variant_b.current_score"},
                "total_regenerations": {"$sum": "$regeneration_count"}
            }
        },
        {
            "$addFields": {
                "score_diff": {"$abs": {"$subtract": ["$avg_score_a", "$avg_score_b"]}}
            }
        },
        {"$sort": {"score_diff": -1}},
        {"$limit": limit}
    ]

    results = list(scores_collection.aggregate(pipeline))

    leaderboard = []
    for r in results:
        avg_a = r.get("avg_score_a", 0) or 0
        avg_b = r.get("avg_score_b", 0) or 0
        leaderboard.append({
            "component_id": r["_id"],
            "total_users": r.get("total_users", 0),
            "variant_a_avg": round(avg_a, 2),
            "variant_b_avg": round(avg_b, 2),
            "winning_variant": "A" if avg_a > avg_b else "B" if avg_b > avg_a else "Tie",
            "score_difference": round(r.get("score_diff", 0), 2),
            "total_regenerations": r.get("total_regenerations", 0)
        })

    return {
        "business_id": business.business_id,
        "leaderboard": leaderboard
    }


# ----------------------------------------
# Integration with tagAi / rewardTag (Component Generation)
# ----------------------------------------
import httpx

COMPONENT_GEN_URL = os.getenv("COMPONENT_GEN_URL", "http://localhost:3000")


class TagAiRequest(BaseModel):
    """Request for component generation"""
    user_id: str
    component_id: str
    changing_html: str
    context_html: str


class RewardTagRequest(BaseModel):
    """Request for rewarding a variant"""
    user_id: str
    component_id: str
    variant: str  # "A" or "B"
    reward: float
    context_html: str
    interaction_type: str = "conversion"  # Type of interaction that triggered reward


@app.post("/api/component/generate")
async def generate_component(
    request: TagAiRequest,
    business: Business = Depends(verify_api_key)
):
    """
    Generate/get a component variant for A/B testing.
    Calls the tagAi endpoint internally.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{COMPONENT_GEN_URL}/tagAi",
                json={
                    "user_id": f"{business.business_id}_{request.user_id}",
                    "changingHtml": request.changing_html,
                    "contextHtml": request.context_html
                },
                timeout=30.0
            )

            result = response.json()

            # Track which variant was served
            variant = result.get("variant", "A")
            scores = get_or_create_user_scores(
                business.business_id,
                request.user_id,
                request.component_id
            )

            # Update active variant
            scores_collection.update_one(
                {
                    "business_id": business.business_id,
                    "user_id": request.user_id,
                    "component_id": request.component_id
                },
                {"$set": {"active_variant": variant}}
            )

            return {
                "status": "ok",
                "component_id": request.component_id,
                "variant": variant,
                "html": result.get("changingHtml", request.changing_html),
                "user_id": request.user_id
            }

    except Exception as e:
        # Fallback: return original HTML
        return {
            "status": "fallback",
            "component_id": request.component_id,
            "variant": "A",
            "html": request.changing_html,
            "error": str(e)
        }


@app.post("/api/component/reward")
async def reward_component(
    request: RewardTagRequest,
    business: Business = Depends(verify_api_key)
):
    """
    Reward a component variant and check for regeneration.
    Calls rewardTag endpoint and scoring system.
    """
    # First, score the interaction
    config = get_business_weights(business.business_id)
    weights = config["weights"]
    threshold = config["score_threshold"]

    scores = get_or_create_user_scores(
        business.business_id,
        request.user_id,
        request.component_id
    )

    # Calculate score delta based on interaction type and reward
    base_delta = calculate_score_delta(request.interaction_type, weights)
    score_delta = base_delta * request.reward if request.reward > 0 else base_delta

    variant_key = f"variant_{request.variant.lower()}"
    current_score = scores.get(variant_key, {}).get("current_score", 0.0)
    new_score = current_score + score_delta

    # Update score
    scores_collection.update_one(
        {
            "business_id": business.business_id,
            "user_id": request.user_id,
            "component_id": request.component_id
        },
        {
            "$set": {
                f"{variant_key}.current_score": new_score,
                f"{variant_key}.last_interaction": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            "$inc": {f"{variant_key}.interaction_count": 1}
        }
    )

    # Get updated scores
    updated_scores = scores_collection.find_one({
        "business_id": business.business_id,
        "user_id": request.user_id,
        "component_id": request.component_id
    })

    score_a = updated_scores.get("variant_a", {}).get("current_score", 0.0)
    score_b = updated_scores.get("variant_b", {}).get("current_score", 0.0)

    # Check if regeneration needed
    should_regen, regen_variant = should_trigger_regeneration(score_a, score_b, threshold)

    result = {
        "status": "rewarded",
        "component_id": request.component_id,
        "variant": request.variant,
        "reward": request.reward,
        "score_delta": score_delta,
        "new_score": new_score,
        "variant_a_score": score_a,
        "variant_b_score": score_b,
        "should_regenerate": should_regen
    }

    # If regeneration needed, call rewardTag to trigger it
    if should_regen:
        try:
            async with httpx.AsyncClient() as client:
                regen_response = await client.post(
                    f"{COMPONENT_GEN_URL}/rewardTag",
                    json={
                        "user_id": f"{business.business_id}_{request.user_id}",
                        "variantAttributed": request.variant,
                        "reward": request.reward,
                        "contextHtml": request.context_html
                    },
                    timeout=30.0
                )

                result["regeneration_triggered"] = True
                result["regeneration_response"] = regen_response.json()

                # Increment regeneration count
                scores_collection.update_one(
                    {
                        "business_id": business.business_id,
                        "user_id": request.user_id,
                        "component_id": request.component_id
                    },
                    {"$inc": {"regeneration_count": 1}}
                )

        except Exception as e:
            result["regeneration_error"] = str(e)

    return result


# ----------------------------------------
# Health Check
# ----------------------------------------
@app.get("/")
def root():
    return {
        "status": "running",
        "service": "html.ai - Multi-Tenant B2B Platform",
        "version": "3.0.0",
        "features": ["multi-tenant", "cross-site-tracking", "data-sharing", "ab-scoring"]
    }


@app.get("/health")
def health():
    return {"status": "healthy", "mongo": "connected" if client else "disconnected"}


# ----------------------------------------
# Run Server
# ----------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
