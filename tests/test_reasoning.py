"""Tests for Layer 2: Reasoning Engine."""

import pytest
from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore
from teachdiffusion.reasoning.inference_engine import InferenceEngine
from teachdiffusion.reasoning.decomposer import Decomposer
from teachdiffusion.reasoning.analogy_builder import AnalogyBuilder


class TestInferenceEngine:
    def setup_method(self):
        self.graph = ConceptGraph()
        self.graph.load_default()
        self.engine = InferenceEngine(self.graph)

    def test_find_knowledge_gaps(self):
        gaps = self.engine.find_knowledge_gaps(
            known={"arithmetic_basics"}, target="quadratic_equations"
        )
        assert len(gaps) > 0
        gap_ids = {g.concept.id for g in gaps}
        assert "factoring" in gap_ids

    def test_no_gaps_when_ready(self):
        prereqs = {"factoring", "square_roots", "exponents", "arithmetic_basics", "variables_expressions"}
        gaps = self.engine.find_knowledge_gaps(known=prereqs, target="quadratic_equations")
        assert len(gaps) == 0

    def test_assess_readiness_not_ready(self):
        result = self.engine.assess_readiness(
            known={"arithmetic_basics"}, target="eigenvalues"
        )
        assert not result.is_ready
        assert result.readiness_score < 1.0
        assert len(result.missing_prerequisites) > 0

    def test_assess_readiness_ready(self):
        result = self.engine.assess_readiness(
            known={"determinants", "polynomials", "matrices", "vectors",
                   "systems_of_equations", "coordinate_geometry", "basic_geometry",
                   "linear_equations", "variables_expressions", "arithmetic_basics",
                   "fractions", "exponents", "square_roots", "factoring",
                   "quadratic_equations"},
            target="eigenvalues"
        )
        assert result.is_ready
        assert result.readiness_score == 1.0


class TestDecomposer:
    def setup_method(self):
        self.graph = ConceptGraph()
        self.graph.load_default()
        self.decomposer = Decomposer(self.graph)

    def test_decompose_known_concept(self):
        result = self.decomposer.decompose("quadratic equations")
        assert result.original_topic == "Quadratic Equations"
        assert result.root is not None
        assert result.total_estimated_minutes > 0

    def test_decompose_unknown_concept(self):
        result = self.decomposer.decompose("nonexistent_topic_xyz")
        assert result.root is not None
        assert result.total_estimated_minutes > 0


class TestAnalogyBuilder:
    def setup_method(self):
        self.graph = ConceptGraph()
        self.graph.load_default()
        self.definitions = DefinitionStore()
        self.definitions.load_defaults()
        self.builder = AnalogyBuilder(self.graph, self.definitions)

    def test_get_analogies_from_store(self):
        analogies = self.builder.get_analogies("quadratic_equations", count=2)
        assert len(analogies) > 0
        assert len(analogies[0].analogy) > 0
