from reference_repositories.agent_skills._common.comm import AgentCommunication
from reference_repositories.agent_skills.OPTIMIZED.multi_agent_supervisor import CompactSupervisor

# adapter to create comm and supervisor

def make_comm_and_supervisor():
    comm = AgentCommunication()
    sup = CompactSupervisor(name='opt', comm=comm)
    # register two workers
    sup.register_worker('w1', ['search','analyze'])
    sup.register_worker('w2', ['search'])
    return comm, sup
