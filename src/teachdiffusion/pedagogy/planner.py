"""Pedagogical Planner — designs lessons the way expert math teachers do.

Uses Claude API to generate structured lesson plans with
pedagogy-aware step sequencing: hook → intuition → formal → examples → practice.
"""

from __future__ import annotations

import json
import os
from typing import Optional

from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore
from teachdiffusion.pedagogy.schema import (
    GestureType,
    PacingType,
    StepType,
    TeachingScript,
    TeachingStep,
    VisualType,
)


class PedagogicalPlanner:
    """Designs structured teaching scripts using Claude API.

    Usage:
        planner = PedagogicalPlanner(graph, definitions)
        script = planner.plan_lesson("quadratic equations")
    """

    def __init__(
        self,
        graph: ConceptGraph,
        definitions: DefinitionStore,
    ) -> None:
        self._graph = graph
        self._definitions = definitions

    def plan_lesson(
        self,
        topic: str,
        difficulty: str = "intermediate",
        target_audience: str = "high school student",
        max_steps: int = 8,
    ) -> TeachingScript:
        """Plan a complete lesson on a topic.

        Args:
            topic: The math topic to teach.
            difficulty: Target difficulty level.
            target_audience: Who the lesson is for.
            max_steps: Maximum number of teaching steps.

        Returns:
            A TeachingScript ready for video generation.
        """
        # Try Claude API first
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                return self._plan_with_llm(
                    topic, difficulty, target_audience, max_steps, api_key
                )
            except Exception:
                pass

        # Fallback to template-based planning
        return self._plan_with_template(topic, difficulty, target_audience)

    def _plan_with_llm(
        self,
        topic: str,
        difficulty: str,
        target_audience: str,
        max_steps: int,
        api_key: str,
    ) -> TeachingScript:
        """Generate a lesson plan using Claude API."""
        import anthropic

        # Gather context from knowledge base
        concept = self._graph.find_concept_by_name(topic)
        context = ""
        if concept:
            defn = self._definitions.get(concept.id)
            if defn:
                context = (
                    f"Formal definition: {defn.formal}\n"
                    f"Intuitive explanation: {defn.intuitive}\n"
                    f"Common misconceptions: {', '.join(defn.misconceptions)}\n"
                    f"Analogies: {', '.join(defn.analogies)}"
                )

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system=(
                "You are an expert math teacher and curriculum designer. "
                "Design a structured lesson plan as a sequence of teaching steps. "
                "Follow expert pedagogy: hook → build intuition → formal definition → "
                "worked example → common mistakes → practice → summary.\n\n"
                "Respond ONLY with valid JSON, no markdown. Format:\n"
                '{"steps": [{"step_type": "hook|build_intuition|formal_definition|'
                'worked_example|common_mistake|practice|summary", '
                '"content": "what the teacher says", '
                '"gesture": "pointing|writing|open_hand|counting|nodding|thinking|emphasis|neutral", '
                '"pacing": "slow|normal|fast|pause", '
                '"visual_type": "equation|graph|diagram|step_by_step|animation|none", '
                '"visual_content": "specific visual description", '
                '"board_text": "what appears on whiteboard", '
                '"duration_seconds": 15, '
                '"teacher_position": "left|center|right"}]}'
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Topic: {topic}\n"
                        f"Difficulty: {difficulty}\n"
                        f"Audience: {target_audience}\n"
                        f"Max steps: {max_steps}\n"
                        f"Context:\n{context}"
                    ),
                }
            ],
        )

        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        concept_id = concept.id if concept else topic.lower().replace(" ", "_")

        script = TeachingScript(
            topic=topic,
            concept_id=concept_id,
            target_audience=target_audience,
            difficulty=difficulty,
        )

        for i, step_data in enumerate(data.get("steps", [])[:max_steps]):
            step = TeachingStep(
                step_number=i + 1,
                step_type=StepType(step_data.get("step_type", "build_intuition")),
                content=step_data["content"],
                gesture=GestureType(step_data.get("gesture", "neutral")),
                pacing=PacingType(step_data.get("pacing", "normal")),
                visual_type=VisualType(step_data.get("visual_type", "none")),
                visual_content=step_data.get("visual_content", ""),
                board_text=step_data.get("board_text", ""),
                duration_seconds=step_data.get("duration_seconds", 15),
                teacher_position=step_data.get("teacher_position", "center"),
            )
            script.add_step(step)

        return script

    def _plan_with_template(
        self,
        topic: str,
        difficulty: str,
        target_audience: str,
    ) -> TeachingScript:
        """Generate a lesson plan using templates (fallback when no API key)."""
        concept = self._graph.find_concept_by_name(topic)
        concept_id = concept.id if concept else topic.lower().replace(" ", "_")
        defn = self._definitions.get(concept_id) if concept else None

        script = TeachingScript(
            topic=topic,
            concept_id=concept_id,
            target_audience=target_audience,
            difficulty=difficulty,
        )

        # Step 1: Hook
        script.add_step(TeachingStep(
            step_number=1,
            step_type=StepType.HOOK,
            content=f"Let me show you why {topic} matters and where you'll use it in real life.",
            gesture=GestureType.OPEN_HAND,
            pacing=PacingType.NORMAL,
            duration_seconds=15,
        ))

        # Step 2: Build Intuition
        intuition = defn.intuitive if defn else f"Let's build an intuitive understanding of {topic}."
        script.add_step(TeachingStep(
            step_number=2,
            step_type=StepType.BUILD_INTUITION,
            content=intuition,
            gesture=GestureType.OPEN_HAND,
            pacing=PacingType.SLOW,
            visual_type=VisualType.DIAGRAM,
            duration_seconds=25,
        ))

        # Step 3: Formal Definition
        formal = defn.formal if defn else f"Here is the precise definition of {topic}."
        script.add_step(TeachingStep(
            step_number=3,
            step_type=StepType.FORMAL_DEFINITION,
            content=formal,
            gesture=GestureType.WRITING,
            pacing=PacingType.SLOW,
            visual_type=VisualType.EQUATION,
            duration_seconds=20,
        ))

        # Step 4: Worked Example
        example_text = defn.examples[0] if defn and defn.examples else f"Let's work through an example of {topic} step by step."
        script.add_step(TeachingStep(
            step_number=4,
            step_type=StepType.WORKED_EXAMPLE,
            content=f"Let's work through this: {example_text}",
            gesture=GestureType.WRITING,
            pacing=PacingType.SLOW,
            visual_type=VisualType.STEP_BY_STEP,
            duration_seconds=30,
        ))

        # Step 5: Common Mistake
        if defn and defn.misconceptions:
            script.add_step(TeachingStep(
                step_number=5,
                step_type=StepType.COMMON_MISTAKE,
                content=f"Watch out — a very common mistake here is: {defn.misconceptions[0]}",
                gesture=GestureType.EMPHASIS,
                pacing=PacingType.SLOW,
                visual_type=VisualType.EQUATION,
                duration_seconds=15,
            ))

        # Step 6: Summary
        script.add_step(TeachingStep(
            step_number=len(script.steps) + 1,
            step_type=StepType.SUMMARY,
            content=f"Let's recap what we learned about {topic} today.",
            gesture=GestureType.OPEN_HAND,
            pacing=PacingType.NORMAL,
            duration_seconds=15,
        ))

        return script
