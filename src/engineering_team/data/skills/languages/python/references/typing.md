# Python Type Hints and Pydantic Patterns

## Table of Contents
- [Basic Type Annotations](#basic-type-annotations)
- [Generic Types](#generic-types)
- [TypedDict](#typeddict)
- [Protocol](#protocol)
- [Literal and Final](#literal-and-final)
- [Pydantic Models](#pydantic-models)
- [Runtime Type Checking](#runtime-type-checking)

## Basic Type Annotations

### Function Signatures

```python
from typing import Optional
from collections.abc import Sequence, Mapping, Callable

# Basic types
def greet(name: str) -> str:
    return f"Hello, {name}"

# Optional (can be None)
def find_user(user_id: str) -> Optional[User]:
    return db.get(user_id)

# Same as Optional, using union syntax (Python 3.10+)
def find_user(user_id: str) -> User | None:
    return db.get(user_id)

# Multiple return types
def parse_value(raw: str) -> int | float | str:
    try:
        return int(raw)
    except ValueError:
        try:
            return float(raw)
        except ValueError:
            return raw

# Callable types
def apply_transform(
    items: list[str],
    transform: Callable[[str], str]
) -> list[str]:
    return [transform(item) for item in items]

# Callable with optional args
Handler = Callable[[Request], Response]
Middleware = Callable[[Request, Handler], Response]
```

### Collection Types

```python
from collections.abc import Sequence, Mapping, Set, Iterable, Iterator

# Use built-in generics (Python 3.9+)
names: list[str] = ["alice", "bob"]
counts: dict[str, int] = {"a": 1, "b": 2}
unique: set[int] = {1, 2, 3}
point: tuple[float, float] = (1.0, 2.0)
mixed: tuple[str, int, bool] = ("a", 1, True)
variable_tuple: tuple[int, ...] = (1, 2, 3, 4, 5)

# Abstract collection types for function parameters
def process_names(names: Sequence[str]) -> None:
    """Accept list, tuple, or any sequence."""
    for name in names:
        print(name)

def merge_configs(configs: Mapping[str, str]) -> dict[str, str]:
    """Accept dict or any mapping."""
    return dict(configs)

def unique_items(items: Iterable[str]) -> set[str]:
    """Accept any iterable."""
    return set(items)
```

### Class Attributes

```python
from typing import ClassVar

class Counter:
    # Class variable (shared across instances)
    total_count: ClassVar[int] = 0

    # Instance variables
    name: str
    count: int

    def __init__(self, name: str) -> None:
        self.name = name
        self.count = 0
        Counter.total_count += 1
```

## Generic Types

### Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Box(Generic[T]):
    """A container for a single value."""

    def __init__(self, value: T) -> None:
        self._value = value

    def get(self) -> T:
        return self._value

    def map(self, func: Callable[[T], V]) -> "Box[V]":
        return Box(func(self._value))

# Usage
string_box: Box[str] = Box("hello")
int_box: Box[int] = Box(42)
```

### Generic Functions

```python
from typing import TypeVar, overload

T = TypeVar("T")

def first(items: Sequence[T]) -> T | None:
    """Return first item or None if empty."""
    return items[0] if items else None

def identity(value: T) -> T:
    """Return the value unchanged."""
    return value

# Bounded type variables
Numeric = TypeVar("Numeric", int, float)

def add(a: Numeric, b: Numeric) -> Numeric:
    return a + b

# Upper bound
Comparable = TypeVar("Comparable", bound="SupportsLessThan")

def min_value(items: Sequence[Comparable]) -> Comparable:
    return min(items)
```

### Overloaded Functions

```python
from typing import overload, Literal

@overload
def get_item(items: list[T], index: int) -> T: ...
@overload
def get_item(items: list[T], index: int, default: T) -> T: ...

def get_item(items: list[T], index: int, default: T | None = None) -> T | None:
    try:
        return items[index]
    except IndexError:
        return default

# With Literal for different return types
@overload
def fetch(url: str, *, json: Literal[True]) -> dict: ...
@overload
def fetch(url: str, *, json: Literal[False] = ...) -> str: ...

def fetch(url: str, *, json: bool = False) -> dict | str:
    response = requests.get(url)
    if json:
        return response.json()
    return response.text
```

## TypedDict

TypedDict defines dictionaries with specific keys and value types:

```python
from typing import TypedDict, Required, NotRequired

class UserDict(TypedDict):
    id: str
    name: str
    email: str

class UserDictOptional(TypedDict, total=False):
    """All keys are optional."""
    id: str
    name: str
    email: str

class UserDictMixed(TypedDict):
    """Mix of required and optional keys."""
    id: Required[str]
    name: Required[str]
    email: NotRequired[str]
    phone: NotRequired[str]

# Usage
user: UserDict = {"id": "1", "name": "Alice", "email": "alice@example.com"}

def create_user(data: UserDict) -> User:
    return User(**data)

# Inheritance
class AdminDict(UserDict):
    role: str
    permissions: list[str]
```

### TypedDict with ReadOnly (Python 3.13+)

```python
from typing import TypedDict, ReadOnly

class Config(TypedDict):
    name: ReadOnly[str]  # Cannot be modified
    debug: bool          # Can be modified
```

## Protocol

Protocols define structural typing (duck typing with type checking):

```python
from typing import Protocol, runtime_checkable

class Readable(Protocol):
    def read(self, n: int = -1) -> str: ...

class Writable(Protocol):
    def write(self, data: str) -> int: ...

class ReadWritable(Readable, Writable, Protocol):
    """Combines both protocols."""
    pass

def process_file(f: Readable) -> str:
    """Accept any object with a read method."""
    return f.read()

# Works with file objects, StringIO, or any class with read()
with open("file.txt") as f:
    content = process_file(f)

# Runtime checkable protocol
@runtime_checkable
class Closeable(Protocol):
    def close(self) -> None: ...

def is_closeable(obj: object) -> bool:
    return isinstance(obj, Closeable)
```

### Protocol with Properties

```python
from typing import Protocol

class Named(Protocol):
    @property
    def name(self) -> str: ...

class Sized(Protocol):
    def __len__(self) -> int: ...

class NamedCollection(Named, Sized, Protocol):
    """Has a name and supports len()."""
    pass
```

## Literal and Final

### Literal Types

```python
from typing import Literal

# Restrict to specific values
Direction = Literal["north", "south", "east", "west"]
HttpMethod = Literal["GET", "POST", "PUT", "DELETE"]

def move(direction: Direction) -> None:
    match direction:
        case "north":
            y += 1
        case "south":
            y -= 1
        case "east":
            x += 1
        case "west":
            x -= 1

# Combine with overload for different return types
@overload
def fetch(url: str, method: Literal["GET"]) -> str: ...
@overload
def fetch(url: str, method: Literal["POST"], body: dict) -> dict: ...
```

### Final

```python
from typing import Final, final

# Constant value (cannot be reassigned)
MAX_CONNECTIONS: Final[int] = 100
API_VERSION: Final = "v2"  # Type inferred as Literal["v2"]

# Final class (cannot be subclassed)
@final
class Singleton:
    _instance: "Singleton | None" = None

# Final method (cannot be overridden)
class Base:
    @final
    def id(self) -> str:
        return self._id
```

## Pydantic Models

### Basic Models

```python
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class User(BaseModel):
    id: str
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    age: int = Field(default=0, ge=0, lt=150)
    created_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)

# Create from dict
user = User(id="1", name="Alice", email="alice@example.com")

# Access as attributes
print(user.name)

# Convert to dict
user_dict = user.model_dump()

# Convert to JSON
user_json = user.model_dump_json()
```

### Validation

```python
from pydantic import BaseModel, field_validator, model_validator, EmailStr
from typing import Self

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    password_confirm: str

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("must be alphanumeric")
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self
```

### Nested Models and Custom Types

```python
from pydantic import BaseModel, field_serializer
from datetime import datetime
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class Address(BaseModel):
    street: str
    city: str
    country: str

class User(BaseModel):
    id: str
    name: str
    status: Status
    address: Address | None = None

    @field_serializer("status")
    def serialize_status(self, status: Status) -> str:
        return status.value

# Nested validation works automatically
user = User(
    id="1",
    name="Alice",
    status="active",
    address={"street": "123 Main", "city": "NYC", "country": "USA"}
)
```

### Settings with Environment Variables

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = "My App"
    debug: bool = False
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    redis_url: str = "redis://localhost:6379"

    model_config = {
        "env_prefix": "APP_",
        "env_file": ".env",
    }

# Reads from environment: APP_DEBUG, DATABASE_URL, APP_REDIS_URL
settings = Settings()
```

### ORM Mode

```python
from pydantic import BaseModel, ConfigDict

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    email: str

# Convert from SQLAlchemy/dataclass/any object with attributes
class UserORM:
    def __init__(self, id: str, name: str, email: str, password_hash: str):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash

orm_user = UserORM("1", "Alice", "alice@example.com", "hash...")
response = UserResponse.model_validate(orm_user)  # Excludes password_hash
```

## Runtime Type Checking

### Type Guards

```python
from typing import TypeGuard, TypeIs

def is_string_list(val: list[object]) -> TypeGuard[list[str]]:
    """Check if all items are strings."""
    return all(isinstance(item, str) for item in val)

def process(items: list[object]) -> None:
    if is_string_list(items):
        # items is now list[str]
        for item in items:
            print(item.upper())

# TypeIs (Python 3.13+) - narrower, more precise
def is_str(val: object) -> TypeIs[str]:
    return isinstance(val, str)
```

### Assert Type

```python
from typing import assert_type

def get_name() -> str:
    return "Alice"

# Static assertion - fails type check if wrong
name = get_name()
assert_type(name, str)  # OK
# assert_type(name, int)  # Type error
```

### Runtime Validation with Pydantic

```python
from pydantic import TypeAdapter

# Validate arbitrary types at runtime
string_list_adapter = TypeAdapter(list[str])

# Raises ValidationError if invalid
validated = string_list_adapter.validate_python(["a", "b", "c"])

# Check without raising
try:
    string_list_adapter.validate_python([1, 2, 3])
except ValidationError as e:
    print(f"Invalid: {e}")
```
