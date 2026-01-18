"""
Weighted Scoring Model for User Interactions

Each interaction type has a configurable weight multiplier.
Variant A and B each accumulate scores based on user interactions.
When score difference exceeds threshold, component regeneration is triggered.
"""
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime


# Default weight multipliers for each interaction type
DEFAULT_WEIGHTS = {
    # Positive interactions (increase score)
    "click": 1.0,
    "cta_click": 3.0,          # Call-to-action clicks are high value
    "add_to_cart": 5.0,        # Strong purchase intent
    "purchase": 10.0,          # Conversion - highest value
    "form_submit": 4.0,
    "signup": 6.0,
    "share": 2.0,
    "save": 2.5,
    "hover_long": 0.5,         # Engagement signal (hover > 2s)
    "scroll_to_bottom": 1.5,   # Read through content
    "video_play": 1.0,
    "video_complete": 3.0,

    # Negative interactions (decrease score)
    "bounce": -2.0,            # Left quickly
    "rage_click": -1.5,        # Frustration signal
    "dead_click": -0.5,        # Clicked non-interactive element
    "scroll_fast": -0.3,       # Skimming, not engaged
    "exit_intent": -1.0,       # Mouse moved to close
    "tab_switch": -0.2,        # Lost attention

    # Neutral/contextual
    "page_view": 0.1,
    "component_view": 0.2,
    "scroll": 0.05,
    "mouse_move": 0.0,         # Too noisy to score
}

# Threshold for triggering component regeneration
DEFAULT_SCORE_THRESHOLD = 5.0  # When A-B or B-A exceeds this, regenerate losing variant


class ScoringWeights(BaseModel):
    """Configurable weights for each interaction type"""
    weights: Dict[str, float] = Field(default_factory=lambda: DEFAULT_WEIGHTS.copy())
    score_threshold: float = DEFAULT_SCORE_THRESHOLD
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VariantScore(BaseModel):
    """Score tracking for a single variant"""
    variant_id: str  # "A" or "B"
    current_score: float = 0.0
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    score_history: list = Field(default_factory=list)  # Track score over time


class UserScores(BaseModel):
    """Scores for both variants for a user"""
    user_id: str
    business_id: str
    component_id: str
    variant_a: VariantScore = Field(default_factory=lambda: VariantScore(variant_id="A"))
    variant_b: VariantScore = Field(default_factory=lambda: VariantScore(variant_id="B"))
    active_variant: str = "A"  # Which variant is currently shown
    regeneration_count: int = 0  # How many times we've regenerated
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InteractionEvent(BaseModel):
    """An interaction event to be scored"""
    user_id: str
    business_id: str
    component_id: str
    interaction_type: str  # e.g., "click", "cta_click", "purchase"
    variant: str  # "A" or "B"
    properties: Dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ScoreUpdateResult(BaseModel):
    """Result of updating a score"""
    user_id: str
    component_id: str
    variant: str
    interaction_type: str
    weight_applied: float
    score_delta: float
    new_score: float
    variant_a_score: float
    variant_b_score: float
    score_difference: float
    threshold: float
    should_regenerate: bool
    regenerate_variant: Optional[str] = None


def calculate_score_delta(interaction_type: str, weights: Dict[str, float]) -> float:
    """Calculate score change for an interaction"""
    return weights.get(interaction_type, 0.0)


def should_trigger_regeneration(
    score_a: float,
    score_b: float,
    threshold: float
) -> tuple[bool, Optional[str]]:
    """
    Check if score difference warrants regeneration.
    Returns (should_regenerate, variant_to_regenerate)
    """
    diff = abs(score_a - score_b)

    if diff >= threshold:
        # Regenerate the losing variant
        if score_a > score_b:
            return True, "B"
        else:
            return True, "A"

    return False, None
