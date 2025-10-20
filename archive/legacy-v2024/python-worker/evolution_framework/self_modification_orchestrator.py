"""
Self-Modification Orchestrator

Orchestrates autonomous code improvements and self-modification.
"""

import os
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .evolution_manager import EvolutionManager
from .knowledge_manager import VectorKnowledgeManager
from .metrics_collector import MetricsCollector
from .code_analyzer import CodeAnalyzer
from .config import EvolutionConfig


class SelfModificationOrchestrator:
    """Orchestrates the self-modification process for autonomous improvements."""
    
    def __init__(self, project_root: str = ".", config: Optional[EvolutionConfig] = None):
        """
        Initialize the self-modification orchestrator.
        
        Args:
            project_root: Root directory of the project
            config: Evolution framework configuration
        """
        self.project_root = project_root
        self.config = config or EvolutionConfig()
        self.evolution_manager = EvolutionManager(config)
        self.knowledge_manager = VectorKnowledgeManager(config)
        self.metrics_collector = MetricsCollector()
        self.code_analyzer = CodeAnalyzer()
        self.logger = logging.getLogger("self_modification_orchestrator")
        
        # Track modifications
        self.modification_history = []
    
    def identify_improvement_opportunities(
        self,
        min_quality_score: float = 70.0,
        max_opportunities: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Scan project for areas needing improvement based on code analysis.
        
        Args:
            min_quality_score: Minimum quality score threshold
            max_opportunities: Maximum number of opportunities to return
            
        Returns:
            List of improvement opportunities
        """
        self.logger.info("Identifying improvement opportunities...")
        self.metrics_collector.record_metric("opportunity_scan", "started", "count")
        
        opportunities = []
        
        # Analyze Python files in the project
        for root, _, files in os.walk(self.project_root):
            # Skip certain directories
            if any(skip in root for skip in [
                'node_modules', 'venv', '.git', '__pycache__',
                'dist', 'build', 'evolution_framework'  # Don't modify self
            ]):
                continue
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                        
                        # Analyze code quality
                        analysis = self.code_analyzer.analyze_code(code_content, file_path)
                        
                        if analysis and analysis['quality_score'] < min_quality_score:
                            # Search knowledge base for similar improvements
                            knowledge_results = self.knowledge_manager.search_knowledge(
                                f"code improvement for {file}",
                                category="pattern",
                                limit=3
                            )
                            
                            opportunities.append({
                                "file_path": file_path,
                                "quality_score": analysis['quality_score'],
                                "issues": analysis['issues'],
                                "analysis": analysis,
                                "related_knowledge": knowledge_results,
                                "priority": self._calculate_priority(analysis)
                            })
                    
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
        
        # Sort by priority and limit
        opportunities.sort(key=lambda x: x['priority'], reverse=True)
        opportunities = opportunities[:max_opportunities]
        
        self.metrics_collector.record_metric(
            "opportunities_identified",
            len(opportunities),
            "count"
        )
        
        self.logger.info(f"Identified {len(opportunities)} improvement opportunities")
        return opportunities
    
    def _calculate_priority(self, analysis: Dict[str, Any]) -> float:
        """
        Calculate priority score for an improvement opportunity.
        
        Args:
            analysis: Code analysis results
            
        Returns:
            Priority score (higher is more urgent)
        """
        # Start with inverse of quality score
        priority = 100 - analysis['quality_score']
        
        # Increase priority for critical issues
        critical_issues = sum(
            1 for issue in analysis['issues']
            if issue.get('severity') == 'critical'
        )
        priority += critical_issues * 20
        
        # Increase priority for high severity issues
        high_issues = sum(
            1 for issue in analysis['issues']
            if issue.get('severity') == 'high'
        )
        priority += high_issues * 10
        
        # Increase priority for large files with issues
        if analysis['structure']['loc'] > 300:
            priority += 5
        
        return priority
    
    def propose_modification(self, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Propose a code modification for an improvement opportunity.
        
        Args:
            opportunity: Improvement opportunity details
            
        Returns:
            Proposed modification, or None if proposal fails
        """
        file_path = opportunity['file_path']
        analysis = opportunity['analysis']
        
        self.logger.info(f"Proposing modification for {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            # Create context for the evolution manager
            context = {
                "analysis": analysis,
                "issues": analysis['issues'],
                "quality_score": analysis['quality_score'],
                "related_knowledge": opportunity.get('related_knowledge', []),
                "goals": [
                    "Improve code readability",
                    "Reduce complexity",
                    "Increase maintainability",
                    "Fix identified issues"
                ]
            }
            
            # Propose improvement using evolution manager
            event_id = self.evolution_manager.propose_improvement(
                component=file_path,
                description=f"Code quality improvement for {os.path.basename(file_path)}",
                metrics_before={"quality_score": analysis['quality_score']},
                metadata=context
            )
            
            if not event_id:
                self.logger.error(f"Failed to create evolution event for {file_path}")
                return None
            
            # Generate improved code (placeholder - would use LLM in production)
            proposed_code = self._generate_improved_code(original_code, context)
            
            if not proposed_code:
                self.logger.error(f"Failed to generate improved code for {file_path}")
                return None
            
            # Analyze proposed code
            proposed_analysis = self.code_analyzer.analyze_code(proposed_code, file_path)
            
            if not proposed_analysis:
                self.logger.error(f"Failed to analyze proposed code for {file_path}")
                return None
            
            # Calculate confidence based on improvement
            confidence = self._calculate_confidence(analysis, proposed_analysis)
            
            return {
                "event_id": event_id,
                "file_path": file_path,
                "original_code": original_code,
                "proposed_code": proposed_code,
                "original_analysis": analysis,
                "proposed_analysis": proposed_analysis,
                "confidence": confidence,
                "improvement": proposed_analysis['quality_score'] - analysis['quality_score']
            }
        
        except Exception as e:
            self.logger.error(f"Error proposing modification for {file_path}: {e}")
            return None
    
    def _generate_improved_code(
        self,
        original_code: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate improved code based on analysis and context.
        
        This is a placeholder that would integrate with LLM in production.
        
        Args:
            original_code: Original source code
            context: Improvement context
            
        Returns:
            Improved code, or None if generation fails
        """
        # In production, this would call the LLM with a detailed prompt
        # For now, return original code (no modification)
        # This prevents actual code changes during testing
        
        self.logger.info("Code improvement generation (placeholder - no actual changes)")
        return original_code
    
    def _calculate_confidence(
        self,
        original_analysis: Dict[str, Any],
        proposed_analysis: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for a proposed modification.
        
        Args:
            original_analysis: Analysis of original code
            proposed_analysis: Analysis of proposed code
            
        Returns:
            Confidence score (0-1)
        """
        # Start with base confidence
        confidence = 0.5
        
        # Increase confidence if quality score improves
        quality_improvement = proposed_analysis['quality_score'] - original_analysis['quality_score']
        if quality_improvement > 0:
            confidence += min(0.3, quality_improvement / 100)
        else:
            confidence -= 0.2
        
        # Increase confidence if issues are reduced
        original_issues = len(original_analysis['issues'])
        proposed_issues = len(proposed_analysis['issues'])
        if proposed_issues < original_issues:
            confidence += min(0.2, (original_issues - proposed_issues) * 0.05)
        
        # Ensure confidence is within bounds
        return max(0.0, min(1.0, confidence))
    
    def validate_modification(self, modification: Dict[str, Any]) -> bool:
        """
        Validate a proposed modification before application.
        
        Args:
            modification: Proposed modification details
            
        Returns:
            True if modification is valid and safe, False otherwise
        """
        self.logger.info(f"Validating modification for {modification['file_path']}")
        
        # Check confidence threshold
        if modification['confidence'] < self.config.auto_apply_threshold:
            self.logger.warning(
                f"Confidence {modification['confidence']:.2f} below threshold "
                f"{self.config.auto_apply_threshold}"
            )
            return False
        
        # Check that quality improves
        if modification['improvement'] <= 0:
            self.logger.warning("No quality improvement detected")
            return False
        
        # Check that proposed code is syntactically valid
        try:
            compile(modification['proposed_code'], modification['file_path'], 'exec')
        except SyntaxError as e:
            self.logger.error(f"Proposed code has syntax error: {e}")
            return False
        
        # Additional validation checks could be added here
        # e.g., run tests, check for breaking changes, etc.
        
        return True
    
    def apply_modification(self, modification: Dict[str, Any]) -> bool:
        """
        Apply a validated modification to the codebase.
        
        Args:
            modification: Modification details
            
        Returns:
            True if application successful, False otherwise
        """
        file_path = modification['file_path']
        self.logger.info(f"Applying modification to {file_path}")
        
        try:
            # Create backup
            backup_path = f"{file_path}.backup"
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Apply modification
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modification['proposed_code'])
            
            # Update evolution event
            self.evolution_manager.apply_improvement(
                modification['event_id'],
                metrics_after={"quality_score": modification['proposed_analysis']['quality_score']}
            )
            
            # Record in knowledge base
            self.knowledge_manager.add_knowledge(
                content=f"Applied code improvement to {file_path}",
                category="outcome",
                source="self_modification_orchestrator",
                confidence=modification['confidence'],
                metadata={
                    "file_path": file_path,
                    "improvement": modification['improvement'],
                    "original_quality": modification['original_analysis']['quality_score'],
                    "new_quality": modification['proposed_analysis']['quality_score']
                }
            )
            
            # Track modification
            self.modification_history.append({
                "timestamp": datetime.now().isoformat(),
                "file_path": file_path,
                "event_id": modification['event_id'],
                "improvement": modification['improvement'],
                "confidence": modification['confidence']
            })
            
            self.metrics_collector.record_metric(
                "modification_applied",
                1,
                "count"
            )
            
            self.logger.info(f"Successfully applied modification to {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error applying modification to {file_path}: {e}")
            
            # Attempt to restore from backup
            try:
                if os.path.exists(backup_path):
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        backup_content = f.read()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(backup_content)
                    self.logger.info(f"Restored {file_path} from backup")
            except Exception as restore_error:
                self.logger.error(f"Error restoring backup: {restore_error}")
            
            return False
    
    def run_self_modification_cycle(
        self,
        min_quality_score: float = 70.0,
        max_modifications: int = 5,
        auto_apply: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a complete self-modification cycle.
        
        Args:
            min_quality_score: Minimum quality score threshold
            max_modifications: Maximum number of modifications to apply
            auto_apply: Whether to automatically apply validated modifications
            
        Returns:
            Summary of the modification cycle
        """
        self.logger.info("Starting self-modification cycle")
        self.metrics_collector.start_timer("self_modification_cycle")
        
        # Identify opportunities
        opportunities = self.identify_improvement_opportunities(
            min_quality_score=min_quality_score,
            max_opportunities=max_modifications
        )
        
        proposed_modifications = []
        applied_modifications = []
        
        # Propose modifications
        for opportunity in opportunities:
            modification = self.propose_modification(opportunity)
            if modification:
                proposed_modifications.append(modification)
        
        # Validate and optionally apply modifications
        for modification in proposed_modifications:
            if self.validate_modification(modification):
                if auto_apply:
                    if self.apply_modification(modification):
                        applied_modifications.append(modification)
                else:
                    self.logger.info(
                        f"Modification validated but not applied (auto_apply=False): "
                        f"{modification['file_path']}"
                    )
        
        duration = self.metrics_collector.end_timer("self_modification_cycle")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": duration,
            "opportunities_identified": len(opportunities),
            "modifications_proposed": len(proposed_modifications),
            "modifications_applied": len(applied_modifications),
            "applied_modifications": applied_modifications
        }
        
        self.logger.info(
            f"Self-modification cycle complete: "
            f"{len(applied_modifications)}/{len(proposed_modifications)} applied"
        )
        
        return summary

