"""Quiz Generator — auto-generates adaptive quizzes for math concepts.

Generates questions that target common misconceptions and adapt
to the student's current knowledge level.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum


class QuestionType(str, Enum):
    """Types of quiz questions."""

    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"


@dataclass
class QuizQuestion:
    """A single quiz question."""

    question_id: str
    concept_id: str
    question_type: QuestionType
    question_text: str
    correct_answer: str
    options: list[str] = field(default_factory=list)  # For multiple choice
    explanation: str = ""
    difficulty: str = "intermediate"
    targets_misconception: str = ""  # Which misconception this question tests


@dataclass
class Quiz:
    """A complete quiz for a concept."""

    concept_id: str
    title: str
    questions: list[QuizQuestion] = field(default_factory=list)
    difficulty: str = "intermediate"

    @property
    def num_questions(self) -> int:
        return len(self.questions)


class QuizGenerator:
    """Generates adaptive quizzes for math concepts.

    Usage:
        gen = QuizGenerator()
        quiz = gen.generate("quadratic_equations", num_questions=5)
    """

    def generate(
        self,
        concept_id: str,
        num_questions: int = 5,
        difficulty: str = "intermediate",
        target_misconceptions: list[str] | None = None,
    ) -> Quiz:
        """Generate a quiz for a concept.

        Args:
            concept_id: The concept to quiz on.
            num_questions: Number of questions to generate.
            difficulty: Difficulty level.
            target_misconceptions: Specific misconceptions to test.

        Returns:
            A Quiz with the requested number of questions.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                return self._generate_with_llm(
                    concept_id, num_questions, difficulty, target_misconceptions, api_key
                )
            except Exception:
                pass

        return self._generate_fallback(concept_id, num_questions, difficulty)

    def _generate_with_llm(
        self,
        concept_id: str,
        num_questions: int,
        difficulty: str,
        target_misconceptions: list[str] | None,
        api_key: str,
    ) -> Quiz:
        """Generate quiz using Claude API."""
        import anthropic

        misconception_context = ""
        if target_misconceptions:
            misconception_context = (
                f"\nTarget these specific misconceptions: "
                f"{', '.join(target_misconceptions)}"
            )

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=(
                "Generate math quiz questions. Include wrong options that reflect "
                "common misconceptions. Respond ONLY with valid JSON:\n"
                '{"questions": [{"question_type": "multiple_choice|short_answer|true_false", '
                '"question_text": "...", "correct_answer": "...", '
                '"options": ["A", "B", "C", "D"], '
                '"explanation": "...", "targets_misconception": "..."}]}'
            ),
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Generate {num_questions} {difficulty} questions for: {concept_id}"
                        f"{misconception_context}"
                    ),
                }
            ],
        )

        text = response.content[0].text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text)

        questions = []
        for i, q in enumerate(data.get("questions", [])[:num_questions]):
            questions.append(QuizQuestion(
                question_id=f"{concept_id}_q{i + 1}",
                concept_id=concept_id,
                question_type=QuestionType(q.get("question_type", "multiple_choice")),
                question_text=q["question_text"],
                correct_answer=q["correct_answer"],
                options=q.get("options", []),
                explanation=q.get("explanation", ""),
                difficulty=difficulty,
                targets_misconception=q.get("targets_misconception", ""),
            ))

        return Quiz(
            concept_id=concept_id,
            title=f"Quiz: {concept_id.replace('_', ' ').title()}",
            questions=questions,
            difficulty=difficulty,
        )

    def _generate_fallback(
        self, concept_id: str, num_questions: int, difficulty: str
    ) -> Quiz:
        """Generate basic quiz questions without API."""
        templates = {
            "quadratic_equations": [
                QuizQuestion(
                    question_id="qe_q1", concept_id="quadratic_equations",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    question_text="Solve x² - 5x + 6 = 0",
                    correct_answer="x = 2 or x = 3",
                    options=["x = 2 or x = 3", "x = -2 or x = -3", "x = 1 or x = 6", "x = 3 only"],
                    explanation="Factor: (x-2)(x-3) = 0, so x = 2 or x = 3.",
                    targets_misconception="forgot_plus_minus",
                ),
                QuizQuestion(
                    question_id="qe_q2", concept_id="quadratic_equations",
                    question_type=QuestionType.TRUE_FALSE,
                    question_text="Every quadratic equation has exactly two real solutions.",
                    correct_answer="False",
                    explanation="Some quadratics have one repeated root or no real roots (discriminant ≤ 0).",
                    targets_misconception="always_two_roots",
                ),
                QuizQuestion(
                    question_id="qe_q3", concept_id="quadratic_equations",
                    question_type=QuestionType.SHORT_ANSWER,
                    question_text="What is the discriminant of 2x² + 3x - 5 = 0?",
                    correct_answer="49",
                    explanation="b² - 4ac = 9 - 4(2)(-5) = 9 + 40 = 49.",
                    targets_misconception="wrong_discriminant",
                ),
            ],
            "derivatives": [
                QuizQuestion(
                    question_id="d_q1", concept_id="derivatives",
                    question_type=QuestionType.SHORT_ANSWER,
                    question_text="What is the derivative of f(x) = x³ + 2x?",
                    correct_answer="3x² + 2",
                    explanation="Power rule: d/dx(x³) = 3x², d/dx(2x) = 2.",
                ),
                QuizQuestion(
                    question_id="d_q2", concept_id="derivatives",
                    question_type=QuestionType.MULTIPLE_CHOICE,
                    question_text="The derivative represents:",
                    correct_answer="The instantaneous rate of change",
                    options=[
                        "The instantaneous rate of change",
                        "The area under the curve",
                        "The average value of the function",
                        "The y-intercept",
                    ],
                ),
            ],
        }

        questions = templates.get(concept_id, [
            QuizQuestion(
                question_id=f"{concept_id}_q1", concept_id=concept_id,
                question_type=QuestionType.SHORT_ANSWER,
                question_text=f"Explain the key idea behind {concept_id.replace('_', ' ')}.",
                correct_answer="See textbook definition.",
                explanation="Review the concept and its core definition.",
            ),
        ])

        return Quiz(
            concept_id=concept_id,
            title=f"Quiz: {concept_id.replace('_', ' ').title()}",
            questions=questions[:num_questions],
            difficulty=difficulty,
        )
