"""Student Model — tracks what each student knows, their confidence, and misconceptions.

This is what makes TeachDiffusion adaptive. Without it, every student
gets the same video. With it, lessons are personalized.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class ConceptKnowledge:
    """What a student knows about a specific concept."""

    concept_id: str
    mastery: float = 0.0  # 0.0 (unknown) to 1.0 (mastered)
    confidence: float = 0.5  # Student's self-reported confidence
    attempts: int = 0  # Number of practice attempts
    correct: int = 0  # Number of correct answers
    misconceptions: list[str] = field(default_factory=list)
    last_studied: Optional[str] = None  # ISO timestamp
    notes: str = ""

    @property
    def accuracy(self) -> float:
        """Accuracy rate across all attempts."""
        if self.attempts == 0:
            return 0.0
        return self.correct / self.attempts


@dataclass
class StudentProfile:
    """Complete profile for a single student."""

    student_id: str
    name: str = ""
    created_at: str = ""
    knowledge: dict[str, ConceptKnowledge] = field(default_factory=dict)
    total_study_minutes: float = 0.0
    sessions_completed: int = 0
    preferred_pacing: str = "normal"  # slow, normal, fast
    preferred_difficulty: str = "intermediate"

    def knows(self, concept_id: str) -> bool:
        """Check if the student has studied a concept."""
        return concept_id in self.knowledge

    def mastery_of(self, concept_id: str) -> float:
        """Get mastery level for a concept (0.0 if not studied)."""
        ck = self.knowledge.get(concept_id)
        return ck.mastery if ck else 0.0

    def known_concepts(self, threshold: float = 0.5) -> set[str]:
        """Return set of concept IDs the student knows above a threshold."""
        return {
            cid for cid, ck in self.knowledge.items() if ck.mastery >= threshold
        }

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "created_at": self.created_at,
            "total_study_minutes": self.total_study_minutes,
            "sessions_completed": self.sessions_completed,
            "preferred_pacing": self.preferred_pacing,
            "preferred_difficulty": self.preferred_difficulty,
            "knowledge": {
                cid: {
                    "mastery": ck.mastery,
                    "confidence": ck.confidence,
                    "attempts": ck.attempts,
                    "correct": ck.correct,
                    "misconceptions": ck.misconceptions,
                    "last_studied": ck.last_studied,
                    "notes": ck.notes,
                }
                for cid, ck in self.knowledge.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> StudentProfile:
        """Deserialize from dictionary."""
        profile = cls(
            student_id=data["student_id"],
            name=data.get("name", ""),
            created_at=data.get("created_at", ""),
            total_study_minutes=data.get("total_study_minutes", 0.0),
            sessions_completed=data.get("sessions_completed", 0),
            preferred_pacing=data.get("preferred_pacing", "normal"),
            preferred_difficulty=data.get("preferred_difficulty", "intermediate"),
        )
        for cid, ck_data in data.get("knowledge", {}).items():
            profile.knowledge[cid] = ConceptKnowledge(
                concept_id=cid,
                mastery=ck_data.get("mastery", 0.0),
                confidence=ck_data.get("confidence", 0.5),
                attempts=ck_data.get("attempts", 0),
                correct=ck_data.get("correct", 0),
                misconceptions=ck_data.get("misconceptions", []),
                last_studied=ck_data.get("last_studied"),
                notes=ck_data.get("notes", ""),
            )
        return profile


class StudentModel:
    """Manages student profiles with persistence.

    Usage:
        model = StudentModel(storage_dir="./data/students")
        profile = model.get_or_create("student_01")
        model.record_attempt(profile, "quadratic_equations", correct=True)
        model.save(profile)
    """

    def __init__(self, storage_dir: str = "./data/students") -> None:
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._profiles: dict[str, StudentProfile] = {}

    def get_or_create(self, student_id: str, name: str = "") -> StudentProfile:
        """Get existing profile or create a new one."""
        if student_id in self._profiles:
            return self._profiles[student_id]

        # Try to load from disk
        filepath = self._storage_dir / f"{student_id}.json"
        if filepath.exists():
            with open(filepath, "r") as f:
                data = json.load(f)
                profile = StudentProfile.from_dict(data)
                self._profiles[student_id] = profile
                return profile

        # Create new
        profile = StudentProfile(
            student_id=student_id,
            name=name,
            created_at=datetime.now().isoformat(),
        )
        self._profiles[student_id] = profile
        return profile

    def save(self, profile: StudentProfile) -> None:
        """Save a student profile to disk."""
        filepath = self._storage_dir / f"{profile.student_id}.json"
        with open(filepath, "w") as f:
            json.dump(profile.to_dict(), f, indent=2)

    def record_attempt(
        self,
        profile: StudentProfile,
        concept_id: str,
        correct: bool,
        misconception: str = "",
    ) -> None:
        """Record a practice attempt for a concept.

        Updates mastery based on recent performance.
        """
        if concept_id not in profile.knowledge:
            profile.knowledge[concept_id] = ConceptKnowledge(concept_id=concept_id)

        ck = profile.knowledge[concept_id]
        ck.attempts += 1
        if correct:
            ck.correct += 1
        if misconception and misconception not in ck.misconceptions:
            ck.misconceptions.append(misconception)
        ck.last_studied = datetime.now().isoformat()

        # Update mastery using exponential moving average
        result = 1.0 if correct else 0.0
        alpha = 0.3  # Learning rate
        ck.mastery = alpha * result + (1 - alpha) * ck.mastery

    def record_lesson_completed(
        self, profile: StudentProfile, concept_id: str, duration_minutes: float
    ) -> None:
        """Record that a student completed a lesson on a concept."""
        if concept_id not in profile.knowledge:
            profile.knowledge[concept_id] = ConceptKnowledge(concept_id=concept_id)

        ck = profile.knowledge[concept_id]
        ck.last_studied = datetime.now().isoformat()
        # Boost mastery slightly for watching a lesson
        ck.mastery = min(1.0, ck.mastery + 0.1)

        profile.total_study_minutes += duration_minutes
        profile.sessions_completed += 1

    def get_weakest_concepts(
        self, profile: StudentProfile, n: int = 5
    ) -> list[ConceptKnowledge]:
        """Get the N concepts with lowest mastery that have been studied."""
        studied = [
            ck for ck in profile.knowledge.values() if ck.attempts > 0
        ]
        studied.sort(key=lambda ck: ck.mastery)
        return studied[:n]

    def list_students(self) -> list[str]:
        """List all student IDs with saved profiles."""
        return [
            f.stem for f in self._storage_dir.glob("*.json")
        ]
