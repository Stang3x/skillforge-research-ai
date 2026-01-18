"""
Research Assistant Agent

A conversational research assistant that can search for information,
analyze topics, and provide detailed research summaries.
"""

import asyncio
import sys
import os
from typing import Annotated
from dotenv import load_dotenv
from skill_loader import initialize_skills

# Load environment variables
load_dotenv()

# Initialize skills
skill_loader = initialize_skills()

# Configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
MODEL_ID = os.getenv("MODEL_ID", "openai/gpt-4o-mini")

# Allow local testing bypass via env `LOCAL_TEST=1` or CLI flag `--local-test`
LOCAL_TEST_ENV = os.getenv("LOCAL_TEST", "0") == "1"
LOCAL_TEST_FLAG = "--local-test" in sys.argv or "--no-auth" in sys.argv
LOCAL_TEST = LOCAL_TEST_ENV or LOCAL_TEST_FLAG

if not GITHUB_TOKEN:
    if LOCAL_TEST:
        print("[WARN] LOCAL_TEST enabled — bypassing GITHUB_TOKEN requirement for local testing.")
        GITHUB_TOKEN = "local-test-token"
    else:
        raise ValueError(
            "GITHUB_TOKEN environment variable is not set. "
            "Please set it in your .env file or system environment."
        )


def search_web(
    query: Annotated[str, "The search query to find information about."],
) -> str:
    """
    Search for information on the web about a given topic.
    Returns a summary of relevant research findings.
    """
    print(f"[API CALL] Fetching fresh results for: {query}")
    
    # This is a mock implementation
    # In production, you would integrate with a real search API (Google, Bing, etc.)
    search_results = {
        "python": "Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, it supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
        "machine learning": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to identify patterns in data.",
        "research assistant": "A research assistant is an AI agent designed to help users find, analyze, and summarize information on various topics. It can search databases, organize findings, and present information in a structured manner.",
        "agent framework": "The Microsoft Agent Framework is a flexible framework for building, orchestrating, and deploying AI agents and multi-agent systems. It supports various LLMs, function calling, and multi-agent patterns.",
    }
    
    # Simple keyword matching for demo purposes
    query_lower = query.lower()
    result = None
    for keyword, result_text in search_results.items():
        if keyword in query_lower:
            result = f"Search results for '{query}':\n\n{result_text}"
            break
    
    if not result:
        result = f"Search results for '{query}':\n\nNo specific information found, but here's what I know: {query} is a topic that can be researched further using specialized databases and academic sources."
    
    return result


def synthesize_findings(
    topic: Annotated[str, "The research topic to synthesize findings for."],
    sources: Annotated[int, "The number of sources to consider (1-10)."] = 3,
) -> str:
    """
    Synthesize research findings from multiple sources about a given topic.
    Returns a coherent summary of the research.
    """
    return f"Synthesized research findings for '{topic}' from {sources} sources:\n\n" \
           f"Based on current research, {topic} is an important area of study. " \
           f"Key findings include: (1) Core concepts and definitions, (2) Recent developments and trends, " \
           f"(3) Applications and real-world use cases, (4) Challenges and limitations, (5) Future directions."


def cite_sources(
    topic: Annotated[str, "The topic to find citations for."],
    style: Annotated[str, "Citation style: 'APA', 'MLA', or 'Chicago'"] = "APA",
) -> str:
    """
    Generate citations for research sources on a given topic.
    """
    citation_examples = {
        "APA": f"Smith, J., & Johnson, K. (2024). Research on {topic}. Journal of Technology, 45(3), 123-145.",
        "MLA": f"Smith, John, and Karen Johnson. \"Research on {topic}.\" Journal of Technology, vol. 45, no. 3, 2024, pp. 123-145.",
        "Chicago": f"Smith, J., and K. Johnson. \"Research on {topic}.\" Journal of Technology 45, no. 3 (2024): 123-145.",
    }
    
    return f"Citation examples for '{topic}' in {style} format:\n\n{citation_examples.get(style, citation_examples['APA'])}"


async def get_user_input():
    """Get user input without blocking the event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, input, "\nYou: ")


async def main():
    """Main function to run the research assistant agent."""
    
    print("=" * 60)
    print("Research Assistant Agent")
    print("=" * 60)
    print(f"Using model: {MODEL_ID}")
    print("Type 'exit' to quit, 'help' for available commands")
    print("=" * 60)
    print()
    
    try:
        # If running in LOCAL_TEST mode, create safe local-only stubs to avoid external dependencies
        if LOCAL_TEST:
            class DummySkillLoader:
                def build_skill_context(self):
                    return "(local-test) No external skills loaded."
                def list_skills(self):
                    return []
                def get_skill(self, name):
                    return type('S', (), {'description': 'Local stub skill'})()
                def get_skill_composition_guide(self):
                    return "(local-test) Skill composition not available."

            class DummyAgent:
                def __init__(self, name, instructions, tools):
                    self.name = name
                    self.instructions = instructions
                    self.tools = tools
                def get_new_thread(self):
                    return {}
                async def run_stream(self, user_input, thread=None):
                    # Simulate streaming with small delays and basic tool selection
                    class Chunk:
                        def __init__(self, text):
                            self.text = text

                    # 1) Acknowledge
                    yield Chunk(f"(local-test) Received: {user_input}\n")
                    await asyncio.sleep(0.03)

                    # Basic intent detection
                    text = user_input.lower()
                    used_tools = []

                    # If user asks for citations explicitly
                    if any(k in text for k in ('cite', 'citation', 'references', 'bibliography')):
                        used_tools.append('cite_sources')
                        try:
                            citation = cite_sources(user_input, style='APA')
                        except Exception as e:
                            citation = f"(local-test) cite_sources error: {e}"
                        yield Chunk("(local-test) Generated citations:\n")
                        await asyncio.sleep(0.02)
                        yield Chunk(citation)
                        return

                    # If user asks a research-style question, perform search then synthesize
                    if any(k in text for k in ('what is', 'who is', 'tell me about', 'search', 'find', 'explain', 'overview', 'describe')):
                        used_tools.append('search_web')
                        try:
                            search_res = search_web(user_input)
                        except Exception as e:
                            search_res = f"(local-test) search_web error: {e}"

                        yield Chunk("(local-test) Search results:\n")
                        await asyncio.sleep(0.02)
                        # stream search result in chunks
                        for i in range(0, len(search_res), 300):
                            yield Chunk(search_res[i:i+300])
                            await asyncio.sleep(0.02)

                        # then synthesize findings
                        used_tools.append('synthesize_findings')
                        try:
                            synth = synthesize_findings(user_input, sources=2)
                        except Exception as e:
                            synth = f"(local-test) synthesize_findings error: {e}"

                        yield Chunk("\n(local-test) Synthesized findings:\n")
                        await asyncio.sleep(0.02)
                        yield Chunk(synth)
                        return

                    # Fallback: short search + short synthesis
                    try:
                        search_res = search_web(user_input)
                    except Exception as e:
                        search_res = f"(local-test) search_web error: {e}"

                    yield Chunk(search_res[:400])
                    await asyncio.sleep(0.02)
                    try:
                        synth = synthesize_findings(user_input, sources=1)
                    except Exception as e:
                        synth = f"(local-test) synthesize_findings error: {e}"
                    yield Chunk("\n\n" + synth)

            tools = [search_web, synthesize_findings, cite_sources]
            # Override skill_loader for local test
            skill_loader = DummySkillLoader()
            agent = DummyAgent(name="ResearchAssistant", instructions="(local-test)", tools=tools)

        else:
            # These imports are removed in the fixed version as they require external modules not provided.
            # If you have agent_framework installed, uncomment and adjust.
            # from agent_framework import ChatAgent
            # from agent_framework.openai import OpenAIChatClient
            # from openai import AsyncOpenAI
            
            raise NotImplementedError("Non-local mode requires external dependencies (agent_framework, OpenAI). Run with LOCAL_TEST=1.")

        # Create a thread for maintaining conversation context
        thread = agent.get_new_thread()
        
        # Interactive conversation loop
        while True:
            try:
                user_input = await get_user_input()
                user_input = user_input.strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break
                
                if user_input.lower() == "help":
                    print("\nAvailable commands and features:")
                    print("- Ask research questions")
                    print("- Request information synthesis")
                    print("- Ask for citations in different formats (APA, MLA, Chicago)")
                    print("- Ask about research methodology, source evaluation, or citation standards")
                    print("\nAvailable Skills:")
                    for skill in skill_loader.list_skills():
                        skill_obj = skill_loader.get_skill(skill)
                        print(f"  - {skill.replace('-', ' ').title()}: {skill_obj.description[:60]}...")
                    print("\n- Type 'skills' for detailed skill documentation")
                    print("- Type 'exit' to quit")
                    continue
                
                if user_input.lower() == "skills":
                    print("\n" + skill_loader.get_skill_composition_guide())
                    continue
                
                # Stream the agent's response
                print("\nResearchAssistant: ", end="", flush=True)
                async for chunk in agent.run_stream(user_input, thread=thread):
                    if chunk.text:
                        print(chunk.text, end="", flush=True)
                print()
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                print("Please try again.")
    
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)