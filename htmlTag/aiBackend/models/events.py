"""
Event models for Amplitude-style behavioral analytics
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Supported event types"""
    # Core events
    PAGE_VIEWED = "page_viewed"
    COMPONENT_VIEWED = "component_viewed"
    SCROLL_DEPTH_REACHED = "scroll_depth_reached"
    TIME_ON_COMPONENT = "time_on_component"
    CLICK = "click"
    BACKTRACK = "backtrack"
    ADD_TO_CART = "add_to_cart"
    CONVERSION_COMPLETED = "conversion_completed"
    VARIANT_SHOWN = "variant_shown"

    # Mouse tracking
    MOUSE_HESITATION = "mouse_hesitation"
    MOUSE_IDLE_START = "mouse_idle_start"
    MOUSE_IDLE_END = "mouse_idle_end"

    # Scroll tracking
    SCROLL_DIRECTION_CHANGE = "scroll_direction_change"
    SCROLL_FAST = "scroll_fast"
    SCROLL_PAUSE = "scroll_pause"

    # Click tracking
    RAGE_CLICK = "rage_click"
    DEAD_CLICK = "dead_click"
    RIGHT_CLICK = "right_click"
    DOUBLE_CLICK = "double_click"

    # Hover tracking
    HOVER = "hover"
    HOVER_END = "hover_end"

    # Visibility tracking
    TAB_HIDDEN = "tab_hidden"
    TAB_VISIBLE = "tab_visible"
    WINDOW_BLUR = "window_blur"
    WINDOW_FOCUS = "window_focus"

    # Form tracking
    FIELD_FOCUS = "field_focus"
    FIELD_BLUR = "field_blur"
    FIELD_PASTE = "field_paste"
    FORM_SUBMIT = "form_submit"

    # Navigation tracking
    FIRST_INTERACTION = "first_interaction"
    PAGE_EXIT_INTENT = "page_exit_intent"
    EXTERNAL_LINK_CLICK = "external_link_click"
    BACK_NAVIGATION = "back_navigation"

    # Product tracking
    PRODUCT_CLICK = "product_click"


class Event(BaseModel):
    """
    Amplitude-style event schema
    """
    event_name: EventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str
    user_id: Optional[str] = None
    component_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "event_name": "component_viewed",
                "timestamp": "2026-01-17T12:00:00Z",
                "session_id": "abc123",
                "user_id": "user_456",
                "component_id": "hero",
                "properties": {
                    "variant_shown": "confident_v2",
                    "scroll_depth": 0.5
                }
            }
        }


class BehavioralVector(BaseModel):
    """
    Computed behavioral identity vector from event history
    """
    exploration_score: float = Field(ge=0.0, le=1.0, description="How much the user is exploring vs. focused")
    hesitation_score: float = Field(ge=0.0, le=1.0, description="Degree of indecision/backtracking")
    engagement_depth: float = Field(ge=0.0, le=1.0, description="Time spent vs. content consumed")
    decision_velocity: float = Field(ge=0.0, le=1.0, description="Speed of progression through funnel")
    content_focus_ratio: float = Field(ge=0.0, le=1.0, description="Focused browsing vs. scattered attention")

    def to_dict(self) -> Dict[str, float]:
        return {
            "exploration_score": self.exploration_score,
            "hesitation_score": self.hesitation_score,
            "engagement_depth": self.engagement_depth,
            "decision_velocity": self.decision_velocity,
            "content_focus_ratio": self.content_focus_ratio
        }


class IdentityState(str, Enum):
    """Semantic identity states interpreted from behavioral vector"""
    EXPLORATORY = "exploratory"
    OVERWHELMED = "overwhelmed"
    COMPARISON_FOCUSED = "comparison_focused"
    CONFIDENT = "confident"
    READY_TO_DECIDE = "ready_to_decide"
    CAUTIOUS = "cautious"
    IMPULSE_BUYER = "impulse_buyer"


class UserSession(BaseModel):
    """
    User session state passed between agents
    """
    session_id: str
    user_id: Optional[str] = None
    language: str = "en"
    event_history: list[Event] = Field(default_factory=list)
    behavioral_vector: Optional[BehavioralVector] = None
    identity_state: Optional[IdentityState] = None
    identity_confidence: float = 0.0
    last_variant_shown: Optional[str] = None
    outcome_metrics: Dict[str, Any] = Field(default_factory=dict)
    audit_log: list[str] = Field(default_factory=list)

    def add_event(self, event: Event):
        """Add event to history with recency limit"""
        self.event_history.append(event)
        # Keep only last 50 events for performance
        if len(self.event_history) > 50:
            self.event_history = self.event_history[-50:]

    def add_audit_entry(self, entry: str):
        """Add audit log entry"""
        timestamp = datetime.utcnow().isoformat()
        self.audit_log.append(f"[{timestamp}] {entry}")
