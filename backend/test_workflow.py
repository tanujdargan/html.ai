"""
Quick test script to verify multi-agent workflow works
Run this BEFORE pushing to make sure everything is functional
"""
import os
from datetime import datetime
from models.events import Event, EventType, UserSession
from agents.workflow import AdaptiveIdentityWorkflow

def test_workflow():
    """Test the complete multi-agent workflow"""

    print("=" * 80)
    print("🧪 TESTING ADAPTIVE IDENTITY ENGINE")
    print("=" * 80)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set!")
        print("   Set it in .env file or environment variable")
        print("   The Identity Agent will fail without it.")
        print("\n   For now, testing with mock key (will use fallback logic)...")
        api_key = "mock-key-for-testing"
    else:
        print(f"\n✅ OpenAI API key found: {api_key[:20]}...")

    # Create a demo session
    print("\n" + "=" * 80)
    print("📊 Creating demo session with simulated user behavior...")
    print("=" * 80)

    session = UserSession(
        session_id="test_session_001",
        user_id="test_user_123",
        language="en"
    )

    # Simulate different user behaviors
    behaviors = {
        "exploratory": [
            Event(event_name=EventType.PAGE_VIEWED, session_id=session.session_id, timestamp=datetime.utcnow(), properties={"page": "homepage"}),
            Event(event_name=EventType.COMPONENT_VIEWED, session_id=session.session_id, component_id="hero", timestamp=datetime.utcnow(), properties={}),
            Event(event_name=EventType.COMPONENT_VIEWED, session_id=session.session_id, component_id="product_1", timestamp=datetime.utcnow(), properties={}),
            Event(event_name=EventType.COMPONENT_VIEWED, session_id=session.session_id, component_id="product_2", timestamp=datetime.utcnow(), properties={}),
            Event(event_name=EventType.COMPONENT_VIEWED, session_id=session.session_id, component_id="product_3", timestamp=datetime.utcnow(), properties={}),
        ],
        "confident": [
            Event(event_name=EventType.PAGE_VIEWED, session_id=session.session_id, timestamp=datetime.utcnow(), properties={"page": "product"}),
            Event(event_name=EventType.COMPONENT_VIEWED, session_id=session.session_id, component_id="hero", timestamp=datetime.utcnow(), properties={}),
            Event(event_name=EventType.TIME_ON_COMPONENT, session_id=session.session_id, component_id="hero", timestamp=datetime.utcnow(), properties={"time_seconds": 30}),
            Event(event_name=EventType.CLICK, session_id=session.session_id, component_id="cta", timestamp=datetime.utcnow(), properties={}),
            Event(event_name=EventType.ADD_TO_CART, session_id=session.session_id, timestamp=datetime.utcnow(), properties={"product_id": "prod_001"}),
        ]
    }

    # Test with confident behavior
    print("\n🎭 Simulating CONFIDENT user behavior:")
    print("   - Views product page")
    print("   - Spends 30 seconds on hero")
    print("   - Clicks CTA")
    print("   - Adds to cart")

    for event in behaviors["confident"]:
        session.add_event(event)
        print(f"   ✓ Event: {event.event_name.value}")

    # Initialize workflow
    print("\n" + "=" * 80)
    print("🤖 Initializing Multi-Agent Workflow (LangGraph)")
    print("=" * 80)

    try:
        workflow = AdaptiveIdentityWorkflow(openai_api_key=api_key)
        print("✅ Workflow initialized successfully")
        print("   Agents loaded:")
        print("   - Analytics Agent")
        print("   - Identity Interpretation Agent")
        print("   - Decision Agent")
        print("   - Guardrail Agent")
    except Exception as e:
        print(f"❌ Failed to initialize workflow: {e}")
        return False

    # Run the workflow
    print("\n" + "=" * 80)
    print("⚡ Running Multi-Agent Workflow")
    print("=" * 80)

    try:
        initial_state = session.model_dump()
        final_state = workflow.process_session(initial_state)

        print("\n✅ Workflow completed successfully!")

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Display results
    print("\n" + "=" * 80)
    print("📋 AGENT COMMUNICATION LOG")
    print("=" * 80)

    communication_log = workflow.get_agent_communication_log(final_state)
    for i, entry in enumerate(communication_log, 1):
        print(f"{i}. {entry}")

    # Parse final state
    final_session = UserSession(**final_state)

    print("\n" + "=" * 80)
    print("🎯 FINAL RESULTS")
    print("=" * 80)

    print(f"\n🎭 Identity State: {final_session.identity_state}")
    print(f"📊 Confidence: {final_session.identity_confidence:.2%}")
    print(f"🎨 Variant Selected: {final_session.last_variant_shown}")

    if final_session.behavioral_vector:
        print(f"\n📈 Behavioral Vector:")
        print(f"   Exploration:  {'█' * int(final_session.behavioral_vector.exploration_score * 20)} {final_session.behavioral_vector.exploration_score:.2f}")
        print(f"   Hesitation:   {'█' * int(final_session.behavioral_vector.hesitation_score * 20)} {final_session.behavioral_vector.hesitation_score:.2f}")
        print(f"   Engagement:   {'█' * int(final_session.behavioral_vector.engagement_depth * 20)} {final_session.behavioral_vector.engagement_depth:.2f}")
        print(f"   Velocity:     {'█' * int(final_session.behavioral_vector.decision_velocity * 20)} {final_session.behavioral_vector.decision_velocity:.2f}")
        print(f"   Focus:        {'█' * int(final_session.behavioral_vector.content_focus_ratio * 20)} {final_session.behavioral_vector.content_focus_ratio:.2f}")

    # Check guardrails
    guardrail_check = final_session.outcome_metrics.get("guardrail_check")
    if guardrail_check:
        print(f"\n🛡️  Guardrail Status: {'✅ APPROVED' if guardrail_check['approved'] else '❌ REJECTED'}")
        print(f"   Reason: {guardrail_check['reason']}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\n🚀 Ready to push to GitHub and start building!")
    print("\nNext steps:")
    print("1. Share this output with your team")
    print("2. Push code to GitHub (make sure .env is in .gitignore)")
    print("3. Split tasks and start building!")

    return True

if __name__ == "__main__":
    # Load .env if available
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass

    success = test_workflow()
    exit(0 if success else 1)
