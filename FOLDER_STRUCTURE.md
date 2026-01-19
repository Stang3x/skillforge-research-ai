# 📁 Project Folder Structure

**Established:** January 17, 2026  
**Based On:** reference-repositories/ pattern  
**Status:** ✅ Reorganized for clarity and scalability

---

## 🏗️ Root Directory Structure

```
Gemini projects/
├── documentation/              # All docs, guides, analysis
│   ├── ROADMAP.md             # Master implementation timeline
│   ├── PRIORITIES.md          # Critical/High priority tasks
│   ├── ANALYSIS_COMPLETE.md   # Analysis documentation
│   └── guides/                # Implementation guides
│
├── research-assistant/        # Main agent application
│   ├── researchassistant.py  # Core agent
│   ├── skill_loader.py        # Skill management
│   ├── .env                   # Configuration
│   ├── requirements.txt       # Dependencies
│   └── skills/                # Custom skills (local)
│
├── agent-skills/              # Skill definitions & patterns
│   ├── research-methodology/  # Your skill
│   ├── source-evaluation/     # Your skill
│   ├── citation-standards/    # Your skill
│   └── templates/             # SKILL.md templates
│
├── agent-frameworks/          # Framework references
│   ├── microsoft-agent-framework/
│   ├── anthropic-patterns/
│   └── frameworks-analysis.md
│
├── agent-examples/            # Complete system examples
│   ├── digital-brain-skill/
│   ├── llm-as-judge-skills/
│   ├── orchestrator-pattern/
│   └── examples-index.md
│
├── evaluation/                # Evaluation & benchmarking
│   ├── evaluator.py           # LLM-as-Judge implementation
│   ├── benchmark.py           # Testing suite
│   ├── PERFORMANCE_METRICS.md # Benchmark results
│   └── rubrics/               # Evaluation standards
│
├── context-optimization/      # Caching & performance
│   ├── caching.py             # Cache implementation
│   ├── compression.py         # Token compression
│   └── strategies.md          # Optimization patterns
│
├── memory-systems/            # Knowledge & memory management
│   ├── memory.py              # Append-only memory
│   ├── knowledge-graph.py     # Entity relationships
│   └── memory-architecture.md
│
├── tools/                     # Tool implementations
│   ├── search_web.py          # Search tool
│   ├── synthesize.py          # Synthesis tool
│   ├── tool-design-guide.md   # Tool patterns
│   └── mcp/                   # Model Context Protocol
│
├── orchestration/             # Multi-agent orchestration
│   ├── orchestrator.py        # Orchestrator pattern
│   ├── agents/                # Specialist agents
│   │   ├── methodology_agent.py
│   │   ├── evaluation_agent.py
│   │   └── citation_agent.py
│   └── orchestration-guide.md
│
├── research/                  # Research & analysis
│   ├── reference-repositories/
│   │   ├── 00-START-HERE.md
│   │   ├── REPOSITORY_INDEX.md
│   │   ├── CONTEXT_ENGINEERING_ANALYSIS.md
│   │   └── references/        # Cloned repos
│   ├── learning-materials/
│   └── case-studies/
│
├── .venv/                     # Python virtual environment
├── google-cloud-sdk/          # Google Cloud tools
├── reference-repositories/    # (Legacy - for transition)
└── requirements.txt           # Project dependencies
```

---

## 📊 Directory Purposes

### 📖 documentation/
**Purpose:** All guides, roadmaps, analysis, specifications  
**Contains:**
- ROADMAP.md (8-week timeline)
- PRIORITIES.md (critical tasks)
- Implementation guides
- Architecture documentation
- Analysis reports

**Who uses:** Everyone (planning, understanding, reference)

---

### 🤖 research-assistant/
**Purpose:** Main agent application  
**Contains:**
- Core agent implementation
- Skill loader system
- Local skill definitions
- Configuration & environment

**Who uses:** Developers (active development, testing)

---

### 🧠 agent-skills/
**Purpose:** Skill definitions & library  
**Contains:**
- Custom skills (research-methodology, evaluation, citations)
- Skill templates (SKILL.md patterns)
- Skill documentation
- Skill examples

**Who uses:** Skill developers, agent users

---

### 🔧 agent-frameworks/
**Purpose:** Framework references & patterns  
**Contains:**
- Microsoft Agent Framework patterns
- Anthropic skill patterns
- Comparative analysis
- Framework integration guides

**Who uses:** Architects, learning resources

---

### 💎 agent-examples/
**Purpose:** Complete working examples  
**Contains:**
- Digital Brain personal OS
- LLM-as-Judge evaluation system
- Orchestrator pattern example
- Multi-agent synthesis

**Who uses:** Learning, pattern reference, inspiration

---

### 📊 evaluation/
**Purpose:** Quality assessment & benchmarking  
**Contains:**
- Evaluator implementation (LLM-as-Judge)
- Benchmark suite
- Performance metrics
- Evaluation rubrics

**Who uses:** QA team, Week 4 benchmarking

---

### ⚡ context-optimization/
**Purpose:** Performance & cost optimization  
**Contains:**
- Caching layer (100x speedup)
- Token compression strategies
- Optimization patterns
- Performance guides

**Who uses:** Week 4+ optimization phase

---

### 🧠 memory-systems/
**Purpose:** Knowledge & memory architecture  
**Contains:**
- Append-only memory (JSONL)
- Knowledge graphs
- Entity relationships
- Memory design patterns

**Who uses:** Week 5+ implementation

---

### 🛠️ tools/
**Purpose:** Agent tool implementations  
**Contains:**
- Search tool
- Synthesis tool
- Tool design guidelines
- MCP (Model Context Protocol)

**Who uses:** Tool developers, Week 4+

---

### 🎭 orchestration/
**Purpose:** Multi-agent architecture  
**Contains:**
- Orchestrator pattern implementation
- Specialist agents (methodology, evaluation, citation)
- Orchestration patterns
- Agent communication

**Who uses:** Week 5+ multi-agent phase

---

### 🔍 research/
**Purpose:** Learning & research  
**Contains:**
- Reference repository index
- Repository clones
- Learning materials
- Case studies
- Research documentation

**Who uses:** Learning phase, references

---

## 🔄 File Organization Principles

### 1. **By Function, Not Framework**
- Organized by what the code does (optimization, memory, evaluation)
- Not by which framework or library
- Enables easy swapping of implementations

### 2. **Modular & Independent**
- Each folder can stand alone
- Clear dependencies between modules
- Easy to understand scope

### 3. **Documentation Close to Code**
- Each folder has its own guide/README
- Implementation examples included
- Design rationale documented

### 4. **Scalability Built-In**
- Easy to add new agent types
- Simple to extend with new tools
- Clear patterns for new skills

### 5. **Learning-Oriented**
- Examples folder for patterns
- Reference documentation clear
- Case studies for real-world usage

---

## 📈 Migration Path

### Phase 1: Core Setup ✅ (TODAY)
- ✅ Created organized folder structure
- ✅ Established documentation home
- ✅ Set up specialized directories

### Phase 2: Move Existing Files (Week 1-2)
- Move research-assistant files to research-assistant/
- Move analysis docs to documentation/
- Move reference materials to research/

### Phase 3: Week 4 Implementation
- Evaluation files → evaluation/
- Caching code → context-optimization/
- Benchmarking → evaluation/

### Phase 4: Week 5+ Expansion
- Orchestrator files → orchestration/
- Memory system → memory-systems/
- Additional skills → agent-skills/

---

## 🎯 Quick Navigation

**Want to...**
- 🚀 Run the agent? → research-assistant/
- 📖 Understand roadmap? → documentation/ROADMAP.md
- 🧠 Learn skills? → agent-skills/
- 📊 See benchmarks? → evaluation/
- 🔍 Research frameworks? → research/reference-repositories/
- 🎭 Build multi-agent? → orchestration/
- ⚡ Optimize performance? → context-optimization/

---

## 📋 Folder Checklist

- ✅ agent-skills/ (custom skills)
- ✅ agent-frameworks/ (framework references)
- ✅ agent-examples/ (working examples)
- ✅ evaluation/ (QA & benchmarking)
- ✅ context-optimization/ (performance)
- ✅ memory-systems/ (knowledge)
- ✅ tools/ (agent tools)
- ✅ orchestration/ (multi-agent)
- ✅ documentation/ (guides & roadmap)
- ✅ research/ (learning materials)

**Status:** All folders created and ready for use

---

**Structure Ready:** January 17, 2026  
**Next:** Move files into new structure + update roadmap with priorities
