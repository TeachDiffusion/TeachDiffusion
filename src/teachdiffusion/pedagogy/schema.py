"""Pedagogy Schema — the novel core of TeachDiffusion.

This module defines the structured representation of teaching intent.
The key innovation: encoding pedagogical decisions (step type, gesture,
pacing, visual cues) into a schema that can condition video generation.

Nobody has built this for math education video generation specifically.
This is TeachDiffusion's original contribution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class StepType(str, Enum):
    """Type of teaching step — determines pedagogical strategy."""

    HOOK = "hook"  # Grab attention, motivate the topic
    BUILD_INTUITION = "build_intuition"  # Visual/conceptual understanding first
    FORMAL_DEFINITION = "formal_definition"  # Precise mathematical statement
    WORKED_EXAMPLE = "worked_example"  # Step-by-step problem solving
    COMMON_MISTAKE = "common_mistake"  # Address typical misconceptions
    PRACTICE = "practice"  # Guided practice problem
    SUMMARY = "summary"  # Recap key ideas
    TRANSITION = "transition"  # Connect to next concept
    CHECK_UNDERSTANDING = "check_understanding"  # Quick verification


class GestureType(str, Enum):
    """Teacher gesture type — drives the avatar's body language."""

    POINTING = "pointing"  # Point at specific element on board
    WRITING = "writing"  # Writing on whiteboard
    OPEN_HAND = "open_hand"  # Open palm, explaining broadly
    COUNTING = "counting"  # Counting on fingers
    NODDING = "nodding"  # Affirming, encouraging
    THINKING = "thinking"  # Hand on chin, modeling reflection
    EMPHASIS = "emphasis"  # Hand chop or finger point for emphasis
    REVEALING = "revealing"  # Gesture of unveiling something
    NEUTRAL = "neutral"  # Standing naturally


class PacingType(str, Enum):
    """How fast the teacher should speak/move during this step."""

    SLOW = "slow"  # New or difficult concept, give time to absorb
    NORMAL = "normal"  # Standard teaching pace
    FAST = "fast"  # Review or familiar material
    PAUSE = "pause"  # Deliberate pause for student thinking


class VisualType(str, Enum):
    """Type of visual content to overlay during this step."""

    EQUATION = "equation"  # Display a math equation
    GRAPH = "graph"  # Plot a function or data
    DIAGRAM = "diagram"  # Geometric or schematic diagram
    STEP_BY_STEP = "step_by_step"  # Step-by-step derivation
    ANIMATION = "animation"  # Animated transformation
    TABLE = "table"  # Data table or comparison
    NONE = "none"  # No visual overlay


@dataclass
class TeachingStep:
    """A single step in a teaching sequence.

    This is the atomic unit of TeachDiffusion's pedagogy system.
    Each step encodes WHAT to teach, HOW to present it physically,
    and WHAT visual support to show.
    """

    step_number: int
    step_type: StepType
    content: str  # What the teacher says/explains
    gesture: GestureType = GestureType.NEUTRAL
    pacing: PacingType = PacingType.NORMAL
    visual_type: VisualType = VisualType.NONE
    visual_content: str = ""  # Specific visual to render (equation, graph spec, etc.)
    duration_seconds: int = 15
    board_text: str = ""  # What appears on the whiteboard
    emphasis_words: list[str] = field(default_factory=list)  # Words to stress
    teacher_position: str = "center"  # left, center, right
    notes: str = ""  # Internal notes for the pipeline

    def to_video_prompt(self, persona_name: str = "Professor Aria") -> str:
        """Convert this teaching step into a prompt for the video diffusion model.

        This is the key method — it translates pedagogical intent
        into a text prompt that conditions video generation.
        """
        gesture_desc = {
            GestureType.POINTING: "pointing at the whiteboard with their right hand",
            GestureType.WRITING: "writing on the whiteboard",
            GestureType.OPEN_HAND: "gesturing with an open palm while explaining",
            GestureType.COUNTING: "counting on their fingers",
            GestureType.NODDING: "nodding encouragingly",
            GestureType.THINKING: "pausing with hand on chin, thinking",
            GestureType.EMPHASIS: "making an emphatic gesture to stress a point",
            GestureType.REVEALING: "gesturing as if revealing something new",
            GestureType.NEUTRAL: "standing naturally while speaking",
        }

        pacing_desc = {
            PacingType.SLOW: "speaking slowly and clearly",
            PacingType.NORMAL: "speaking at a natural pace",
            PacingType.FAST: "speaking briskly",
            PacingType.PAUSE: "pausing deliberately for the student to think",
        }

        parts = [
            f"{persona_name} stands in front of a clean whiteboard,",
            gesture_desc.get(self.gesture, "standing naturally"),
            f"while {pacing_desc.get(self.pacing, 'speaking naturally')}.",
        ]

        if self.board_text:
            parts.append(f'The whiteboard shows: "{self.board_text}".')

        if self.visual_type != VisualType.NONE and self.visual_content:
            parts.append(f"A {self.visual_type.value} of {self.visual_content} is visible.")

        parts.append(f"The teacher is on the {self.teacher_position} side of the frame.")

        return " ".join(parts)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "step_number": self.step_number,
            "step_type": self.step_type.value,
            "content": self.content,
            "gesture": self.gesture.value,
            "pacing": self.pacing.value,
            "visual_type": self.visual_type.value,
            "visual_content": self.visual_content,
            "duration_seconds": self.duration_seconds,
            "board_text": self.board_text,
            "emphasis_words": self.emphasis_words,
            "teacher_position": self.teacher_position,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> TeachingStep:
        """Deserialize from dictionary."""
        return cls(
            step_number=data["step_number"],
            step_type=StepType(data["step_type"]),
            content=data["content"],
            gesture=GestureType(data.get("gesture", "neutral")),
            pacing=PacingType(data.get("pacing", "normal")),
            visual_type=VisualType(data.get("visual_type", "none")),
            visual_content=data.get("visual_content", ""),
            duration_seconds=data.get("duration_seconds", 15),
            board_text=data.get("board_text", ""),
            emphasis_words=data.get("emphasis_words", []),
            teacher_position=data.get("teacher_position", "center"),
            notes=data.get("notes", ""),
        )


@dataclass
class TeachingScript:
    """A complete teaching script — an ordered sequence of TeachingSteps.

    This is the full lesson plan that drives video generation.
    """

    topic: str
    concept_id: str
    target_audience: str = "high school student"
    difficulty: str = "intermediate"
    steps: list[TeachingStep] = field(default_factory=list)
    persona: str = "Professor Aria"
    total_duration_seconds: int = 0

    def add_step(self, step: TeachingStep) -> None:
        """Add a step to the script."""
        self.steps.append(step)
        self.total_duration_seconds = sum(s.duration_seconds for s in self.steps)

    @property
    def num_steps(self) -> int:
        return len(self.steps)

    @property
    def total_duration_minutes(self) -> float:
        return self.total_duration_seconds / 60.0

    def get_video_prompts(self) -> list[str]:
        """Generate video prompts for all steps."""
        return [step.to_video_prompt(self.persona) for step in self.steps]

    def to_dict(self) -> dict:
        """Serialize the entire script."""
        return {
            "topic": self.topic,
            "concept_id": self.concept_id,
            "target_audience": self.target_audience,
            "difficulty": self.difficulty,
            "persona": self.persona,
            "total_duration_seconds": self.total_duration_seconds,
            "steps": [s.to_dict() for s in self.steps],
        }

    @classmethod
    def from_dict(cls, data: dict) -> TeachingScript:
        """Deserialize from dictionary."""
        script = cls(
            topic=data["topic"],
            concept_id=data["concept_id"],
            target_audience=data.get("target_audience", "high school student"),
            difficulty=data.get("difficulty", "intermediate"),
            persona=data.get("persona", "Professor Aria"),
        )
        for step_data in data.get("steps", []):
            script.add_step(TeachingStep.from_dict(step_data))
        return script
