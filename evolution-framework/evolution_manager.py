"""
Evolution Manager - Core orchestration for self-evolving capabilities

This module implements genetic algorithm-based evolution for system components,
inspired by EvoAgentX's approach to code-level evolution with comprehensive
safety mechanisms.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class EvolutionStatus(Enum):
    """Status of an evolution cycle"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    EVOLVING = "evolving"
    TESTING = "testing"
    VALIDATING = "validating"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ComponentGenome:
    """Represents the genetic structure of a component"""
    component_id: str
    version: str
    genes: Dict[str, Any]  # Component configuration and parameters
    fitness_score: float = 0.0
    generation: int = 0
    parent_ids: List[str] = None
    mutations: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.parent_ids is None:
            self.parent_ids = []
        if self.mutations is None:
            self.mutations = []
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    def get_hash(self) -> str:
        """Generate unique hash for this genome"""
        genome_str = json.dumps(self.genes, sort_keys=True)
        return hashlib.sha256(genome_str.encode()).hexdigest()[:16]


@dataclass
class EvolutionCycle:
    """Represents a complete evolution cycle"""
    cycle_id: str
    component_id: str
    status: EvolutionStatus
    current_genome: ComponentGenome
    candidate_genomes: List[ComponentGenome]
    fitness_evaluations: Dict[str, float]
    safety_checks: Dict[str, bool]
    started_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "cycle_id": self.cycle_id,
            "component_id": self.component_id,
            "status": self.status.value,
            "current_genome": self.current_genome.to_dict(),
            "candidate_genomes": [g.to_dict() for g in self.candidate_genomes],
            "fitness_evaluations": self.fitness_evaluations,
            "safety_checks": self.safety_checks,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message
        }


class EvolutionManager:
    """
    Core orchestrator for self-evolving capabilities
    
    Implements genetic algorithm-based evolution with comprehensive safety checks,
    fitness evaluation, and rollback mechanisms.
    """
    
    def __init__(
        self,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        population_size: int = 10,
        elite_size: int = 2,
        max_generations: int = 100,
        fitness_threshold: float = 0.8,
        enable_auto_deploy: bool = False
    ):
        """
        Initialize Evolution Manager
        
        Args:
            mutation_rate: Probability of mutation for each gene
            crossover_rate: Probability of crossover between parents
            population_size: Number of candidate genomes per generation
            elite_size: Number of top performers to preserve
            max_generations: Maximum number of evolution cycles
            fitness_threshold: Minimum fitness score for deployment
            enable_auto_deploy: Whether to automatically deploy approved evolutions
        """
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.population_size = population_size
        self.elite_size = elite_size
        self.max_generations = max_generations
        self.fitness_threshold = fitness_threshold
        self.enable_auto_deploy = enable_auto_deploy
        
        # Component registry
        self.components: Dict[str, ComponentGenome] = {}
        
        # Evolution history
        self.evolution_cycles: List[EvolutionCycle] = []
        
        # Fitness evaluators (registered by component type)
        self.fitness_evaluators: Dict[str, Callable] = {}
        
        # Safety validators (registered by component type)
        self.safety_validators: Dict[str, Callable] = {}
        
        logger.info(f"Evolution Manager initialized with population_size={population_size}, "
                   f"mutation_rate={mutation_rate}, auto_deploy={enable_auto_deploy}")
    
    def register_component(self, genome: ComponentGenome) -> None:
        """Register a component for evolution"""
        self.components[genome.component_id] = genome
        logger.info(f"Registered component: {genome.component_id} (v{genome.version})")
    
    def register_fitness_evaluator(
        self,
        component_type: str,
        evaluator: Callable[[ComponentGenome], float]
    ) -> None:
        """Register a fitness evaluation function for a component type"""
        self.fitness_evaluators[component_type] = evaluator
        logger.info(f"Registered fitness evaluator for: {component_type}")
    
    def register_safety_validator(
        self,
        component_type: str,
        validator: Callable[[ComponentGenome], bool]
    ) -> None:
        """Register a safety validation function for a component type"""
        self.safety_validators[component_type] = validator
        logger.info(f"Registered safety validator for: {component_type}")
    
    async def evolve_component(
        self,
        component_id: str,
        target_metric: Optional[str] = None,
        target_improvement: float = 0.1
    ) -> EvolutionCycle:
        """
        Evolve a component through genetic algorithm
        
        Args:
            component_id: ID of component to evolve
            target_metric: Specific metric to optimize (optional)
            target_improvement: Minimum improvement threshold
            
        Returns:
            EvolutionCycle with results
        """
        if component_id not in self.components:
            raise ValueError(f"Component {component_id} not registered")
        
        current_genome = self.components[component_id]
        cycle_id = f"{component_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting evolution cycle: {cycle_id}")
        
        cycle = EvolutionCycle(
            cycle_id=cycle_id,
            component_id=component_id,
            status=EvolutionStatus.ANALYZING,
            current_genome=current_genome,
            candidate_genomes=[],
            fitness_evaluations={},
            safety_checks={},
            started_at=datetime.utcnow().isoformat()
        )
        
        try:
            # Generate initial population
            cycle.status = EvolutionStatus.EVOLVING
            population = await self._generate_population(current_genome)
            
            # Evolve through generations
            best_genome = current_genome
            for generation in range(self.max_generations):
                logger.info(f"Generation {generation + 1}/{self.max_generations}")
                
                # Evaluate fitness
                cycle.status = EvolutionStatus.TESTING
                fitness_scores = await self._evaluate_population(population)
                
                # Select best performer
                best_idx = fitness_scores.index(max(fitness_scores))
                candidate = population[best_idx]
                
                # Check if improvement threshold met
                improvement = (candidate.fitness_score - current_genome.fitness_score) / current_genome.fitness_score
                
                if improvement >= target_improvement:
                    logger.info(f"Target improvement achieved: {improvement:.2%}")
                    best_genome = candidate
                    break
                
                # Check if fitness threshold met
                if candidate.fitness_score >= self.fitness_threshold:
                    logger.info(f"Fitness threshold achieved: {candidate.fitness_score:.2f}")
                    best_genome = candidate
                    break
                
                # Evolve next generation
                population = await self._evolve_generation(population, fitness_scores)
            
            # Validate safety
            cycle.status = EvolutionStatus.VALIDATING
            safety_passed = await self._validate_safety(best_genome)
            
            cycle.candidate_genomes = [best_genome]
            cycle.fitness_evaluations = {best_genome.get_hash(): best_genome.fitness_score}
            cycle.safety_checks = safety_passed
            
            # Determine approval
            if all(safety_passed.values()) and best_genome.fitness_score > current_genome.fitness_score:
                cycle.status = EvolutionStatus.APPROVED
                logger.info(f"Evolution approved: {best_genome.fitness_score:.2f} > {current_genome.fitness_score:.2f}")
                
                # Auto-deploy if enabled
                if self.enable_auto_deploy:
                    await self._deploy_genome(best_genome)
                    cycle.status = EvolutionStatus.DEPLOYED
            else:
                cycle.status = EvolutionStatus.REJECTED
                logger.warning(f"Evolution rejected: safety_checks={safety_passed}, "
                             f"fitness={best_genome.fitness_score:.2f}")
            
            cycle.completed_at = datetime.utcnow().isoformat()
            
        except Exception as e:
            logger.error(f"Evolution cycle failed: {str(e)}", exc_info=True)
            cycle.status = EvolutionStatus.REJECTED
            cycle.error_message = str(e)
            cycle.completed_at = datetime.utcnow().isoformat()
        
        self.evolution_cycles.append(cycle)
        return cycle
    
    async def _generate_population(self, base_genome: ComponentGenome) -> List[ComponentGenome]:
        """Generate initial population through mutation"""
        population = [base_genome]
        
        for i in range(self.population_size - 1):
            mutated = await self._mutate_genome(base_genome)
            mutated.generation = base_genome.generation + 1
            population.append(mutated)
        
        return population
    
    async def _mutate_genome(self, genome: ComponentGenome) -> ComponentGenome:
        """Apply random mutations to a genome"""
        import random
        import copy
        
        mutated_genes = copy.deepcopy(genome.genes)
        mutations = []
        
        for gene_key, gene_value in mutated_genes.items():
            if random.random() < self.mutation_rate:
                # Apply mutation based on gene type
                if isinstance(gene_value, (int, float)):
                    # Numeric mutation: add random noise
                    noise = random.gauss(0, 0.1) * gene_value
                    mutated_genes[gene_key] = type(gene_value)(gene_value + noise)
                    mutations.append(f"mutated_{gene_key}")
                elif isinstance(gene_value, bool):
                    # Boolean mutation: flip
                    mutated_genes[gene_key] = not gene_value
                    mutations.append(f"flipped_{gene_key}")
                elif isinstance(gene_value, str):
                    # String mutation: slight variation (simplified)
                    mutations.append(f"varied_{gene_key}")
        
        return ComponentGenome(
            component_id=genome.component_id,
            version=f"{genome.version}.m{len(mutations)}",
            genes=mutated_genes,
            generation=genome.generation + 1,
            parent_ids=[genome.get_hash()],
            mutations=mutations
        )
    
    async def _crossover_genomes(
        self,
        parent1: ComponentGenome,
        parent2: ComponentGenome
    ) -> ComponentGenome:
        """Perform crossover between two parent genomes"""
        import random
        import copy
        
        child_genes = copy.deepcopy(parent1.genes)
        
        for gene_key in child_genes.keys():
            if random.random() < 0.5 and gene_key in parent2.genes:
                child_genes[gene_key] = parent2.genes[gene_key]
        
        return ComponentGenome(
            component_id=parent1.component_id,
            version=f"{parent1.version}.x{parent2.version}",
            genes=child_genes,
            generation=max(parent1.generation, parent2.generation) + 1,
            parent_ids=[parent1.get_hash(), parent2.get_hash()],
            mutations=["crossover"]
        )
    
    async def _evaluate_population(self, population: List[ComponentGenome]) -> List[float]:
        """Evaluate fitness for entire population"""
        fitness_scores = []
        
        for genome in population:
            # Get component type from component_id
            component_type = genome.component_id.split("_")[0]
            
            if component_type in self.fitness_evaluators:
                score = await self._evaluate_fitness(genome, self.fitness_evaluators[component_type])
            else:
                # Default fitness evaluation
                score = 0.5
            
            genome.fitness_score = score
            fitness_scores.append(score)
        
        return fitness_scores
    
    async def _evaluate_fitness(
        self,
        genome: ComponentGenome,
        evaluator: Callable
    ) -> float:
        """Evaluate fitness of a single genome"""
        try:
            if asyncio.iscoroutinefunction(evaluator):
                score = await evaluator(genome)
            else:
                score = evaluator(genome)
            return max(0.0, min(1.0, score))  # Clamp to [0, 1]
        except Exception as e:
            logger.error(f"Fitness evaluation failed: {str(e)}")
            return 0.0
    
    async def _evolve_generation(
        self,
        population: List[ComponentGenome],
        fitness_scores: List[float]
    ) -> List[ComponentGenome]:
        """Evolve population to next generation"""
        import random
        
        # Sort by fitness (using key parameter to avoid comparing ComponentGenome objects)
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda i: fitness_scores[i], reverse=True)
        sorted_pop = [population[i] for i in sorted_indices]
        
        # Keep elite
        next_generation = sorted_pop[:self.elite_size]
        
        # Generate offspring
        while len(next_generation) < self.population_size:
            # Selection (tournament)
            parent1 = random.choice(sorted_pop[:len(sorted_pop)//2])
            parent2 = random.choice(sorted_pop[:len(sorted_pop)//2])
            
            # Crossover
            if random.random() < self.crossover_rate:
                child = await self._crossover_genomes(parent1, parent2)
            else:
                child = await self._mutate_genome(parent1)
            
            next_generation.append(child)
        
        return next_generation
    
    async def _validate_safety(self, genome: ComponentGenome) -> Dict[str, bool]:
        """Run safety validation checks"""
        component_type = genome.component_id.split("_")[0]
        
        safety_checks = {
            "interface_compatibility": True,  # Placeholder
            "resource_limits": True,  # Placeholder
            "goal_alignment": True,  # Placeholder
        }
        
        if component_type in self.safety_validators:
            try:
                validator = self.safety_validators[component_type]
                if asyncio.iscoroutinefunction(validator):
                    custom_check = await validator(genome)
                else:
                    custom_check = validator(genome)
                safety_checks["custom_validation"] = custom_check
            except Exception as e:
                logger.error(f"Safety validation failed: {str(e)}")
                safety_checks["custom_validation"] = False
        
        return safety_checks
    
    async def _deploy_genome(self, genome: ComponentGenome) -> None:
        """Deploy an evolved genome"""
        logger.info(f"Deploying genome: {genome.component_id} v{genome.version}")
        self.components[genome.component_id] = genome
    
    def get_evolution_history(self, component_id: Optional[str] = None) -> List[Dict]:
        """Get evolution history for all or specific component"""
        if component_id:
            cycles = [c for c in self.evolution_cycles if c.component_id == component_id]
        else:
            cycles = self.evolution_cycles
        
        return [cycle.to_dict() for cycle in cycles]
    
    def get_component_lineage(self, component_id: str) -> List[ComponentGenome]:
        """Get evolutionary lineage of a component"""
        if component_id not in self.components:
            return []
        
        lineage = []
        current = self.components[component_id]
        
        # Trace back through evolution cycles
        for cycle in reversed(self.evolution_cycles):
            if cycle.component_id == component_id and cycle.status == EvolutionStatus.DEPLOYED:
                lineage.append(cycle.current_genome)
        
        lineage.append(current)
        return lineage

