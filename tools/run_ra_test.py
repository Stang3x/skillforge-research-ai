import importlib.util
import sys

path = 'research-assistant/research_assistant.py'
spec = importlib.util.spec_from_file_location('ra', path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print(mod.search_web('Python'))
print('\n---\n')
print(mod.synthesize_findings('Python', 2))
