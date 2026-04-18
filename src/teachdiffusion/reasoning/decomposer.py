"""Decomposer — breaks complex math topics into teachable sub-concepts.

Uses the concept graph for known concepts, and optionally Claude API
for topics not yet in the knowledge base.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from teachdiffusion.knowledge.concept_graph import Concept, ConceptGraph


@dataclass
class DecompositionNode:
    """A single node in a topic decomposition tree."""

    title: str
    description: str
    difficulty_relative: str  # "easier", "same", "harder"
    estimated_minutes: int = 10
    sub_nodes: list[DecompositionNode] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return len(self.sub_nodes) == 0


@dataclass
class Decomposition:
    """Complete decomposition of a topic into sub-concepts."""

    original_topic: str
    root: DecompositionNode
    total_estimated_minutes: int = 0

    def get_all_leaves(self) -> list[DecompositionNode]:
        """Get all leaf nodes (atomic teachable units)."""
        leaves = []
        self._collect_leaves(self.root, leaves)
        return leaves

    def _collect_leaves(
        self, node: DecompositionNode, leaves: list[DecompositionNode]
    ) -> None:
        if node.is_leaf:
            leaves.append(node)
        else:
            for child in node.sub_nodes:
                self._collect_leaves(child, leaves)


class Decomposer:
    """Breaks complex math topics into teachable sub-concepts.

    First checks the concept graph for known decompositions.
    Falls back to Claude API for novel or complex topics.

    Usage:
        decomposer = Decomposer(concept_graph)
        decomposition = decomposer.decompose("quadratic equations")
    """

    def __init__(self, graph: ConceptGraph) -> None:
        self._graph = graph

    def decompose(self, topic: str, max_depth: int = 3) -> Decomposition:
        """Decompose a topic into sub-concepts.

        Args:
            topic: The math topic to decompose.
            max_depth: Maximum depth of decomposition tree.

        Returns:
            Decomposition with a tree of sub-concepts.
        """
        # Try to find the concept in the graph first
        concept = self._graph.find_concept_by_name(topic)
        if concept:
            return self._decompose_from_graph(concept, max_depth)

        # Fall back to Claude API for unknown topics
        return self._decompose_with_llm(topic, max_depth)

    def _decompose_from_graph(
        self, concept: Concept, max_depth: int
    ) -> Decomposition:
        """Decompose using the knowledge graph."""
        prereqs = self._graph.get_prerequisites(concept.id)

        sub_nodes = []
        for prereq in prereqs:
            child = DecompositionNode(
                title=prereq.name,
                description=prereq.description,
                difficulty_relative="easier",
                estimated_minutes=prereq.estimated_minutes,
            )
            # Recurse one level for prerequisites of prerequisites
            if max_depth > 1:
                sub_prereqs = self._graph.get_prerequisites(prereq.id)
                child.sub_nodes = [
                    DecompositionNode(
                        title=sp.name,
                        description=sp.description,
                        difficulty_relative="easier",
                        estimated_minutes=sp.estimated_minutes,
                    )
                    for sp in sub_prereqs
                ]
            sub_nodes.append(child)

        # Add the concept itself as the final node
        root = DecompositionNode(
            title=concept.name,
            description=concept.description,
            difficulty_relative="same",
            estimated_minutes=concept.estimated_minutes,
            sub_nodes=sub_nodes,
        )

        decomp = Decomposition(
            original_topic=concept.name,
            root=root,
            total_estimated_minutes=0,
        )
        # Calculate total time from leaves
        leaves = decomp.get_all_leaves()
        decomp.total_estimated_minutes = sum(l.estimated_minutes for l in leaves)
        return decomp

    def _decompose_with_llm(self, topic: str, max_depth: int) -> Decomposition:
        """Decompose using Claude API for topics not in the graph."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            # Return a simple single-node decomposition as fallback
            root = DecompositionNode(
                title=topic,
                description=f"Teach the concept of {topic}.",
                difficulty_relative="same",
                estimated_minutes=20,
            )
            return Decomposition(
                original_topic=topic,
                root=root,
                total_estimated_minutes=20,
            )

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1500,
                system=(
                    "You are a math curriculum designer. Decompose the given topic "
                    "into 3-5 sub-concepts that should be taught in order. "
                    "Respond ONLY with valid JSON, no markdown. Format:\n"
                    '{"title": "...", "description": "...", "estimated_minutes": N, '
                    '"sub_concepts": [{"title": "...", "description": "...", '
                    '"estimated_minutes": N, "difficulty": "easier|same|harder"}]}'
                ),
                messages=[
                    {"role": "user", "content": f"Decompose: {topic}"}
                ],
            )

            text = response.content[0].text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

            sub_nodes = [
                DecompositionNode(
                    title=sc["title"],
                    description=sc["description"],
                    difficulty_relative=sc.get("difficulty", "same"),
                    estimated_minutes=sc.get("estimated_minutes", 10),
                )
                for sc in data.get("sub_concepts", [])
            ]

            root = DecompositionNode(
                title=data["title"],
                description=data["description"],
                difficulty_relative="same",
                estimated_minutes=data.get("estimated_minutes", 20),
                sub_nodes=sub_nodes,
            )

            total = sum(n.estimated_minutes for n in sub_nodes) if sub_nodes else root.estimated_minutes

            return Decomposition(
                original_topic=topic,
                root=root,
                total_estimated_minutes=total,
            )

        except Exception:
            root = DecompositionNode(
                title=topic,
                description=f"Teach the concept of {topic}.",
                difficulty_relative="same",
                estimated_minutes=20,
            )
            return Decomposition(
                original_topic=topic,
                root=root,
                total_estimated_minutes=20,
            )
