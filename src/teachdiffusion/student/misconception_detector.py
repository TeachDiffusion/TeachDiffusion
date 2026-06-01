"""Misconception Detector — analyzes student responses to identify specific misconceptions.

Uses pattern matching for common errors and Claude API for deeper analysis.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass


@dataclass
class MisconceptionResult:
    """Result of analyzing a student's answer for misconceptions."""

    is_correct: bool
    student_answer: str
    correct_answer: str
    misconception: str = ""  # Empty if correct
    explanation: str = ""  # Why the misconception is wrong
    remediation: str = ""  # What to review to fix it
    confidence: float = 1.0  # How confident we are in the analysis


# Common misconception patterns — checked before calling the API
COMMON_PATTERNS: dict[str, list[dict]] = {
    "quadratic_equations": [
        {
            "pattern": "forgot_plus_minus",
            "description": "Forgetting ± in the quadratic formula, giving only one root",
            "remediation": "Remember: the ± means there are TWO solutions. Always check both.",
        },
        {
            "pattern": "wrong_discriminant",
            "description": "Computing b² - 4ac incorrectly",
            "remediation": "Carefully identify a, b, c first. Then compute b² - 4ac step by step.",
        },
    ],
    "derivatives": [
        {
            "pattern": "power_rule_everywhere",
            "description": "Applying the power rule to non-polynomial functions",
            "remediation": "The power rule only works for x^n. For sin, cos, e^x, etc., use their specific rules.",
        },
        {
            "pattern": "forgot_chain_rule",
            "description": "Differentiating composite functions without the chain rule",
            "remediation": "When a function is inside another function, multiply by the derivative of the inner function.",
        },
    ],
    "integrals": [
        {
            "pattern": "forgot_constant",
            "description": "Forgetting +C in indefinite integrals",
            "remediation": "Every indefinite integral has +C because differentiation loses constant information.",
        },
    ],
    "matrices": [
        {
            "pattern": "commutative_multiplication",
            "description": "Assuming AB = BA for matrices",
            "remediation": "Matrix multiplication is NOT commutative. AB ≠ BA in general. Always check the order.",
        },
    ],
}


class MisconceptionDetector:
    """Detects misconceptions in student answers.

    Usage:
        detector = MisconceptionDetector()
        result = detector.analyze(
            concept_id="quadratic_equations",
            question="Solve x² - 5x + 6 = 0",
            student_answer="x = 3",
            correct_answer="x = 2 or x = 3"
        )
    """

    def analyze(
        self,
        concept_id: str,
        question: str,
        student_answer: str,
        correct_answer: str,
    ) -> MisconceptionResult:
        """Analyze a student's answer for misconceptions.

        Args:
            concept_id: The concept being tested.
            question: The question asked.
            student_answer: What the student answered.
            correct_answer: The correct answer.

        Returns:
            MisconceptionResult with analysis.
        """
        # Quick check: is it correct?
        if self._answers_match(student_answer, correct_answer):
            return MisconceptionResult(
                is_correct=True,
                student_answer=student_answer,
                correct_answer=correct_answer,
            )

        # Try pattern-based detection first
        pattern_result = self._check_patterns(
            concept_id, question, student_answer, correct_answer
        )
        if pattern_result:
            return pattern_result

        # Fall back to Claude API for deeper analysis
        return self._analyze_with_llm(
            concept_id, question, student_answer, correct_answer
        )

    def _answers_match(self, student: str, correct: str) -> bool:
        """Simple check if answers match (normalized)."""
        s = student.strip().lower().replace(" ", "")
        c = correct.strip().lower().replace(" ", "")
        return s == c

    def _check_patterns(
        self,
        concept_id: str,
        question: str,
        student_answer: str,
        correct_answer: str,
    ) -> MisconceptionResult | None:
        """Check against known misconception patterns."""
        patterns = COMMON_PATTERNS.get(concept_id, [])

        for pattern in patterns:
            # Simple heuristic checks
            if pattern["pattern"] == "forgot_plus_minus":
                # Student gave one root but correct has two
                if "or" in correct_answer.lower() and "or" not in student_answer.lower():
                    return MisconceptionResult(
                        is_correct=False,
                        student_answer=student_answer,
                        correct_answer=correct_answer,
                        misconception=pattern["description"],
                        explanation="You found one solution but missed the other.",
                        remediation=pattern["remediation"],
                        confidence=0.8,
                    )

            if pattern["pattern"] == "forgot_constant":
                if "+c" not in student_answer.lower() and "+c" in correct_answer.lower():
                    return MisconceptionResult(
                        is_correct=False,
                        student_answer=student_answer,
                        correct_answer=correct_answer,
                        misconception=pattern["description"],
                        explanation="You forgot the constant of integration.",
                        remediation=pattern["remediation"],
                        confidence=0.9,
                    )

        return None

    def _analyze_with_llm(
        self,
        concept_id: str,
        question: str,
        student_answer: str,
        correct_answer: str,
    ) -> MisconceptionResult:
        """Use Claude API for deep misconception analysis."""
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return MisconceptionResult(
                is_correct=False,
                student_answer=student_answer,
                correct_answer=correct_answer,
                misconception="Unknown error",
                explanation="The answer is incorrect.",
                remediation=f"Review the concept of {concept_id}.",
                confidence=0.3,
            )

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=(
                    "You are a math tutor analyzing a student's wrong answer. "
                    "Identify the specific misconception. "
                    "Respond ONLY with valid JSON, no markdown:\n"
                    '{"misconception": "...", "explanation": "...", "remediation": "..."}'
                ),
                messages=[
                    {
                        "role": "user",
                        "content": (
                            f"Concept: {concept_id}\n"
                            f"Question: {question}\n"
                            f"Student answered: {student_answer}\n"
                            f"Correct answer: {correct_answer}\n"
                            f"What specific misconception led to this error?"
                        ),
                    }
                ],
            )

            text = response.content[0].text.strip()
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

            return MisconceptionResult(
                is_correct=False,
                student_answer=student_answer,
                correct_answer=correct_answer,
                misconception=data.get("misconception", "Unknown"),
                explanation=data.get("explanation", ""),
                remediation=data.get("remediation", ""),
                confidence=0.85,
            )

        except Exception:
            return MisconceptionResult(
                is_correct=False,
                student_answer=student_answer,
                correct_answer=correct_answer,
                misconception="Analysis unavailable",
                explanation="The answer is incorrect.",
                remediation=f"Review {concept_id} and try again.",
                confidence=0.2,
            )
