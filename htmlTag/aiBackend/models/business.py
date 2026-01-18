"""
Multi-tenant business models for B2B SaaS
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import secrets
import hashlib


class DataSharingLevel(str, Enum):
    """What data can be shared between businesses"""
    NONE = "none"  # No sharing - default
    AGGREGATE = "aggregate"  # Only aggregated behavioral profiles
    FULL = "full"  # Full user journey across partner sites


class BusinessTier(str, Enum):
    """Subscription tiers"""
    FREE = "free"  # Limited tracking, no cross-site
    STARTER = "starter"  # Basic cross-site, limited partners
    GROWTH = "growth"  # Full cross-site, up to 10 partners
    ENTERPRISE = "enterprise"  # Unlimited, custom features


class Business(BaseModel):
    """
    Business/tenant model
    Each business gets their own API key and isolated data
    """
    business_id: str = Field(description="Unique business identifier")
    name: str
    domain: str  # Primary domain (e.g., "shoes.com")
    allowed_domains: List[str] = Field(default_factory=list)  # Additional domains

    # Authentication
    api_key: str = Field(description="Public API key for SDK")
    api_secret_hash: str = Field(description="Hashed secret for server-to-server")

    # Subscription
    tier: BusinessTier = BusinessTier.FREE

    # Data sharing
    sharing_level: DataSharingLevel = DataSharingLevel.NONE
    partner_ids: List[str] = Field(default_factory=list)  # Approved partner business IDs

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

    # Usage limits based on tier
    monthly_event_limit: int = 10000  # Free tier default
    monthly_events_used: int = 0

    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "biz_abc123",
                "name": "Awesome Shoes Co",
                "domain": "awesomeshoes.com",
                "api_key": "pk_live_xxxxx",
                "tier": "growth"
            }
        }


class DataSharingAgreement(BaseModel):
    """
    Represents a data sharing agreement between two businesses
    Both must opt-in for sharing to work
    """
    agreement_id: str
    from_business_id: str
    to_business_id: str

    # What's being shared
    sharing_level: DataSharingLevel

    # Granular permissions
    permissions: Dict[str, bool] = Field(default_factory=lambda: {
        "share_behavioral_vectors": True,
        "share_identity_states": True,
        "share_conversion_data": False,
        "share_raw_events": False
    })

    # Status
    status: str = "pending"  # pending, active, revoked
    initiated_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "agreement_id": "agr_xyz789",
                "from_business_id": "biz_shoes",
                "to_business_id": "biz_clothes",
                "sharing_level": "aggregate",
                "status": "active"
            }
        }


class GlobalUser(BaseModel):
    """
    Global user identity that links UIDs across businesses
    This is the central tracking record
    """
    global_uid: str = Field(description="Universal user ID set by tracking domain")

    # Business-specific UIDs mapped to this global user
    business_uids: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of business_id -> local_uid"
    )

    # Aggregated profile (shared with partners based on permissions)
    aggregated_profile: Dict[str, Any] = Field(default_factory=lambda: {
        "behavioral_tendency": None,  # e.g., "price_sensitive", "brand_loyal"
        "engagement_level": None,  # e.g., "high", "medium", "low"
        "cross_site_visits": 0,
        "total_conversions": 0
    })

    # First seen / last seen
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    last_business_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "global_uid": "guid_abc123xyz",
                "business_uids": {
                    "biz_shoes": "user_123",
                    "biz_clothes": "user_456"
                }
            }
        }


# Helper functions for API key generation
def generate_api_key(prefix: str = "pk_live") -> str:
    """Generate a public API key"""
    random_part = secrets.token_urlsafe(24)
    return f"{prefix}_{random_part}"


def generate_api_secret() -> tuple[str, str]:
    """Generate API secret and its hash"""
    secret = secrets.token_urlsafe(32)
    secret_hash = hashlib.sha256(secret.encode()).hexdigest()
    return secret, secret_hash


def generate_business_id() -> str:
    """Generate unique business ID"""
    return f"biz_{secrets.token_urlsafe(8)}"


def generate_agreement_id() -> str:
    """Generate unique agreement ID"""
    return f"agr_{secrets.token_urlsafe(8)}"


def generate_global_uid() -> str:
    """Generate global user ID"""
    return f"guid_{secrets.token_urlsafe(16)}"


# Tier limits
TIER_LIMITS = {
    BusinessTier.FREE: {
        "monthly_events": 10000,
        "max_partners": 0,
        "cross_site_tracking": False,
        "data_export": False
    },
    BusinessTier.STARTER: {
        "monthly_events": 100000,
        "max_partners": 3,
        "cross_site_tracking": True,
        "data_export": False
    },
    BusinessTier.GROWTH: {
        "monthly_events": 1000000,
        "max_partners": 10,
        "cross_site_tracking": True,
        "data_export": True
    },
    BusinessTier.ENTERPRISE: {
        "monthly_events": -1,  # Unlimited
        "max_partners": -1,  # Unlimited
        "cross_site_tracking": True,
        "data_export": True
    }
}
