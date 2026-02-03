---
name: python
description: "Python development expertise for modern applications. Use when writing Python code, implementing type-safe patterns, working with async/await, or reviewing Python for best practices. Covers: type hints, dataclasses, Pydantic, error handling, context managers, async programming, and project structure."
---

# Python Development

## Quick Reference

| Task | Guide |
|------|-------|
| Type hints (annotations, generics, TypedDict, Protocol) | See [typing.md](references/typing.md) |
| Testing patterns (pytest, fixtures, mocking) | See [testing.md](references/testing.md) |

## Dependency Management

Use **uv** as the preferred dependency manager for Python projects. It handles virtual environments, dependencies, and Python versions.

```bash
uv init                  # Initialize a new project
uv add <package>         # Add a dependency
uv sync                  # Install all dependencies
uv run <command>         # Run a command in the project environment
```

## Core Principles

### Type Hints

Add type hints to function signatures and class attributes. Let inference work for local variables.

```python
from typing import Optional

def get_user(user_id: str) -> Optional[User]:
    """Fetch a user by ID."""
    return db.users.get(user_id)

def process_items(items: list[str]) -> dict[str, int]:
    """Count occurrences of each item."""
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts
```

### Dataclasses for Data

Use dataclasses for simple data containers:

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    tags: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class Point:
    """Immutable point - hashable and can be used in sets/dicts."""
    x: float
    y: float
```

### Pydantic for Validation

Use Pydantic models when you need validation, serialization, or settings:

```python
from pydantic import BaseModel, EmailStr, Field

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, lt=150)

class UserResponse(BaseModel):
    id: str
    name: str
    email: str

    model_config = {"from_attributes": True}

# Validation happens automatically
request = CreateUserRequest(name="Alice", email="alice@example.com", age=30)

# Convert from ORM/dataclass
user_response = UserResponse.model_validate(user_obj)
```

## Error Handling

### Custom Exceptions

```python
class AppError(Exception):
    """Base exception for application errors."""
    def __init__(self, message: str, code: str = "UNKNOWN"):
        self.message = message
        self.code = code
        super().__init__(message)

class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str):
        super().__init__(
            f"{resource} with id {resource_id} not found",
            code="NOT_FOUND"
        )

class ValidationError(AppError):
    def __init__(self, message: str, errors: dict[str, list[str]]):
        self.errors = errors
        super().__init__(message, code="VALIDATION_ERROR")
```

### Result Pattern

For operations that can fail in expected ways, consider returning a result:

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]

def parse_int(value: str) -> Result[int, str]:
    try:
        return Ok(int(value))
    except ValueError:
        return Err(f"Cannot parse '{value}' as integer")

# Usage
match parse_int("42"):
    case Ok(value):
        print(f"Got {value}")
    case Err(error):
        print(f"Error: {error}")
```

## Context Managers

### Using contextlib

```python
from contextlib import contextmanager, asynccontextmanager
from typing import Iterator, AsyncIterator

@contextmanager
def temporary_setting(key: str, value: str) -> Iterator[None]:
    """Temporarily change a setting."""
    original = settings.get(key)
    settings[key] = value
    try:
        yield
    finally:
        if original is None:
            del settings[key]
        else:
            settings[key] = original

@asynccontextmanager
async def database_transaction() -> AsyncIterator[Connection]:
    """Manage a database transaction."""
    conn = await get_connection()
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    finally:
        await conn.close()
```

### Class-Based Context Managers

```python
class Timer:
    """Measure execution time."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.elapsed: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: object) -> None:
        self.elapsed = time.perf_counter() - self._start
        print(f"{self.name} took {self.elapsed:.3f}s")

# Usage
with Timer("Database query"):
    results = db.execute(query)
```

## Async Programming

### Basic Async/Await

```python
import asyncio
from typing import Sequence

async def fetch_user(user_id: str) -> User:
    """Fetch a single user."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{user_id}")
        return User(**response.json())

async def fetch_all_users(user_ids: Sequence[str]) -> list[User]:
    """Fetch multiple users concurrently."""
    tasks = [fetch_user(uid) for uid in user_ids]
    return await asyncio.gather(*tasks)

async def fetch_with_timeout(user_id: str, timeout: float = 5.0) -> User | None:
    """Fetch with timeout, returning None on timeout."""
    try:
        return await asyncio.wait_for(fetch_user(user_id), timeout)
    except asyncio.TimeoutError:
        return None
```

### Async Iteration

```python
from typing import AsyncIterator

async def stream_results(query: str) -> AsyncIterator[dict]:
    """Stream results from an API."""
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", "/search", params={"q": query}) as response:
            async for line in response.aiter_lines():
                yield json.loads(line)

# Usage
async for result in stream_results("python"):
    process(result)
```

### Semaphore for Rate Limiting

```python
async def fetch_many_with_limit(
    urls: list[str],
    max_concurrent: int = 10
) -> list[Response]:
    """Fetch URLs with concurrency limit."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(url: str) -> Response:
        async with semaphore:
            async with httpx.AsyncClient() as client:
                return await client.get(url)

    return await asyncio.gather(*[fetch_one(url) for url in urls])
```

## Code Style

### Naming Conventions

- `snake_case`: Functions, methods, variables, modules
- `PascalCase`: Classes, type aliases, exceptions
- `SCREAMING_SNAKE_CASE`: Constants
- `_leading_underscore`: Private/internal names

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
import json
import os
from collections.abc import Sequence
from datetime import datetime
from typing import Optional

import httpx
from pydantic import BaseModel

from myapp.core import settings
from myapp.models import User

from .utils import helper
```

### Function Arguments

```python
def create_user(
    name: str,
    email: str,
    *,  # Force keyword-only arguments after this
    role: str = "user",
    notify: bool = True,
) -> User:
    """Create a new user.

    Args:
        name: The user's display name.
        email: The user's email address.
        role: The user's role (default: "user").
        notify: Whether to send a welcome email.

    Returns:
        The created user object.

    Raises:
        ValidationError: If the email is invalid.
    """
    ...
```

## Project Structure

Standard layout for a uv-managed Python project:

```
my-project/
├── pyproject.toml        # Project config and dependencies
├── .python-version       # Python version for uv
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── cli.py        # CLI entry point
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── models.py
│       └── services/
│           ├── __init__.py
│           └── user.py
├── tests/
│   ├── conftest.py       # Shared fixtures
│   ├── test_cli.py
│   └── test_services/
│       └── test_user.py
└── README.md
```

### pyproject.toml

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My Python project"
requires-python = ">=3.12"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[project.scripts]
my-project = "my_project.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]
```

## Common Patterns

### Singleton with Module-Level Instance

```python
# config.py
class Settings:
    def __init__(self):
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///app.db")

settings = Settings()  # Module-level singleton
```

### Factory Functions

```python
def create_http_client(
    base_url: str,
    timeout: float = 30.0,
    retries: int = 3,
) -> httpx.AsyncClient:
    """Create a configured HTTP client."""
    transport = httpx.AsyncHTTPTransport(retries=retries)
    return httpx.AsyncClient(
        base_url=base_url,
        timeout=timeout,
        transport=transport,
    )
```

### Dependency Injection

```python
from typing import Protocol

class UserRepository(Protocol):
    async def get(self, user_id: str) -> User | None: ...
    async def save(self, user: User) -> None: ...

class UserService:
    def __init__(self, repo: UserRepository, email_client: EmailClient):
        self._repo = repo
        self._email = email_client

    async def create_user(self, data: CreateUserRequest) -> User:
        user = User(id=generate_id(), **data.model_dump())
        await self._repo.save(user)
        await self._email.send_welcome(user.email)
        return user
```
