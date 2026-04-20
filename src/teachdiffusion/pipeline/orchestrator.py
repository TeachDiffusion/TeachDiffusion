"""Orchestrator — connects all 8 layers of TeachDiffusion end-to-end.

This is the main pipeline. Topic in → teaching video out.

Flow:
    User Input → Knowledge Base → Reasoning Engine → Pedagogical Planner
    → Student Model → Explanation Generator → Visualization Engine
    → Video Diffusion → Feedback & Evaluation → Update Student Model
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from teachdiffusion.knowledge.concept_graph import ConceptGraph
from teachdiffusion.knowledge.definition_store import DefinitionStore
from teachdiffusion.knowledge.proof_store import ProofStore
from teachdiffusion.reasoning.inference_engine import InferenceEngine
from teachdiffusion.reasoning.decomposer import Decomposer
from teachdiffusion.reasoning.analogy_builder import AnalogyBuilder
from teachdiffusion.pedagogy.planner import PedagogicalPlanner
from teachdiffusion.pedagogy.schema import TeachingScript
from teachdiffusion.pedagogy.difficulty import DifficultyEstimator
from teachdiffusion.student.student_model import StudentModel, StudentProfile
from teachdiffusion.student.misconception_detector import MisconceptionDetector
from teachdiffusion.student.progress_tracker import ProgressTracker
from teachdiffusion.explanation.generator import ExplanationGenerator, Explanation
from teachdiffusion.visualization.manim_renderer import ManimRenderer
from teachdiffusion.video.generator import VideoGenerator, GeneratedClip
from teachdiffusion.video.voice_engine import VoiceEngine, AudioClip
from teachdiffusion.video.compositor import Compositor, CompositeResult
from teachdiffusion.feedback.quiz_generator import QuizGenerator, Quiz
from teachdiffusion.feedback.evaluator import Evaluator, QuizResult
from teachdiffusion.feedback.learning_gain import LearningGainCalculator


@dataclass
class LessonResult:
    """Complete result of generating a teaching lesson."""

    topic: str
    concept_id: str
    script: TeachingScript
    explanation: Explanation
    video_clips: list[GeneratedClip] = field(default_factory=list)
    audio_clips: list[AudioClip] = field(default_factory=list)
    animation_paths: list[str] = field(default_factory=list)
    composite: Optional[CompositeResult] = None
    quiz: Optional[Quiz] = None
    is_stub: bool = True


class TeachDiffusionPipeline:
    """Main pipeline — topic in, teaching video out.

    Usage:
        pipeline = TeachDiffusionPipeline()
        result = pipeline.generate_lesson("quadratic equations")
        print(f"Video: {result.composite.output_path}")

        # With student adaptation
        result = pipeline.generate_lesson(
            topic="derivatives",
            student_id="student_01"
        )

        # Generate a quiz
        quiz_result = pipeline.run_quiz("quadratic_equations", student_id="student_01")
    """

    def __init__(self, output_dir: str = "./outputs") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

        # Layer 1: Knowledge Base
        self.graph = ConceptGraph()
        self.graph.load_default()
        self.definitions = DefinitionStore()
        self.definitions.load_defaults()
        self.proofs = ProofStore()
        self.proofs.load_defaults()

        # Layer 2: Reasoning Engine
        self.inference = InferenceEngine(self.graph)
        self.decomposer = Decomposer(self.graph)
        self.analogy_builder = AnalogyBuilder(self.graph, self.definitions)

        # Layer 3: Pedagogical Planner
        self.planner = PedagogicalPlanner(self.graph, self.definitions)
        self.difficulty = DifficultyEstimator(self.graph)

        # Layer 4: Student Model
        self.student_model = StudentModel(
            storage_dir=str(self._output_dir / "students")
        )
        self.misconception_detector = MisconceptionDetector()
        self.progress_tracker = ProgressTracker(
            storage_dir=str(self._output_dir / "progress")
        )

        # Layer 5: Explanation Generator
        self.explanation_gen = ExplanationGenerator(self.graph, self.definitions)

        # Layer 6: Visualization Engine
        self.manim = ManimRenderer(
            output_dir=str(self._output_dir / "animations")
        )

        # Layer 7: Video Generation
        self.video_gen = VideoGenerator(
            output_dir=str(self._output_dir / "clips")
        )
        self.voice = VoiceEngine(
            output_dir=str(self._output_dir / "audio")
        )
        self.compositor = Compositor(
            output_dir=str(self._output_dir / "final")
        )

        # Layer 8: Feedback
        self.quiz_gen = QuizGenerator()
        self.evaluator = Evaluator()
        self.learning_gain = LearningGainCalculator()

    def generate_lesson(
        self,
        topic: str,
        student_id: str = "",
        difficulty: str = "intermediate",
        persona: str = "Professor Aria",
    ) -> LessonResult:
        """Generate a complete teaching lesson.

        This is the main entry point. It:
        1. Resolves the topic to a concept
        2. Checks student readiness (if student_id provided)
        3. Plans the lesson with pedagogy
        4. Generates explanation content
        5. Renders math animations
        6. Generates teacher video clips
        7. Synthesizes voice narration
        8. Composites the final video

        Args:
            topic: The math topic to teach.
            student_id: Optional student ID for personalization.
            difficulty: Target difficulty.
            persona: Name of the AI teacher.

        Returns:
            LessonResult with all generated assets.
        """
        # Step 1: Resolve concept
        concept = self.graph.find_concept_by_name(topic)
        concept_id = concept.id if concept else topic.lower().replace(" ", "_")

        # Step 2: Check student readiness
        if student_id:
            profile = self.student_model.get_or_create(student_id)
            known = profile.known_concepts()

            # Adjust difficulty based on student
            estimate = self.difficulty.estimate(concept_id, known)
            if estimate.prerequisite_coverage < 0.5:
                # Student isn't ready — suggest prerequisites
                gaps = self.inference.find_knowledge_gaps(known, concept_id)
                if gaps:
                    # Teach the most important prerequisite instead
                    concept_id = gaps[0].concept.id
                    topic = gaps[0].concept.name

        # Step 3: Plan the lesson
        script = self.planner.plan_lesson(
            topic=topic,
            difficulty=difficulty,
            target_audience="high school student",
        )
        script.persona = persona

        # Step 4: Generate explanation
        explanation = self.explanation_gen.generate(concept_id, difficulty)

        # Step 5: Render math animations
        animation_paths = []
        for step in script.steps:
            if step.visual_content and step.visual_type.value != "none":
                path = self.manim.render_equation(
                    step.visual_content, title=f"step_{step.step_number}"
                )
                animation_paths.append(path)

        # Step 6: Generate video clips
        video_clips = self.video_gen.generate_clips(script)

        # Step 7: Synthesize voice
        audio_clips = self.voice.batch_synthesize(script.steps)

        # Step 8: Composite final video
        composite = self.compositor.composite(
            video_clips=video_clips,
            audio_clips=audio_clips,
            animation_paths=animation_paths,
            output_name=concept_id,
        )

        # Update student model if tracking
        if student_id:
            self.student_model.record_lesson_completed(
                profile, concept_id, script.total_duration_minutes
            )
            self.student_model.save(profile)

        return LessonResult(
            topic=topic,
            concept_id=concept_id,
            script=script,
            explanation=explanation,
            video_clips=video_clips,
            audio_clips=audio_clips,
            animation_paths=animation_paths,
            composite=composite,
            is_stub=composite.is_stub if composite else True,
        )

    def generate_quiz(
        self,
        concept_id: str,
        num_questions: int = 5,
        difficulty: str = "intermediate",
    ) -> Quiz:
        """Generate a quiz for a concept."""
        return self.quiz_gen.generate(concept_id, num_questions, difficulty)

    def evaluate_quiz(
        self,
        quiz: Quiz,
        answers: dict[str, str],
        student_id: str = "",
    ) -> QuizResult:
        """Evaluate a completed quiz and update student model."""
        result = self.evaluator.evaluate_quiz(quiz, answers)

        if student_id:
            profile = self.student_model.get_or_create(student_id)
            for answer in result.answers:
                self.student_model.record_attempt(
                    profile,
                    quiz.concept_id,
                    correct=answer.is_correct,
                    misconception=answer.misconception,
                )
            self.student_model.save(profile)

        return result

    def get_concept_info(self, topic: str) -> dict:
        """Get information about a concept from the knowledge base."""
        concept = self.graph.find_concept_by_name(topic)
        if not concept:
            return {"error": f"Concept '{topic}' not found in knowledge base."}

        defn = self.definitions.get(concept.id)
        prereqs = self.graph.get_prerequisites(concept.id)
        dependents = self.graph.get_dependents(concept.id)

        return {
            "id": concept.id,
            "name": concept.name,
            "domain": concept.domain.value,
            "difficulty": concept.difficulty.value,
            "description": concept.description,
            "prerequisites": [p.name for p in prereqs],
            "leads_to": [d.name for d in dependents],
            "formal_definition": defn.formal if defn else "",
            "intuitive_explanation": defn.intuitive if defn else "",
            "misconceptions": defn.misconceptions if defn else [],
            "estimated_minutes": concept.estimated_minutes,
        }

    def get_student_info(self, student_id: str) -> dict:
        """Get student profile information."""
        profile = self.student_model.get_or_create(student_id)
        known = profile.known_concepts()
        next_concepts = self.graph.get_next_concepts(known)

        return {
            "student_id": profile.student_id,
            "concepts_known": len(known),
            "known_list": sorted(known),
            "total_study_minutes": profile.total_study_minutes,
            "sessions_completed": profile.sessions_completed,
            "can_learn_next": [c.name for c in next_concepts[:5]],
            "weakest": [
                {"concept": ck.concept_id, "mastery": ck.mastery}
                for ck in self.student_model.get_weakest_concepts(profile, 3)
            ],
        }
