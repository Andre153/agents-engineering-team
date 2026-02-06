# Engineering Team CLI

A Python CLI tool that installs Claude Code agents and skills into projects.

## Project Overview

This is a Python package using:
- **uv** for dependency management
- **Typer** for CLI framework
- **questionary** for interactive prompts
- **Pydantic** for data validation
- **Rich** for terminal output formatting
- **hatchling** for building

## Quick Commands

```bash
uv sync                              # Install dependencies
uv run engineering-team --help       # Show CLI help
uv run engineering-team list         # List available agents/skills
uv run engineering-team init         # Initialize a project
uv run engineering-team sync         # Update installed files
uv run engineering-team status       # Show project configuration
uv run pytest                        # Run tests
```

## Architecture

```
src/engineering_team/
├── cli.py              # Main Typer app, registers commands
├── commands/
│   ├── init.py         # Interactive project initialization
│   ├── sync.py         # Re-copy agents/skills to project
│   ├── list.py         # Display available agents/skills
│   └── status.py       # Show project configuration status
├── core/
│   ├── schema.py       # Pydantic models (AgentInfo, SkillInfo, StackItem)
│   ├── database.py     # SQLite database handling and repository layer
│   ├── registry.py     # Discover agents/skills from data/ directory
│   └── copier.py       # Copy files to .claude/ directory
├── ui/
│   └── prompts.py      # questionary interactive prompts
└── data/
    ├── agents/         # Bundled agent .md files
    └── skills/         # Bundled skills organized by category
        ├── languages/
        ├── frameworks/
        ├── databases/
        ├── design/
        ├── cloud/
        └── test-tools/
```

## Key Files

- `pyproject.toml` - Package config, dependencies, entry point
- `.python-version` - Pins Python 3.12 for uv
- `engineering-team.db` - SQLite database created in target projects, stores selections and project stack

## Data Flow

1. **Registry** (`core/registry.py`) discovers agents/skills from `data/` by parsing YAML frontmatter
2. **Prompts** (`ui/prompts.py`) present interactive selection using questionary (includes project stack selection)
3. **Database** (`core/database.py`) saves selections to `engineering-team.db` SQLite database
4. **Copier** (`core/copier.py`) copies selected files to `.claude/agents/` and `.claude/skills/`

## Adding New Agents

1. Create `agents/<name>.md` with YAML frontmatter:
   ```yaml
   ---
   name: my-agent
   description: What this agent does
   tools: Read, Write, Edit, Glob, Grep, Bash
   model: sonnet
   skills:
     - typescript
   ---
   ```
2. Copy to `src/engineering_team/data/agents/`
3. Reinstall: `uv sync`

## Adding New Skills

1. Create `skills/<category>/<name>/SKILL.md` with frontmatter
2. Optionally add `references/` and `assets/` subdirectories
3. Copy to `src/engineering_team/data/skills/<category>/`
4. Reinstall: `uv sync`

## Skill Categories

- `languages` - Programming languages (python, typescript)
- `frameworks` - Frameworks (flutter)
- `databases` - Database skills (database-firestore)
- `design` - Design/documentation (mermaid)
- `cloud` - Cloud platforms (gcp-cloud-firebase)
- `test-tools` - Testing tools (typescript-unit-testing)
- `product` - Product skills (empty, for future use)

## Documentation

- [docs/publishing.md](docs/publishing.md) - Publishing to PyPI
