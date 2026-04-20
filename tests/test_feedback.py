"""Tests for Layer 8: Feedback & Evaluation."""

from teachdiffusion.feedback.quiz_generator import QuizGenerator, QuestionType
from teachdiffusion.feedback.evaluator import Evaluator
from teachdiffusion.feedback.learning_gain import LearningGainCalculator, GainLevel


class TestQuizGenerator:
    def test_generate_fallback(self):
        gen = QuizGenerator()
        quiz = gen.generate("quadratic_equations", num_questions=3)
        assert quiz.concept_id == "quadratic_equations"
        assert quiz.num_questions >= 1

    def test_generate_unknown_concept(self):
        gen = QuizGenerator()
        quiz = gen.generate("nonexistent_xyz", num_questions=2)
        assert quiz.num_questions >= 1


class TestEvaluator:
    def test_evaluate_correct(self):
        gen = QuizGenerator()
        quiz = gen.generate("quadratic_equations")
        evaluator = Evaluator()
        if quiz.questions:
            q = quiz.questions[0]
            result = evaluator.evaluate_answer(q, q.correct_answer)
            assert result.is_correct

    def test_evaluate_quiz(self):
        gen = QuizGenerator()
        quiz = gen.generate("quadratic_equations")
        evaluator = Evaluator()
        answers = {q.question_id: q.correct_answer for q in quiz.questions}
        result = evaluator.evaluate_quiz(quiz, answers)
        assert result.score == 1.0
        assert result.passed

    def test_evaluate_wrong_answers(self):
        gen = QuizGenerator()
        quiz = gen.generate("quadratic_equations")
        evaluator = Evaluator()
        answers = {q.question_id: "completely wrong" for q in quiz.questions}
        result = evaluator.evaluate_quiz(quiz, answers)
        assert result.score < 1.0


class TestLearningGainCalculator:
    def setup_method(self):
        self.calc = LearningGainCalculator()

    def test_high_gain(self):
        result = self.calc.compute("test", "s1", pre_score=0.2, post_score=0.9)
        assert result.gain_level == GainLevel.HIGH
        assert result.normalized_gain > 0.7

    def test_medium_gain(self):
        result = self.calc.compute("test", "s1", pre_score=0.3, post_score=0.6)
        assert result.gain_level == GainLevel.MEDIUM

    def test_low_gain(self):
        result = self.calc.compute("test", "s1", pre_score=0.5, post_score=0.55)
        assert result.gain_level == GainLevel.LOW

    def test_negative_gain(self):
        result = self.calc.compute("test", "s1", pre_score=0.8, post_score=0.5)
        assert result.gain_level == GainLevel.NEGATIVE

    def test_perfect_pre_score(self):
        result = self.calc.compute("test", "s1", pre_score=1.0, post_score=1.0)
        assert result.gain_level == GainLevel.NOT_APPLICABLE

    def test_class_average(self):
        results = [
            self.calc.compute("t", "s1", 0.2, 0.8),
            self.calc.compute("t", "s2", 0.3, 0.7),
        ]
        avg = self.calc.compute_class_average(results)
        assert 0.0 < avg < 1.0
