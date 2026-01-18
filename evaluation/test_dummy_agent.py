"""
Test harness to exercise the DummyAgent logic offline.
Run: python evaluation/test_dummy_agent.py
"""
import asyncio
from pathlib import Path
import importlib.util

# Load `research_assistant.py` by path because the package name contains a hyphen
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RA_PATH = PROJECT_ROOT / 'research-assistant' / 'researchassistant.py'
spec = importlib.util.spec_from_file_location('research_assistant_mod', str(RA_PATH))
ra = importlib.util.module_from_spec(spec)
import sys
# Ensure the research-assistant folder is on sys.path for relative imports
ra_dir = str(RA_PATH.parent)
if ra_dir not in sys.path:
    sys.path.insert(0, ra_dir)
spec.loader.exec_module(ra)

search_web = ra.search_web
synthesize_findings = ra.synthesize_findings
cite_sources = ra.cite_sources

class DummyAgentTest:
    def __init__(self, tools):
        self.tools = tools
    def get_new_thread(self):
        return {}
    async def run_stream(self, user_input, thread=None):
        class Chunk:
            def __init__(self, text):
                self.text = text
        # Acknowledge
        yield Chunk(f"(test) Received: {user_input}\n")
        await asyncio.sleep(0.02)
        text = user_input.lower()
        if any(k in text for k in ('cite', 'citation', 'references')):
            try:
                citation = cite_sources(user_input, style='APA')
            except Exception as e:
                citation = f"(test) cite_sources error: {e}"
            yield Chunk("(test) Citations:\n")
            await asyncio.sleep(0.01)
            yield Chunk(citation)
            return
        if any(k in text for k in ('what is', 'who is', 'tell me about', 'search', 'find', 'explain', 'overview', 'describe')):
            try:
                search_res = search_web(user_input)
            except Exception as e:
                search_res = f"(test) search_web error: {e}"
            yield Chunk("(test) Search results:\n")
            await asyncio.sleep(0.01)
            yield Chunk(search_res[:400])
            await asyncio.sleep(0.01)
            try:
                synth = synthesize_findings(user_input, sources=2)
            except Exception as e:
                synth = f"(test) synthesize_findings error: {e}"
            yield Chunk("\n(test) Synthesized:\n")
            await asyncio.sleep(0.01)
            yield Chunk(synth)
            return
        # fallback
        try:
            search_res = search_web(user_input)
        except Exception as e:
            search_res = f"(test) search_web error: {e}"
        yield Chunk(search_res[:300])
        await asyncio.sleep(0.01)
        try:
            synth = synthesize_findings(user_input, sources=1)
        except Exception as e:
            synth = f"(test) synthesize_findings error: {e}"
        yield Chunk("\n\n" + synth)

async def run_test():
    agent = DummyAgentTest(tools=[search_web, synthesize_findings, cite_sources])
    async for chunk in agent.run_stream('Tell me about Python programming language'):
        print(chunk.text, end='')
    print('\n---')
    async for chunk in agent.run_stream('Provide citations for research assistant'):
        print(chunk.text, end='')

if __name__ == '__main__':
    asyncio.run(run_test())
