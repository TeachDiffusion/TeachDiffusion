"""Analogy Store — curated collection of analogies organized by concept.

Supplements the analogy builder with a static, high-quality set of
analogies that don't require API calls.
"""

from __future__ import annotations

from dataclasses import dataclass

_CURATED_ANALOGIES: dict[str, list[dict[str, str]]] = {
    "functions": [
        {"analogy": "A vending machine: put in a coin (input), get exactly one snack (output).",
         "why": "Emphasizes the one-input-one-output rule."},
        {"analogy": "A recipe: ingredients (inputs) produce exactly one dish (output).",
         "why": "Familiar, concrete process with deterministic outcome."},
    ],
    "derivatives": [
        {"analogy": "A speedometer: it tells you how fast you're going RIGHT NOW, not your total distance.",
         "why": "Instantaneous rate of change vs cumulative quantity."},
        {"analogy": "The steepness of a hill as you walk along it — always changing.",
         "why": "Connects slope to physical experience."},
    ],
    "integrals": [
        {"analogy": "Filling a bathtub: the integral of the flow rate gives you the total water.",
         "why": "Accumulation of a rate over time."},
        {"analogy": "Adding up thin pizza slices to find the area of the whole pizza.",
         "why": "Sum of infinitely thin pieces = total area."},
    ],
    "eigenvalues": [
        {"analogy": "A guitar string vibrates at specific frequencies — those are its eigenvalues.",
         "why": "Natural modes / resonant frequencies = eigenvalues of the system."},
        {"analogy": "Pushing a door along its hinge axis — it moves but stays on the same line.",
         "why": "Eigenvectors don't change direction, only scale."},
    ],
    "matrices": [
        {"analogy": "A matrix is like a funhouse mirror — it transforms what you put in front of it.",
         "why": "Linear transformation as visual distortion."},
        {"analogy": "A recipe multiplier: the matrix tells you how to mix ingredients into outputs.",
         "why": "Linear combinations as mixing."},
    ],
    "limits": [
        {"analogy": "Walking toward a wall — you can always get closer, but the wall is the limit.",
         "why": "Approaching without necessarily reaching."},
        {"analogy": "Zooming in on a map — the more you zoom, the clearer the destination becomes.",
         "why": "Progressive refinement toward a value."},
    ],
    "quadratic_equations": [
        {"analogy": "Throwing a ball — the path is a parabola, and where it lands are the roots.",
         "why": "Physical trajectory modeled by quadratics."},
        {"analogy": "A bridge arch — the quadratic tells you its shape and where it meets the ground.",
         "why": "Architectural application of parabolas."},
    ],
    "logarithms": [
        {"analogy": "How many times do you halve a number before reaching 1? That's roughly the log.",
         "why": "Logarithm as 'how many doublings/halvings'."},
        {"analogy": "The Richter scale: each step up is 10x more energy — that's logarithmic.",
         "why": "Real-world logarithmic scale everyone has heard of."},
    ],
}


@dataclass
class StoredAnalogy:
    """An analogy from the curated store."""

    concept_id: str
    analogy: str
    why_it_works: str


class AnalogyStore:
    """Retrieves curated analogies for math concepts.

    Usage:
        store = AnalogyStore()
        analogies = store.get("derivatives")
    """

    def get(self, concept_id: str) -> list[StoredAnalogy]:
        """Get all curated analogies for a concept."""
        entries = _CURATED_ANALOGIES.get(concept_id, [])
        return [
            StoredAnalogy(
                concept_id=concept_id,
                analogy=entry["analogy"],
                why_it_works=entry["why"],
            )
            for entry in entries
        ]

    def has(self, concept_id: str) -> bool:
        """Check if curated analogies exist for a concept."""
        return concept_id in _CURATED_ANALOGIES

    def all_concept_ids(self) -> list[str]:
        """Return all concept IDs with curated analogies."""
        return list(_CURATED_ANALOGIES.keys())
