"""Example Builder — generates worked examples for math concepts.

Produces step-by-step solutions that show not just WHAT to do,
but WHY each step works.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class WorkedStep:
    """A single step in a worked example."""

    step_number: int
    action: str  # What we do
    result: str  # What we get
    reasoning: str  # Why we do it


@dataclass
class WorkedExample:
    """A complete worked example with step-by-step solution."""

    concept_id: str
    problem: str
    difficulty: str = "intermediate"
    steps: list[WorkedStep] = field(default_factory=list)
    final_answer: str = ""
    key_insight: str = ""


class ExampleBuilder:
    """Generates worked examples for math concepts.

    Usage:
        builder = ExampleBuilder()
        example = builder.build("quadratic_equations", "Solve x² - 5x + 6 = 0")
    """

    def build(
        self,
        concept_id: str,
        problem: str = "",
        difficulty: str = "intermediate",
    ) -> WorkedExample:
        """Build a worked example.

        Args:
            concept_id: The concept this example demonstrates.
            problem: Specific problem to solve (optional).
            difficulty: Difficulty level.

        Returns:
            WorkedExample with step-by-step solution.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                return self._build_with_llm(concept_id, problem, difficulty, api_key)
            except Exception:
                pass

        return self._build_fallback(concept_id, problem, difficulty)

    def _build_with_llm(
        self, concept_id: str, problem: str, difficulty: str, api_key: str
    ) -> WorkedExample:
        """Generate worked example using Claude API."""
        import anthropic

        prompt = f"Create a worked example for: {concept_id}"
        if problem:
            prompt += f"\nSpecific problem: {problem}"
        prompt += f"\nDifficulty: {difficulty}"

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=(
                "Generate a step-by-step worked math example. "
                "Respond ONLY with valid JSON:\n"
                '{"problem": "...", "steps": [{"action": "...", "result": "...", '
                '"reasoning": "..."}], "final_answer": "...", "key_insight": "..."}'
            ),
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        steps = [
            WorkedStep(
                step_number=i + 1,
                action=s["action"],
                result=s["result"],
                reasoning=s.get("reasoning", ""),
            )
            for i, s in enumerate(data.get("steps", []))
        ]

        return WorkedExample(
            concept_id=concept_id,
            problem=data.get("problem", problem),
            difficulty=difficulty,
            steps=steps,
            final_answer=data.get("final_answer", ""),
            key_insight=data.get("key_insight", ""),
        )

    def _build_fallback(
        self, concept_id: str, problem: str, difficulty: str
    ) -> WorkedExample:
        """Fallback when no API key is available."""
        return WorkedExample(
            concept_id=concept_id,
            problem=problem or f"A {difficulty} problem on {concept_id}",
            difficulty=difficulty,
            steps=[
                WorkedStep(
                    step_number=1,
                    action="Identify what we're given and what we need to find",
                    result="Problem understood",
                    reasoning="Always start by understanding the problem.",
                ),
                WorkedStep(
                    step_number=2,
                    action="Apply the relevant formula or technique",
                    result="Expression simplified",
                    reasoning="Use the tools we've learned.",
                ),
                WorkedStep(
                    step_number=3,
                    action="Solve and verify",
                    result="Solution found",
                    reasoning="Always check your answer.",
                ),
            ],
            final_answer="See steps above",
            key_insight=f"The key to {concept_id} problems is understanding the underlying concept.",
        )
