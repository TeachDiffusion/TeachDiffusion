"""Tests for Layer 5: Explanation Generator."""

from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore
from teachdiffusion.explanation.generator import ExplanationGenerator
from teachdiffusion.explanation.example_builder import ExampleBuilder
from teachdiffusion.explanation.analogy_store import AnalogyStore


class TestExplanationGenerator:
    def setup_method(self):
        self.graph = ConceptGraph()
        self.graph.load_default()
        self.defns = DefinitionStore()
        self.defns.load_defaults()
        self.gen = ExplanationGenerator(self.graph, self.defns)

    def test_generate_known_concept(self):
        exp = self.gen.generate("quadratic_equations")
        assert exp.concept_name == "Quadratic Equations"
        assert len(exp.hook) > 0
        assert len(exp.intuition) > 0
        assert len(exp.formal) > 0

    def test_generate_full_text(self):
        exp = self.gen.generate("derivatives")
        text = exp.to_full_text()
        assert "[Hook]" in text
        assert "[Intuition]" in text


class TestExampleBuilder:
    def test_build_fallback(self):
        builder = ExampleBuilder()
        example = builder.build("quadratic_equations", "Solve x² - 4 = 0")
        assert len(example.steps) >= 1
        assert example.concept_id == "quadratic_equations"


class TestAnalogyStore:
    def test_get_analogies(self):
        store = AnalogyStore()
        analogies = store.get("derivatives")
        assert len(analogies) >= 1
        assert "speedometer" in analogies[0].analogy.lower() or len(analogies[0].analogy) > 0

    def test_has(self):
        store = AnalogyStore()
        assert store.has("eigenvalues")
        assert not store.has("nonexistent")
