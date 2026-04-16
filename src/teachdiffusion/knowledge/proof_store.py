"""Proof Store — stores mathematical proofs and derivations for concepts.

Each proof has:
- A step-by-step formal derivation
- An intuitive explanation of why each step works
- The proof technique used (direct, contradiction, induction, etc.)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ProofTechnique(str, Enum):
    """Standard mathematical proof techniques."""

    DIRECT = "direct"
    CONTRADICTION = "contradiction"
    INDUCTION = "induction"
    CONSTRUCTION = "construction"
    CONTRAPOSITIVE = "contrapositive"
    EXHAUSTION = "exhaustion"


@dataclass
class ProofStep:
    """A single step in a proof."""

    statement: str
    justification: str
    intuition: str = ""


@dataclass
class Proof:
    """A mathematical proof with formal steps and intuitive explanations."""

    concept_id: str
    title: str
    theorem: str
    technique: ProofTechnique
    steps: list[ProofStep] = field(default_factory=list)
    key_insight: str = ""


class ProofStore:
    """Stores and retrieves proofs for math concepts.

    Usage:
        store = ProofStore()
        store.load_defaults()
        proofs = store.get_proofs("quadratic_equations")
    """

    def __init__(self) -> None:
        self._proofs: dict[str, list[Proof]] = {}

    def add(self, proof: Proof) -> None:
        """Add a proof."""
        if proof.concept_id not in self._proofs:
            self._proofs[proof.concept_id] = []
        self._proofs[proof.concept_id].append(proof)

    def get_proofs(self, concept_id: str) -> list[Proof]:
        """Get all proofs for a concept."""
        return self._proofs.get(concept_id, [])

    def has_proofs(self, concept_id: str) -> bool:
        """Check if any proofs exist for a concept."""
        return concept_id in self._proofs and len(self._proofs[concept_id]) > 0

    def load_defaults(self) -> None:
        """Load default proofs for key concepts."""
        for proof in _build_default_proofs():
            self.add(proof)


def _build_default_proofs() -> list[Proof]:
    """Build default proofs."""
    return [
        Proof(
            concept_id="quadratic_equations",
            title="Derivation of the Quadratic Formula",
            theorem="If ax² + bx + c = 0 and a ≠ 0, then x = (-b ± √(b²-4ac)) / (2a).",
            technique=ProofTechnique.DIRECT,
            key_insight="Completing the square transforms any quadratic into a form we can solve with square roots.",
            steps=[
                ProofStep(
                    statement="Start with ax² + bx + c = 0",
                    justification="Given equation",
                    intuition="Our starting point — we want to isolate x.",
                ),
                ProofStep(
                    statement="Divide by a: x² + (b/a)x + c/a = 0",
                    justification="a ≠ 0, so division is valid",
                    intuition="Make the x² coefficient 1 to simplify.",
                ),
                ProofStep(
                    statement="Move constant: x² + (b/a)x = -c/a",
                    justification="Subtract c/a from both sides",
                    intuition="Isolate the x terms on one side.",
                ),
                ProofStep(
                    statement="Complete the square: x² + (b/a)x + (b/2a)² = -c/a + (b/2a)²",
                    justification="Add (b/2a)² to both sides",
                    intuition="The key trick — add the right number to make a perfect square.",
                ),
                ProofStep(
                    statement="Factor left side: (x + b/2a)² = (b² - 4ac) / (4a²)",
                    justification="Left is a perfect square; right simplified",
                    intuition="Now we have (something)² = a number.",
                ),
                ProofStep(
                    statement="Take square root: x + b/2a = ± √(b² - 4ac) / (2a)",
                    justification="Square root of both sides (don't forget ±)",
                    intuition="Undo the square — but remember both positive and negative roots.",
                ),
                ProofStep(
                    statement="Isolate x: x = (-b ± √(b² - 4ac)) / (2a)",
                    justification="Subtract b/2a from both sides",
                    intuition="The quadratic formula.",
                ),
            ],
        ),
        Proof(
            concept_id="pythagorean_theorem",
            title="Proof of the Pythagorean Theorem (Geometric)",
            theorem="In a right triangle with legs a, b and hypotenuse c: a² + b² = c².",
            technique=ProofTechnique.CONSTRUCTION,
            key_insight="Arrange four copies of the triangle inside a square to show the areas must balance.",
            steps=[
                ProofStep(
                    statement="Construct a square with side length (a + b)",
                    justification="Construction",
                    intuition="Start with a big square whose area we know: (a+b)².",
                ),
                ProofStep(
                    statement="Place four copies of the right triangle inside, forming a smaller square of side c in the center",
                    justification="The hypotenuses of the four triangles form the inner square",
                    intuition="The gap in the middle is a tilted square with side c.",
                ),
                ProofStep(
                    statement="Area of big square = (a + b)² = a² + 2ab + b²",
                    justification="Expansion",
                    intuition="Total area computed algebraically.",
                ),
                ProofStep(
                    statement="Area of big square = area of 4 triangles + area of inner square = 4(½ab) + c² = 2ab + c²",
                    justification="Sum of parts equals the whole",
                    intuition="Same area computed geometrically.",
                ),
                ProofStep(
                    statement="Therefore a² + 2ab + b² = 2ab + c², so a² + b² = c²",
                    justification="Equate the two expressions and cancel 2ab",
                    intuition="The 2ab cancels, leaving exactly a² + b² = c².",
                ),
            ],
        ),
        Proof(
            concept_id="fundamental_theorem",
            title="Fundamental Theorem of Calculus (Part 1)",
            theorem="If f is continuous on [a,b] and F(x) = ∫ₐˣ f(t)dt, then F'(x) = f(x).",
            technique=ProofTechnique.DIRECT,
            key_insight="The rate at which area accumulates equals the height of the function.",
            steps=[
                ProofStep(
                    statement="Define F(x) = ∫ₐˣ f(t)dt",
                    justification="Definition of the accumulation function",
                    intuition="F(x) measures the total area under f from a to x.",
                ),
                ProofStep(
                    statement="Consider F(x+h) - F(x) = ∫ₓˣ⁺ʰ f(t)dt",
                    justification="Splitting the integral",
                    intuition="The change in area is just the thin strip from x to x+h.",
                ),
                ProofStep(
                    statement="By the Mean Value Theorem for integrals: ∫ₓˣ⁺ʰ f(t)dt = f(c)·h for some c between x and x+h",
                    justification="MVT for integrals (f continuous)",
                    intuition="The thin strip's area is approximately height × width.",
                ),
                ProofStep(
                    statement="So [F(x+h) - F(x)] / h = f(c), and as h→0, c→x",
                    justification="Squeeze / continuity of f",
                    intuition="As the strip gets thinner, c gets squeezed to x.",
                ),
                ProofStep(
                    statement="Therefore F'(x) = lim_{h→0} [F(x+h) - F(x)] / h = f(x)",
                    justification="Definition of derivative + continuity",
                    intuition="The rate of area accumulation at x equals the function height at x.",
                ),
            ],
        ),
    ]
