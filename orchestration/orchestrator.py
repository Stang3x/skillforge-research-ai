"""
Orchestration adapter: thin wrapper around integrated multi-agent coordination module.
"""
from pathlib import Path
import sys
# Ensure reference modules are importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reference-repositories' / 'agent_skills' / 'multi-agent-patterns'))

from scripts.coordination import AgentCommunication, SupervisorAgent, HandoffProtocol

def make_orchestrator(name: str = 'coordinator'):
    comm = AgentCommunication()
    supervisor = SupervisorAgent(name=name, communication=comm)
    handoff = HandoffProtocol(communication=comm)
    return {
        'communication': comm,
        'supervisor': supervisor,
        'handoff': handoff
    }

if __name__ == '__main__':
    o = make_orchestrator()
    print('Orchestrator initialized with supervisor:', o['supervisor'].name)
