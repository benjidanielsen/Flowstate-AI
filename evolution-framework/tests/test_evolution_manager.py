"""
Tests for Evolution Manager
"""

import pytest
import asyncio
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolution_manager import (
    EvolutionManager,
    ComponentGenome,
    EvolutionStatus,
    EvolutionCycle
)


@pytest.fixture
def evolution_manager():
    """Create an Evolution Manager instance for testing"""
    return EvolutionManager(
        mutation_rate=0.2,
        crossover_rate=0.7,
        population_size=5,
        elite_size=1,
        max_generations=10,
        fitness_threshold=0.8,
        enable_auto_deploy=False
    )


@pytest.fixture
def sample_genome():
    """Create a sample component genome"""
    return ComponentGenome(
        component_id="nba_service",
        version="1.0.0",
        genes={
            "recommendation_threshold": 0.7,
            "max_recommendations": 5,
            "use_historical_data": True,
            "weight_recency": 0.3,
            "weight_frequency": 0.4,
            "weight_importance": 0.3
        },
        fitness_score=0.6,
        generation=0
    )


class TestComponentGenome:
    """Test ComponentGenome class"""
    
    def test_genome_creation(self, sample_genome):
        """Test genome creation"""
        assert sample_genome.component_id == "nba_service"
        assert sample_genome.version == "1.0.0"
        assert sample_genome.fitness_score == 0.6
        assert sample_genome.generation == 0
        assert len(sample_genome.genes) == 6
    
    def test_genome_to_dict(self, sample_genome):
        """Test genome serialization"""
        genome_dict = sample_genome.to_dict()
        assert isinstance(genome_dict, dict)
        assert genome_dict["component_id"] == "nba_service"
        assert "genes" in genome_dict
    
    def test_genome_hash(self, sample_genome):
        """Test genome hash generation"""
        hash1 = sample_genome.get_hash()
        assert isinstance(hash1, str)
        assert len(hash1) == 16
        
        # Same genes should produce same hash
        genome2 = ComponentGenome(
            component_id="nba_service",
            version="2.0.0",
            genes=sample_genome.genes.copy()
        )
        hash2 = genome2.get_hash()
        assert hash1 == hash2


class TestEvolutionManager:
    """Test EvolutionManager class"""
    
    def test_manager_initialization(self, evolution_manager):
        """Test manager initialization"""
        assert evolution_manager.mutation_rate == 0.2
        assert evolution_manager.population_size == 5
        assert len(evolution_manager.components) == 0
        assert len(evolution_manager.evolution_cycles) == 0
    
    def test_register_component(self, evolution_manager, sample_genome):
        """Test component registration"""
        evolution_manager.register_component(sample_genome)
        assert "nba_service" in evolution_manager.components
        assert evolution_manager.components["nba_service"] == sample_genome
    
    def test_register_fitness_evaluator(self, evolution_manager):
        """Test fitness evaluator registration"""
        def dummy_evaluator(genome):
            return 0.8
        
        evolution_manager.register_fitness_evaluator("nba", dummy_evaluator)
        assert "nba" in evolution_manager.fitness_evaluators
    
    def test_register_safety_validator(self, evolution_manager):
        """Test safety validator registration"""
        def dummy_validator(genome):
            return True
        
        evolution_manager.register_safety_validator("nba", dummy_validator)
        assert "nba" in evolution_manager.safety_validators
    
    @pytest.mark.asyncio
    async def test_mutate_genome(self, evolution_manager, sample_genome):
        """Test genome mutation"""
        mutated = await evolution_manager._mutate_genome(sample_genome)
        
        assert mutated.component_id == sample_genome.component_id
        assert mutated.generation == sample_genome.generation + 1
        assert len(mutated.parent_ids) == 1
        assert mutated.parent_ids[0] == sample_genome.get_hash()
        
        # Some genes should be different (with high probability)
        # Note: This is probabilistic, so we check structure rather than values
        assert len(mutated.genes) == len(sample_genome.genes)
    
    @pytest.mark.asyncio
    async def test_crossover_genomes(self, evolution_manager, sample_genome):
        """Test genome crossover"""
        parent2 = ComponentGenome(
            component_id="nba_service",
            version="1.0.1",
            genes={
                "recommendation_threshold": 0.8,
                "max_recommendations": 3,
                "use_historical_data": False,
                "weight_recency": 0.4,
                "weight_frequency": 0.3,
                "weight_importance": 0.3
            },
            fitness_score=0.7,
            generation=0
        )
        
        child = await evolution_manager._crossover_genomes(sample_genome, parent2)
        
        assert child.component_id == sample_genome.component_id
        assert child.generation == 1
        assert len(child.parent_ids) == 2
        assert len(child.genes) == len(sample_genome.genes)
    
    @pytest.mark.asyncio
    async def test_generate_population(self, evolution_manager, sample_genome):
        """Test population generation"""
        population = await evolution_manager._generate_population(sample_genome)
        
        assert len(population) == evolution_manager.population_size
        assert population[0] == sample_genome
        
        # All others should be mutations
        for genome in population[1:]:
            assert genome.generation == sample_genome.generation + 1
    
    @pytest.mark.asyncio
    async def test_evaluate_fitness(self, evolution_manager, sample_genome):
        """Test fitness evaluation"""
        def evaluator(genome):
            # Simple evaluator based on threshold
            return genome.genes.get("recommendation_threshold", 0.5)
        
        score = await evolution_manager._evaluate_fitness(sample_genome, evaluator)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert score == 0.7  # Based on sample_genome's threshold
    
    @pytest.mark.asyncio
    async def test_validate_safety(self, evolution_manager, sample_genome):
        """Test safety validation"""
        def validator(genome):
            # Check that weights sum to 1.0
            total_weight = (
                genome.genes.get("weight_recency", 0) +
                genome.genes.get("weight_frequency", 0) +
                genome.genes.get("weight_importance", 0)
            )
            return abs(total_weight - 1.0) < 0.01
        
        evolution_manager.register_safety_validator("nba", validator)
        
        safety_checks = await evolution_manager._validate_safety(sample_genome)
        
        assert isinstance(safety_checks, dict)
        assert "interface_compatibility" in safety_checks
        assert "custom_validation" in safety_checks
        assert safety_checks["custom_validation"] is True
    
    @pytest.mark.asyncio
    async def test_evolve_component_not_registered(self, evolution_manager):
        """Test evolving unregistered component raises error"""
        with pytest.raises(ValueError, match="not registered"):
            await evolution_manager.evolve_component("nonexistent")
    
    @pytest.mark.asyncio
    async def test_evolve_component_basic(self, evolution_manager, sample_genome):
        """Test basic evolution cycle"""
        # Register component
        evolution_manager.register_component(sample_genome)
        
        # Register fitness evaluator
        def evaluator(genome):
            # Reward higher thresholds
            return genome.genes.get("recommendation_threshold", 0.5)
        
        evolution_manager.register_fitness_evaluator("nba", evaluator)
        
        # Run evolution with limited generations
        evolution_manager.max_generations = 3
        cycle = await evolution_manager.evolve_component(
            "nba_service",
            target_improvement=0.1
        )
        
        assert isinstance(cycle, EvolutionCycle)
        assert cycle.component_id == "nba_service"
        assert cycle.status in [EvolutionStatus.APPROVED, EvolutionStatus.REJECTED]
        assert len(cycle.candidate_genomes) > 0
        assert cycle.completed_at is not None
    
    def test_get_evolution_history(self, evolution_manager, sample_genome):
        """Test evolution history retrieval"""
        # Create a mock evolution cycle
        cycle = EvolutionCycle(
            cycle_id="test_cycle",
            component_id="nba_service",
            status=EvolutionStatus.APPROVED,
            current_genome=sample_genome,
            candidate_genomes=[sample_genome],
            fitness_evaluations={sample_genome.get_hash(): 0.8},
            safety_checks={"test": True},
            started_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat()
        )
        
        evolution_manager.evolution_cycles.append(cycle)
        
        # Get all history
        history = evolution_manager.get_evolution_history()
        assert len(history) == 1
        assert history[0]["cycle_id"] == "test_cycle"
        
        # Get component-specific history
        history = evolution_manager.get_evolution_history("nba_service")
        assert len(history) == 1
        
        # Get non-existent component
        history = evolution_manager.get_evolution_history("nonexistent")
        assert len(history) == 0
    
    def test_get_component_lineage(self, evolution_manager, sample_genome):
        """Test component lineage retrieval"""
        evolution_manager.register_component(sample_genome)
        
        lineage = evolution_manager.get_component_lineage("nba_service")
        assert len(lineage) >= 1
        assert lineage[-1] == sample_genome


@pytest.mark.asyncio
async def test_full_evolution_workflow():
    """Test complete evolution workflow"""
    # Create manager
    manager = EvolutionManager(
        population_size=5,
        max_generations=5,
        enable_auto_deploy=True
    )
    
    # Create initial genome
    genome = ComponentGenome(
        component_id="test_component",
        version="1.0.0",
        genes={
            "param_a": 0.5,
            "param_b": 10,
            "param_c": True
        },
        fitness_score=0.5
    )
    
    # Register component
    manager.register_component(genome)
    
    # Register fitness evaluator (reward higher param_a)
    def fitness_eval(g):
        return g.genes.get("param_a", 0.0)
    
    manager.register_fitness_evaluator("test", fitness_eval)
    
    # Register safety validator
    def safety_check(g):
        return 0.0 <= g.genes.get("param_a", 0.5) <= 1.0
    
    manager.register_safety_validator("test", safety_check)
    
    # Run evolution
    cycle = await manager.evolve_component("test_component", target_improvement=0.2)
    
    # Verify results
    assert cycle.status in [EvolutionStatus.APPROVED, EvolutionStatus.DEPLOYED, EvolutionStatus.REJECTED]
    assert len(cycle.candidate_genomes) > 0
    
    if cycle.status == EvolutionStatus.DEPLOYED:
        # Check that component was updated
        updated_genome = manager.components["test_component"]
        assert updated_genome.fitness_score >= genome.fitness_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

