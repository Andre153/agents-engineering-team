# Engineering Team CLI

A CLI tool to configure Claude Code agents and skills for your projects.

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd <repo-name>

# Install with uv
uv sync

# Run the CLI
uv run engineering-team --help
```

### Using pip

```bash
pip install git+<repo-url>
engineering-team --help
```

### Global Installation with uv

```bash
uv tool install git+<repo-url>
engineering-team --help
```

## Quick Start

```bash
# Initialize a project with agents and skills
uv run engineering-team init

# List available agents and skills
uv run engineering-team list

# Update installed agents/skills to latest versions
uv run engineering-team sync
```

## Commands

### `engineering-team init`

Interactive setup that:
1. Prompts you to select agents
2. Prompts you to select skills by category
3. Creates `engineering-team.json` in your project
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

## Configuration

The `engineering-team.json` file stores your project's configuration:

```json
{
  "version": "1.0",
  "agents": ["backend-architect", "senior-backend-developer"],
  "skills": ["typescript", "mermaid"],
  "installedAt": "2026-02-02T12:00:00Z",
  "cliVersion": "0.1.0"
}
```

## Available Agents

| Agent | Description |
|-------|-------------|
| `backend-architect` | Senior backend architect for system design, technical planning, and architecture diagrams. Read-only, hands off to developers. |
| `senior-backend-developer` | Senior polyglot backend developer for API development, DDD, and vertical slice architecture. |
| `mobile-architect` | Senior mobile architect for cross-platform system design and mobile architecture. |
| `senior-mobile-developer` | Senior mobile developer for Flutter/React Native implementation. |

## Available Skills

### Languages
- **typescript** - TypeScript development patterns, type system, async programming, testing

### Frameworks
- **flutter** - Flutter with Material Design, BLoC/Cubit, GoRouter navigation

### Databases
- **database-firestore** - Firestore data modeling, queries, security rules

### Design & Documentation
- **mermaid** - Mermaid diagramming for architecture documentation

### Cloud & Infrastructure
- **gcp-cloud-firebase** - GCP and Firebase services (Cloud Run, Auth, Storage, Functions)

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

```bash
# Clone and install
git clone <repo-url>
cd <repo-name>
uv sync

# Run CLI
uv run engineering-team --help

# Run tests
uv run pytest
```

## Project Structure

```
├── pyproject.toml              # Package configuration
├── .python-version             # Python version pin (3.12)
├── src/engineering_team/       # CLI source code
│   ├── cli.py                  # Main Typer CLI
│   ├── commands/               # init, sync, list commands
│   ├── core/                   # Config, registry, copier
│   ├── ui/                     # Interactive prompts
│   └── data/                   # Bundled agents and skills
│       ├── agents/
│       └── skills/
├── agents/                     # Source agent definitions (for reference)
├── skills/                     # Source skill definitions (for reference)
├── docs/                       # Documentation
└── tests/                      # Test files
```

## Documentation

- [Publishing to PyPI](docs/publishing.md) - How to publish the package

## License

MIT
