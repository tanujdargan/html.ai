"""
UI variant models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class UIVariant(BaseModel):
    """
    A UI variant for a specific component
    """
    variant_id: str
    component_id: str
    variant_type: str  # "headline", "cta", "image", "layout"
    content: Dict[str, Any]  # Actual variant content
    target_identity: Optional[str] = None  # Which identity state this targets
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "variant_id": "hero_confident_v1",
                "component_id": "hero",
                "variant_type": "headline",
                "content": {
                    "headline": "Complete Your Purchase Today",
                    "subheadline": "Join thousands of satisfied customers",
                    "cta_text": "Buy Now"
                },
                "target_identity": "confident",
                "performance_metrics": {
                    "conversion_rate": 0.12,
                    "avg_time_to_conversion": 45.2
                }
            }
        }


class VariantDecision(BaseModel):
    """
    Decision made by Decision Agent
    """
    selected_variant: UIVariant
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    exploration_factor: float = Field(ge=0.0, le=1.0, description="Explore vs exploit balance")

    class Config:
        json_schema_extra = {
            "example": {
                "selected_variant": {"variant_id": "hero_confident_v1", "...": "..."},
                "rationale": "User shows high decision velocity and low hesitation - confident variant selected",
                "confidence": 0.85,
                "exploration_factor": 0.15
            }
        }


class GuardrailCheck(BaseModel):
    """
    Result from Guardrail Agent validation
    """
    approved: bool
    reason: str
    violated_rules: list[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "approved": True,
                "reason": "All privacy and ethics checks passed",
                "violated_rules": []
            }
        }
