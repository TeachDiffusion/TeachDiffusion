"""Concept Graph — a directed acyclic graph of math concepts and their prerequisites.

This is the backbone of TeachDiffusion's knowledge. Every teaching decision
flows from understanding which concepts exist, how they relate, and what
must be learned before what.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import networkx as nx


class MathDomain(str, Enum):
    """Top-level math domains."""

    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    GEOMETRY = "geometry"
    TRIGONOMETRY = "trigonometry"
    CALCULUS = "calculus"
    LINEAR_ALGEBRA = "linear_algebra"
    PROBABILITY = "probability"
    NUMBER_THEORY = "number_theory"


class DifficultyLevel(str, Enum):
    """How hard a concept is for a typical student."""

    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class Concept:
    """A single math concept in the knowledge graph."""

    id: str
    name: str
    domain: MathDomain
    difficulty: DifficultyLevel
    description: str
    prerequisites: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    typical_misconceptions: list[str] = field(default_factory=list)
    estimated_minutes: int = 15

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Concept):
            return self.id == other.id
        return False


class ConceptGraph:
    """A directed graph of math concepts where edges represent prerequisites.

    Usage:
        graph = ConceptGraph()
        graph.load_default()

        # Find what a student needs to learn before tackling eigenvalues
        prereqs = graph.get_all_prerequisites("eigenvalues")

        # Find the optimal learning path
        path = graph.get_learning_path("arithmetic_basics", "eigenvalues")
    """

    def __init__(self) -> None:
        self._graph = nx.DiGraph()
        self._concepts: dict[str, Concept] = {}

    def add_concept(self, concept: Concept) -> None:
        """Add a concept to the graph."""
        self._concepts[concept.id] = concept
        self._graph.add_node(concept.id)
        for prereq_id in concept.prerequisites:
            self._graph.add_edge(prereq_id, concept.id)

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Get a concept by ID."""
        return self._concepts.get(concept_id)

    def get_all_concepts(self) -> list[Concept]:
        """Return all concepts in the graph."""
        return list(self._concepts.values())

    def get_concepts_by_domain(self, domain: MathDomain) -> list[Concept]:
        """Return all concepts in a given domain."""
        return [c for c in self._concepts.values() if c.domain == domain]

    def get_prerequisites(self, concept_id: str) -> list[Concept]:
        """Return direct prerequisites of a concept."""
        if concept_id not in self._graph:
            return []
        prereq_ids = list(self._graph.predecessors(concept_id))
        return [self._concepts[pid] for pid in prereq_ids if pid in self._concepts]

    def get_all_prerequisites(self, concept_id: str) -> list[Concept]:
        """Return ALL prerequisites (transitive) of a concept, topologically sorted."""
        if concept_id not in self._graph:
            return []
        ancestors = nx.ancestors(self._graph, concept_id)
        subgraph = self._graph.subgraph(ancestors)
        sorted_ids = list(nx.topological_sort(subgraph))
        return [self._concepts[cid] for cid in sorted_ids if cid in self._concepts]

    def get_dependents(self, concept_id: str) -> list[Concept]:
        """Return concepts that depend on this concept."""
        if concept_id not in self._graph:
            return []
        dep_ids = list(self._graph.successors(concept_id))
        return [self._concepts[did] for did in dep_ids if did in self._concepts]

    def get_learning_path(self, start_id: str, target_id: str) -> list[Concept]:
        """Return the shortest prerequisite path from start to target."""
        if start_id not in self._graph or target_id not in self._graph:
            return []
        try:
            path_ids = nx.shortest_path(self._graph, start_id, target_id)
            return [self._concepts[cid] for cid in path_ids if cid in self._concepts]
        except nx.NetworkXNoPath:
            return []

    def get_next_concepts(self, known_ids: set[str]) -> list[Concept]:
        """Given a set of known concepts, return what the student can learn next.

        A concept is 'learnable' if all its prerequisites are in known_ids.
        """
        learnable = []
        for concept_id, concept in self._concepts.items():
            if concept_id in known_ids:
                continue
            prereqs = set(concept.prerequisites)
            if prereqs.issubset(known_ids):
                learnable.append(concept)
        return sorted(learnable, key=lambda c: c.difficulty.value)

    def find_concept_by_name(self, query: str) -> Optional[Concept]:
        """Fuzzy search for a concept by name or keyword."""
        query_lower = query.lower().strip()
        # Exact match
        for concept in self._concepts.values():
            if concept.name.lower() == query_lower:
                return concept
        # Keyword match
        for concept in self._concepts.values():
            if query_lower in concept.name.lower():
                return concept
            if any(query_lower in kw.lower() for kw in concept.keywords):
                return concept
        return None

    def validate(self) -> list[str]:
        """Check graph integrity. Returns list of issues."""
        issues = []
        # Check for cycles
        if not nx.is_directed_acyclic_graph(self._graph):
            cycles = list(nx.simple_cycles(self._graph))
            issues.append(f"Graph has cycles: {cycles}")
        # Check for missing prerequisites
        for concept in self._concepts.values():
            for prereq_id in concept.prerequisites:
                if prereq_id not in self._concepts:
                    issues.append(
                        f"Concept '{concept.id}' requires '{prereq_id}' "
                        f"which does not exist"
                    )
        return issues

    @property
    def num_concepts(self) -> int:
        return len(self._concepts)

    @property
    def num_edges(self) -> int:
        return self._graph.number_of_edges()

    def load_default(self) -> None:
        """Load the default math concept graph with 34+ concepts."""
        concepts = _build_default_concepts()
        for concept in concepts:
            self.add_concept(concept)


def _build_default_concepts() -> list[Concept]:
    """Build the default set of 34+ math concepts."""
    return [
        # --- Arithmetic ---
        Concept(
            id="arithmetic_basics",
            name="Arithmetic Basics",
            domain=MathDomain.ARITHMETIC,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Addition, subtraction, multiplication, division of integers.",
            keywords=["addition", "subtraction", "multiplication", "division", "integers"],
            typical_misconceptions=["Order of operations confusion", "Negative number arithmetic"],
            estimated_minutes=10,
        ),
        Concept(
            id="fractions",
            name="Fractions",
            domain=MathDomain.ARITHMETIC,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Representing and operating on parts of a whole.",
            prerequisites=["arithmetic_basics"],
            keywords=["fraction", "numerator", "denominator", "rational"],
            typical_misconceptions=["Adding numerators and denominators separately"],
            estimated_minutes=15,
        ),
        Concept(
            id="decimals",
            name="Decimals",
            domain=MathDomain.ARITHMETIC,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Base-10 fractional representation.",
            prerequisites=["fractions"],
            keywords=["decimal", "decimal point", "place value"],
            estimated_minutes=10,
        ),
        Concept(
            id="percentages",
            name="Percentages",
            domain=MathDomain.ARITHMETIC,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Expressing quantities as parts per hundred.",
            prerequisites=["fractions", "decimals"],
            keywords=["percent", "percentage", "ratio"],
            estimated_minutes=10,
        ),
        Concept(
            id="exponents",
            name="Exponents & Powers",
            domain=MathDomain.ARITHMETIC,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Repeated multiplication and its notation.",
            prerequisites=["arithmetic_basics"],
            keywords=["exponent", "power", "squared", "cubed", "base"],
            typical_misconceptions=["Negative exponents mean negative numbers"],
            estimated_minutes=12,
        ),
        Concept(
            id="square_roots",
            name="Square Roots",
            domain=MathDomain.ARITHMETIC,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="The inverse operation of squaring.",
            prerequisites=["exponents"],
            keywords=["square root", "radical", "sqrt"],
            typical_misconceptions=["Square root of a sum equals sum of square roots"],
            estimated_minutes=10,
        ),
        # --- Algebra ---
        Concept(
            id="variables_expressions",
            name="Variables & Expressions",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Using letters to represent unknown quantities.",
            prerequisites=["arithmetic_basics"],
            keywords=["variable", "expression", "term", "coefficient"],
            estimated_minutes=12,
        ),
        Concept(
            id="linear_equations",
            name="Linear Equations",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Equations of the form ax + b = c.",
            prerequisites=["variables_expressions", "fractions"],
            keywords=["linear", "equation", "solve", "isolate"],
            typical_misconceptions=["Not applying operations to both sides"],
            estimated_minutes=15,
        ),
        Concept(
            id="inequalities",
            name="Inequalities",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Relations using <, >, ≤, ≥ and their solutions.",
            prerequisites=["linear_equations"],
            keywords=["inequality", "less than", "greater than"],
            typical_misconceptions=["Forgetting to flip sign when multiplying by negative"],
            estimated_minutes=12,
        ),
        Concept(
            id="systems_of_equations",
            name="Systems of Linear Equations",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Multiple linear equations solved simultaneously.",
            prerequisites=["linear_equations"],
            keywords=["system", "simultaneous", "substitution", "elimination"],
            estimated_minutes=20,
        ),
        Concept(
            id="factoring",
            name="Factoring",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Breaking expressions into products of simpler expressions.",
            prerequisites=["variables_expressions", "exponents"],
            keywords=["factor", "factoring", "common factor", "grouping"],
            typical_misconceptions=["Only looking for common factors, missing patterns"],
            estimated_minutes=18,
        ),
        Concept(
            id="quadratic_equations",
            name="Quadratic Equations",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Equations of the form ax² + bx + c = 0.",
            prerequisites=["factoring", "square_roots"],
            related=["discriminant", "complex_numbers"],
            keywords=["quadratic", "parabola", "vertex", "roots", "quadratic formula"],
            typical_misconceptions=[
                "Forgetting ± in quadratic formula",
                "Confusing vertex form with standard form",
            ],
            estimated_minutes=25,
        ),
        Concept(
            id="discriminant",
            name="The Discriminant",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="b² - 4ac determines the nature of quadratic roots.",
            prerequisites=["quadratic_equations"],
            keywords=["discriminant", "b squared minus 4ac", "nature of roots"],
            estimated_minutes=10,
        ),
        Concept(
            id="polynomials",
            name="Polynomials",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Expressions with multiple terms of varying degree.",
            prerequisites=["quadratic_equations"],
            keywords=["polynomial", "degree", "coefficient", "leading term"],
            estimated_minutes=20,
        ),
        Concept(
            id="complex_numbers",
            name="Complex Numbers",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.ADVANCED,
            description="Numbers of the form a + bi where i² = -1.",
            prerequisites=["quadratic_equations", "square_roots"],
            keywords=["complex", "imaginary", "real part", "imaginary part", "i"],
            typical_misconceptions=["Imaginary numbers aren't 'real' mathematics"],
            estimated_minutes=20,
        ),
        # --- Functions ---
        Concept(
            id="functions",
            name="Functions",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Mappings from inputs to outputs: f(x).",
            prerequisites=["variables_expressions", "linear_equations"],
            keywords=["function", "domain", "range", "mapping", "f(x)"],
            typical_misconceptions=["Confusing f(x) with f times x"],
            estimated_minutes=18,
        ),
        Concept(
            id="function_transformations",
            name="Function Transformations",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Shifting, scaling, reflecting, and stretching graphs.",
            prerequisites=["functions"],
            keywords=["shift", "scale", "reflect", "transform", "translation"],
            estimated_minutes=15,
        ),
        Concept(
            id="logarithms",
            name="Logarithms",
            domain=MathDomain.ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="The inverse of exponentiation: log_b(x) = y means b^y = x.",
            prerequisites=["exponents", "functions"],
            keywords=["logarithm", "log", "ln", "natural log", "base"],
            typical_misconceptions=["log(a+b) = log(a) + log(b)"],
            estimated_minutes=20,
        ),
        # --- Geometry ---
        Concept(
            id="basic_geometry",
            name="Basic Geometry",
            domain=MathDomain.GEOMETRY,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Points, lines, angles, and basic shapes.",
            prerequisites=["arithmetic_basics"],
            keywords=["point", "line", "angle", "triangle", "circle", "polygon"],
            estimated_minutes=15,
        ),
        Concept(
            id="coordinate_geometry",
            name="Coordinate Geometry",
            domain=MathDomain.GEOMETRY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Geometry on the Cartesian plane: distance, midpoint, slope.",
            prerequisites=["basic_geometry", "linear_equations"],
            keywords=["coordinate", "cartesian", "slope", "distance", "midpoint"],
            estimated_minutes=18,
        ),
        Concept(
            id="pythagorean_theorem",
            name="Pythagorean Theorem",
            domain=MathDomain.GEOMETRY,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="a² + b² = c² for right triangles.",
            prerequisites=["basic_geometry", "square_roots"],
            keywords=["pythagorean", "hypotenuse", "right triangle"],
            estimated_minutes=12,
        ),
        # --- Trigonometry ---
        Concept(
            id="trigonometric_ratios",
            name="Trigonometric Ratios",
            domain=MathDomain.TRIGONOMETRY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="sin, cos, tan as ratios in right triangles.",
            prerequisites=["pythagorean_theorem", "fractions"],
            keywords=["sine", "cosine", "tangent", "soh cah toa", "trig"],
            typical_misconceptions=["Confusing which ratio is which"],
            estimated_minutes=18,
        ),
        Concept(
            id="unit_circle",
            name="The Unit Circle",
            domain=MathDomain.TRIGONOMETRY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Trig functions defined on the circle of radius 1.",
            prerequisites=["trigonometric_ratios", "coordinate_geometry"],
            keywords=["unit circle", "radians", "degrees", "pi"],
            estimated_minutes=20,
        ),
        Concept(
            id="trig_identities",
            name="Trigonometric Identities",
            domain=MathDomain.TRIGONOMETRY,
            difficulty=DifficultyLevel.ADVANCED,
            description="Fundamental trig relationships: sin²+cos²=1, double angle, etc.",
            prerequisites=["unit_circle"],
            keywords=["identity", "double angle", "sum formula", "pythagorean identity"],
            estimated_minutes=25,
        ),
        # --- Calculus ---
        Concept(
            id="limits",
            name="Limits",
            domain=MathDomain.CALCULUS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="The value a function approaches as input approaches a point.",
            prerequisites=["functions"],
            keywords=["limit", "approaches", "continuity", "epsilon-delta"],
            typical_misconceptions=["The limit equals the function value at that point"],
            estimated_minutes=22,
        ),
        Concept(
            id="derivatives",
            name="Derivatives",
            domain=MathDomain.CALCULUS,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Rate of change of a function — the slope at every point.",
            prerequisites=["limits", "polynomials"],
            keywords=["derivative", "differentiation", "rate of change", "slope", "tangent"],
            typical_misconceptions=[
                "Derivative is the same as the function value",
                "Power rule applies to all functions",
            ],
            estimated_minutes=25,
        ),
        Concept(
            id="chain_rule",
            name="Chain Rule",
            domain=MathDomain.CALCULUS,
            difficulty=DifficultyLevel.ADVANCED,
            description="Differentiating compositions of functions.",
            prerequisites=["derivatives"],
            keywords=["chain rule", "composite function", "inner outer"],
            estimated_minutes=18,
        ),
        Concept(
            id="integrals",
            name="Integrals",
            domain=MathDomain.CALCULUS,
            difficulty=DifficultyLevel.ADVANCED,
            description="Accumulation of quantities — area under a curve.",
            prerequisites=["derivatives"],
            keywords=["integral", "integration", "antiderivative", "area"],
            typical_misconceptions=["Integration is just the reverse of differentiation (missing +C)"],
            estimated_minutes=28,
        ),
        Concept(
            id="fundamental_theorem",
            name="Fundamental Theorem of Calculus",
            domain=MathDomain.CALCULUS,
            difficulty=DifficultyLevel.ADVANCED,
            description="Links differentiation and integration as inverse processes.",
            prerequisites=["integrals"],
            keywords=["fundamental theorem", "FTC", "antiderivative"],
            estimated_minutes=20,
        ),
        # --- Linear Algebra ---
        Concept(
            id="vectors",
            name="Vectors",
            domain=MathDomain.LINEAR_ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Quantities with magnitude and direction.",
            prerequisites=["coordinate_geometry"],
            keywords=["vector", "magnitude", "direction", "component"],
            estimated_minutes=15,
        ),
        Concept(
            id="matrices",
            name="Matrices",
            domain=MathDomain.LINEAR_ALGEBRA,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Rectangular arrays of numbers and their operations.",
            prerequisites=["vectors", "systems_of_equations"],
            keywords=["matrix", "row", "column", "multiplication", "transpose"],
            typical_misconceptions=["Matrix multiplication is commutative"],
            estimated_minutes=22,
        ),
        Concept(
            id="determinants",
            name="Determinants",
            domain=MathDomain.LINEAR_ALGEBRA,
            difficulty=DifficultyLevel.ADVANCED,
            description="A scalar value encoding properties of a square matrix.",
            prerequisites=["matrices"],
            keywords=["determinant", "det", "cofactor", "minor"],
            estimated_minutes=18,
        ),
        Concept(
            id="eigenvalues",
            name="Eigenvalues & Eigenvectors",
            domain=MathDomain.LINEAR_ALGEBRA,
            difficulty=DifficultyLevel.ADVANCED,
            description="Vectors that only scale (don't rotate) under a transformation.",
            prerequisites=["determinants", "polynomials"],
            keywords=["eigenvalue", "eigenvector", "characteristic polynomial", "spectrum"],
            typical_misconceptions=["Eigenvectors are unique (they're not — any scalar multiple works)"],
            estimated_minutes=30,
        ),
        # --- Probability ---
        Concept(
            id="basic_probability",
            name="Basic Probability",
            domain=MathDomain.PROBABILITY,
            difficulty=DifficultyLevel.ELEMENTARY,
            description="Likelihood of events occurring.",
            prerequisites=["fractions", "percentages"],
            keywords=["probability", "event", "outcome", "sample space"],
            typical_misconceptions=["Gambler's fallacy"],
            estimated_minutes=15,
        ),
        Concept(
            id="combinations_permutations",
            name="Combinations & Permutations",
            domain=MathDomain.PROBABILITY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            description="Counting arrangements with and without order.",
            prerequisites=["basic_probability", "factoring"],
            keywords=["combination", "permutation", "factorial", "choose", "nCr"],
            typical_misconceptions=["Confusing when order matters"],
            estimated_minutes=18,
        ),
    ]
