"""Tests for Layer 7: Video Generation."""

import tempfile
from teachdiffusion.video.wan_lora import WanLoRAModel, GenerationConfig
from teachdiffusion.video.generator import VideoGenerator
from teachdiffusion.video.voice_engine import VoiceEngine
from teachdiffusion.video.compositor import Compositor
from teachdiffusion.pedagogy.schema import TeachingStep, TeachingScript, StepType, GestureType, PacingType


class TestWanLoRAModel:
    def test_stub_mode(self):
        model = WanLoRAModel(stub_mode=True)
        assert model.is_stub
        path = model.generate("A teacher explaining math")
        assert len(path) > 0

    def test_stub_output_content(self):
        model = WanLoRAModel(stub_mode=True)
        path = model.generate("Test prompt", output_path="/tmp/test_stub.txt")
        with open(path) as f:
            content = f.read()
        assert "Test prompt" in content


class TestVideoGenerator:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.gen = VideoGenerator(output_dir=self.tmpdir)

    def test_generate_single_clip(self):
        step = TeachingStep(
            step_number=1, step_type=StepType.HOOK,
            content="Welcome to our lesson.", gesture=GestureType.OPEN_HAND,
        )
        clip = self.gen.generate_clip(step)
        assert clip.step_number == 1
        assert clip.is_stub
        assert len(clip.prompt_used) > 0

    def test_generate_clips_from_script(self):
        script = TeachingScript(topic="Test", concept_id="test")
        script.add_step(TeachingStep(step_number=1, step_type=StepType.HOOK, content="Hello"))
        script.add_step(TeachingStep(step_number=2, step_type=StepType.SUMMARY, content="Bye"))
        clips = self.gen.generate_clips(script)
        assert len(clips) == 2


class TestVoiceEngine:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.engine = VoiceEngine(output_dir=self.tmpdir)

    def test_synthesize_stub(self):
        step = TeachingStep(
            step_number=1, step_type=StepType.BUILD_INTUITION,
            content="The derivative tells you how fast something changes.",
            pacing=PacingType.SLOW,
        )
        audio = self.engine.synthesize(step)
        assert audio.step_number == 1
        assert audio.is_stub
        assert audio.duration_seconds > 0


class TestCompositor:
    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.compositor = Compositor(output_dir=self.tmpdir)

    def test_composite_stub(self):
        from teachdiffusion.video.generator import GeneratedClip
        clips = [
            GeneratedClip(step_number=1, video_path="/tmp/a.txt", prompt_used="test", duration_seconds=10, is_stub=True),
            GeneratedClip(step_number=2, video_path="/tmp/b.txt", prompt_used="test", duration_seconds=10, is_stub=True),
        ]
        result = self.compositor.composite(clips, output_name="test_lesson")
        assert result.is_stub
        assert result.num_clips == 2
        assert result.total_duration_seconds == 20
