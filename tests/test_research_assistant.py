import os
import sys
import time
import importlib.util


def _load_module():
    root = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(root, "research-assistant", "research_assistant.py")
    spec = importlib.util.spec_from_file_location("ra", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_make_snippet():
    os.environ["LOCAL_TEST"] = "1"
    m = _load_module()
    txt = "word " * 100
    s = m._make_snippet(txt, max_len=50)
    assert len(s) <= 53
    assert s.endswith("...")


def test_search_and_cache_ttl(monkeypatch):
    monkeypatch.setenv("LOCAL_TEST", "1")
    monkeypatch.setenv("CACHE_TTL_SECONDS", "1")
    m = _load_module()

    q = "python caching"
    r1 = m.search_web(q)
    assert r1 and "Python" in r1

    # immediate second call should hit cache and be identical
    r2 = m.search_web(q)
    assert r1 == r2

    # after TTL, cache should expire (sleep slightly longer)
    time.sleep(1.2)
    r3 = m.search_web(q)
    assert r3


def test_synthesize_findings():
    os.environ["LOCAL_TEST"] = "1"
    m = _load_module()
    s = m.synthesize_findings("machine learning")
    assert "SYNTHESIS" in s
