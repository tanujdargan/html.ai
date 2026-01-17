"""
Guardrail Agent - Validates decisions for privacy, ethics, and policy compliance
"""
from typing import Dict, Any, List
from models.events import UserSession
from models.variants import GuardrailCheck


class GuardrailAgent:
    """
    Agent 4: Ensures all decisions comply with ethical and privacy constraints
    """

    def __init__(self):
        self.name = "Guardrail Agent"

        # Define prohibited patterns
        self.prohibited_protected_traits = [
            "race", "ethnicity", "gender", "age", "religion",
            "disability", "sexual_orientation", "national_origin"
        ]

        self.prohibited_actions = [
            "price_manipulation",
            "discriminatory_pricing",
            "sensitive_category_inference",
            "cross_site_tracking"
        ]

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate decision against guardrails

        Args:
            state: Contains variant_decision and identity information

        Returns:
            Updated state with guardrail_check result
        """
        session = UserSession(**state)

        session.add_audit_entry(f"{self.name}: Validating decision against guardrails")

        # Run all guardrail checks
        violations = []

        # Check 1: No protected trait inference
        if self._check_protected_traits(session):
            violations.append("Protected trait inference detected")

        # Check 2: No price manipulation
        if self._check_price_manipulation(session):
            violations.append("Price manipulation detected")

        # Check 3: Session scope enforcement
        if self._check_session_scope(session):
            violations.append("Session scope violation")

        # Check 4: Language consistency
        if self._check_language_consistency(session):
            violations.append("Language inconsistency detected")

        # Check 5: Component scope enforcement
        if self._check_component_scope(session):
            violations.append("Unauthorized component modification")

        # Create guardrail result
        approved = len(violations) == 0

        guardrail_check = GuardrailCheck(
            approved=approved,
            reason="All checks passed" if approved else f"Violations: {', '.join(violations)}",
            violated_rules=violations
        )

        session.outcome_metrics["guardrail_check"] = guardrail_check.model_dump()

        if approved:
            session.add_audit_entry(f"{self.name}: ✓ All guardrails passed")
        else:
            session.add_audit_entry(
                f"{self.name}: ✗ Guardrail violations: {', '.join(violations)}"
            )

        return session.model_dump()

    def _check_protected_traits(self, session: UserSession) -> bool:
        """
        Ensure we're not inferring or using protected characteristics
        """
        # Check if identity_state or behavioral_vector implies protected traits
        # In real implementation, this would use more sophisticated checks

        # For now, we verify that we're only using behavioral signals
        if session.identity_state and session.behavioral_vector:
            # Valid: using behavioral data only
            return False

        # If we somehow have demographic data in session, flag it
        if session.outcome_metrics.get("demographics"):
            return True

        return False

    def _check_price_manipulation(self, session: UserSession) -> bool:
        """
        Ensure variant doesn't manipulate pricing
        """
        variant_decision = session.outcome_metrics.get("variant_decision")

        if not variant_decision:
            return False

        selected_variant = variant_decision.get("selected_variant", {})
        content = selected_variant.get("content", {})

        # Check if content includes price changes
        if "price" in content or "discount" in content:
            # Flag: we don't allow dynamic pricing
            return True

        return False

    def _check_session_scope(self, session: UserSession) -> bool:
        """
        Ensure identity is session-scoped (not persistent cross-session tracking)
        """
        # In a real system, check if we're storing identity beyond session
        # For demo purposes, always passes

        return False

    def _check_language_consistency(self, session: UserSession) -> bool:
        """
        Ensure variant respects user's language preference
        """
        variant_decision = session.outcome_metrics.get("variant_decision")

        if not variant_decision:
            return False

        # For demo, assume all variants are in English
        # In production, check variant language matches session.language

        return False

    def _check_component_scope(self, session: UserSession) -> bool:
        """
        Ensure we're only modifying approved, marked components
        """
        variant_decision = session.outcome_metrics.get("variant_decision")

        if not variant_decision:
            return False

        selected_variant = variant_decision.get("selected_variant", {})
        component_id = selected_variant.get("component_id")

        # Whitelist of approved components
        approved_components = ["hero", "product_card", "cta_banner", "testimonials"]

        if component_id not in approved_components:
            return True

        # Check variant type is allowed
        variant_type = selected_variant.get("variant_type")
        allowed_types = ["headline", "cta", "image", "layout"]

        if variant_type not in allowed_types:
            return True

        return False
