import asyncio
import logging
from datetime import datetime
import json
import aiofiles
from pathlib import Path

logger = logging.getLogger(__name__)

class SelfImprovementAgent:
    def __init__(self, monitor_instance):
        self.monitor = monitor_instance
        self.project_root = self.monitor.project_root
        self.feedback_dir = self.project_root / "feedback"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)

    async def analyze_performance(self, ai_id):
        """Analyze the performance of a specific AI agent."""
        metrics = await self.monitor.db.get_latest_performance_metrics(ai_id, limit=100)
        if not metrics:
            logger.info(f"No performance metrics found for AI: {ai_id}")
            return None

        # Example: Simple average performance score
        total_score = sum(m["value"] for m in metrics if m["metric_name"] == "performance_score")
        average_score = total_score / len(metrics) if metrics else 0

        logger.info(f"AI {ai_id} average performance score: {average_score:.2f}")
        return {"average_performance_score": average_score}

    async def generate_feedback(self, ai_id, performance_data):
        """Generate feedback based on performance data."""
        feedback = {
            "ai_id": ai_id,
            "timestamp": datetime.now().isoformat(),
            "performance_summary": performance_data,
            "suggestions": []
        }

        if performance_data and performance_data["average_performance_score"] < 80:
            feedback["suggestions"].append("Consider optimizing task execution for better performance.")
            await self.monitor.db.log_system_event(
                "AI_FEEDBACK", 
                f"AI {ai_id} performance below threshold. Suggesting optimization.", 
                datetime.now().isoformat()
            )
        else:
            feedback["suggestions"].append("Performance is satisfactory. Continue current operations.")

        feedback_file = self.feedback_dir / f"{ai_id}_feedback.json"
        async with aiofiles.open(feedback_file, mode="w") as f:
            await f.write(json.dumps(feedback, indent=4))
        logger.info(f"Generated feedback for AI {ai_id} and saved to {feedback_file}")
        return feedback

    async def apply_self_improvement(self, ai_id, feedback):
        """Apply self-improvement based on generated feedback."""
        if "Consider optimizing task execution" in feedback.get("suggestions", []):
            logger.info(f"AI {ai_id}: Applying optimization strategy (simulated).")
            await self.monitor.db.log_system_event(
                "AI_SELF_IMPROVEMENT", 
                f"AI {ai_id} applied optimization strategy based on feedback.", 
                datetime.now().isoformat()
            )
            
            if self.monitor.github_integration:
                issue_title = f"AI {ai_id} Performance Optimization Needed"
                perf_summary = feedback["performance_summary"]
                issue_body = f"The AI agent {ai_id} has shown performance below acceptable thresholds. \n\n**Performance Summary:**\n```json\n{json.dumps(perf_summary, indent=2)}\n```\n\n**Suggestions:**\n- Consider optimizing task execution for better performance.\n\nFurther investigation and potential code modifications are recommended."
                
                self.monitor.github_integration.create_issue(
                    title=issue_title,
                    body=issue_body,
                    labels=["performance", "ai-optimization", ai_id],
                    assignees=[] # Assign to relevant human or AI team if applicable
                )
                logger.info(f"Created GitHub issue for AI {ai_id} performance optimization.")

        logger.info(f"AI {ai_id}: Self-improvement process completed (simulated).")

    async def run_self_improvement_cycle(self):
        """Run a full self-improvement cycle for all active AI agents."""
        logger.info("Starting AI self-improvement cycle...")
        for ai_id in self.monitor.ai_agents.keys():
            logger.info(f"Processing self-improvement for AI: {ai_id}")
            performance_data = await self.analyze_performance(ai_id)
            if performance_data:
                feedback = await self.generate_feedback(ai_id, performance_data)
                await self.apply_self_improvement(ai_id, feedback)
        logger.info("AI self-improvement cycle completed.")

