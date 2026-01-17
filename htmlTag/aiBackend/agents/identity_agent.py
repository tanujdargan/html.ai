"""
Identity Interpretation Agent - Interprets behavioral vector into semantic identity state
"""
from typing import Dict, Any
from models.events import UserSession, BehavioralVector, IdentityState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import json


class IdentityInterpretationAgent:
    """
    Agent 2: Interprets behavioral vector into human-readable identity state
    """

    def __init__(self, api_key: str):
        self.name = "Identity Interpretation Agent"
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.3,
            google_api_key=api_key
        )

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an identity interpretation agent that analyzes user behavior patterns.

Given a behavioral vector with these dimensions (all 0.0 to 1.0):
- exploration_score: How much the user is exploring vs focused (high = exploring many items)
- hesitation_score: Degree of indecision/backtracking (high = uncertain/hesitant)
- engagement_depth: Time spent vs content consumed (high = deep engagement)
- decision_velocity: Speed of progression through funnel (high = moving fast)
- content_focus_ratio: Focused vs scattered attention (high = focused on specific content)

Interpret the user's current identity state. Choose ONE from:
- exploratory: Browsing many options, high exploration
- overwhelmed: High exploration + high hesitation, struggling to choose
- comparison_focused: High engagement + moderate exploration, researching carefully
- confident: Low hesitation + high velocity, knows what they want
- ready_to_decide: High engagement + high velocity + low hesitation
- cautious: Low velocity + high engagement, being very careful
- impulse_buyer: High velocity + low engagement, quick decisions

Return ONLY a JSON object with:
{{
  "identity_state": "one_of_the_states_above",
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation"
}}"""),
            ("user", "Behavioral vector:\n{vector}")
        ])

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Interpret behavioral vector into identity state

        Args:
            state: Contains behavioral_vector

        Returns:
            Updated state with identity_state and confidence
        """
        session = UserSession(**state)

        session.add_audit_entry(f"{self.name}: Interpreting behavioral vector")

        if not session.behavioral_vector:
            # Fallback if no vector computed yet
            session.identity_state = IdentityState.EXPLORATORY
            session.identity_confidence = 0.5
            session.add_audit_entry(f"{self.name}: No vector available, defaulting to EXPLORATORY")
            return session.model_dump()

        # Use LLM to interpret vector
        vector_str = json.dumps(session.behavioral_vector.to_dict(), indent=2)

        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"vector": vector_str})
            result = json.loads(response.content)

            identity_state = IdentityState(result["identity_state"])
            confidence = float(result["confidence"])
            reasoning = result["reasoning"]

            session.identity_state = identity_state
            session.identity_confidence = confidence
            session.add_audit_entry(
                f"{self.name}: Identified as {identity_state.value} "
                f"(confidence={confidence:.2f}) - {reasoning}"
            )

        except Exception as e:
            # Fallback on error
            session.identity_state = self._rule_based_fallback(session.behavioral_vector)
            session.identity_confidence = 0.6
            session.add_audit_entry(f"{self.name}: LLM error, using rule-based fallback: {str(e)}")

        return session.model_dump()

    def _rule_based_fallback(self, vector: BehavioralVector) -> IdentityState:
        """Simple rule-based fallback if LLM fails"""

        if vector.hesitation_score > 0.7 and vector.exploration_score > 0.6:
            return IdentityState.OVERWHELMED
        elif vector.decision_velocity > 0.7 and vector.hesitation_score < 0.3:
            return IdentityState.CONFIDENT
        elif vector.engagement_depth > 0.7 and vector.content_focus_ratio > 0.6:
            return IdentityState.COMPARISON_FOCUSED
        elif vector.decision_velocity > 0.7 and vector.engagement_depth < 0.4:
            return IdentityState.IMPULSE_BUYER
        elif vector.exploration_score > 0.6:
            return IdentityState.EXPLORATORY
        else:
            return IdentityState.CAUTIOUS
