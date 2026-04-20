"""Tests for the Pipeline Orchestrator."""

import tempfile
from teachdiffusion.pipeline.orchestrator import TeachDiffusionPipeline


class TestTeachDiffusionPipeline:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.pipeline = TeachDiffusionPipeline(output_dir=self.tmpdir)

    def test_init(self):
        assert self.pipeline.graph.num_concepts >= 34
        assert len(self.pipeline.definitions.all_ids()) >= 5

    def test_generate_lesson(self):
        result = self.pipeline.generate_lesson("quadratic equations")
        assert result.topic == "quadratic equations"
        assert result.script.num_steps >= 3
        assert len(result.video_clips) >= 3
        assert result.composite is not None

    def test_generate_lesson_with_student(self):
        result = self.pipeline.generate_lesson(
            topic="derivatives", student_id="test_s1"
        )
        assert result.script.num_steps >= 3
        profile = self.pipeline.student_model.get_or_create("test_s1")
        assert profile.sessions_completed >= 1

    def test_get_concept_info(self):
        info = self.pipeline.get_concept_info("eigenvalues")
        assert info["name"] == "Eigenvalues & Eigenvectors"
        assert len(info["prerequisites"]) > 0

    def test_get_concept_info_not_found(self):
        info = self.pipeline.get_concept_info("nonexistent_xyz")
        assert "error" in info

    def test_generate_quiz(self):
        quiz = self.pipeline.generate_quiz("quadratic_equations", num_questions=3)
        assert quiz.num_questions >= 1

    def test_evaluate_quiz(self):
        quiz = self.pipeline.generate_quiz("quadratic_equations")
        answers = {q.question_id: q.correct_answer for q in quiz.questions}
        result = self.pipeline.evaluate_quiz(quiz, answers, student_id="test_s2")
        assert result.score == 1.0

    def test_get_student_info(self):
        self.pipeline.generate_lesson("limits", student_id="test_s3")
        info = self.pipeline.get_student_info("test_s3")
        assert info["sessions_completed"] >= 1
