"""Compact multi-agent supervisor (optimized) - core features only."""
from typing import Dict, List
from dataclasses import dataclass, field
import time, uuid

@dataclass
class Task:
    id: str
    type: str
    description: str
    priority: int = 0

class CompactSupervisor:
    def __init__(self, name: str, comm):
        self.name = name
        self.comm = comm
        self.workers: Dict[str, Dict] = {}

    def register_worker(self, wid: str, capabilities: List[str]):
        self.workers[wid] = {'capabilities': capabilities, 'status': 'available', 'tasks': 0}

    def decompose(self, task: Task):
        if task.type == 'research':
            return [Task(str(uuid.uuid4()), 'search', 'gather'), Task(str(uuid.uuid4()), 'analyze', 'analyze')]
        return [Task(str(uuid.uuid4()), 'exec', task.description)]

    def select_worker(self, task: Task):
        candidates = [w for w,i in self.workers.items() if i['status']=='available' and task.type in i['capabilities']]
        if not candidates:
            candidates = [w for w,i in self.workers.items() if i['status']=='available']
        return min(candidates, key=lambda w: self.workers[w]['tasks']) if candidates else None

    def assign(self, task: Task, worker: str):
        self.workers[worker]['status']='busy'
        self.workers[worker]['tasks'] += 1
        # send minimal message
        self.comm.send({'from': self.name, 'to': worker, 'task': task.id})

    def run(self, task: Task):
        subs = self.decompose(task)
        results = []
        for s in subs:
            w = self.select_worker(s)
            if not w:
                results.append({'success': False, 'summary': 'no worker'})
                continue
            self.assign(s, w)
            # simulate quick work
            time.sleep(0.001)
            results.append({'success': True, 'summary': f'{s.type} done'})
            # free worker
            self.workers[w]['status']='available'
        return {'task': task.id, 'results': results}
