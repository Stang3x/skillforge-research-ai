# SkillForge Research AI

**A local-first AI research assistant with privacy-focused design**

SkillForge Research AI is a modular research assistant that helps students, researchers, and curious minds conduct thorough research with proper citations. It features:

- 🔍 **Real web searches & academic lookups** - DuckDuckGo integration + arXiv/PubMed support
- 📚 **Citation generation** - Automatic formatting in APA, MLA, and Chicago styles
- 🧩 **Modular skills system** - Pluggable architecture for research, synthesis, evaluation, and methodology
- 🔒 **Privacy-focused** - Local execution with offline/mock modes for testing
- ✅ **Full testing suite** - Comprehensive unit and integration tests

## Features

### Core Skills

1. **Research Skill** - Performs web and academic searches across multiple sources
2. **Synthesis Skill** - Synthesizes findings into coherent summaries with key insights
3. **Citation Skill** - Generates properly formatted citations (APA/MLA/Chicago)
4. **Methodology Skill** - Provides research methodology recommendations
5. **Evaluation Skill** - Evaluates source credibility and identifies research gaps

### Privacy & Offline Support

- Uses privacy-focused DuckDuckGo for web searches
- Mock data mode for offline testing and development
- No tracking or data collection
- Local-first architecture

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install from source

```bash
# Clone the repository
git clone https://github.com/Stang3x/skillforge-research-ai.git
cd skillforge-research-ai

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### Install for development

```bash
# Install with development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run with coverage
pytest --cov=skillforge tests/
```

## Usage

### Command Line Interface

SkillForge provides an intuitive CLI for research tasks:

#### List available skills

```bash
skillforge list-skills
```

#### Perform basic research

```bash
# Online research
skillforge research "quantum computing"

# Offline/mock mode for testing
skillforge research "quantum computing" --mock

# Limit results
skillforge research "machine learning" --max-results 5

# Exclude academic sources
skillforge research "artificial intelligence" --no-academic
```

#### Full research workflow

```bash
# Complete research with synthesis, evaluation, and citations
skillforge full-research "climate change impacts"

# Use different citation style
skillforge full-research "machine learning" --citation-style mla

# Offline mode
skillforge full-research "quantum physics" --mock
```

#### Get methodology recommendations

```bash
# General research methodology
skillforge methodology "user experience research"

# Specific research types
skillforge methodology "survey analysis" --research-type quantitative
skillforge methodology "interviews study" --research-type qualitative
```

### Python API

```python
import asyncio
from skillforge.skills import SkillInput
from skillforge.skills.research import ResearchSkill
from skillforge.skills.synthesis import SynthesisSkill
from skillforge.skills.citation import CitationSkill
from skillforge.citation import CitationStyle

async def research_example():
    # Initialize skills
    research_skill = ResearchSkill(use_mock=False)  # Set to True for offline
    synthesis_skill = SynthesisSkill()
    citation_skill = CitationSkill(style=CitationStyle.APA)
    
    # Perform research
    research_input = SkillInput(
        query="artificial intelligence ethics",
        options={"max_results": 10}
    )
    research_result = await research_skill.execute(research_input)
    
    if research_result.success:
        results = research_result.data["results"]
        print(f"Found {len(results)} sources")
        
        # Synthesize findings
        synthesis_input = SkillInput(
            query="artificial intelligence ethics",
            context={"results": results}
        )
        synthesis_result = await synthesis_skill.execute(synthesis_input)
        
        if synthesis_result.success:
            print(synthesis_result.data["summary"])
        
        # Generate citations
        citation_input = SkillInput(
            query="artificial intelligence ethics",
            context={"results": results}
        )
        citation_result = await citation_skill.execute(citation_input)
        
        if citation_result.success:
            print("\nBibliography:")
            print(citation_result.data["bibliography"])

# Run the example
asyncio.run(research_example())
```

## Architecture

### Modular Skills System

SkillForge uses a pluggable skills architecture:

```python
from skillforge.skills.base import Skill, SkillInput, SkillOutput

class CustomSkill(Skill):
    def __init__(self):
        super().__init__(
            name="custom",
            description="My custom skill"
        )
    
    async def execute(self, skill_input: SkillInput) -> SkillOutput:
        # Your skill logic here
        return SkillOutput(
            success=True,
            data={"result": "custom output"}
        )
```

### Skill Registry

Register and manage skills dynamically:

```python
from skillforge.skills import skill_registry

# Register a skill
skill_registry.register(CustomSkill())

# Get a skill
skill = skill_registry.get("custom")

# List all skills
all_skills = skill_registry.list_skills()
```

## Testing

SkillForge includes a comprehensive testing suite:

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run with coverage report
pytest --cov=skillforge --cov-report=html tests/

# Run specific test file
pytest tests/unit/test_skills_base.py
```

### Test Coverage

- Unit tests for all skills and components
- Integration tests for complete workflows
- Mock data for offline testing
- 100+ test cases covering core functionality

## Project Structure

```
skillforge-research-ai/
├── skillforge/              # Main package
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── skills/             # Skills module
│   │   ├── base.py         # Base skill classes
│   │   ├── research.py     # Research skill
│   │   ├── synthesis.py    # Synthesis skill
│   │   ├── citation.py     # Citation skill
│   │   ├── methodology.py  # Methodology skill
│   │   └── evaluation.py   # Evaluation skill
│   ├── search/             # Search functionality
│   │   └── web.py          # Web & academic search
│   └── citation/           # Citation formatting
│       └── formatter.py    # Citation generators
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black skillforge/

# Lint code
flake8 skillforge/

# Type checking
mypy skillforge/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Privacy & Security

SkillForge is designed with privacy in mind:

- **Local-first**: All processing happens on your machine
- **No tracking**: No analytics or telemetry
- **Privacy-focused search**: Uses DuckDuckGo (no user profiling)
- **Offline mode**: Full functionality with mock data
- **No API keys required**: Works without external services

## Roadmap

- [ ] Support for more academic databases (IEEE, SpringerLink, etc.)
- [ ] Local LLM integration for synthesis (Ollama, LLaMA, etc.)
- [ ] Export to markdown/PDF
- [ ] Web interface
- [ ] More citation styles (IEEE, Harvard, etc.)
- [ ] Research project management
- [ ] Collaboration features

## Support

For issues, questions, or contributions, please visit:
- GitHub Issues: https://github.com/Stang3x/skillforge-research-ai/issues

## Acknowledgments

Built with:
- [aiohttp](https://docs.aiohttp.org/) - Async HTTP client
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
- [pytest](https://pytest.org/) - Testing framework
