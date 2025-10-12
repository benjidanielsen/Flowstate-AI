import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class XAINBA:
    """
    Provides Explainable AI (XAI) capabilities for Next Best Action (NBA) recommendations.
    """
    def __init__(self, knowledge_manager):
        self.knowledge_manager = knowledge_manager

    def explain_nba_recommendation(self, recommendation: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a human-understandable explanation for an NBA recommendation.
        """
        explanation = {
            "recommendation": recommendation,
            "reasoning_factors": [],
            "impact_analysis": {},
            "confidence_score": recommendation.get("confidence", 0.0)
        }

        # Example: Extracting reasoning factors from context and recommendation
        customer_segment = context.get("customer_segment", "unknown")
        customer_history = context.get("customer_history", {})
        product_interest = context.get("product_interest", [])
        
        explanation["reasoning_factors"].append(f"Customer belongs to the \"{customer_segment}\" segment.")
        if customer_history.get("last_purchase_date"): 
            explanation["reasoning_factors"].append(f"Last purchase was on {customer_history["last_purchase_date"]}.")
        if product_interest:
            explanation["reasoning_factors"].append(f"Customer has shown interest in: {', '.join(product_interest)}.")

        action_type = recommendation.get("action_type", "")
        if action_type == "offer_discount":
            explanation["reasoning_factors"].append("A discount is recommended to incentivize a purchase.")
            explanation["impact_analysis"]["expected_conversion_increase"] = "5-10%"
            explanation["impact_analysis"]["expected_revenue_increase"] = "15%"
        elif action_type == "send_followup":
            explanation["reasoning_factors"].append("A follow-up is recommended to re-engage the customer.")
            explanation["impact_analysis"]["expected_engagement_increase"] = "20%"
        
        # Store explanation in knowledge manager
        self.knowledge_manager.store_knowledge(
            f"nba_explanation_{recommendation.get("id", "unknown")}",
            json.dumps(explanation),
            tags=["xai", "nba_explanation", customer_segment]
        )

        logger.info(f"Generated XAI explanation for NBA recommendation: {recommendation.get("id", "unknown")}")
        return explanation

    def get_feature_importance(self, model_id: str) -> Dict[str, float]:
        """
        Retrieves feature importance for a given NBA model.
        This would typically come from the model itself (e.g., tree-based models).
        """
        logger.info(f"Retrieving feature importance for model: {model_id}")
        # Simulate feature importance
        feature_importance = {
            "customer_segment": 0.3,
            "customer_history_length": 0.2,
            "product_interest_score": 0.25,
            "last_interaction_sentiment": 0.15,
            "time_since_last_purchase": 0.1
        }
        return feature_importance

    def visualize_explanation(self, explanation: Dict[str, Any]) -> str:
        """
        Generates a simple text-based visualization of the explanation.
        In a real UI, this would be a rich graphical representation.
        """
        viz = f"--- NBA Recommendation Explanation ---\n"
        viz += f"Recommendation: {explanation["recommendation"].get("action_type", "N/A")} for {explanation["recommendation"].get("customer_id", "N/A")}\n"
        viz += f"Confidence: {explanation["confidence_score"]:.2f}\n"
        viz += "\nReasoning Factors:\n"
        for factor in explanation["reasoning_factors"]:
            viz += f"- {factor}\n"
        if explanation["impact_analysis"]:
            viz += "\nExpected Impact:\n"
            for key, value in explanation["impact_analysis"].items():
                viz += f"- {key.replace("_", " ").title()}: {value}\n"
        viz += "------------------------------------\n"
        return viz

