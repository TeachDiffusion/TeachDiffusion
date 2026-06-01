"""Tests for Layer 1: Knowledge Base."""

import pytest
from teachdiffusion.knowledge.concept_graph import (
    Concept, ConceptGraph, MathDomain, DifficultyLevel,
)
from teachdiffusion.knowledge.definition_store import DefinitionStore
from teachdiffusion.knowledge.proof_store import ProofStore


class TestConceptGraph:
    def setup_method(self):
        self.graph = ConceptGraph()
        self.graph.load_default()

    def test_load_default_concepts(self):
        assert self.graph.num_concepts >= 34

    def test_get_concept(self):
        c = self.graph.get_concept("quadratic_equations")
        assert c is not None
        assert c.name == "Quadratic Equations"
        assert c.domain == MathDomain.ALGEBRA

    def test_get_prerequisites(self):
        prereqs = self.graph.get_prerequisites("quadratic_equations")
        prereq_ids = {p.id for p in prereqs}
        assert "factoring" in prereq_ids
        assert "square_roots" in prereq_ids

    def test_get_all_prerequisites(self):
        all_prereqs = self.graph.get_all_prerequisites("eigenvalues")
        assert len(all_prereqs) > 2
        ids = {p.id for p in all_prereqs}
        assert "matrices" in ids
        assert "determinants" in ids

    def test_get_learning_path(self):
        path = self.graph.get_learning_path("arithmetic_basics", "quadratic_equations")
        assert len(path) >= 3
        assert path[0].id == "arithmetic_basics"
        assert path[-1].id == "quadratic_equations"

    def test_find_concept_by_name(self):
        c = self.graph.find_concept_by_name("derivatives")
        assert c is not None
        assert c.id == "derivatives"

    def test_find_concept_by_keyword(self):
        c = self.graph.find_concept_by_name("parabola")
        assert c is not None
        assert c.id == "quadratic_equations"

    def test_get_next_concepts(self):
        known = {"arithmetic_basics", "fractions", "decimals", "exponents"}
        next_concepts = self.graph.get_next_concepts(known)
        assert len(next_concepts) > 0
        # All returned concepts should have their prereqs satisfied
        for c in next_concepts:
            for prereq_id in c.prerequisites:
                assert prereq_id in known

    def test_validate(self):
        issues = self.graph.validate()
        assert len(issues) == 0, f"Graph validation issues: {issues}"

    def test_get_concepts_by_domain(self):
        calc = self.graph.get_concepts_by_domain(MathDomain.CALCULUS)
        assert len(calc) >= 4
        for c in calc:
            assert c.domain == MathDomain.CALCULUS


class TestDefinitionStore:
    def setup_method(self):
        self.store = DefinitionStore()
        self.store.load_defaults()

    def test_load_defaults(self):
        assert len(self.store.all_ids()) >= 5

    def test_get_definition(self):
        defn = self.store.get("quadratic_equations")
        assert defn is not None
        assert len(defn.formal) > 0
        assert len(defn.intuitive) > 0
        assert len(defn.misconceptions) > 0

    def test_has_definition(self):
        assert self.store.has("derivatives")
        assert not self.store.has("nonexistent_concept")


class TestProofStore:
    def setup_method(self):
        self.store = ProofStore()
        self.store.load_defaults()

    def test_has_proofs(self):
        assert self.store.has_proofs("quadratic_equations")
        assert self.store.has_proofs("pythagorean_theorem")

    def test_proof_has_steps(self):
        proofs = self.store.get_proofs("quadratic_equations")
        assert len(proofs) >= 1
        assert len(proofs[0].steps) >= 5
