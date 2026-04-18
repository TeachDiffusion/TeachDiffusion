"""Inference Engine — reasons about student knowledge gaps and concept readiness.

Given what a student knows and what they want to learn, the inference engine
determines: what's missing, what's ready to learn, and the optimal sequence.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from teachdiffusion.knowledge.concept_graph import Concept, ConceptGraph


@dataclass
class KnowledgeGap:
    """A gap in a student's knowledge."""

    concept: Concept
    importance: float  # 0-1, how critical this gap is
    reason: str  # why this gap matters


@dataclass
class ReadinessAssessment:
    """Assessment of whether a student is ready to learn a concept."""

    concept: Concept
    is_ready: bool
    readiness_score: float  # 0-1
    missing_prerequisites: list[Concept] = field(default_factory=list)
    recommendation: str = ""


class InferenceEngine:
    """Reasons about student knowledge and determines learning readiness.

    Usage:
        engine = InferenceEngine(concept_graph)
        gaps = engine.find_knowledge_gaps(
            known={"arithmetic_basics", "fractions"},
            target="quadratic_equations"
        )
        readiness = engine.assess_readiness(
            known={"arithmetic_basics", "fractions"},
            target="quadratic_equations"
        )
    """

    def __init__(self, graph: ConceptGraph) -> None:
        self._graph = graph

    def find_knowledge_gaps(
        self, known: set[str], target: str
    ) -> list[KnowledgeGap]:
        """Find all knowledge gaps between what a student knows and what they need.

        Args:
            known: Set of concept IDs the student already knows.
            target: The concept ID the student wants to learn.

        Returns:
            List of KnowledgeGap objects, sorted by importance (most important first).
        """
        all_prereqs = self._graph.get_all_prerequisites(target)
        gaps = []

        for prereq in all_prereqs:
            if prereq.id not in known:
                # Calculate importance based on how many downstream concepts depend on it
                dependents = self._graph.get_dependents(prereq.id)
                # Check how many of the target's prerequisites depend on this
                target_prereq_ids = {p.id for p in all_prereqs}
                relevant_deps = [
                    d for d in dependents if d.id in target_prereq_ids or d.id == target
                ]
                importance = min(1.0, len(relevant_deps) / max(len(all_prereqs), 1))

                gaps.append(
                    KnowledgeGap(
                        concept=prereq,
                        importance=importance,
                        reason=(
                            f"Required before learning {target}. "
                            f"{len(relevant_deps)} concept(s) in the path depend on this."
                        ),
                    )
                )

        # Sort by importance, then difficulty (easier first)
        gaps.sort(key=lambda g: (-g.importance, g.concept.difficulty.value))
        return gaps

    def assess_readiness(
        self, known: set[str], target: str
    ) -> ReadinessAssessment:
        """Assess if a student is ready to learn a specific concept.

        Args:
            known: Set of concept IDs the student knows.
            target: The concept ID to assess readiness for.

        Returns:
            ReadinessAssessment with score, missing prereqs, and recommendation.
        """
        concept = self._graph.get_concept(target)
        if concept is None:
            return ReadinessAssessment(
                concept=Concept(
                    id=target, name=target, domain="algebra",
                    difficulty="intermediate", description="Unknown concept"
                ),
                is_ready=False,
                readiness_score=0.0,
                recommendation=f"Concept '{target}' not found in knowledge base.",
            )

        direct_prereqs = self._graph.get_prerequisites(target)
        missing = [p for p in direct_prereqs if p.id not in known]

        if not direct_prereqs:
            score = 1.0
        else:
            score = 1.0 - (len(missing) / len(direct_prereqs))

        is_ready = len(missing) == 0

        if is_ready:
            recommendation = f"Ready to learn {concept.name}. All prerequisites are met."
        elif score >= 0.5:
            missing_names = ", ".join(m.name for m in missing)
            recommendation = (
                f"Almost ready for {concept.name}. "
                f"Review {missing_names} first for the best experience."
            )
        else:
            missing_names = ", ".join(m.name for m in missing)
            recommendation = (
                f"Not yet ready for {concept.name}. "
                f"Need to learn: {missing_names}."
            )

        return ReadinessAssessment(
            concept=concept,
            is_ready=is_ready,
            readiness_score=score,
            missing_prerequisites=missing,
            recommendation=recommendation,
        )

    def suggest_learning_sequence(
        self, known: set[str], target: str
    ) -> list[Concept]:
        """Suggest the optimal sequence of concepts to learn to reach the target.

        Returns concepts in the order they should be learned, skipping
        any the student already knows.
        """
        all_prereqs = self._graph.get_all_prerequisites(target)
        target_concept = self._graph.get_concept(target)
        to_learn = [p for p in all_prereqs if p.id not in known]
        if target_concept and target not in known:
            to_learn.append(target_concept)
        return to_learn

    def estimate_study_time(self, known: set[str], target: str) -> int:
        """Estimate total minutes needed to reach a target concept.

        Returns estimated minutes based on concept estimated_minutes values.
        """
        sequence = self.suggest_learning_sequence(known, target)
        return sum(c.estimated_minutes for c in sequence)
