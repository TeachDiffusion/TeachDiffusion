"""Script Engine — converts a topic into a fully fleshed-out teaching script.

This is the 'brain' of TeachDiffusion. It takes a topic string and produces
a complete TeachingScript with all steps, gestures, visuals, and timing
specified. It's the bridge between the knowledge layer and the video layer.
"""

from __future__ import annotations

from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore
from teachdiffusion.pedagogy.planner import PedagogicalPlanner
from teachdiffusion.pedagogy.schema import TeachingScript


class ScriptEngine:
    """High-level interface: topic string → complete TeachingScript.

    Usage:
        engine = ScriptEngine(graph, definitions)
        script = engine.generate("quadratic equations")
        for step in script.steps:
            print(step.to_video_prompt())
    """

    def __init__(
        self,
        graph: ConceptGraph,
        definitions: DefinitionStore,
    ) -> None:
        self._graph = graph
        self._definitions = definitions
        self._planner = PedagogicalPlanner(graph, definitions)

    def generate(
        self,
        topic: str,
        difficulty: str = "intermediate",
        target_audience: str = "high school student",
        persona: str = "Professor Aria",
        max_steps: int = 8,
    ) -> TeachingScript:
        """Generate a complete teaching script for a topic.

        Args:
            topic: The math topic to teach.
            difficulty: Target difficulty level.
            target_audience: Who the lesson is for.
            persona: Name of the AI teacher persona.
            max_steps: Maximum number of teaching steps.

        Returns:
            A complete TeachingScript ready for video generation.
        """
        script = self._planner.plan_lesson(
            topic=topic,
            difficulty=difficulty,
            target_audience=target_audience,
            max_steps=max_steps,
        )
        script.persona = persona
        return script

    def generate_from_concept_id(
        self,
        concept_id: str,
        difficulty: str = "intermediate",
        target_audience: str = "high school student",
        persona: str = "Professor Aria",
    ) -> TeachingScript:
        """Generate a script from a known concept ID.

        Args:
            concept_id: ID from the concept graph.
            difficulty: Target difficulty level.
            target_audience: Who the lesson is for.
            persona: Name of the AI teacher persona.

        Returns:
            A complete TeachingScript.
        """
        concept = self._graph.get_concept(concept_id)
        if concept is None:
            raise ValueError(f"Unknown concept: {concept_id}")

        return self.generate(
            topic=concept.name,
            difficulty=difficulty,
            target_audience=target_audience,
            persona=persona,
        )
