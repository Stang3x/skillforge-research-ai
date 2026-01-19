# Skills Installation Guide

This guide walks you through installing and configuring Claude Code skills for your Agentic Workflows workspace.

## Prerequisites

- Claude Code CLI installed and configured
- Git installed
- Basic command-line knowledge

## Understanding Skills

**Skills** are extensions that add custom commands (like `/command-name`) to Claude Code. They can:
- Automate common workflows
- Integrate with external tools and APIs
- Provide specialized agent behaviors
- Enhance Claude Code's capabilities

## Installation Methods

### Method 1: Manual Git Clone (Recommended)

Most skills are distributed as Git repositories:

```bash
# General pattern
git clone <skill-repository-url> ~/.claude/skills/<skill-name>

# Example: Installing Superpowers
git clone https://github.com/obra/superpowers ~/.claude/skills/superpowers

# Example: Installing Claude Codex Settings
git clone https://github.com/fcakyon/claude-codex-settings ~/.claude/skills/claude-codex-settings
```

### Method 2: Symlink Existing Directory

If you've cloned a skill elsewhere:

```bash
# Link to Claude skills directory
ln -s /path/to/skill ~/.claude/skills/skill-name

# Example
ln -s ~/projects/my-custom-skill ~/.claude/skills/my-custom-skill
```

### Method 3: Create Custom Skill

For simple custom skills:

```bash
# Create skill directory
mkdir -p ~/.claude/skills/my-skill

# Create skill configuration
cat > ~/.claude/skills/my-skill/skill.json <<EOF
{
  "name": "my-skill",
  "description": "My custom skill",
  "version": "1.0.0",
  "prompt": "Instructions for Claude Code when this skill is invoked"
}
EOF
```

## Recommended Skills for Agentic Workflows

### 1. Superpowers (Essential)

**Purpose**: Engineering best practices and workflows
**Installation**:
```bash
git clone https://github.com/obra/superpowers ~/.claude/skills/superpowers
```

**Provides**:
- Planning workflows
- Code review processes
- Testing strategies
- Debugging approaches

**Usage**: Follow Superpowers documentation for specific commands

---

### 2. Context Engineering Kit (Advanced)

**Purpose**: Optimize agent quality with minimal token usage
**Installation**:
```bash
git clone https://github.com/NeoLabHQ/context-engineering-kit ~/.claude/skills/context-engineering-kit
```

**Provides**:
- Advanced context patterns
- Token optimization techniques
- Quality improvement strategies

**Use When**: You need to optimize Claude Code's performance

---

### 3. Claude Codex Settings (Comprehensive)

**Purpose**: Full-stack development toolkit
**Installation**:
```bash
git clone https://github.com/fcakyon/claude-codex-settings ~/.claude/skills/claude-codex-settings
```

**Provides**:
- GitHub integration
- Azure tools
- MongoDB support
- Tavily search
- Playwright automation

**Use When**: Working on full-stack projects with multiple integrations

---

## Verifying Installation

After installing skills:

1. **Check skills directory**:
   ```bash
   ls -la ~/.claude/skills/
   ```

2. **Test in Claude Code**:
   ```bash
   # Start Claude Code
   claude

   # List available skills (skills should appear when typing /)
   /[TAB]
   ```

3. **Check skill configuration**:
   ```bash
   # Most skills have a README
   cat ~/.claude/skills/superpowers/README.md
   ```

## Installing Supporting Tools

### recall (Session Search)

```bash
# Install using cargo (Rust)
cargo install recall

# Or build from source
git clone https://github.com/zippoxer/recall
cd recall
cargo build --release
sudo cp target/release/recall /usr/local/bin/
```

**Usage**:
```bash
# Search past Claude Code sessions
recall "agent loop pattern"
```

### ccflare (Usage Dashboard)

```bash
# Install via npm
npm install -g ccflare

# Run dashboard
ccflare
```

Access at http://localhost:3000 to see usage metrics

### claudia-statusline (Monitoring)

```bash
# Install via cargo
cargo install claudia-statusline

# Configure in your shell rc file (.bashrc, .zshrc)
eval "$(claudia-statusline init)"
```

### cchooks (Hook Development)

```bash
# Install Python SDK
pip install cchooks

# Or use poetry
poetry add cchooks
```

**Create a simple hook**:
```python
from cchooks import Hook, HookType

@Hook(HookType.BEFORE_EXECUTE)
def my_hook(context):
    print(f"About to execute: {context.command}")
    return context
```

## Updating Skills

### Update a specific skill:
```bash
cd ~/.claude/skills/superpowers
git pull origin main
```

### Update all skills:
```bash
# Create an update script
cat > ~/update-claude-skills.sh <<'EOF'
#!/bin/bash
for skill in ~/.claude/skills/*/; do
    echo "Updating $(basename $skill)..."
    cd "$skill"
    git pull
done
EOF

chmod +x ~/update-claude-skills.sh

# Run updates
~/update-claude-skills.sh
```

## Uninstalling Skills

```bash
# Remove a skill
rm -rf ~/.claude/skills/skill-name

# Example
rm -rf ~/.claude/skills/superpowers
```

## Creating Your Own Skill

### Basic Skill Structure

```
my-skill/
├── skill.json          # Skill metadata and configuration
├── README.md           # Documentation
├── prompts/           # Prompt templates (optional)
│   └── main.md
└── hooks/             # Custom hooks (optional)
    └── pre-execute.py
```

### skill.json Example

```json
{
  "name": "pattern-extractor",
  "description": "Extract patterns from reference repositories",
  "version": "1.0.0",
  "author": "Your Name",
  "prompt": "You are helping extract and document design patterns from reference repositories. Follow these steps:\n\n1. Read the specified file from the reference repository\n2. Analyze the code for reusable patterns\n3. Extract the core pattern, removing project-specific details\n4. Document the pattern in the appropriate docs/patterns/ file\n5. Include source file path and line numbers\n\nAlways test patterns before documenting them.",
  "commands": {
    "extract": {
      "description": "Extract a pattern from a reference file",
      "prompt": "Extract and document the pattern from {file}"
    }
  }
}
```

### Creating the Skill

```bash
# Create skill directory
mkdir -p ~/.claude/skills/pattern-extractor

# Create skill.json
cat > ~/.claude/skills/pattern-extractor/skill.json <<'EOF'
{
  "name": "pattern-extractor",
  "description": "Extract patterns from reference repositories",
  "version": "1.0.0",
  "prompt": "Extract and document design patterns from reference code..."
}
EOF

# Create README
cat > ~/.claude/skills/pattern-extractor/README.md <<'EOF'
# Pattern Extractor Skill

Extracts design patterns from reference repositories and documents them.

## Usage

/pattern-extractor <file-path>

## Example

/pattern-extractor references/AutoGPT/autogpt/agent.py
EOF
```

## Troubleshooting

### Skill not appearing

1. **Check directory location**:
   ```bash
   ls -la ~/.claude/skills/
   ```

2. **Verify skill.json syntax**:
   ```bash
   cat ~/.claude/skills/skill-name/skill.json | jq .
   ```

3. **Check permissions**:
   ```bash
   chmod -R 755 ~/.claude/skills/
   ```

### Skill not working

1. **Check Claude Code version**:
   ```bash
   claude --version
   ```

2. **Review skill documentation**:
   ```bash
   cat ~/.claude/skills/skill-name/README.md
   ```

3. **Check for dependencies**:
   Some skills require additional tools or environment variables

## Best Practices

### Do:
- Read skill documentation before installing
- Keep skills updated regularly
- Test skills in non-critical projects first
- Document custom skills you create
- Share useful custom skills with the community

### Don't:
- Install skills from untrusted sources
- Modify third-party skills (fork instead)
- Skip reading installation instructions
- Install too many skills at once (start with 2-3)
- Forget to update skills periodically

## Recommended Skill Combinations

### For Agentic Workflows Research:
```bash
# Core skills
git clone https://github.com/obra/superpowers ~/.claude/skills/superpowers
git clone https://github.com/NeoLabHQ/context-engineering-kit ~/.claude/skills/context-engineering-kit

# Supporting tools
cargo install recall
pip install cchooks
```

### For Full-Stack Development:
```bash
git clone https://github.com/fcakyon/claude-codex-settings ~/.claude/skills/claude-codex-settings
npm install -g ccflare
cargo install claudia-statusline
```

### For Testing & Quality:
```bash
git clone https://github.com/obra/superpowers ~/.claude/skills/superpowers
git clone https://github.com/nizos/tdd-guard ~/.claude/skills/tdd-guard
```

## Next Steps

1. **Install 2-3 essential skills** from the recommended list
2. **Test each skill** with simple commands
3. **Read skill documentation** to understand full capabilities
4. **Create a custom skill** for your agentic workflows needs
5. **Document your setup** in this workspace

## Resources

- **Awesome Claude Code**: https://github.com/hesreallyhim/awesome-claude-code
- **Claude Code Docs**: https://docs.claude.com/en/home
- **Full Resources**: [CLAUDE_CODE_RESOURCES.md](./CLAUDE_CODE_RESOURCES.md)

---

*For comprehensive information on all available skills, see [CLAUDE_CODE_RESOURCES.md](./CLAUDE_CODE_RESOURCES.md)*
