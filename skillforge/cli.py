"""CLI interface for SkillForge Research AI."""

import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

from skillforge.skills import skill_registry, SkillInput
from skillforge.skills.research import ResearchSkill
from skillforge.skills.synthesis import SynthesisSkill
from skillforge.skills.citation import CitationSkill
from skillforge.skills.methodology import MethodologySkill
from skillforge.skills.evaluation import EvaluationSkill
from skillforge.citation import CitationStyle

console = Console()


def initialize_skills(use_mock: bool = False):
    """Initialize and register all available skills."""
    skill_registry.register(ResearchSkill(use_mock=use_mock))
    skill_registry.register(SynthesisSkill())
    skill_registry.register(CitationSkill(style=CitationStyle.APA))
    skill_registry.register(MethodologySkill())
    skill_registry.register(EvaluationSkill())


@click.group()
@click.version_option(version="0.1.0")
def main():
    """SkillForge Research AI - A local-first AI research assistant."""
    pass


@main.command()
def list_skills():
    """List all available skills."""
    initialize_skills()

    table = Table(title="Available Skills")
    table.add_column("Skill Name", style="cyan")
    table.add_column("Description", style="green")

    for skill_name, skill in skill_registry.get_all().items():
        table.add_row(skill_name, skill.description)

    console.print(table)


@main.command()
@click.argument("query")
@click.option("--mock", is_flag=True, help="Use mock data for offline testing")
@click.option("--max-results", default=10, help="Maximum number of search results")
@click.option("--no-academic", is_flag=True, help="Exclude academic sources")
def research(query: str, mock: bool, max_results: int, no_academic: bool):
    """Perform research on a topic."""
    initialize_skills(use_mock=mock)

    async def _research():
        console.print(Panel(f"[bold cyan]Researching:[/bold cyan] {query}"))

        research_skill = skill_registry.get("research")
        if not research_skill:
            console.print("[red]Error: Research skill not found[/red]")
            return

        skill_input = SkillInput(
            query=query,
            options={
                "max_results": max_results,
                "include_academic": not no_academic,
            },
        )

        with console.status("[bold green]Searching..."):
            result = await research_skill.execute(skill_input)

        if result.success:
            console.print(f"\n[green]✓ Found {result.data['count']} results[/green]\n")

            for i, res in enumerate(result.data["results"], 1):
                console.print(f"[bold]{i}. {res['title']}[/bold]")
                console.print(f"   [dim]{res['url']}[/dim]")
                console.print(f"   {res['snippet'][:150]}...")
                console.print(f"   [cyan]Source: {res['source']}[/cyan]\n")
        else:
            console.print(f"[red]Error: {result.error}[/red]")

    asyncio.run(_research())


@main.command()
@click.argument("query")
@click.option("--mock", is_flag=True, help="Use mock data for offline testing")
@click.option("--citation-style", default="apa", help="Citation style (apa/mla/chicago)")
def full_research(query: str, mock: bool, citation_style: str):
    """Perform full research workflow with synthesis and citations."""
    initialize_skills(use_mock=mock)

    async def _full_research():
        console.print(Panel(f"[bold cyan]Full Research Workflow:[/bold cyan] {query}"))

        # Step 1: Research
        console.print("\n[bold]Step 1: Gathering information...[/bold]")
        research_skill = skill_registry.get("research")
        research_input = SkillInput(query=query, options={"max_results": 10})

        with console.status("[bold green]Searching..."):
            research_result = await research_skill.execute(research_input)

        if not research_result.success:
            console.print(f"[red]Error: {research_result.error}[/red]")
            return

        results = research_result.data["results"]
        console.print(f"[green]✓ Found {len(results)} sources[/green]")

        # Step 2: Synthesis
        console.print("\n[bold]Step 2: Synthesizing findings...[/bold]")
        synthesis_skill = skill_registry.get("synthesis")
        synthesis_input = SkillInput(query=query, context={"results": results})

        with console.status("[bold green]Analyzing..."):
            synthesis_result = await synthesis_skill.execute(synthesis_input)

        if synthesis_result.success:
            console.print("[green]✓ Synthesis complete[/green]\n")
            console.print(Panel(synthesis_result.data["summary"], title="Summary"))

            console.print("\n[bold]Key Findings:[/bold]")
            for i, finding in enumerate(synthesis_result.data["key_findings"][:5], 1):
                console.print(f"{i}. {finding}")

            console.print(f"\n[bold]Themes:[/bold] {', '.join(synthesis_result.data['themes'])}")

        # Step 3: Evaluation
        console.print("\n[bold]Step 3: Evaluating sources...[/bold]")
        eval_skill = skill_registry.get("evaluation")
        eval_input = SkillInput(query=query, context={"results": results})

        with console.status("[bold green]Evaluating..."):
            eval_result = await eval_skill.execute(eval_input)

        if eval_result.success:
            console.print("[green]✓ Evaluation complete[/green]\n")
            eval_data = eval_result.data

            console.print(f"Total Sources: {eval_data['total_sources']}")
            console.print(
                f"Average Credibility: {eval_data['average_credibility']}/100"
            )
            console.print(f"Assessment: {eval_data['credibility_assessment']}\n")

            console.print("[bold]Recommendations:[/bold]")
            for rec in eval_data["recommendations"]:
                console.print(f"  • {rec}")

        # Step 4: Citations
        console.print(f"\n[bold]Step 4: Generating {citation_style.upper()} citations...[/bold]")
        citation_skill = skill_registry.get("citation")
        citation_input = SkillInput(
            query=query,
            context={"results": results},
            options={"style": citation_style},
        )

        with console.status("[bold green]Formatting citations..."):
            citation_result = await citation_skill.execute(citation_input)

        if citation_result.success:
            console.print("[green]✓ Citations generated[/green]\n")
            console.print(Panel(citation_result.data["bibliography"], title="Bibliography"))

    asyncio.run(_full_research())


@main.command()
@click.argument("topic")
@click.option("--research-type", default="general", help="Research type (general/quantitative/qualitative)")
def methodology(topic: str, research_type: str):
    """Get research methodology recommendations."""
    initialize_skills()

    async def _methodology():
        console.print(Panel(f"[bold cyan]Research Methodology for:[/bold cyan] {topic}"))

        method_skill = skill_registry.get("methodology")
        skill_input = SkillInput(query=topic, options={"research_type": research_type})

        with console.status("[bold green]Generating methodology..."):
            result = await method_skill.execute(skill_input)

        if result.success:
            data = result.data
            console.print(f"\n[bold]Research Type:[/bold] {data['research_type']}\n")

            console.print("[bold]Core Steps:[/bold]")
            for i, step in enumerate(data["core_steps"], 1):
                console.print(f"{i}. {step}")

            console.print("\n[bold]Specific Methods:[/bold]")
            for i, method in enumerate(data["specific_methods"], 1):
                console.print(f"{i}. {method}")

            console.print("\n[bold]Best Practices:[/bold]")
            for practice in data["best_practices"]:
                console.print(f"  • {practice}")
        else:
            console.print(f"[red]Error: {result.error}[/red]")

    asyncio.run(_methodology())


if __name__ == "__main__":
    main()
