# Publishing to PyPI

This guide explains how to publish the `engineering-team` CLI to PyPI (Python Package Index).

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Create an API token at https://pypi.org/manage/account/token/

## Publishing

### Build the package

```bash
uv build
```

This creates distributable files in `dist/`:
- `engineering_team-0.1.0-py3-none-any.whl` (wheel)
- `engineering_team-0.1.0.tar.gz` (source)

### Publish to PyPI

```bash
uv publish --token <your-pypi-token>
```

Or set the token as an environment variable:

```bash
export UV_PUBLISH_TOKEN=<your-pypi-token>
uv publish
```

### Test with TestPyPI first (optional)

TestPyPI is a separate instance for testing:

```bash
# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/ --token <test-pypi-token>

# Install from TestPyPI to test
uv tool install --index-url https://test.pypi.org/simple/ engineering-team
```

## After Publishing

Users can install globally with:

```bash
# Using uv (recommended)
uv tool install engineering-team

# Using pipx
pipx install engineering-team

# Using pip
pip install engineering-team
```

## Version Bumping

Update the version in `src/engineering_team/__init__.py`:

```python
__version__ = "0.2.0"
```

And in `pyproject.toml`:

```toml
version = "0.2.0"
```

Then build and publish again.
