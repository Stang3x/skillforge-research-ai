"""Supervisor integration demo

Wrap local research tools as supervisor agents and run an integration demo.
"""
import asyncio
import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from week5.agent_supervisor import Supervisor

# Import the local research tools from the research-assistant script.
# The repo layout uses a folder named `research-assistant` (with a hyphen),
# so import by file path to be robust.
# For robustness in CI/local-test we implement small, local versions
# of the research tool functions (copied from the research_assistant demo).

search_results = {
    "python": "Python is a high-level, interpreted programming language known for its simplicity and readability. Created by Guido van Rossum in 1991, it supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
    "machine learning": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It uses algorithms and statistical models to identify patterns in data.",
    "research assistant": "A research assistant is an AI agent designed to help users find, analyze, and summarize information on various topics. It can search databases, organize findings, and present information in a structured manner.",
    "agent framework": "The Microsoft Agent Framework is a flexible framework for building, orchestrating, and deploying AI agents and multi-agent systems. It supports various LLMs, function calling, and multi-agent patterns.",
}


def search_web(query: str) -> str:
    query_lower = query.lower()
    result = None
    for keyword, result_text in search_results.items():
        if keyword in query_lower:
            result = f"Search results for '{query}':\n\n{result_text}"
            break

    if not result:
        result = f"Search results for '{query}':\n\nNo specific information found, but here's what I know: {query} is a topic that can be researched further using specialized databases and academic sources."

    return result


def synthesize_findings(topic: str, sources: int = 3) -> str:
    return f"Synthesized research findings for '{topic}' from {sources} sources:\n\n" \
           f"Based on current research, {topic} is an important area of study. Key findings include: (1) Core concepts and definitions, (2) Recent developments and trends, " \
           f"(3) Applications and real-world use cases, (4) Challenges and limitations, (5) Future directions."


def cite_sources(topic: str, style: str = "APA") -> str:
    citation_examples = {
        "APA": f"Smith, J., & Johnson, K. (2024). Research on {topic}. Journal of Technology, 45(3), 123-145.",
        "MLA": f"Smith, John, and Karen Johnson. \"Research on {topic}.\" Journal of Technology, vol. 45, no. 3, 2024, pp. 123-145.",
        "Chicago": f"Smith, J., and K. Johnson. \"Research on {topic}.\" Journal of Technology 45, no. 3 (2024): 123-145.",
    }
    return f"Citation examples for '{topic}' in {style} format:\n\n{citation_examples.get(style, citation_examples['APA'])}"


async def run_integration_demo():
    sup = Supervisor(concurrency=4)

    # Adapter wrappers that expose the function as an async handler
    async def search_agent(msg):
        # reuse search_web (sync) in an async wrapper
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: search_web(msg))

    async def synth_agent(msg):
        loop = asyncio.get_running_loop()
        # default to 2 sources for demo
        return await loop.run_in_executor(None, lambda: synthesize_findings(msg, sources=2))

    async def cite_agent(msg):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: cite_sources(msg, style="APA"))

    sup.register("search", search_agent, role="search")
    sup.register("synthesizer", synth_agent, role="synth")
    sup.register("citation", cite_agent, role="citation")

    print("Registered agents:", sup.list_agents())

    # Fan out to search + synthesizer and take first response
    first = await sup.delegate_first_response(["search", "synthesizer"], "Explain agent orchestration in simple terms", timeout=3.0)
    print("First response:", first)

    # Gather all results for reporting
    all_res = await sup.gather_all(["search", "synthesizer", "citation"], "agent orchestration overview", timeout=3.0)
    for r in all_res:
        print("Result:", r)


if __name__ == "__main__":
    # If requested, attempt to initialize real ChatAgent-backed handlers.
    use_real = "--use-real-agents" in sys.argv
    if use_real:
        print("Attempting to initialize real ChatAgent agents (guarded). If this fails, falling back to local stubs.")
        try:
            # Lazy import heavy dependencies
            from agent_framework import ChatAgent
            from agent_framework.openai import OpenAIChatClient
            from openai import AsyncOpenAI
            # Try to import research_assistant machinery to reuse MODEL_ID and token
            ra_mod = None
            try:
                import importlib.util
                ra_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "research-assistant", "research_assistant.py")
                spec = importlib.util.spec_from_file_location("ra_module", ra_path)
                ra_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ra_mod)
            except Exception:
                ra_mod = None

            GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
            MODEL_ID = os.getenv("MODEL_ID", "openai/gpt-4o-mini")

            if not GITHUB_TOKEN:
                raise RuntimeError("GITHUB_TOKEN not found in environment — cannot initialize real agents")

            # Create clients and ChatAgent instances (wrappers)
            async_client = AsyncOpenAI(base_url="https://models.github.ai/inference", api_key=GITHUB_TOKEN)
            chat_client = OpenAIChatClient(async_client=async_client, model_id=MODEL_ID)

            # Create ChatAgent wrappers that expose an async handler accepting a message
            def make_chat_handler(name: str, instructions: str):
                agent = ChatAgent(chat_client=chat_client, name=name, instructions=instructions, tools=[search_web, synthesize_findings, cite_sources])
                async def handler(msg: str):
                    # run as synchronous gather to produce a single string result
                    thread = agent.get_new_thread()
                    collected = []
                    async for chunk in agent.run_stream(msg, thread=thread):
                        if getattr(chunk, 'text', None):
                            collected.append(chunk.text)
                    return "".join(collected)
                return handler

            # Replace registrations with real handlers
            try:
                sup = Supervisor(concurrency=4)
                sup.register("search", make_chat_handler("SearchAgent", "Use search_web tool first."), role="search")
                sup.register("synthesizer", make_chat_handler("SynthAgent", "Synthesize findings."), role="synth")
                sup.register("citation", make_chat_handler("CitationAgent", "Provide citations."), role="citation")
                print("Real ChatAgent agents initialized and registered.")
            except Exception as e:
                print(f"Failed to create ChatAgent handlers: {e}\nFalling back to local stub agents.")

        except Exception as e:
            print(f"Real agent initialization failed: {e}\nProceeding with local demo agents.")

    asyncio.run(run_integration_demo())
