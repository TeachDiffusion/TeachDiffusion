"""Tests for Layer 3: Pedagogical Planner."""

import pytest
from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore
from teachdiffusion.pedagogy.schema import (
    TeachingStep, TeachingScript, StepType, GestureType, PacingType, VisualType,
)
from teachdiffusion.pedagogy.planner import PedagogicalPlanner
from teachdiffusion.pedagogy.difficulty import DifficultyEstimator


class TestTeachingStep:
    def test_create_step(self):
        step = TeachingStep(
            step_number=1,
            step_type=StepType.HOOK,
            content="Let me show you why quadratics matter.",
            gesture=GestureType.OPEN_HAND,
            pacing=PacingType.NORMAL,
        )
        assert step.step_number == 1
        assert step.step_type == StepType.HOOK

    def test_to_video_prompt(self):
        step = TeachingStep(
            step_number=1,
            step_type=StepType.BUILD_INTUITION,
            content="Imagine throwing a ball...",
            gesture=GestureType.POINTING,
            pacing=PacingType.SLOW,
            board_text="y = ax² + bx + c",
        )
        prompt = step.to_video_prompt("Professor Aria")
        assert "Professor Aria" in prompt
        assert "pointing" in prompt
        assert "slowly" in prompt
        assert "y = ax² + bx + c" in prompt

    def test_serialize_deserialize(self):
        step = TeachingStep(
            step_number=2,
            step_type=StepType.WORKED_EXAMPLE,
            content="Let's solve this step by step.",
            gesture=GestureType.WRITING,
            visual_type=VisualType.STEP_BY_STEP,
        )
        data = step.to_dict()
        restored = TeachingStep.from_dict(data)
        assert restored.step_number == step.step_number
        assert restored.step_type == step.step_type
        assert restored.gesture == step.gesture


class TestTeachingScript:
    def test_create_and_add_steps(self):
        script = TeachingScript(topic="Quadratics", concept_id="quadratic_equations")
        script.add_step(TeachingStep(step_number=1, step_type=StepType.HOOK, content="Hook", duration_seconds=10))
        script.add_step(TeachingStep(step_number=2, step_type=StepType.SUMMARY, content="Summary", duration_seconds=10))
        assert script.num_steps == 2
        assert script.total_duration_seconds == 20

    def test_get_video_prompts(self):
        script = TeachingScript(topic="Test", concept_id="test")
        script.add_step(TeachingStep(step_number=1, step_type=StepType.HOOK, content="Hello"))
        prompts = script.get_video_prompts()
        assert len(prompts) == 1
        assert "Professor Aria" in prompts[0]


class TestPedagogicalPlanner:
    def test_plan_lesson_template(self):
        graph = ConceptGraph()
        graph.load_default()
        defns = DefinitionStore()
        defns.load_defaults()
        planner = PedagogicalPlanner(graph, defns)

        script = planner.plan_lesson("quadratic equations")
        assert script.num_steps >= 3
        step_types = [s.step_type for s in script.steps]
        assert StepType.HOOK in step_types


class TestDifficultyEstimator:
    def setup_method(self):
        self.graph = ConceptGraph()
        self.graph.load_default()
        self.estimator = DifficultyEstimator(self.graph)

    def test_estimate_with_full_prereqs(self):
        known = {"determinants", "polynomials"}
        result = self.estimator.estimate("eigenvalues", known)
        assert result.prerequisite_coverage == 1.0
        assert "Ready" in result.recommendation

    def test_estimate_without_prereqs(self):
        result = self.estimator.estimate("eigenvalues", set())
        assert result.prerequisite_coverage == 0.0
        assert result.adjusted_difficulty > result.base_difficulty
