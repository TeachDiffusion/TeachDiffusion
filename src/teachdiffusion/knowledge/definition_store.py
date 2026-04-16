"""Definition Store — formal and intuitive definitions for every concept.

Each concept has:
- A formal mathematical definition
- An intuitive plain-language explanation
- Common misconceptions students hold
- Key notation used
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Definition:
    """A definition for a math concept — both formal and intuitive."""

    concept_id: str
    formal: str
    intuitive: str
    notation: list[str] = field(default_factory=list)
    misconceptions: list[str] = field(default_factory=list)
    analogies: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


class DefinitionStore:
    """Stores and retrieves definitions for math concepts.

    Usage:
        store = DefinitionStore()
        store.load_defaults()
        defn = store.get("quadratic_equations")
        print(defn.intuitive)
    """

    def __init__(self) -> None:
        self._definitions: dict[str, Definition] = {}

    def add(self, definition: Definition) -> None:
        """Add a definition."""
        self._definitions[definition.concept_id] = definition

    def get(self, concept_id: str) -> Definition | None:
        """Get a definition by concept ID."""
        return self._definitions.get(concept_id)

    def has(self, concept_id: str) -> bool:
        """Check if a definition exists."""
        return concept_id in self._definitions

    def all_ids(self) -> list[str]:
        """Return all concept IDs with definitions."""
        return list(self._definitions.keys())

    def load_defaults(self) -> None:
        """Load default definitions for core math concepts."""
        for defn in _build_default_definitions():
            self.add(defn)


def _build_default_definitions() -> list[Definition]:
    """Build default definitions for key concepts."""
    return [
        Definition(
            concept_id="quadratic_equations",
            formal=(
                "A quadratic equation is a polynomial equation of degree 2, "
                "written in standard form as ax² + bx + c = 0 where a ≠ 0. "
                "Its solutions are given by x = (-b ± √(b²-4ac)) / (2a)."
            ),
            intuitive=(
                "A quadratic is an equation where the variable gets squared. "
                "When you graph it, you get a parabola — a U-shaped curve. "
                "The solutions are where that curve crosses the x-axis."
            ),
            notation=["ax² + bx + c = 0", "x = (-b ± √(b²-4ac)) / (2a)"],
            misconceptions=[
                "Forgetting the ± gives only one solution instead of two",
                "Thinking every quadratic has two real solutions (some have none)",
                "Confusing the vertex with the roots",
            ],
            analogies=[
                "A thrown ball follows a parabola — the quadratic tells you when it hits the ground",
                "Like finding where a bridge arch meets the water level",
            ],
            examples=[
                "x² - 5x + 6 = 0 → (x-2)(x-3) = 0 → x = 2 or x = 3",
                "x² + 1 = 0 → no real solutions (parabola never crosses x-axis)",
            ],
        ),
        Definition(
            concept_id="derivatives",
            formal=(
                "The derivative of f at x is defined as "
                "f'(x) = lim_{h→0} [f(x+h) - f(x)] / h, "
                "provided this limit exists."
            ),
            intuitive=(
                "The derivative tells you how fast something is changing at any moment. "
                "It's the slope of the curve at a single point — zoom in far enough "
                "on any smooth curve and it looks like a straight line. The derivative "
                "is the slope of that line."
            ),
            notation=["f'(x)", "dy/dx", "df/dx", "d/dx[f(x)]"],
            misconceptions=[
                "The derivative IS the function value (it's the rate of change)",
                "You can always use the power rule (not for sin, cos, e^x, etc.)",
                "The derivative at a max/min is always zero (true, but zero derivative doesn't always mean max/min)",
            ],
            analogies=[
                "Speed is the derivative of position — it tells you how fast your position changes",
                "If your bank balance is f(t), the derivative is how fast you're earning or spending",
            ],
            examples=[
                "f(x) = x² → f'(x) = 2x",
                "f(x) = sin(x) → f'(x) = cos(x)",
            ],
        ),
        Definition(
            concept_id="eigenvalues",
            formal=(
                "Given a square matrix A, a scalar λ is an eigenvalue of A if there "
                "exists a nonzero vector v such that Av = λv. The vector v is the "
                "corresponding eigenvector."
            ),
            intuitive=(
                "Most vectors change direction when you multiply them by a matrix. "
                "Eigenvectors are special — they only stretch or shrink, staying on "
                "the same line. The eigenvalue tells you how much they stretch."
            ),
            notation=["Av = λv", "det(A - λI) = 0"],
            misconceptions=[
                "Eigenvectors are unique (any scalar multiple of an eigenvector is also one)",
                "Every matrix has real eigenvalues (complex eigenvalues exist)",
                "Eigenvalues are always positive (they can be negative or zero)",
            ],
            analogies=[
                "Imagine pushing a door — most pushes change its angle AND position. "
                "An eigenvector is like pushing exactly along the hinge axis: "
                "the door moves but stays on the same line.",
            ],
            examples=[
                "A = [[2,1],[0,3]] has eigenvalues λ₁=2, λ₂=3",
                "The identity matrix has eigenvalue 1 for every vector",
            ],
        ),
        Definition(
            concept_id="integrals",
            formal=(
                "The definite integral of f from a to b is defined as "
                "∫ₐᵇ f(x)dx = lim_{n→∞} Σᵢ f(xᵢ)Δx, the limit of Riemann sums."
            ),
            intuitive=(
                "Integration adds up infinitely many infinitely thin slices to find "
                "the total. Think of it as measuring the area under a curve by "
                "filling it with thinner and thinner rectangles."
            ),
            notation=["∫f(x)dx", "∫ₐᵇ f(x)dx", "F(b) - F(a)"],
            misconceptions=[
                "Forgetting the constant of integration (+C) in indefinite integrals",
                "Thinking area is always positive (integral can be negative)",
                "Integration is just 'reverse differentiation' (it's accumulation)",
            ],
            analogies=[
                "If speed is the derivative of distance, then distance is the integral of speed",
                "Like computing total rainfall by adding up every moment's rain rate",
            ],
            examples=[
                "∫x² dx = x³/3 + C",
                "∫₀¹ x² dx = 1/3 (area under x² from 0 to 1)",
            ],
        ),
        Definition(
            concept_id="matrices",
            formal=(
                "A matrix is a rectangular array of numbers arranged in rows and columns. "
                "An m×n matrix has m rows and n columns. Matrix multiplication AB is defined "
                "when A is m×p and B is p×n, yielding an m×n matrix."
            ),
            intuitive=(
                "A matrix is a grid of numbers that represents a transformation. "
                "Multiplying a vector by a matrix transforms it — rotating, scaling, "
                "shearing, or projecting it. A system of linear equations is really "
                "just a matrix equation in disguise."
            ),
            notation=["A = [aᵢⱼ]", "AB ≠ BA (generally)", "Aᵀ"],
            misconceptions=[
                "Matrix multiplication is commutative (AB ≠ BA in general)",
                "You can divide by a matrix (you multiply by the inverse instead)",
                "A matrix is just a table of data (it represents a linear transformation)",
            ],
            analogies=[
                "A matrix is like a machine: put a vector in, get a transformed vector out",
                "A recipe that tells you how to mix ingredients (input vector) to get a dish (output vector)",
            ],
            examples=[
                "[[1,0],[0,1]] is the identity matrix — it leaves every vector unchanged",
                "[[0,-1],[1,0]] rotates vectors 90° counterclockwise",
            ],
        ),
        Definition(
            concept_id="limits",
            formal=(
                "The limit of f(x) as x approaches a is L, written lim_{x→a} f(x) = L, "
                "if for every ε > 0 there exists δ > 0 such that "
                "0 < |x - a| < δ implies |f(x) - L| < ε."
            ),
            intuitive=(
                "A limit asks: what value does a function get closer and closer to "
                "as you approach a certain point? You never have to reach the point — "
                "you just need to see where the function is heading."
            ),
            notation=["lim_{x→a} f(x) = L", "lim_{x→a⁺}", "lim_{x→a⁻}"],
            misconceptions=[
                "The limit equals the function value at that point (it doesn't have to)",
                "If the function is undefined at a point, the limit doesn't exist (it can)",
                "Limits are only for calculus (they appear everywhere in analysis)",
            ],
            analogies=[
                "Walking toward a wall — the limit is the wall, even if you never touch it",
                "Predicting where a car is heading by watching its trajectory, even if it stops before arriving",
            ],
            examples=[
                "lim_{x→2} (x² - 4)/(x - 2) = 4 (even though the function is undefined at x=2)",
                "lim_{x→0} sin(x)/x = 1",
            ],
        ),
        Definition(
            concept_id="linear_equations",
            formal=(
                "A linear equation in one variable is an equation of the form "
                "ax + b = 0 where a ≠ 0. Its solution is x = -b/a."
            ),
            intuitive=(
                "A linear equation is a balance scale. Whatever you do to one side, "
                "you must do to the other to keep it balanced. The goal is to get "
                "the variable alone on one side."
            ),
            notation=["ax + b = c", "y = mx + b"],
            misconceptions=[
                "Not applying the same operation to both sides",
                "Confusing the slope with the y-intercept in y = mx + b",
            ],
            analogies=[
                "A seesaw — to keep it level, whatever weight you add to one side you must add to the other",
            ],
            examples=[
                "2x + 3 = 7 → 2x = 4 → x = 2",
                "5 - 3x = -1 → -3x = -6 → x = 2",
            ],
        ),
        Definition(
            concept_id="functions",
            formal=(
                "A function f: A → B is a relation that assigns to each element "
                "in the domain A exactly one element in the codomain B."
            ),
            intuitive=(
                "A function is a machine: you put in a number, it does something "
                "to it, and out comes exactly one result. Every input gives exactly "
                "one output — no ambiguity."
            ),
            notation=["f(x)", "f: A → B", "domain", "range"],
            misconceptions=[
                "f(x) means f times x (it's notation for 'f of x')",
                "Every equation is a function (vertical line test)",
                "Functions must be defined by a formula (they can be defined by a table or rule)",
            ],
            analogies=[
                "A vending machine: insert a coin (input), get exactly one snack (output)",
                "A phone contacts list: each name maps to exactly one phone number",
            ],
            examples=[
                "f(x) = x² maps 3 → 9 and -3 → 9",
                "f(x) = √x is a function only for x ≥ 0 (if we want real outputs)",
            ],
        ),
    ]
