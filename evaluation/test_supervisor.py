import asyncio
import os
import sys

# Ensure project root is on the import path when running tests directly
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from week5.agent_supervisor import Supervisor

async def run_test():
    sup = Supervisor(concurrency=2)

    async def fast_agent(msg):
        await asyncio.sleep(0.01)
        return f"fast:{msg}"

    async def slow_agent(msg):
        await asyncio.sleep(0.2)
        return f"slow:{msg}"

    sup.register("fast", fast_agent)
    sup.register("slow", slow_agent)

    # delegate_first_response should return fast agent's result
    res = await sup.delegate_first_response(["slow", "fast"], "ping", timeout=1.0)
    assert res.success and res.agent == "fast", f"Expected fast agent, got {res}"

    # dispatch with short timeout should fail for slow agent
    res2 = await sup.dispatch("slow", "ping", timeout=0.05, retries=0)
    assert not res2.success, "Expected timeout failure for slow agent"

    print("test_supervisor: OK")

if __name__ == '__main__':
    asyncio.run(run_test())
