"""Difficulty Estimator — estimates and adjusts concept difficulty for students.

Takes into account: the concept's inherent difficulty, the student's
knowledge state, and prerequisite coverage.
"""

from __future__ import annotations

from dataclasses import dataclass

from teachdiffusion.knowledge.concept_graph import ConceptGraph, DifficultyLevel


DIFFICULTY_SCORES = {
    DifficultyLevel.ELEMENTARY: 1.0,
    DifficultyLevel.INTERMEDIATE: 2.0,
    DifficultyLevel.ADVANCED: 3.0,
    DifficultyLevel.EXPERT: 4.0,
}


@dataclass
class DifficultyEstimate:
    """Estimated difficulty of a concept for a specific student."""

    concept_id: str
    base_difficulty: float  # 1-4 scale
    adjusted_difficulty: float  # Adjusted for student knowledge
    prerequisite_coverage: float  # 0-1, fraction of prereqs known
    recommendation: str  # Human-readable recommendation


class DifficultyEstimator:
    """Estimates concept difficulty adjusted for a student's knowledge.

    Usage:
        estimator = DifficultyEstimator(graph)
        estimate = estimator.estimate("eigenvalues", known={"matrices", "determinants"})
    """

    def __init__(self, graph: ConceptGraph) -> None:
        self._graph = graph

    def estimate(
        self, concept_id: str, known: set[str] | None = None
    ) -> DifficultyEstimate:
        """Estimate difficulty of a concept for a student.

        Args:
            concept_id: The concept to estimate difficulty for.
            known: Set of concept IDs the student already knows.

        Returns:
            DifficultyEstimate with base and adjusted scores.
        """
        known = known or set()
        concept = self._graph.get_concept(concept_id)

        if concept is None:
            return DifficultyEstimate(
                concept_id=concept_id,
                base_difficulty=2.0,
                adjusted_difficulty=2.0,
                prerequisite_coverage=0.0,
                recommendation=f"Unknown concept: {concept_id}",
            )

        base = DIFFICULTY_SCORES.get(concept.difficulty, 2.0)

        # Calculate prerequisite coverage
        prereqs = self._graph.get_prerequisites(concept_id)
        if prereqs:
            covered = sum(1 for p in prereqs if p.id in known)
            coverage = covered / len(prereqs)
        else:
            coverage = 1.0

        # Adjust difficulty based on prerequisite coverage
        # Missing prerequisites makes a concept harder
        if coverage >= 1.0:
            adjusted = base
        elif coverage >= 0.5:
            adjusted = base + 0.5
        else:
            adjusted = base + 1.5

        adjusted = min(adjusted, 5.0)

        # Generate recommendation
        if coverage >= 1.0:
            recommendation = f"Ready to learn {concept.name}."
        elif coverage >= 0.5:
            missing_names = [p.name for p in prereqs if p.id not in known]
            recommendation = (
                f"Mostly ready for {concept.name}. "
                f"Review {', '.join(missing_names)} for best results."
            )
        else:
            missing_names = [p.name for p in prereqs if p.id not in known]
            recommendation = (
                f"{concept.name} will be challenging. "
                f"First learn: {', '.join(missing_names)}."
            )

        return DifficultyEstimate(
            concept_id=concept_id,
            base_difficulty=base,
            adjusted_difficulty=adjusted,
            prerequisite_coverage=coverage,
            recommendation=recommendation,
        )

    def rank_by_difficulty(
        self, concept_ids: list[str], known: set[str] | None = None
    ) -> list[DifficultyEstimate]:
        """Rank multiple concepts by adjusted difficulty (easiest first).

        Args:
            concept_ids: List of concept IDs to rank.
            known: Set of concept IDs the student knows.

        Returns:
            List of DifficultyEstimate sorted from easiest to hardest.
        """
        estimates = [self.estimate(cid, known) for cid in concept_ids]
        estimates.sort(key=lambda e: e.adjusted_difficulty)
        return estimates
