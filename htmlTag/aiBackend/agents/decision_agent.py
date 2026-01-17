"""
Decision Agent - Selects optimal UI variant using contextual bandit algorithm
"""
from typing import Dict, Any, List
import random
from models.events import UserSession, IdentityState
from models.variants import UIVariant, VariantDecision


class DecisionAgent:
    """
    Agent 3: Chooses which UI variant to show based on identity state
    """

    def __init__(self, variants_db: Dict[str, List[UIVariant]]):
        self.name = "Decision Agent"
        self.variants_db = variants_db  # component_id -> list of variants
        self.epsilon = 0.2  # Exploration rate for epsilon-greedy

    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select optimal variant using contextual bandit

        Args:
            state: Contains identity_state, component context

        Returns:
            Updated state with selected_variant and decision rationale
        """
        session = UserSession(**state)

        session.add_audit_entry(f"{self.name}: Selecting variant for identity={session.identity_state}")

        # For demo, assume we're optimizing "hero" component
        component_id = "hero"
        available_variants = self.variants_db.get(component_id, [])

        if not available_variants:
            session.add_audit_entry(f"{self.name}: No variants available for {component_id}")
            return session.model_dump()

        # Contextual bandit: epsilon-greedy with identity matching
        if random.random() < self.epsilon:
            # Explore: random variant
            selected = random.choice(available_variants)
            exploration_factor = 1.0
            rationale = f"Exploration mode: randomly selected {selected.variant_id}"
        else:
            # Exploit: choose best variant for this identity state
            selected, rationale = self._select_best_variant(
                available_variants,
                session.identity_state,
                session.identity_confidence
            )
            exploration_factor = 0.0

        decision = VariantDecision(
            selected_variant=selected,
            rationale=rationale,
            confidence=session.identity_confidence,
            exploration_factor=exploration_factor
        )

        session.last_variant_shown = selected.variant_id
        session.outcome_metrics["variant_decision"] = decision.model_dump()
        session.add_audit_entry(
            f"{self.name}: Selected '{selected.variant_id}' - {rationale}"
        )

        return session.model_dump()

    def _select_best_variant(
        self,
        variants: List[UIVariant],
        identity: IdentityState,
        confidence: float
    ) -> tuple[UIVariant, str]:
        """
        Select best variant based on identity matching and past performance
        """
        # Filter variants that target this identity
        matching_variants = [
            v for v in variants
            if v.target_identity == identity.value or v.target_identity is None
        ]

        if not matching_variants:
            matching_variants = variants

        # Sort by conversion rate (if available)
        scored_variants = []
        for variant in matching_variants:
            conversion_rate = variant.performance_metrics.get("conversion_rate", 0.0)
            # Thompson sampling style: add some randomness based on uncertainty
            sample = conversion_rate + random.gauss(0, 0.1 * (1 - confidence))
            scored_variants.append((variant, sample))

        scored_variants.sort(key=lambda x: x[1], reverse=True)
        best_variant = scored_variants[0][0]

        rationale = (
            f"Exploitation mode: selected {best_variant.variant_id} "
            f"(target_identity={best_variant.target_identity}, "
            f"conversion_rate={best_variant.performance_metrics.get('conversion_rate', 0.0):.2%})"
        )

        return best_variant, rationale


# Demo variant database
DEMO_VARIANTS = {
    "hero": [
        UIVariant(
            variant_id="hero_confident_v1",
            component_id="hero",
            variant_type="headline",
            content={
                "headline": "Premium Tech at Your Fingertips",
                "subheadline": "Fast, reliable shipping on all orders",
                "cta_text": "Shop Now",
                "urgency": "high"
            },
            target_identity="confident",
            performance_metrics={"conversion_rate": 0.15}
        ),
        UIVariant(
            variant_id="hero_exploratory_v1",
            component_id="hero",
            variant_type="headline",
            content={
                "headline": "Discover Premium Electronics",
                "subheadline": "Browse our curated collection of the latest tech",
                "cta_text": "Browse Collection",
                "urgency": "low"
            },
            target_identity="exploratory",
            performance_metrics={"conversion_rate": 0.08}
        ),
        UIVariant(
            variant_id="hero_overwhelmed_v1",
            component_id="hero",
            variant_type="headline",
            content={
                "headline": "Not Sure What You Need?",
                "subheadline": "We've picked our top 4 best-sellers just for you",
                "cta_text": "See Our Picks",
                "urgency": "medium"
            },
            target_identity="overwhelmed",
            performance_metrics={"conversion_rate": 0.12}
        ),
        UIVariant(
            variant_id="hero_comparison_v1",
            component_id="hero",
            variant_type="headline",
            content={
                "headline": "Compare Features & Specs",
                "subheadline": "Find the perfect match for your needs",
                "cta_text": "Compare Products",
                "urgency": "low"
            },
            target_identity="comparison_focused",
            performance_metrics={"conversion_rate": 0.11}
        ),
        UIVariant(
            variant_id="hero_ready_v1",
            component_id="hero",
            variant_type="headline",
            content={
                "headline": "Complete Your Order Today",
                "subheadline": "Free shipping on orders over $50",
                "cta_text": "View Cart",
                "urgency": "high"
            },
            target_identity="ready_to_decide",
            performance_metrics={"conversion_rate": 0.18}
        ),
        UIVariant(
            variant_id="hero_cautious_v1",
            component_id="hero",
            variant_type="headline",
            content={
                "headline": "Shop Risk-Free with 30-Day Returns",
                "subheadline": "Trusted by 10,000+ customers, secure checkout guaranteed",
                "cta_text": "Shop Safely",
                "urgency": "medium",
                "trust_badges": ["30-day returns", "Secure checkout", "10k+ reviews"]
            },
            target_identity="cautious",
            performance_metrics={"conversion_rate": 0.13}
        ),
        UIVariant(
            variant_id="hero_impulse_v1",
            component_id="hero",
            variant_type="headline",
            content={
                "headline": "FLASH SALE - 40% OFF!",
                "subheadline": "Limited time only! Ends in 3 hours",
                "cta_text": "Shop Sale Now",
                "urgency": "extreme",
                "countdown": "3:00:00"
            },
            target_identity="impulse_buyer",
            performance_metrics={"conversion_rate": 0.22}
        )
    ]
}
