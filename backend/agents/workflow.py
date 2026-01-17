"""
LangGraph Multi-Agent Orchestration Workflow

This orchestrates the 4 specialized agents with explicit state hand-offs:
1. Analytics Agent → computes behavioral vector
2. Identity Agent → interprets identity state
3. Decision Agent → selects UI variant
4. Guardrail Agent → validates decision

State flows sequentially through all agents.
"""
from langgraph.graph import StateGraph, END
from typing import TypedDict, Dict, Any
import os

from agents.analytics_agent import AnalyticsAgent
from agents.identity_agent import IdentityInterpretationAgent
from agents.decision_agent import DecisionAgent, DEMO_VARIANTS
from agents.guardrail_agent import GuardrailAgent


class AdaptiveIdentityWorkflow:
    """
    Multi-agent workflow using LangGraph
    """

    def __init__(self, openai_api_key: str):
        # Initialize all agents
        self.analytics_agent = AnalyticsAgent()
        self.identity_agent = IdentityInterpretationAgent(api_key=openai_api_key)
        self.decision_agent = DecisionAgent(variants_db=DEMO_VARIANTS)
        self.guardrail_agent = GuardrailAgent()

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build LangGraph workflow with explicit state transitions
        """
        # Define the graph
        workflow = StateGraph(dict)

        # Add nodes (each agent is a node)
        workflow.add_node("analytics", self.analytics_agent.process)
        workflow.add_node("identity", self.identity_agent.process)
        workflow.add_node("decision", self.decision_agent.process)
        workflow.add_node("guardrail", self.guardrail_agent.process)

        # Define edges (state transitions)
        workflow.set_entry_point("analytics")
        workflow.add_edge("analytics", "identity")
        workflow.add_edge("identity", "decision")
        workflow.add_edge("decision", "guardrail")
        workflow.add_edge("guardrail", END)

        return workflow.compile()

    def process_session(self, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the full multi-agent workflow on a session

        Args:
            session_state: Initial UserSession state dict

        Returns:
            Final state after all agents have processed
        """
        # Execute the workflow
        final_state = self.workflow.invoke(session_state)

        return final_state

    def get_agent_communication_log(self, final_state: Dict[str, Any]) -> list[str]:
        """
        Extract the audit log showing agent-to-agent communication

        This is required for the Foresters challenge to demonstrate
        clear step-by-step internal reasoning and communication.
        """
        return final_state.get("audit_log", [])


# Example usage and testing
if __name__ == "__main__":
    from models.events import Event, EventType, UserSession
    from datetime import datetime

    # Create a demo session with some events
    session = UserSession(
        session_id="demo_session_001",
        user_id="user_123",
        language="en"
    )

    # Simulate user behavior: exploring multiple products, some hesitation
    events = [
        Event(
            event_name=EventType.PAGE_VIEWED,
            session_id=session.session_id,
            timestamp=datetime.utcnow(),
            properties={"page": "homepage"}
        ),
        Event(
            event_name=EventType.COMPONENT_VIEWED,
            session_id=session.session_id,
            component_id="hero",
            timestamp=datetime.utcnow(),
            properties={}
        ),
        Event(
            event_name=EventType.TIME_ON_COMPONENT,
            session_id=session.session_id,
            component_id="hero",
            timestamp=datetime.utcnow(),
            properties={"time_seconds": 15}
        ),
        Event(
            event_name=EventType.CLICK,
            session_id=session.session_id,
            component_id="product_card",
            timestamp=datetime.utcnow(),
            properties={"product_id": "prod_001"}
        ),
        Event(
            event_name=EventType.BACKTRACK,
            session_id=session.session_id,
            timestamp=datetime.utcnow(),
            properties={}
        ),
        Event(
            event_name=EventType.COMPONENT_VIEWED,
            session_id=session.session_id,
            component_id="product_card",
            timestamp=datetime.utcnow(),
            properties={"product_id": "prod_002"}
        )
    ]

    for event in events:
        session.add_event(event)

    # Initialize workflow
    api_key = os.getenv("OPENAI_API_KEY", "")
    workflow = AdaptiveIdentityWorkflow(openai_api_key=api_key)

    # Process session through multi-agent system
    print("=" * 80)
    print("MULTI-AGENT WORKFLOW EXECUTION")
    print("=" * 80)

    initial_state = session.model_dump()
    final_state = workflow.process_session(initial_state)

    # Display agent communication log
    print("\n" + "=" * 80)
    print("AGENT COMMUNICATION LOG")
    print("=" * 80)

    communication_log = workflow.get_agent_communication_log(final_state)
    for entry in communication_log:
        print(entry)

    # Display final results
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    from models.events import UserSession as US
    final_session = US(**final_state)

    print(f"\nIdentity State: {final_session.identity_state}")
    print(f"Confidence: {final_session.identity_confidence:.2f}")
    print(f"Variant Shown: {final_session.last_variant_shown}")

    if final_session.behavioral_vector:
        print(f"\nBehavioral Vector:")
        print(f"  Exploration: {final_session.behavioral_vector.exploration_score:.2f}")
        print(f"  Hesitation: {final_session.behavioral_vector.hesitation_score:.2f}")
        print(f"  Engagement: {final_session.behavioral_vector.engagement_depth:.2f}")
        print(f"  Velocity: {final_session.behavioral_vector.decision_velocity:.2f}")
        print(f"  Focus: {final_session.behavioral_vector.content_focus_ratio:.2f}")

    print("\n" + "=" * 80)
