"""
LRU Cache wrapper around the existing file-based SearchResultCache.

Provides a small in-memory LRU layer to speed up warm reads while keeping
the persistent JSON store as a backing store.
"""
from collections import OrderedDict
from typing import Any


class LRUCacheWrapper:
    def __init__(self, persistent_cache, capacity: int = 128):
        self.persistent = persistent_cache
        self.capacity = int(capacity)
        self.store = OrderedDict()
        # In-memory counters
        self.memory_hits = 0
        self.memory_misses = 0

    def _normalize(self, query: str) -> str:
        return query.lower().strip()

    def get(self, query: str) -> Any:
        key = self._normalize(query)
        # In-memory hit
        if key in self.store:
            val = self.store.pop(key)
            # re-insert to mark recent
            self.store[key] = val
            # record memory hit
            try:
                self.memory_hits += 1
            except Exception:
                pass
            return val

        # Fallback to persistent store
        val = None
        try:
            val = self.persistent.get(query)
        except Exception:
            val = None

        if val is not None:
            # populate memory
            self.store[key] = val
            # enforce capacity
            while len(self.store) > self.capacity:
                self.store.popitem(last=False)
        else:
            # record memory miss when fallback to persistent returned nothing
            try:
                self.memory_misses += 1
            except Exception:
                pass

        return val

    def set(self, query: str, result: Any) -> None:
        key = self._normalize(query)
        # write-through: keep in-memory and persist
        self.store[key] = result
        while len(self.store) > self.capacity:
            self.store.popitem(last=False)
        try:
            self.persistent.set(query, result)
        except Exception:
            pass

    def clear(self) -> None:
        self.store.clear()
        try:
            self.persistent.clear()
        except Exception:
            pass

    def stats(self) -> dict:
        s = {}
        try:
            s = self.persistent.stats()
        except Exception:
            s = {"entries": 0}
        s.update({
            "memory_entries": len(self.store),
            "memory_capacity": self.capacity,
            "memory_hits": getattr(self, 'memory_hits', 0),
            "memory_misses": getattr(self, 'memory_misses', 0),
        })
        return s
