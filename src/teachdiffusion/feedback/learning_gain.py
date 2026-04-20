"""Learning Gain — measures how much a student actually learned.

Uses Hake's normalized gain (g) — the standard physics/math education
metric for measuring learning effectiveness:

    g = (post_score - pre_score) / (1.0 - pre_score)

Where:
- g >= 0.7 → High gain (excellent teaching)
- 0.3 <= g < 0.7 → Medium gain (good teaching)
- g < 0.3 → Low gain (teaching needs improvement)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GainLevel(str, Enum):
    """Classification of learning gain."""

    HIGH = "high"  # g >= 0.7
    MEDIUM = "medium"  # 0.3 <= g < 0.7
    LOW = "low"  # g < 0.3
    NEGATIVE = "negative"  # g < 0 (student got worse)
    NOT_APPLICABLE = "not_applicable"  # Can't compute (perfect pre-score)


@dataclass
class LearningGainResult:
    """Result of a learning gain measurement."""

    concept_id: str
    student_id: str
    pre_score: float  # 0.0 to 1.0
    post_score: float  # 0.0 to 1.0
    normalized_gain: float  # Hake's g
    gain_level: GainLevel
    interpretation: str


class LearningGainCalculator:
    """Measures learning gain using Hake's normalized gain.

    Usage:
        calc = LearningGainCalculator()
        result = calc.compute(
            concept_id="quadratic_equations",
            student_id="student_01",
            pre_score=0.3,
            post_score=0.8
        )
        print(result.interpretation)
    """

    def compute(
        self,
        concept_id: str,
        student_id: str,
        pre_score: float,
        post_score: float,
    ) -> LearningGainResult:
        """Compute Hake's normalized learning gain.

        Args:
            concept_id: The concept being measured.
            student_id: The student.
            pre_score: Score before learning (0.0 to 1.0).
            post_score: Score after learning (0.0 to 1.0).

        Returns:
            LearningGainResult with gain score and interpretation.
        """
        pre_score = max(0.0, min(1.0, pre_score))
        post_score = max(0.0, min(1.0, post_score))

        if pre_score >= 1.0:
            return LearningGainResult(
                concept_id=concept_id,
                student_id=student_id,
                pre_score=pre_score,
                post_score=post_score,
                normalized_gain=0.0,
                gain_level=GainLevel.NOT_APPLICABLE,
                interpretation=(
                    "Pre-test score was already perfect. "
                    "Cannot compute normalized gain."
                ),
            )

        # Hake's g
        g = (post_score - pre_score) / (1.0 - pre_score)

        # Classify
        if g < 0:
            level = GainLevel.NEGATIVE
            interpretation = (
                f"Negative gain (g = {g:.2f}). The student scored lower after learning. "
                f"This may indicate confusion introduced during the lesson, "
                f"or the post-test was harder than the pre-test."
            )
        elif g < 0.3:
            level = GainLevel.LOW
            interpretation = (
                f"Low gain (g = {g:.2f}). Some learning occurred but below typical benchmarks. "
                f"Consider adjusting pacing, adding more examples, or revisiting prerequisites."
            )
        elif g < 0.7:
            level = GainLevel.MEDIUM
            interpretation = (
                f"Medium gain (g = {g:.2f}). Solid learning — typical of well-designed instruction. "
                f"The student improved meaningfully from {pre_score:.0%} to {post_score:.0%}."
            )
        else:
            level = GainLevel.HIGH
            interpretation = (
                f"High gain (g = {g:.2f}). Excellent learning outcome. "
                f"The student improved from {pre_score:.0%} to {post_score:.0%}, "
                f"capturing {g:.0%} of the possible improvement."
            )

        return LearningGainResult(
            concept_id=concept_id,
            student_id=student_id,
            pre_score=pre_score,
            post_score=post_score,
            normalized_gain=round(g, 3),
            gain_level=level,
            interpretation=interpretation,
        )

    def compute_class_average(
        self,
        results: list[LearningGainResult],
    ) -> float:
        """Compute average normalized gain across multiple students.

        Args:
            results: List of individual LearningGainResults.

        Returns:
            Average Hake's g across all students.
        """
        valid = [
            r.normalized_gain
            for r in results
            if r.gain_level != GainLevel.NOT_APPLICABLE
        ]
        if not valid:
            return 0.0
        return sum(valid) / len(valid)
