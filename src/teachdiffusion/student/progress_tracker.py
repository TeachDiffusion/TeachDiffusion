"""Progress Tracker — tracks student learning sessions and progress over time.

Records what was studied, when, for how long, and what the outcomes were.
Provides analytics on learning velocity and concept retention.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class LearningSession:
    """A single study session."""

    session_id: str
    student_id: str
    concept_id: str
    started_at: str
    ended_at: str = ""
    duration_minutes: float = 0.0
    pre_mastery: float = 0.0
    post_mastery: float = 0.0
    quiz_score: float = 0.0
    quiz_attempts: int = 0
    notes: str = ""

    @property
    def mastery_gain(self) -> float:
        """How much mastery improved in this session."""
        return self.post_mastery - self.pre_mastery


@dataclass
class ProgressSummary:
    """Summary of a student's overall learning progress."""

    student_id: str
    total_sessions: int = 0
    total_study_minutes: float = 0.0
    concepts_studied: int = 0
    concepts_mastered: int = 0  # mastery >= 0.8
    average_mastery: float = 0.0
    average_quiz_score: float = 0.0
    strongest_concept: str = ""
    weakest_concept: str = ""
    study_streak_days: int = 0
    sessions: list[LearningSession] = field(default_factory=list)


class ProgressTracker:
    """Tracks and analyzes student learning progress.

    Usage:
        tracker = ProgressTracker(storage_dir="./data/progress")
        session = tracker.start_session("student_01", "quadratic_equations")
        # ... student studies ...
        tracker.end_session(session, post_mastery=0.7, quiz_score=0.8)
        summary = tracker.get_summary("student_01")
    """

    def __init__(self, storage_dir: str = "./data/progress") -> None:
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, list[LearningSession]] = {}

    def start_session(
        self,
        student_id: str,
        concept_id: str,
        pre_mastery: float = 0.0,
    ) -> LearningSession:
        """Start a new learning session."""
        now = datetime.now()
        session = LearningSession(
            session_id=f"{student_id}_{concept_id}_{now.strftime('%Y%m%d%H%M%S')}",
            student_id=student_id,
            concept_id=concept_id,
            started_at=now.isoformat(),
            pre_mastery=pre_mastery,
        )
        return session

    def end_session(
        self,
        session: LearningSession,
        post_mastery: float = 0.0,
        quiz_score: float = 0.0,
        quiz_attempts: int = 0,
    ) -> None:
        """End a learning session and save it."""
        now = datetime.now()
        session.ended_at = now.isoformat()
        started = datetime.fromisoformat(session.started_at)
        session.duration_minutes = (now - started).total_seconds() / 60.0
        session.post_mastery = post_mastery
        session.quiz_score = quiz_score
        session.quiz_attempts = quiz_attempts

        # Store in memory
        if session.student_id not in self._sessions:
            self._sessions[session.student_id] = []
        self._sessions[session.student_id].append(session)

        # Persist to disk
        self._save_session(session)

    def get_sessions(self, student_id: str) -> list[LearningSession]:
        """Get all sessions for a student."""
        if student_id not in self._sessions:
            self._load_sessions(student_id)
        return self._sessions.get(student_id, [])

    def get_summary(self, student_id: str) -> ProgressSummary:
        """Get a complete progress summary for a student."""
        sessions = self.get_sessions(student_id)

        if not sessions:
            return ProgressSummary(student_id=student_id)

        # Compute per-concept stats
        concept_mastery: dict[str, float] = {}
        concept_scores: dict[str, list[float]] = {}

        for s in sessions:
            concept_mastery[s.concept_id] = max(
                concept_mastery.get(s.concept_id, 0.0), s.post_mastery
            )
            if s.quiz_score > 0:
                if s.concept_id not in concept_scores:
                    concept_scores[s.concept_id] = []
                concept_scores[s.concept_id].append(s.quiz_score)

        all_masteries = list(concept_mastery.values())
        avg_mastery = sum(all_masteries) / len(all_masteries) if all_masteries else 0.0

        all_scores = [s for scores in concept_scores.values() for s in scores]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

        strongest = max(concept_mastery, key=concept_mastery.get) if concept_mastery else ""
        weakest = min(concept_mastery, key=concept_mastery.get) if concept_mastery else ""

        return ProgressSummary(
            student_id=student_id,
            total_sessions=len(sessions),
            total_study_minutes=sum(s.duration_minutes for s in sessions),
            concepts_studied=len(concept_mastery),
            concepts_mastered=sum(1 for m in all_masteries if m >= 0.8),
            average_mastery=avg_mastery,
            average_quiz_score=avg_score,
            strongest_concept=strongest,
            weakest_concept=weakest,
            sessions=sessions,
        )

    def _save_session(self, session: LearningSession) -> None:
        """Save a session to disk."""
        filepath = self._storage_dir / f"{session.student_id}_sessions.json"
        existing = []
        if filepath.exists():
            with open(filepath, "r") as f:
                existing = json.load(f)

        existing.append({
            "session_id": session.session_id,
            "concept_id": session.concept_id,
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "duration_minutes": session.duration_minutes,
            "pre_mastery": session.pre_mastery,
            "post_mastery": session.post_mastery,
            "quiz_score": session.quiz_score,
            "quiz_attempts": session.quiz_attempts,
        })

        with open(filepath, "w") as f:
            json.dump(existing, f, indent=2)

    def _load_sessions(self, student_id: str) -> None:
        """Load sessions from disk."""
        filepath = self._storage_dir / f"{student_id}_sessions.json"
        if not filepath.exists():
            self._sessions[student_id] = []
            return

        with open(filepath, "r") as f:
            data = json.load(f)

        sessions = []
        for item in data:
            sessions.append(LearningSession(
                session_id=item["session_id"],
                student_id=student_id,
                concept_id=item["concept_id"],
                started_at=item["started_at"],
                ended_at=item.get("ended_at", ""),
                duration_minutes=item.get("duration_minutes", 0.0),
                pre_mastery=item.get("pre_mastery", 0.0),
                post_mastery=item.get("post_mastery", 0.0),
                quiz_score=item.get("quiz_score", 0.0),
                quiz_attempts=item.get("quiz_attempts", 0),
            ))

        self._sessions[student_id] = sessions
