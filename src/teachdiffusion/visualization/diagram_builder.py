"""Diagram Builder — generates static math diagrams.

Creates number lines, coordinate planes, geometric shapes, and
other visual aids as SVG or PNG images.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class DiagramSpec:
    """Specification for a static diagram."""

    diagram_type: str  # "number_line", "coordinate_plane", "venn", "tree"
    title: str = ""
    labels: list[str] | None = None
    points: list[tuple[float, float]] | None = None
    annotations: list[str] | None = None
    width: int = 800
    height: int = 400


class DiagramBuilder:
    """Generates static math diagrams as SVG.

    Usage:
        builder = DiagramBuilder(output_dir="./outputs/diagrams")
        svg_path = builder.build_number_line(
            points=[-2, 0, 1, 3],
            labels=["a", "0", "1", "b"],
            title="Number Line"
        )
    """

    def __init__(self, output_dir: str = "./outputs/diagrams") -> None:
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def build_number_line(
        self,
        points: list[float],
        labels: list[str] | None = None,
        title: str = "Number Line",
        range_start: float = -5,
        range_end: float = 5,
    ) -> str:
        """Build a number line SVG with marked points."""
        width, height = 800, 150
        margin = 60
        line_y = height // 2

        # Scale x coordinates
        scale = (width - 2 * margin) / (range_end - range_start)

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            f'<rect width="{width}" height="{height}" fill="white"/>',
            # Main line
            f'<line x1="{margin}" y1="{line_y}" x2="{width - margin}" y2="{line_y}" '
            f'stroke="black" stroke-width="2"/>',
            # Arrowheads
            f'<polygon points="{width - margin},{line_y} {width - margin - 10},{line_y - 5} '
            f'{width - margin - 10},{line_y + 5}" fill="black"/>',
        ]

        # Tick marks and labels for integer positions
        for i in range(int(range_start), int(range_end) + 1):
            x = margin + (i - range_start) * scale
            svg_parts.append(
                f'<line x1="{x}" y1="{line_y - 5}" x2="{x}" y2="{line_y + 5}" '
                f'stroke="black" stroke-width="1"/>'
            )
            svg_parts.append(
                f'<text x="{x}" y="{line_y + 20}" text-anchor="middle" '
                f'font-size="12" fill="gray">{i}</text>'
            )

        # Plot specified points
        labels = labels or [str(p) for p in points]
        for point, label in zip(points, labels):
            x = margin + (point - range_start) * scale
            svg_parts.append(
                f'<circle cx="{x}" cy="{line_y}" r="5" fill="blue"/>'
            )
            svg_parts.append(
                f'<text x="{x}" y="{line_y - 15}" text-anchor="middle" '
                f'font-size="14" fill="blue" font-weight="bold">{label}</text>'
            )

        # Title
        svg_parts.append(
            f'<text x="{width // 2}" y="20" text-anchor="middle" '
            f'font-size="16" fill="black" font-weight="bold">{title}</text>'
        )

        svg_parts.append("</svg>")
        svg = "\n".join(svg_parts)

        output_path = self._output_dir / f"{title.replace(' ', '_').lower()}.svg"
        with open(output_path, "w") as f:
            f.write(svg)

        return str(output_path)

    def build_coordinate_plane(
        self,
        points: list[tuple[float, float]] | None = None,
        labels: list[str] | None = None,
        title: str = "Coordinate Plane",
    ) -> str:
        """Build a coordinate plane SVG with optional plotted points."""
        width, height = 500, 500
        center_x, center_y = width // 2, height // 2
        scale = 40  # pixels per unit

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            f'<rect width="{width}" height="{height}" fill="white"/>',
            # Grid lines
        ]

        for i in range(-5, 6):
            x = center_x + i * scale
            y = center_y - i * scale
            opacity = "0.15" if i != 0 else "0"
            svg_parts.append(
                f'<line x1="{x}" y1="20" x2="{x}" y2="{height - 20}" '
                f'stroke="gray" stroke-width="1" opacity="{opacity}"/>'
            )
            svg_parts.append(
                f'<line x1="20" y1="{y}" x2="{width - 20}" y2="{y}" '
                f'stroke="gray" stroke-width="1" opacity="{opacity}"/>'
            )

        # Axes
        svg_parts.extend([
            f'<line x1="20" y1="{center_y}" x2="{width - 20}" y2="{center_y}" stroke="black" stroke-width="2"/>',
            f'<line x1="{center_x}" y1="20" x2="{center_x}" y2="{height - 20}" stroke="black" stroke-width="2"/>',
            f'<text x="{width - 15}" y="{center_y - 8}" font-size="14" fill="black">x</text>',
            f'<text x="{center_x + 8}" y="18" font-size="14" fill="black">y</text>',
        ])

        # Plot points
        if points:
            labels = labels or [f"P{i}" for i in range(len(points))]
            for (px, py), label in zip(points, labels):
                sx = center_x + px * scale
                sy = center_y - py * scale
                svg_parts.append(f'<circle cx="{sx}" cy="{sy}" r="5" fill="red"/>')
                svg_parts.append(
                    f'<text x="{sx + 8}" y="{sy - 8}" font-size="12" fill="red">'
                    f'{label} ({px},{py})</text>'
                )

        svg_parts.append(
            f'<text x="{width // 2}" y="{height - 5}" text-anchor="middle" '
            f'font-size="14" fill="black">{title}</text>'
        )
        svg_parts.append("</svg>")

        svg = "\n".join(svg_parts)
        output_path = self._output_dir / f"{title.replace(' ', '_').lower()}.svg"
        with open(output_path, "w") as f:
            f.write(svg)

        return str(output_path)
