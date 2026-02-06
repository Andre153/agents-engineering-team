# Engineering Team CLI

A CLI tool to configure Claude Code agents and skills for your projects.

## Installation

```bash
# Install globally with uv
uv tool install git+<repo-url>

# Verify installation
engineering-team --help
```

For local development setup and alternative installation methods, see [docs/local.md](docs/local.md).

## Quick Start

```bash
# Initialize a project with agents and skills
uv run engineering-team init

# List available agents and skills
uv run engineering-team list

# Update installed agents/skills to latest versions
uv run engineering-team sync

# Show installed agents/skills for current project
uv run engineering-team status
```

## Commands

### `engineering-team init`

Interactive setup that:
1. Prompts you to select agents
2. Prompts you to select skills by category
3. Creates `engineering-team.db` database in your project
4. Copies selected files to `.claude/agents/` and `.claude/skills/`

```bash
uv run engineering-team init
uv run engineering-team init -d /path/to/project  # Specify project directory
uv run engineering-team init -f                   # Force reconfiguration
```

### `engineering-team sync`

Re-copies all configured agents and skills from the CLI package, updating them to the latest versions.

```bash
uv run engineering-team sync
uv run engineering-team sync -d /path/to/project  # Specify project directory
```

### `engineering-team list`

Lists all available agents and skills.

```bash
uv run engineering-team list           # Pretty tables
uv run engineering-team list --json    # JSON output
uv run engineering-team list --agents  # Agents only
uv run engineering-team list --skills  # Skills only
```

### `engineering-team status`

Shows currently installed agents and skills for a project.

```bash
uv run engineering-team status
uv run engineering-team status -d /path/to/project  # Specify project directory
```

## Configuration

The `engineering-team.db` SQLite database stores your project's configuration, including selected agents, skills, and project metadata. The database is created in your project root when you run `engineering-team init`.

## Available Agents

| Agent | Description |
|-------|-------------|
| `backend-architect` | Senior backend architect for system design, technical planning, and architecture diagrams. Read-only, hands off to developers. |
| `code-reviewer` | Senior code reviewer for thorough, constructive code reviews. Identifies bugs, security issues, and provides actionable feedback. |
| `mobile-architect` | Senior mobile architect for cross-platform system design and mobile architecture. |
| `senior-backend-developer` | Senior polyglot backend developer for API development, DDD, and vertical slice architecture. |
| `senior-mobile-developer` | Senior mobile developer for Flutter/React Native implementation. |
| `unit-test-engineer` | Polyglot unit test engineer specializing in business-readable tests with BDD-style naming. |

## Available Skills

### Languages
- **python** - Python development with type hints, dataclasses, Pydantic, async patterns
- **typescript** - TypeScript development patterns, type system, async programming, testing

### Frameworks
- **flutter** - Flutter with Material Design, BLoC/Cubit, GoRouter navigation

### Databases
- **database-firestore** - Firestore data modeling, queries, security rules

### Design & Documentation
- **mermaid** - Mermaid diagramming for architecture documentation

### Cloud & Infrastructure
- **gcp-cloud-firebase** - GCP and Firebase services (Cloud Run, Auth, Storage, Functions)

### Test Tools
- **typescript-unit-testing** - TypeScript unit testing with Jest/Vitest, mocking patterns, async testing

## Using Skills with Agents

Skills can be preloaded in agent frontmatter:

```yaml
---
name: senior-backend-developer
skills:
  - typescript
  - gcp-cloud-firebase
---
```

Or mentioned in prompts:

```
Use the senior-backend-developer agent with the typescript skill to build the user API
```

## Development

See [docs/local.md](docs/local.md) for development setup instructions.

## Project Structure

```
├── pyproject.toml              # Package configuration
├── .python-version             # Python version pin (3.12)
├── src/engineering_team/       # CLI source code
│   ├── cli.py                  # Main Typer CLI
│   ├── commands/               # init, sync, list, status commands
│   ├── core/                   # Config, registry, copier
│   ├── ui/                     # Interactive prompts
│   └── data/                   # Bundled agents and skills
│       ├── agents/
│       └── skills/
├── docs/                       # Documentation
└── tests/                      # Test files
```

## Documentation

- [Local Development & Installation](docs/local.md) - Development setup and installation options
- [Publishing to PyPI](docs/publishing.md) - How to publish the package

## License

MIT
