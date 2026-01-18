"""Week 5 Supervisor

Enhancements over the starter scaffold:
- Agent registry with metadata
- Async task dispatch with timeouts and retries
- Delegation helpers (fan-out) and simple aggregation
- Concurrency control (semaphore)

This module is intentionally lightweight and designed for local-test/demo use.
"""

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional


@dataclass
class TaskResult:
    success: bool
    agent: str
    result: Optional[Any]
    error: Optional[BaseException]
    elapsed: float


class Supervisor:
    def __init__(self, concurrency: int = 8):
        self._agents: Dict[str, Callable[[Any], Any]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._semaphore = asyncio.Semaphore(concurrency)

    def register(self, name: str, handler: Callable[[Any], Any], **metadata: Any) -> None:
        """Register an agent handler (sync or async) with optional metadata."""
        self._agents[name] = handler
        self._metadata[name] = metadata

    def unregister(self, name: str) -> None:
        self._agents.pop(name, None)
        self._metadata.pop(name, None)

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())

    async def _invoke(self, name: str, message: Any, timeout: float) -> TaskResult:
        handler = self._agents.get(name)
        if handler is None:
            return TaskResult(False, name, None, ValueError("unknown agent"), 0.0)

        start = time.perf_counter()
        try:
            # run under semaphore to limit concurrency
            async with self._semaphore:
                if asyncio.iscoroutinefunction(handler):
                    coro = handler(message)
                else:
                    # wrap sync handler
                    async def _wrap():
                        return handler(message)

                    coro = _wrap()

                result = await asyncio.wait_for(coro, timeout=timeout)

            elapsed = time.perf_counter() - start
            return TaskResult(True, name, result, None, elapsed)
        except Exception as e:
            elapsed = time.perf_counter() - start
            return TaskResult(False, name, None, e, elapsed)

    async def dispatch(self, to: str, message: Any, timeout: float = 5.0, retries: int = 1, backoff: float = 0.25) -> TaskResult:
        """Dispatch a message to a single agent with retry and timeout support."""
        last_err = None
        for attempt in range(1, retries + 2):
            res = await self._invoke(to, message, timeout)
            if res.success:
                return res
            last_err = res.error
            if attempt <= retries:
                await asyncio.sleep(backoff * attempt)

        return TaskResult(False, to, None, last_err, res.elapsed if 'res' in locals() else 0.0)

    async def delegate_first_response(self, agents: Iterable[str], message: Any, timeout: float = 5.0) -> TaskResult:
        """Fan-out to multiple agents and return the first successful response."""
        coros = [self._invoke(name, message, timeout) for name in agents]
        pending = set(map(asyncio.create_task, coros))
        try:
            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for d in done:
                    tr: TaskResult = d.result()
                    if tr.success:
                        # cancel remaining
                        for p in pending:
                            p.cancel()
                        return tr
                # no success yet; continue until pending exhausted
            # if we reach here nothing succeeded
            # pick the last failure to report
            last = None
            for t in done:
                last = t.result()
            return last or TaskResult(False, "none", None, RuntimeError("no agents responded"), 0.0)
        finally:
            for p in pending:
                p.cancel()

    async def gather_all(self, agents: Iterable[str], message: Any, timeout: float = 5.0) -> List[TaskResult]:
        """Fan-out to all agents and return all results (successful or not)."""
        coros = [self._invoke(name, message, timeout) for name in agents]
        tasks = [asyncio.create_task(c) for c in coros]
        res: List[TaskResult] = []
        for t in asyncio.as_completed(tasks):
            try:
                tr = await t
            except Exception as e:
                tr = TaskResult(False, "unknown", None, e, 0.0)
            res.append(tr)

        return res


async def demo():
    sup = Supervisor(concurrency=4)

    async def researcher(msg):
        # simulate variable latency and intermittent failure
        if "slow" in msg:
            await asyncio.sleep(0.6)
        else:
            await asyncio.sleep(0.05)
        if "fail" in msg:
            raise RuntimeError("simulated failure")
        return f"[researcher] findings for: {msg}"

    async def writer(msg):
        await asyncio.sleep(0.02)
        return f"[writer] draft: {msg}"

    def sync_analyst(msg):
        # synchronous handler example
        time.sleep(0.01)
        return f"[analyst] synthesized: {msg}"

    sup.register("researcher", researcher, role="research")
    sup.register("writer", writer, role="writer")
    sup.register("analyst", sync_analyst, role="analyst")

    print("Agents:", sup.list_agents())

    # simple dispatch with retry
    r = await sup.dispatch("researcher", "Investigate caching benefits", timeout=1.0, retries=1)
    print("dispatch result:", r)

    # dispatch that fails and demonstrates retry/backoff
    r2 = await sup.dispatch("researcher", "fail this task", timeout=0.2, retries=2)
    print("dispatch failure result:", r2)

    # fan-out and return first successful
    first = await sup.delegate_first_response(["researcher", "analyst", "writer"], "quick summary", timeout=1.0)
    print("first response:", first)

    # gather all
    all_res = await sup.gather_all(["researcher", "writer", "analyst"], "summarize model design", timeout=1.0)
    for a in all_res:
        print("gathered:", a)


if __name__ == "__main__":
    asyncio.run(demo())
