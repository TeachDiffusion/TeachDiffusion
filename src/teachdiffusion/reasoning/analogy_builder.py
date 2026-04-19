"""Analogy Builder — generates real-world analogies for math concepts.

Good analogies bridge the gap between abstract math and things students
already understand. This module pulls from curated analogies in the
definition store and generates new ones via Claude API.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore


@dataclass
class Analogy:
    """A real-world analogy for a math concept."""

    concept_id: str
    analogy: str
    why_it_works: str
    limitations: str = ""


class AnalogyBuilder:
    """Generates and retrieves analogies for math concepts.

    Usage:
        builder = AnalogyBuilder(graph, definition_store)
        analogies = builder.get_analogies("eigenvalues")
    """

    def __init__(
        self, graph: ConceptGraph, definitions: DefinitionStore
    ) -> None:
        self._graph = graph
        self._definitions = definitions

    def get_analogies(
        self, concept_id: str, count: int = 2
    ) -> list[Analogy]:
        """Get analogies for a concept.

        First pulls from the definition store, then generates new ones if needed.

        Args:
            concept_id: The concept to get analogies for.
            count: Target number of analogies.

        Returns:
            List of Analogy objects.
        """
        analogies = []

        # Pull curated analogies from definition store
        defn = self._definitions.get(concept_id)
        if defn and defn.analogies:
            for text in defn.analogies[:count]:
                analogies.append(
                    Analogy(
                        concept_id=concept_id,
                        analogy=text,
                        why_it_works="Curated analogy from knowledge base.",
                    )
                )

        # If we need more, try to generate via Claude
        if len(analogies) < count:
            concept = self._graph.get_concept(concept_id)
            if concept:
                generated = self._generate_analogies(
                    concept.name, concept.description, count - len(analogies)
                )
                analogies.extend(generated)

        return analogies[:count]

    def _generate_analogies(
        self, concept_name: str, description: str, count: int
    ) -> list[Analogy]:
        """Generate analogies using Claude API."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return [
                Analogy(
                    concept_id="",
                    analogy=f"Think of {concept_name} as a pattern you see in everyday life.",
                    why_it_works="Fallback analogy — set ANTHROPIC_API_KEY for better results.",
                )
            ]

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=(
                    "You generate intuitive real-world analogies for math concepts. "
                    "Each analogy should connect the math to something a teenager would know. "
                    "Respond ONLY with valid JSON, no markdown. Format:\n"
                    '[{"analogy": "...", "why_it_works": "...", "limitations": "..."}]'
                ),
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Generate {count} analogy(s) for: {concept_name}\n"
                            f"Description: {description}"
                        ),
                    }
                ],
            )

            text = response.content[0].text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

            return [
                Analogy(
                    concept_id="",
                    analogy=item["analogy"],
                    why_it_works=item.get("why_it_works", ""),
                    limitations=item.get("limitations", ""),
                )
                for item in data[:count]
            ]

        except Exception:
            return [
                Analogy(
                    concept_id="",
                    analogy=f"Think of {concept_name} as a pattern in everyday life.",
                    why_it_works="Fallback — Claude API call failed.",
                )
            ]
