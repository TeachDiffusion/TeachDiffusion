"""Evaluator — scores student responses to quiz questions.

Provides both automated scoring and detailed feedback on each answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from teachdiffusion.feedback.quiz_generator import Quiz, QuizQuestion
from teachdiffusion.student.misconception_detector import MisconceptionDetector, MisconceptionResult


@dataclass
class AnswerResult:
    """Result of evaluating a single answer."""

    question_id: str
    is_correct: bool
    student_answer: str
    correct_answer: str
    feedback: str = ""
    misconception: str = ""


@dataclass
class QuizResult:
    """Result of evaluating a complete quiz."""

    concept_id: str
    total_questions: int
    correct_count: int
    score: float  # 0.0 to 1.0
    answers: list[AnswerResult] = field(default_factory=list)
    misconceptions_detected: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Whether the student passed (≥70%)."""
        return self.score >= 0.7


class Evaluator:
    """Evaluates student quiz responses.

    Usage:
        evaluator = Evaluator()
        result = evaluator.evaluate_quiz(
            quiz=quiz,
            answers={"qe_q1": "x = 2 or x = 3", "qe_q2": "True"}
        )
        print(f"Score: {result.score:.0%}")
    """

    def __init__(self) -> None:
        self._detector = MisconceptionDetector()

    def evaluate_answer(
        self, question: QuizQuestion, student_answer: str
    ) -> AnswerResult:
        """Evaluate a single answer.

        Args:
            question: The question asked.
            student_answer: The student's answer.

        Returns:
            AnswerResult with correctness and feedback.
        """
        # Normalize answers for comparison
        is_correct = self._check_correct(student_answer, question.correct_answer)

        misconception = ""
        feedback = ""

        if is_correct:
            feedback = "Correct! " + question.explanation
        else:
            # Try to detect the specific misconception
            result = self._detector.analyze(
                concept_id=question.concept_id,
                question=question.question_text,
                student_answer=student_answer,
                correct_answer=question.correct_answer,
            )
            misconception = result.misconception
            feedback = (
                f"Not quite. {result.explanation} "
                f"The correct answer is: {question.correct_answer}. "
                f"{question.explanation}"
            )

        return AnswerResult(
            question_id=question.question_id,
            is_correct=is_correct,
            student_answer=student_answer,
            correct_answer=question.correct_answer,
            feedback=feedback,
            misconception=misconception,
        )

    def evaluate_quiz(
        self, quiz: Quiz, answers: dict[str, str]
    ) -> QuizResult:
        """Evaluate all answers for a quiz.

        Args:
            quiz: The quiz that was taken.
            answers: Dict of question_id → student answer.

        Returns:
            QuizResult with overall score and per-question results.
        """
        results = []
        correct_count = 0
        misconceptions = []

        for question in quiz.questions:
            student_answer = answers.get(question.question_id, "")
            result = self.evaluate_answer(question, student_answer)
            results.append(result)

            if result.is_correct:
                correct_count += 1
            elif result.misconception:
                misconceptions.append(result.misconception)

        total = len(quiz.questions)
        score = correct_count / total if total > 0 else 0.0

        return QuizResult(
            concept_id=quiz.concept_id,
            total_questions=total,
            correct_count=correct_count,
            score=score,
            answers=results,
            misconceptions_detected=misconceptions,
        )

    def _check_correct(self, student: str, correct: str) -> bool:
        """Check if student answer matches correct answer."""
        s = student.strip().lower().replace(" ", "")
        c = correct.strip().lower().replace(" ", "")

        if s == c:
            return True

        # Handle true/false variations
        true_values = {"true", "t", "yes", "correct"}
        false_values = {"false", "f", "no", "incorrect"}
        if s in true_values and c in true_values:
            return True
        if s in false_values and c in false_values:
            return True

        return False
