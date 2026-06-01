"""Explanation Generator — produces layered explanations for math concepts.

Each explanation follows a proven pedagogical sequence:
1. Hook — why should you care?
2. Intuition — what does it FEEL like?
3. Formal — precise mathematical statement
4. Examples — worked problems
5. Connections — how does this relate to what you already know?
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore


@dataclass
class Explanation:
    """A complete layered explanation of a math concept."""

    concept_id: str
    concept_name: str
    hook: str = ""
    intuition: str = ""
    formal: str = ""
    examples: list[str] = field(default_factory=list)
    connections: list[str] = field(default_factory=list)
    common_mistakes: list[str] = field(default_factory=list)
    summary: str = ""

    def to_full_text(self) -> str:
        """Combine all layers into a single text."""
        parts = []
        if self.hook:
            parts.append(f"[Hook] {self.hook}")
        if self.intuition:
            parts.append(f"[Intuition] {self.intuition}")
        if self.formal:
            parts.append(f"[Formal] {self.formal}")
        if self.examples:
            for i, ex in enumerate(self.examples, 1):
                parts.append(f"[Example {i}] {ex}")
        if self.common_mistakes:
            parts.append("[Watch out] " + " | ".join(self.common_mistakes))
        if self.connections:
            parts.append("[Connections] " + " | ".join(self.connections))
        if self.summary:
            parts.append(f"[Summary] {self.summary}")
        return "\n\n".join(parts)


class ExplanationGenerator:
    """Generates layered explanations for math concepts.

    Uses the knowledge base for curated content and Claude API
    for generating fresh, customized explanations.

    Usage:
        gen = ExplanationGenerator(graph, definitions)
        explanation = gen.generate("quadratic_equations")
        print(explanation.to_full_text())
    """

    def __init__(
        self, graph: ConceptGraph, definitions: DefinitionStore
    ) -> None:
        self._graph = graph
        self._definitions = definitions

    def generate(
        self,
        concept_id: str,
        difficulty: str = "intermediate",
        target_audience: str = "high school student",
    ) -> Explanation:
        """Generate a layered explanation for a concept.

        Args:
            concept_id: The concept to explain.
            difficulty: Target difficulty level.
            target_audience: Who the explanation is for.

        Returns:
            An Explanation with all layers populated.
        """
        concept = self._graph.get_concept(concept_id)
        defn = self._definitions.get(concept_id)

        concept_name = concept.name if concept else concept_id

        # Try Claude API for rich explanation
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                return self._generate_with_llm(
                    concept_id, concept_name, defn, difficulty, target_audience, api_key
                )
            except Exception:
                pass

        # Fallback to knowledge base content
        return self._generate_from_knowledge_base(concept_id, concept_name, defn)

    def _generate_with_llm(
        self,
        concept_id: str,
        concept_name: str,
        defn,
        difficulty: str,
        target_audience: str,
        api_key: str,
    ) -> Explanation:
        """Generate explanation using Claude API."""
        import anthropic

        context = ""
        if defn:
            context = (
                f"Formal definition: {defn.formal}\n"
                f"Intuitive: {defn.intuitive}\n"
                f"Misconceptions: {', '.join(defn.misconceptions)}\n"
                f"Analogies: {', '.join(defn.analogies)}"
            )

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=(
                "You are an expert math teacher. Generate a layered explanation. "
                "Respond ONLY with valid JSON, no markdown:\n"
                '{"hook": "...", "intuition": "...", "formal": "...", '
                '"examples": ["..."], "connections": ["..."], '
                '"common_mistakes": ["..."], "summary": "..."}'
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Explain: {concept_name}\n"
                        f"Difficulty: {difficulty}\n"
                        f"Audience: {target_audience}\n"
                        f"Context:\n{context}"
                    ),
                }
            ],
        )

        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        return Explanation(
            concept_id=concept_id,
            concept_name=concept_name,
            hook=data.get("hook", ""),
            intuition=data.get("intuition", ""),
            formal=data.get("formal", ""),
            examples=data.get("examples", []),
            connections=data.get("connections", []),
            common_mistakes=data.get("common_mistakes", []),
            summary=data.get("summary", ""),
        )

    def _generate_from_knowledge_base(
        self, concept_id: str, concept_name: str, defn
    ) -> Explanation:
        """Generate explanation from knowledge base content (fallback)."""
        explanation = Explanation(
            concept_id=concept_id,
            concept_name=concept_name,
        )

        explanation.hook = f"Let's explore {concept_name} — a concept that shows up everywhere in mathematics and the real world."

        if defn:
            explanation.intuition = defn.intuitive
            explanation.formal = defn.formal
            explanation.examples = list(defn.examples)
            explanation.common_mistakes = list(defn.misconceptions)
            if defn.analogies:
                explanation.connections = list(defn.analogies)
        else:
            explanation.intuition = f"Let's build an intuitive understanding of {concept_name}."
            explanation.formal = f"The precise mathematical definition of {concept_name}."

        explanation.summary = f"That's {concept_name} — remember the key ideas and you'll be ready to apply it."

        return explanation
