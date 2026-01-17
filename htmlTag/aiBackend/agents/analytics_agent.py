"""
Analytics Agent - Transforms raw events into behavioral identity vector
"""
from typing import Dict, Any
from datetime import datetime, timedelta
import math
from models.events import Event, BehavioralVector, UserSession, EventType


class AnalyticsAgent:
    """
    Agent 1: Computes behavioral signals from event stream
    """

    def __init__(self):
        self.name = "Analytics Agent"
        self.recency_window_seconds = 300  # 5 minute window

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform event history into behavioral vector

        Args:
            state: Contains event_history and previous behavioral_vector

        Returns:
            Updated state with new behavioral_vector
        """
        session = UserSession(**state)

        # Add audit log
        session.add_audit_entry(f"{self.name}: Computing behavioral vector from {len(session.event_history)} events")

        # Compute behavioral signals
        vector = self._compute_behavioral_vector(session.event_history)

        session.behavioral_vector = vector
        session.add_audit_entry(
            f"{self.name}: Vector computed - "
            f"exploration={vector.exploration_score:.2f}, "
            f"hesitation={vector.hesitation_score:.2f}, "
            f"engagement={vector.engagement_depth:.2f}"
        )

        return session.model_dump()

    def _compute_behavioral_vector(self, events: list[Event]) -> BehavioralVector:
        """Compute behavioral signals from events with recency weighting"""

        if not events:
            # Default neutral vector
            return BehavioralVector(
                exploration_score=0.5,
                hesitation_score=0.5,
                engagement_depth=0.5,
                decision_velocity=0.5,
                content_focus_ratio=0.5
            )

        now = datetime.utcnow()
        weighted_events = []

        # Apply recency decay
        for event in events:
            age_seconds = (now - event.timestamp).total_seconds()
            weight = math.exp(-age_seconds / self.recency_window_seconds)
            weighted_events.append((event, weight))

        # Compute signals
        exploration_score = self._compute_exploration(weighted_events)
        hesitation_score = self._compute_hesitation(weighted_events)
        engagement_depth = self._compute_engagement(weighted_events)
        decision_velocity = self._compute_velocity(weighted_events)
        content_focus = self._compute_focus(weighted_events)

        return BehavioralVector(
            exploration_score=exploration_score,
            hesitation_score=hesitation_score,
            engagement_depth=engagement_depth,
            decision_velocity=decision_velocity,
            content_focus_ratio=content_focus
        )

    def _compute_exploration(self, weighted_events: list[tuple[Event, float]]) -> float:
        """High score = user is exploring many components"""
        unique_components = set()
        total_weight = 0.0

        for event, weight in weighted_events:
            if event.component_id:
                unique_components.add(event.component_id)
            total_weight += weight

        if total_weight == 0:
            return 0.5

        # Normalize by expected max components
        exploration = min(len(unique_components) / 5.0, 1.0)
        return exploration

    def _compute_hesitation(self, weighted_events: list[tuple[Event, float]]) -> float:
        """High score = user is backtracking or re-viewing content"""
        backtrack_count = 0
        total_weight = 0.0

        for event, weight in weighted_events:
            if event.event_name == EventType.BACKTRACK:
                backtrack_count += weight
            total_weight += weight

        if total_weight == 0:
            return 0.5

        hesitation = min(backtrack_count / total_weight, 1.0)
        return hesitation

    def _compute_engagement(self, weighted_events: list[tuple[Event, float]]) -> float:
        """High score = deep time investment in content"""
        total_time = 0.0
        total_weight = 0.0

        for event, weight in weighted_events:
            if event.event_name == EventType.TIME_ON_COMPONENT:
                time_spent = event.properties.get("time_seconds", 0)
                total_time += time_spent * weight
            total_weight += weight

        if total_weight == 0:
            return 0.5

        # Normalize: 60 seconds = high engagement
        engagement = min(total_time / 60.0, 1.0)
        return engagement

    def _compute_velocity(self, weighted_events: list[tuple[Event, float]]) -> float:
        """High score = rapid progression through funnel"""
        funnel_events = [
            EventType.PAGE_VIEWED,
            EventType.COMPONENT_VIEWED,
            EventType.ADD_TO_CART,
            EventType.CONVERSION_COMPLETED
        ]

        funnel_progression = 0
        total_weight = 0.0

        for event, weight in weighted_events:
            if event.event_name in funnel_events:
                funnel_progression += weight
            total_weight += weight

        if total_weight == 0:
            return 0.5

        velocity = min(funnel_progression / total_weight, 1.0)
        return velocity

    def _compute_focus(self, weighted_events: list[tuple[Event, float]]) -> float:
        """High score = focused on specific content vs scattered attention"""
        component_times: Dict[str, float] = {}

        for event, weight in weighted_events:
            if event.event_name == EventType.TIME_ON_COMPONENT and event.component_id:
                time_spent = event.properties.get("time_seconds", 0) * weight
                component_times[event.component_id] = component_times.get(event.component_id, 0) + time_spent

        if not component_times:
            return 0.5

        # Compute concentration: is time focused on one component or spread out?
        total_time = sum(component_times.values())
        if total_time == 0:
            return 0.5

        # Gini coefficient style: higher if time concentrated
        sorted_times = sorted(component_times.values(), reverse=True)
        focus = sorted_times[0] / total_time if sorted_times else 0.5

        return focus
