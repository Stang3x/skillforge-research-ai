"""Benchmark LOC and a simple runtime comparison between original and optimized supervisor."""
import time
from pathlib import Path

orig = Path('reference-repositories/agent_skills/multi-agent-patterns/scripts/coordination.py')
opt = Path('reference-repositories/agent_skills/OPTIMIZED/multi_agent_supervisor.py')

def count_lines(p: Path):
    return sum(1 for _ in p.open('r', encoding='utf-8'))

# runtime micro-benchmark
import importlib.util
import sys
from pathlib import Path as _P

# Load comm from _common/comm.py
base = _P(__file__).resolve().parents[1] / 'reference-repositories' / 'agent_skills'
comm_path = base / '_common' / 'comm.py'
spec_comm = importlib.util.spec_from_file_location('comm_common', str(comm_path))
comm_mod = importlib.util.module_from_spec(spec_comm)
spec_comm.loader.exec_module(comm_mod)

# Load optimized supervisor
opt_path = base / 'OPTIMIZED' / 'multi_agent_supervisor.py'
spec_opt = importlib.util.spec_from_file_location('opt_sup', str(opt_path))
opt_mod = importlib.util.module_from_spec(spec_opt)
spec_opt.loader.exec_module(opt_mod)

def make_comm_and_supervisor():
    comm = comm_mod.AgentCommunication()
    sup = opt_mod.CompactSupervisor(name='opt', comm=comm)
    sup.register_worker('w1', ['search','analyze'])
    sup.register_worker('w2', ['search'])
    return comm, sup

if __name__ == '__main__':
    orig_lines = count_lines(orig)
    opt_lines = count_lines(opt)
    print(f'Original lines: {orig_lines}')
    print(f'Optimized lines: {opt_lines}')
    # runtime: run optimized supervisor a thousand times
    comm, sup = make_comm_and_supervisor()
    start = time.time()
    for i in range(1000):
        t = type('T', (), {'id': str(i), 'type': 'research', 'description': 'x'})
        sup.run(t)
    dur = time.time() - start
    print(f'Optimized runtime (1000 runs): {dur:.3f}s')
