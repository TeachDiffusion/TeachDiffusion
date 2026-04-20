"""Tests for Layer 4: Student Model."""

import tempfile
import pytest
from teachdiffusion.student.student_model import StudentModel, StudentProfile
from teachdiffusion.student.misconception_detector import MisconceptionDetector
from teachdiffusion.student.progress_tracker import ProgressTracker


class TestStudentModel:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.model = StudentModel(storage_dir=self.tmpdir)

    def test_create_student(self):
        profile = self.model.get_or_create("test_student", name="Test")
        assert profile.student_id == "test_student"
        assert profile.name == "Test"

    def test_record_attempt(self):
        profile = self.model.get_or_create("s1")
        self.model.record_attempt(profile, "quadratic_equations", correct=True)
        assert profile.knowledge["quadratic_equations"].attempts == 1
        assert profile.knowledge["quadratic_equations"].correct == 1
        assert profile.knowledge["quadratic_equations"].mastery > 0

    def test_record_lesson(self):
        profile = self.model.get_or_create("s1")
        self.model.record_lesson_completed(profile, "derivatives", 15.0)
        assert profile.total_study_minutes == 15.0
        assert profile.sessions_completed == 1
        assert profile.knowledge["derivatives"].mastery > 0

    def test_persistence(self):
        profile = self.model.get_or_create("s2")
        self.model.record_attempt(profile, "limits", correct=True)
        self.model.save(profile)

        model2 = StudentModel(storage_dir=self.tmpdir)
        loaded = model2.get_or_create("s2")
        assert loaded.knowledge["limits"].attempts == 1

    def test_known_concepts(self):
        from teachdiffusion.student.student_model import ConceptKnowledge

        profile = self.model.get_or_create("s3")
        profile.knowledge["a"] = ConceptKnowledge(concept_id="a", mastery=0.8)
        profile.knowledge["b"] = ConceptKnowledge(concept_id="b", mastery=0.3)
        known = profile.known_concepts(threshold=0.5)
        assert "a" in known
        assert "b" not in known


class TestMisconceptionDetector:
    def setup_method(self):
        self.detector = MisconceptionDetector()

    def test_correct_answer(self):
        result = self.detector.analyze(
            concept_id="quadratic_equations",
            question="Solve x² - 5x + 6 = 0",
            student_answer="x = 2 or x = 3",
            correct_answer="x = 2 or x = 3",
        )
        assert result.is_correct

    def test_missing_root(self):
        result = self.detector.analyze(
            concept_id="quadratic_equations",
            question="Solve x² - 5x + 6 = 0",
            student_answer="x = 3",
            correct_answer="x = 2 or x = 3",
        )
        assert not result.is_correct
        assert "plus_minus" in result.misconception.lower() or len(result.misconception) > 0

    def test_forgot_constant(self):
        result = self.detector.analyze(
            concept_id="integrals",
            question="Integrate x²",
            student_answer="x³/3",
            correct_answer="x³/3 + C",
        )
        assert not result.is_correct


class TestProgressTracker:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tracker = ProgressTracker(storage_dir=self.tmpdir)

    def test_session_lifecycle(self):
        session = self.tracker.start_session("s1", "limits", pre_mastery=0.2)
        assert session.student_id == "s1"
        self.tracker.end_session(session, post_mastery=0.6, quiz_score=0.75)
        assert session.post_mastery == 0.6
        assert session.mastery_gain == pytest.approx(0.4)

    def test_summary(self):
        s1 = self.tracker.start_session("s1", "limits")
        self.tracker.end_session(s1, post_mastery=0.7, quiz_score=0.8)
        summary = self.tracker.get_summary("s1")
        assert summary.total_sessions == 1
        assert summary.concepts_studied == 1
