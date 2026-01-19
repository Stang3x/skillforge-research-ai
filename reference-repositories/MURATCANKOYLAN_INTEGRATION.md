# Muratcankoylan Context Engineering Integration Guide

**Integration Date:** January 17, 2026  
**Status:** Ready for Implementation  
**Target Completion:** Week 4 (Jan 20-26)

---

## 1. Quick Start: 3-Skill Integration for Week 4

### Step 1: Clone the Repository (30 minutes)
```bash
cd reference-repositories/
git clone https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering.git
cd Agent-Skills-for-Context-Engineering
ls -la skills/  # Verify all 13 skills present
```

### Step 2: Extract Priority Skills (15 minutes)
Copy these 3 skills to your research-assistant project:
```bash
# Create learning folder
mkdir research-assistant/skills-reference/

# Copy critical skills
cp skills/context-optimization/SKILL.md research-assistant/skills-reference/context-optimization.md
cp skills/advanced-evaluation/SKILL.md research-assistant/skills-reference/advanced-evaluation.md
cp skills/multi-agent-patterns/SKILL.md research-assistant/skills-reference/multi-agent-patterns.md
```

### Step 3: Load External Skills in Your Skill Loader (45 minutes)

**File to Modify:** `research-assistant/skill_loader.py`

**Current Code (lines 1-30):**
```python
import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, List

SKILLS_DIR = Path("skills")

@dataclass
class Skill:
    name: str
    description: str
    content: str
    filepath: Path
```

**New Code (Add reference skills support):**
```python
import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, List

SKILLS_DIR = Path("skills")
REFERENCE_SKILLS_DIR = Path("skills-reference")  # NEW: External skills

@dataclass
class Skill:
    name: str
    description: str
    content: str
    filepath: Path
    is_reference: bool = False  # NEW: Track if external skill
```

**Update `_load_skills()` method (NEW):**
```python
def _load_skills(self):
    """Load both local and reference skills"""
    self.skills = {}
    
    # Load local skills (existing)
    if SKILLS_DIR.exists():
        for skill_file in SKILLS_DIR.glob("*.md"):
            skill = self._parse_skill_file(skill_file, is_reference=False)
            if skill:
                self.skills[skill.name] = skill
    
    # Load reference skills (NEW)
    if REFERENCE_SKILLS_DIR.exists():
        for skill_file in REFERENCE_SKILLS_DIR.glob("*.md"):
            skill = self._parse_skill_file(skill_file, is_reference=True)
            if skill:
                self.skills[skill.name] = skill
    
    return self.skills
```

---

## 2. Week 4 Implementation Tasks

### Task 1: Context Optimization (Caching Layer)
**Skill Source:** `skills-reference/context-optimization.md`  
**Time:** 3-4 hours

**What to Build:**
```python
# research-assistant/caching.py (NEW)

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

class SearchResultCache:
    def __init__(self, cache_dir="cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(days=7)  # 7-day cache
    
    def get_cache_key(self, query: str) -> str:
        """Hash query to create cache key"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get(self, query: str) -> Optional[List[dict]]:
        """Retrieve cached results if fresh"""
        key = self.get_cache_key(query)
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        # Check if cache expired
        age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
        if age > self.ttl:
            cache_file.unlink()
            return None
        
        with open(cache_file) as f:
            return json.load(f)
    
    def set(self, query: str, results: List[dict]):
        """Store search results in cache"""
        key = self.get_cache_key(query)
        cache_file = self.cache_dir / f"{key}.json"
        
        with open(cache_file, 'w') as f:
            json.dump(results, f)

# In researchassistant.py
cache = SearchResultCache()

async def search_web(query: str) -> str:
    # Check cache first
    cached = cache.get(query)
    if cached:
        return format_results(cached)  # Skip API call
    
    # Call real API if not cached
    results = await call_google_search_api(query)
    cache.set(query, results)  # Store for next time
    return format_results(results)
```

**Success Criteria:**
- [ ] Cache directory creates automatically
- [ ] Same query within 7 days returns cached results instantly
- [ ] Cache expires after 7 days
- [ ] Benchmarks show 50-80% faster repeat queries

---

### Task 2: Advanced Evaluation (LLM-as-Judge Benchmarking)
**Skill Source:** `skills-reference/advanced-evaluation.md`  
**Time:** 3-4 hours

**What to Build:**
```python
# research-assistant/evaluator.py (NEW)

from agent_framework import ChatAgent
from typing import Tuple

class ResearchEvaluator:
    def __init__(self, model_id="openai/gpt-4o-mini"):
        self.evaluator_agent = ChatAgent(model_id=model_id)
    
    async def evaluate_accuracy(self, response: str, expected_facts: List[str]) -> float:
        """
        LLM-as-Judge: Rate accuracy of response
        Returns: 1.0-5.0 scale
        """
        rubric = """
        Rate this research response on accuracy (1-5):
        1 = Contains significant factual errors
        2 = Some errors, mostly accurate
        3 = Accurate with minor issues
        4 = Accurate with proper citations
        5 = Highly accurate, well-researched, properly cited
        
        Consider these expected facts:
        {facts}
        
        Response: {response}
        
        Rate only 1-5:
        """.format(facts="\n".join(expected_facts), response=response)
        
        score = await self.evaluator_agent.complete(rubric)
        return float(score.strip()[:1])  # Extract first digit
    
    async def evaluate_completeness(self, response: str, required_sections: List[str]) -> float:
        """
        LLM-as-Judge: Rate completeness
        Returns: 1.0-5.0 scale
        """
        rubric = f"""
        Rate this research response on completeness (1-5):
        1 = Missing most required sections
        2 = Missing several sections
        3 = Has most sections
        4 = All sections present
        5 = All sections present + bonus analysis
        
        Required sections: {', '.join(required_sections)}
        Response: {response}
        
        Rate only 1-5:
        """
        
        score = await self.evaluator_agent.complete(rubric)
        return float(score.strip()[:1])
    
    async def pairwise_compare(self, response_a: str, response_b: str, criteria: str) -> Tuple[str, float]:
        """
        Compare two responses, mitigate position bias
        Returns: (winner, confidence)
        """
        # Test both orders to avoid position bias
        prompt_ab = f"""
        Compare these research responses on {criteria}:
        
        Response A: {response_a}
        Response B: {response_b}
        
        Which is better? Answer only "A" or "B":
        """
        
        prompt_ba = f"""
        Compare these research responses on {criteria}:
        
        Response A: {response_b}
        Response B: {response_a}
        
        Which is better? Answer only "A" or "B":
        """
        
        vote_1 = await self.evaluator_agent.complete(prompt_ab)
        vote_2 = await self.evaluator_agent.complete(prompt_ba)
        
        # Count votes (flip second vote back)
        winner = "A" if vote_1.strip() == "A" else "B"
        second_winner = "A" if vote_2.strip() == "B" else "B"  # Flipped
        
        if winner != second_winner:
            confidence = 0.5
            winner = "TIED"
        else:
            confidence = 1.0
        
        return winner, confidence
```

**Update test_skills.py:**
```python
# Add to test_skills.py

async def benchmark_mock_vs_real():
    """Compare mock search vs real Google Custom Search API"""
    evaluator = ResearchEvaluator()
    
    test_queries = [
        "How do I structure a literature review?",
        "What are common research biases?",
        "Best practices for APA citations?",
    ]
    
    results = {
        "mock_api": [],
        "real_api": [],
        "improvements": []
    }
    
    for query in test_queries:
        # Test mock (current)
        mock_response = await agent_mock.research(query)
        mock_accuracy = await evaluator.evaluate_accuracy(mock_response, [])
        
        # Test real (Week 4)
        real_response = await agent_real.research(query)
        real_accuracy = await evaluator.evaluate_accuracy(real_response, [])
        
        improvement = ((real_accuracy - mock_accuracy) / mock_accuracy) * 100
        
        results["mock_api"].append(mock_accuracy)
        results["real_api"].append(real_accuracy)
        results["improvements"].append(improvement)
    
    print(f"Average accuracy improvement: {sum(results['improvements'])/len(results['improvements']):.1f}%")
    return results
```

**Success Criteria:**
- [ ] Evaluator rates responses 1-5 automatically
- [ ] Pairwise comparison works (position bias mitigated)
- [ ] Benchmarking shows 20-30% improvement (accuracy, speed, or both)
- [ ] Results saved to PERFORMANCE_METRICS.md

---

### Task 3: Tool Design Optimization
**Skill Source:** `skills-reference/tool-design.md`  
**Time:** 2 hours

**Current Issue:** search_web() returns verbose HTML, wastes context tokens

**Optimization:**
```python
# In researchassistant.py

@agent.action
def search_web(query: str) -> str:
    """
    Search the web for research information.
    
    Args:
        query: Research question or topic
    
    Returns:
        JSON array of compact search results
    """
    # Old: Returns full HTML (wasteful)
    # New: Returns compact JSON
    
    results = [
        {
            "title": "Title here",
            "url": "https://...",
            "snippet": "First 100 chars only",  # TRUNCATED
            "relevance_score": 0.95  # NEW: AI-computed relevance
        },
        # ... max 3 results (not 10)
    ]
    
    import json
    return json.dumps(results, indent=2)

# In evaluator.py
def compact_results(results_list: List[dict]) -> str:
    """Keep 3 best results, discard redundancy"""
    # Token count: ~200 tokens (vs 2000+ for full HTML)
    return json.dumps(results_list[:3], separators=(',', ':'))
```

**Token Savings:**
- Before: 2000+ tokens per search result
- After: ~200 tokens per search result (10x reduction!)

**Success Criteria:**
- [ ] search_web() returns JSON only (no HTML)
- [ ] Results truncated to 3 best matches
- [ ] Snippets max 100 characters
- [ ] Relevance scores included (AI-computed)

---

## 3. Multi-Agent Architecture (Week 5)

### Design Using multi-agent-patterns Skill

**Pattern: Orchestrator**

```
┌─────────────────────────────────────────────┐
│      ResearchOrchestrator (Manager)         │
│  - Routes queries to specialists            │
│  - Combines results                         │
│  - Handles errors & fallbacks               │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌──────┐  ┌──────┐  ┌──────┐
    │Method│  │Source│  │Citation
    │Agent │  │Agent │  │Agent
    └──────┘  └──────┘  └──────┘
```

**Implementation:**
```python
# research-assistant/orchestrator.py (Week 5)

class ResearchOrchestrator(ChatAgent):
    def __init__(self):
        # Specialist agents with their own skills
        self.methodology_agent = ChatAgent(
            model_id="openai/gpt-4o-mini",
            system_instructions=self.skill_loader.get_skill("research-methodology").content
        )
        self.evaluator_agent = ChatAgent(
            model_id="openai/gpt-4o-mini",
            system_instructions=self.skill_loader.get_skill("source-evaluation").content
        )
        self.citation_agent = ChatAgent(
            model_id="openai/gpt-4o-mini",
            system_instructions=self.skill_loader.get_skill("citation-standards").content
        )
    
    async def research(self, query: str) -> str:
        """Orchestrate research across specialists"""
        
        # Step 1: Plan research methodology
        plan = await self.methodology_agent.complete(
            f"Create a research plan for: {query}"
        )
        
        # Step 2: Search and evaluate sources
        sources = await self.search_web(query)
        evaluated_sources = await self.evaluator_agent.complete(
            f"Evaluate these sources:\n{sources}"
        )
        
        # Step 3: Format citations
        citations = await self.citation_agent.complete(
            f"Format these sources:\n{evaluated_sources}"
        )
        
        return f"Plan: {plan}\n\nSources: {evaluated_sources}\n\nCitations: {citations}"
```

---

## 4. Memory Systems (Week 5+)

**Skill Source:** `skills-reference/memory-systems.md`

Implement append-only memory:
```python
# research-assistant/memory.py

class ResearchMemory:
    def __init__(self, memory_file="memory.jsonl"):
        self.memory_file = Path(memory_file)
    
    def append(self, entry: dict):
        """Append to append-only memory"""
        with open(self.memory_file, 'a') as f:
            json.dump(entry, f)
            f.write('\n')
    
    def get_all(self) -> List[dict]:
        """Read all memory entries"""
        if not self.memory_file.exists():
            return []
        
        with open(self.memory_file) as f:
            return [json.loads(line) for line in f]

# Usage
memory = ResearchMemory()
memory.append({
    "timestamp": datetime.now().isoformat(),
    "query": "how to structure literature review",
    "sources_found": 3,
    "methodology_used": "systematic review"
})
```

---

## 5. File Structure After Integration

```
research-assistant/
├── researchassistant.py          # Core agent (updated)
├── skill_loader.py                # Updated to load reference skills
├── caching.py                     # NEW (Week 4)
├── evaluator.py                   # NEW (Week 4)
├── orchestrator.py                # NEW (Week 5)
├── memory.py                      # NEW (Week 5)
├── .env
├── requirements.txt               # Add: cachetools, jsonl
├── skills/                        # Local skills
│   ├── research-methodology.md
│   ├── citation-standards.md
│   └── source-evaluation.md
├── skills-reference/              # NEW (External skills)
│   ├── context-optimization.md
│   ├── advanced-evaluation.md
│   └── multi-agent-patterns.md
├── cache/                         # NEW (Auto-created)
│   └── [hash].json               # Cached search results
└── memory.jsonl                   # NEW (Append-only memory)

reference-repositories/
└── Agent-Skills-for-Context-Engineering/  # Cloned
    ├── skills/
    │   ├── context-fundamentals/
    │   ├── advanced-evaluation/
    │   ├── multi-agent-patterns/
    │   └── ... (10 more)
    ├── examples/
    └── README.md
```

---

## 6. Testing & Validation Checklist

### Week 4 Checklist
- [ ] Clone muratcankoylan repository
- [ ] Copy 3 reference skills to skills-reference/
- [ ] Update skill_loader.py to load external skills
- [ ] Implement SearchResultCache (context-optimization)
- [ ] Implement ResearchEvaluator (advanced-evaluation)
- [ ] Optimize search_web() output (tool-design)
- [ ] Run benchmarking: mock vs real API
- [ ] Document 20-30% improvement in PERFORMANCE_METRICS.md
- [ ] Verify exit code 0 on all tests

### Week 5 Checklist
- [ ] Design orchestrator architecture (multi-agent-patterns)
- [ ] Implement MethodologyAgent, SourceAgent, CitationAgent
- [ ] Test orchestrator routing and error handling
- [ ] Implement AppendOnlyMemory (memory-systems)
- [ ] Integration tests: all agents working together
- [ ] Performance tests: orchestrator vs single agent

---

## 7. Expected Outcomes

### By End of Week 4
✅ Caching layer reduces repeat queries by 50-80%  
✅ LLM-as-Judge benchmarking shows 20-30% improvement  
✅ Tool optimization reduces tokens per search by 10x  
✅ PERFORMANCE_METRICS.md documents improvements  

### By End of Week 5
✅ Multi-agent orchestrator architecture implemented  
✅ 3 specialist agents (methodology, evaluation, citation) operational  
✅ Append-only memory tracks research history  
✅ ORCHESTRATOR.md documents architecture  

### By End of Month 1
✅ Production-ready agent system  
✅ Comprehensive skills system (from your + muratcankoylan)  
✅ Advanced evaluation and benchmarking  
✅ Clear path to multi-agent scaling (Month 2)  

---

## 8. Reference Links

**Critical Files (Priority Order):**

**Week 4 (Now):**
1. [context-optimization](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/context-optimization/SKILL.md)
2. [advanced-evaluation](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/advanced-evaluation/SKILL.md)
3. [tool-design](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/tool-design/SKILL.md)

**Week 5:**
4. [multi-agent-patterns](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/multi-agent-patterns/SKILL.md)
5. [memory-systems](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/memory-systems/SKILL.md)

**Month 2+:**
6. [hosted-agents](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/hosted-agents/SKILL.md) (serverless deployment)
7. [bdi-mental-states](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/blob/main/skills/bdi-mental-states/SKILL.md) (proactive reasoning)

**Complete Examples:**
- [llm-as-judge-skills](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/examples/llm-as-judge-skills) (TypeScript, 19 tests)
- [digital-brain-skill](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering/tree/main/examples/digital-brain-skill) (personal OS)

---

**Integration Status:** Ready to Begin  
**Estimated Effort:** 10-12 hours (Weeks 4-5)  
**Expected Impact:** 20-30% performance improvement, multi-agent foundation
