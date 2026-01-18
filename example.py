"""
Example usage of SkillForge Research AI.

This script demonstrates how to use the SkillForge Research AI system
programmatically to perform research, synthesize findings, and generate citations.
"""

import asyncio
from skillforge.skills import SkillInput
from skillforge.skills.research import ResearchSkill
from skillforge.skills.synthesis import SynthesisSkill
from skillforge.skills.citation import CitationSkill
from skillforge.skills.evaluation import EvaluationSkill
from skillforge.citation import CitationStyle


async def main():
    """Run a complete research workflow example."""
    print("=" * 80)
    print("SkillForge Research AI - Example Usage")
    print("=" * 80)

    # Topic to research
    topic = "quantum computing applications"
    print(f"\nResearching: {topic}\n")

    # Step 1: Research
    print("Step 1: Gathering information...")
    research_skill = ResearchSkill(use_mock=True)  # Use mock data for demo
    research_input = SkillInput(query=topic, options={"max_results": 5})

    research_result = await research_skill.execute(research_input)

    if research_result.success:
        results = research_result.data["results"]
        print(f"✓ Found {len(results)} sources")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['title']}")
    else:
        print(f"✗ Error: {research_result.error}")
        return

    # Step 2: Synthesis
    print("\nStep 2: Synthesizing findings...")
    synthesis_skill = SynthesisSkill()
    synthesis_input = SkillInput(query=topic, context={"results": results})

    synthesis_result = await synthesis_skill.execute(synthesis_input)

    if synthesis_result.success:
        print("✓ Synthesis complete")
        print(f"\nSummary:\n{synthesis_result.data['summary']}")
        print(f"\nKey Findings:")
        for i, finding in enumerate(synthesis_result.data["key_findings"][:3], 1):
            print(f"  {i}. {finding}")
    else:
        print(f"✗ Error: {synthesis_result.error}")

    # Step 3: Evaluation
    print("\nStep 3: Evaluating sources...")
    eval_skill = EvaluationSkill()
    eval_input = SkillInput(query=topic, context={"results": results})

    eval_result = await eval_skill.execute(eval_input)

    if eval_result.success:
        eval_data = eval_result.data
        print("✓ Evaluation complete")
        print(f"  Average Credibility: {eval_data['average_credibility']}/100")
        print(f"  Assessment: {eval_data['credibility_assessment']}")
    else:
        print(f"✗ Error: {eval_result.error}")

    # Step 4: Citations (APA format)
    print("\nStep 4: Generating citations...")
    citation_skill = CitationSkill(style=CitationStyle.APA)
    citation_input = SkillInput(
        query=topic, context={"results": results}, options={"style": "apa"}
    )

    citation_result = await citation_skill.execute(citation_input)

    if citation_result.success:
        print("✓ Citations generated")
        print(f"\nBibliography (first 2 entries):")
        for citation in citation_result.data["citations"][:2]:
            print(f"  {citation}\n")
    else:
        print(f"✗ Error: {citation_result.error}")

    print("\n" + "=" * 80)
    print("Research workflow completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
