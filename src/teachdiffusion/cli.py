"""TeachDiffusion CLI — command line interface.

Usage:
    teachdiffusion generate --topic "quadratic equations"
    teachdiffusion quiz --topic "derivatives" --student student_01
    teachdiffusion info --topic "eigenvalues"
    teachdiffusion student --id student_01
"""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="teachdiffusion")
def main():
    """TeachDiffusion — Open-Source Video Diffusion for Math Education."""
    pass


@main.command()
@click.option("--topic", "-t", required=True, help="Math topic to teach")
@click.option("--student", "-s", default="", help="Student ID for personalization")
@click.option("--difficulty", "-d", default="intermediate", help="Difficulty level")
@click.option("--output", "-o", default="", help="Output file path")
@click.option("--persona", default="Professor Aria", help="Teacher persona name")
def generate(topic: str, student: str, difficulty: str, output: str, persona: str):
    """Generate a teaching video for a math topic."""
    from teachdiffusion.pipeline.orchestrator import TeachDiffusionPipeline

    console.print(f"\n[bold blue]TeachDiffusion[/bold blue] — Generating lesson on [bold]{topic}[/bold]\n")

    pipeline = TeachDiffusionPipeline()
    result = pipeline.generate_lesson(
        topic=topic,
        student_id=student,
        difficulty=difficulty,
        persona=persona,
    )

    # Display script
    console.print(Panel(f"[bold]{result.topic}[/bold]", title="Lesson Plan"))

    table = Table(title="Teaching Steps")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Type", style="green", width=18)
    table.add_column("Content", style="white")
    table.add_column("Gesture", style="yellow", width=12)
    table.add_column("Duration", style="magenta", width=8)

    for step in result.script.steps:
        table.add_row(
            str(step.step_number),
            step.step_type.value,
            step.content[:80] + ("..." if len(step.content) > 80 else ""),
            step.gesture.value,
            f"{step.duration_seconds}s",
        )

    console.print(table)
    console.print(f"\n[dim]Total duration: {result.script.total_duration_minutes:.1f} minutes[/dim]")

    if result.composite:
        console.print(f"[dim]Output: {result.composite.output_path}[/dim]")
        if result.is_stub:
            console.print("[yellow]Running in stub mode — GPU required for actual video generation.[/yellow]")

    console.print()


@main.command()
@click.option("--topic", "-t", required=True, help="Math topic to quiz on")
@click.option("--student", "-s", default="", help="Student ID")
@click.option("--questions", "-n", default=3, help="Number of questions")
def quiz(topic: str, student: str, questions: int):
    """Take a quiz on a math topic."""
    from teachdiffusion.pipeline.orchestrator import TeachDiffusionPipeline

    pipeline = TeachDiffusionPipeline()

    concept = pipeline.graph.find_concept_by_name(topic)
    concept_id = concept.id if concept else topic.lower().replace(" ", "_")

    q = pipeline.generate_quiz(concept_id, num_questions=questions)

    console.print(f"\n[bold blue]Quiz: {q.title}[/bold blue]\n")

    answers = {}
    for question in q.questions:
        console.print(f"[bold]Q{question.question_id}:[/bold] {question.question_text}")
        if question.options:
            for i, opt in enumerate(question.options):
                console.print(f"  {chr(65 + i)}) {opt}")
        answer = click.prompt("Your answer")
        answers[question.question_id] = answer
        console.print()

    result = pipeline.evaluate_quiz(q, answers, student_id=student)

    console.print(Panel(
        f"Score: [bold]{result.score:.0%}[/bold] "
        f"({result.correct_count}/{result.total_questions})",
        title="Results",
        style="green" if result.passed else "red",
    ))

    for ar in result.answers:
        icon = "✓" if ar.is_correct else "✗"
        style = "green" if ar.is_correct else "red"
        console.print(f"  [{style}]{icon}[/{style}] {ar.feedback[:100]}")

    if result.misconceptions_detected:
        console.print(f"\n[yellow]Misconceptions detected:[/yellow]")
        for m in result.misconceptions_detected:
            console.print(f"  • {m}")

    console.print()


@main.command()
@click.option("--topic", "-t", required=True, help="Math topic to look up")
def info(topic: str):
    """Get information about a math concept."""
    from teachdiffusion.pipeline.orchestrator import TeachDiffusionPipeline

    pipeline = TeachDiffusionPipeline()
    data = pipeline.get_concept_info(topic)

    if "error" in data:
        console.print(f"[red]{data['error']}[/red]")
        console.print("\nAvailable concepts:")
        for c in pipeline.graph.get_all_concepts():
            console.print(f"  • {c.name} ({c.domain.value})")
        return

    console.print(f"\n[bold blue]{data['name']}[/bold blue]")
    console.print(f"[dim]{data['domain']} · {data['difficulty']} · ~{data['estimated_minutes']} min[/dim]\n")
    console.print(f"{data['description']}\n")

    if data['intuitive_explanation']:
        console.print(Panel(data['intuitive_explanation'], title="Intuition"))

    if data['formal_definition']:
        console.print(Panel(data['formal_definition'], title="Formal Definition"))

    if data['prerequisites']:
        console.print(f"[bold]Prerequisites:[/bold] {', '.join(data['prerequisites'])}")

    if data['leads_to']:
        console.print(f"[bold]Leads to:[/bold] {', '.join(data['leads_to'])}")

    if data['misconceptions']:
        console.print(f"\n[yellow]Common Misconceptions:[/yellow]")
        for m in data['misconceptions']:
            console.print(f"  ⚠ {m}")

    console.print()


@main.command()
@click.option("--id", "student_id", required=True, help="Student ID")
def student(student_id: str):
    """View student profile and progress."""
    from teachdiffusion.pipeline.orchestrator import TeachDiffusionPipeline

    pipeline = TeachDiffusionPipeline()
    data = pipeline.get_student_info(student_id)

    console.print(f"\n[bold blue]Student: {data['student_id']}[/bold blue]")
    console.print(f"Concepts known: {data['concepts_known']}")
    console.print(f"Study time: {data['total_study_minutes']:.0f} minutes")
    console.print(f"Sessions: {data['sessions_completed']}")

    if data['known_list']:
        console.print(f"\n[bold]Known concepts:[/bold] {', '.join(data['known_list'])}")

    if data['can_learn_next']:
        console.print(f"\n[bold green]Ready to learn:[/bold green]")
        for name in data['can_learn_next']:
            console.print(f"  → {name}")

    if data['weakest']:
        console.print(f"\n[yellow]Needs review:[/yellow]")
        for w in data['weakest']:
            console.print(f"  • {w['concept']} (mastery: {w['mastery']:.0%})")

    console.print()


if __name__ == "__main__":
    main()
