# Student Model

## Overview

The Student Model (Layer 4) tracks what each student knows, their confidence levels, misconceptions, and learning progress over time. This is what makes TeachDiffusion adaptive.

## Components

- **StudentModel** (`student_model.py`): Per-student knowledge state with JSON persistence.
- **MisconceptionDetector** (`misconception_detector.py`): Analyzes wrong answers to identify specific misconceptions.
- **ProgressTracker** (`progress_tracker.py`): Records learning sessions and computes progress analytics.

## How It Works

Each student has a `StudentProfile` containing a `ConceptKnowledge` entry for each studied concept:

```python
ConceptKnowledge(
    concept_id="quadratic_equations",
    mastery=0.75,          # 0.0 to 1.0
    confidence=0.8,        # Student's self-assessment
    attempts=10,           # Practice attempts
    correct=8,             # Correct answers
    misconceptions=["forgot_plus_minus"],
    last_studied="2026-03-24T10:30:00",
)
```

Mastery is updated using an exponential moving average after each attempt:
```
mastery = α * result + (1 - α) * mastery
```

## Adaptive Behavior

When a student requests a lesson, the pipeline:
1. Checks their prerequisite coverage for the target concept
2. If prerequisites are missing, redirects to teach the most important gap first
3. Adjusts difficulty based on their knowledge state
4. After the lesson, generates a quiz targeting their known misconceptions

## Data Storage

Profiles are saved as JSON files in the configured storage directory. No database required.
