# Local Development & Installation

This guide covers how to install and run the Engineering Team CLI locally for development and testing.

## Development Setup

```bash
# Clone the repository
git clone <repo-url>
cd <repo-name>

# Install dependencies
uv sync

# Run the CLI in development mode
uv run engineering-team --help
```

## Global Installation Options

### Option 1: uv tool install (Recommended)

Installs in an isolated environment with the `engineering-team` command available globally:

```bash
# From local path
uv tool install /path/to/engineering-team

# From git
uv tool install git+<repo-url>
```

### Option 2: pip editable install

Installs globally with live code updates (changes to source are reflected immediately):

```bash
pip install -e /path/to/engineering-team
```

### Option 3: pipx

If you prefer pipx for managing Python CLI tools:

```bash
pipx install /path/to/engineering-team
```

## Verifying Installation

```bash
engineering-team --version
engineering-team --help
```

## Testing on a Project

After global installation, navigate to any project directory:

```bash
cd /path/to/your/project
engineering-team init
```

## Uninstalling

```bash
# If installed with uv tool
uv tool uninstall engineering-team

# If installed with pip
pip uninstall engineering-team

# If installed with pipx
pipx uninstall engineering-team
```

## Running Tests

```bash
uv run pytest
```

## Rebuilding After Changes

If you installed with `uv tool install` from a local path and made changes:

```bash
uv tool install --force /path/to/engineering-team
```

With `pip install -e`, changes are picked up automatically.
