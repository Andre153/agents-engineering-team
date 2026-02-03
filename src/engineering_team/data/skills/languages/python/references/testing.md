# Python Testing Patterns with pytest

## Table of Contents
- [Test Structure](#test-structure)
- [Fixtures](#fixtures)
- [Parametrization](#parametrization)
- [Mocking](#mocking)
- [Async Testing](#async-testing)
- [Test Organization](#test-organization)

## Test Structure

### Basic Test Format

```python
# test_user.py
from myapp.models import User
from myapp.services import UserService

def test_create_user():
    """Test creating a new user."""
    # Arrange
    service = UserService()

    # Act
    user = service.create(name="Alice", email="alice@example.com")

    # Assert
    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.id is not None

def test_create_user_invalid_email():
    """Test that invalid email raises ValidationError."""
    service = UserService()

    with pytest.raises(ValidationError) as exc_info:
        service.create(name="Alice", email="not-an-email")

    assert "email" in str(exc_info.value)
```

### Naming Conventions

```python
# File names: test_<module>.py or <module>_test.py
# Function names: test_<behavior>

def test_user_creation_with_valid_data():
    """Descriptive names that explain what's being tested."""
    ...

def test_user_creation_fails_with_empty_name():
    """Include the expected outcome in the name."""
    ...

def test_get_user_returns_none_when_not_found():
    """Be specific about edge cases."""
    ...
```

## Fixtures

### Basic Fixtures

```python
# conftest.py - shared fixtures
import pytest
from myapp.database import Database
from myapp.models import User

@pytest.fixture
def db():
    """Create a test database connection."""
    database = Database(":memory:")
    database.create_tables()
    yield database
    database.close()

@pytest.fixture
def sample_user(db):
    """Create a sample user in the database."""
    user = User(id="1", name="Alice", email="alice@example.com")
    db.save(user)
    return user

# Using fixtures in tests
def test_get_user(db, sample_user):
    """Fixtures are passed as arguments."""
    user = db.get_user(sample_user.id)
    assert user.name == "Alice"
```

### Fixture Scopes

```python
@pytest.fixture(scope="session")
def database_url():
    """Created once per test session."""
    return "sqlite:///:memory:"

@pytest.fixture(scope="module")
def db_connection(database_url):
    """Created once per test module."""
    conn = create_connection(database_url)
    yield conn
    conn.close()

@pytest.fixture(scope="class")
def test_client():
    """Created once per test class."""
    return TestClient(app)

@pytest.fixture(scope="function")  # Default
def user():
    """Created fresh for each test function."""
    return User(id="1", name="Test")
```

### Factory Fixtures

```python
@pytest.fixture
def user_factory(db):
    """Factory fixture for creating multiple users."""
    created_users = []

    def _create_user(name: str = "Test", email: str | None = None) -> User:
        user = User(
            id=str(len(created_users) + 1),
            name=name,
            email=email or f"{name.lower()}@example.com"
        )
        db.save(user)
        created_users.append(user)
        return user

    yield _create_user

    # Cleanup all created users
    for user in created_users:
        db.delete(user)

def test_multiple_users(user_factory):
    alice = user_factory("Alice")
    bob = user_factory("Bob")

    assert alice.id != bob.id
```

### Request Fixture

```python
@pytest.fixture
def temp_file(request, tmp_path):
    """Create temp file with test-specific name."""
    test_name = request.node.name
    file_path = tmp_path / f"{test_name}.txt"
    file_path.write_text("test content")
    return file_path

@pytest.fixture(params=["sqlite", "postgres"])
def database(request):
    """Parametrized fixture - test runs with each param."""
    db_type = request.param
    db = create_database(db_type)
    yield db
    db.cleanup()
```

## Parametrization

### Basic Parametrize

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
    ("PyThOn", "PYTHON"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```

### Parametrize with IDs

```python
@pytest.mark.parametrize("email,valid", [
    pytest.param("user@example.com", True, id="valid_email"),
    pytest.param("invalid", False, id="no_at_symbol"),
    pytest.param("@example.com", False, id="no_local_part"),
    pytest.param("user@", False, id="no_domain"),
])
def test_email_validation(email, valid):
    assert is_valid_email(email) == valid
```

### Multiple Parametrize Decorators

```python
@pytest.mark.parametrize("x", [1, 2, 3])
@pytest.mark.parametrize("y", [10, 20])
def test_multiplication(x, y):
    """Runs 6 times: (1,10), (1,20), (2,10), (2,20), (3,10), (3,20)"""
    assert x * y == multiply(x, y)
```

### Parametrize Classes

```python
@pytest.mark.parametrize("user_role", ["admin", "user", "guest"])
class TestUserPermissions:
    def test_can_read(self, user_role):
        user = User(role=user_role)
        assert user.can_read()

    def test_dashboard_access(self, user_role):
        user = User(role=user_role)
        expected = user_role == "admin"
        assert user.can_access_dashboard() == expected
```

## Mocking

### Using pytest-mock

```python
def test_send_email(mocker):
    """Mock external dependencies."""
    # Mock a function
    mock_send = mocker.patch("myapp.email.send_email")
    mock_send.return_value = True

    service = NotificationService()
    result = service.notify_user("user@example.com", "Hello")

    assert result is True
    mock_send.assert_called_once_with("user@example.com", "Hello")

def test_http_request(mocker):
    """Mock HTTP client."""
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"id": "1", "name": "Alice"}
    mock_response.status_code = 200

    mock_get = mocker.patch("httpx.get", return_value=mock_response)

    user = fetch_user("1")

    assert user["name"] == "Alice"
    mock_get.assert_called_once()
```

### Mock Context Managers

```python
def test_file_processing(mocker):
    """Mock file operations."""
    mock_file = mocker.mock_open(read_data="file content")
    mocker.patch("builtins.open", mock_file)

    result = process_file("test.txt")

    mock_file.assert_called_once_with("test.txt", "r")
    assert "content" in result
```

### Spy on Methods

```python
def test_logging(mocker):
    """Spy on method calls without replacing."""
    logger = Logger()
    spy = mocker.spy(logger, "info")

    service = Service(logger)
    service.process()

    spy.assert_called()
    assert spy.call_count == 2
```

### Mock Async Functions

```python
@pytest.mark.asyncio
async def test_async_fetch(mocker):
    """Mock async functions."""
    mock_fetch = mocker.patch(
        "myapp.client.fetch_data",
        return_value={"data": "test"}
    )
    # Or use AsyncMock explicitly
    mock_fetch = mocker.patch(
        "myapp.client.fetch_data",
        new_callable=mocker.AsyncMock,
        return_value={"data": "test"}
    )

    result = await process_data()

    assert result["data"] == "test"
    mock_fetch.assert_awaited_once()
```

### Fixture for Common Mocks

```python
# conftest.py
@pytest.fixture
def mock_database(mocker):
    """Common database mock."""
    mock_db = mocker.Mock()
    mock_db.get.return_value = None
    mock_db.save.return_value = True
    mocker.patch("myapp.db.get_database", return_value=mock_db)
    return mock_db

def test_user_creation(mock_database):
    service = UserService()
    user = service.create(name="Alice")

    mock_database.save.assert_called_once()
```

## Async Testing

### Basic Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test an async function."""
    result = await fetch_user("1")
    assert result.name == "Alice"

@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async context managers."""
    async with DatabaseConnection() as conn:
        result = await conn.execute("SELECT 1")
        assert result == 1
```

### Async Fixtures

```python
@pytest.fixture
async def async_client():
    """Async fixture for HTTP client."""
    async with httpx.AsyncClient() as client:
        yield client

@pytest.fixture
async def db_connection():
    """Async database fixture."""
    conn = await create_connection()
    yield conn
    await conn.close()

@pytest.mark.asyncio
async def test_with_async_fixture(async_client, db_connection):
    response = await async_client.get("/users")
    assert response.status_code == 200
```

### Testing Async Generators

```python
@pytest.mark.asyncio
async def test_async_generator():
    """Test async iteration."""
    results = []
    async for item in stream_data():
        results.append(item)

    assert len(results) == 10
    assert all(isinstance(r, dict) for r in results)
```

### Timeout for Async Tests

```python
@pytest.mark.asyncio
@pytest.mark.timeout(5)  # Requires pytest-timeout
async def test_with_timeout():
    """Fail if test takes longer than 5 seconds."""
    result = await slow_operation()
    assert result is not None
```

## Test Organization

### conftest.py Hierarchy

```
tests/
├── conftest.py              # Root fixtures (shared by all)
├── test_models.py
├── integration/
│   ├── conftest.py          # Integration-specific fixtures
│   └── test_api.py
└── unit/
    ├── conftest.py          # Unit test fixtures
    └── test_services.py
```

### Markers

```python
# pytest.ini or pyproject.toml
# [tool.pytest.ini_options]
# markers = [
#     "slow: marks tests as slow",
#     "integration: marks tests as integration tests",
# ]

@pytest.mark.slow
def test_large_dataset():
    """Run with: pytest -m slow"""
    ...

@pytest.mark.integration
def test_database_connection():
    """Run with: pytest -m integration"""
    ...

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    ...

@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Unix only"
)
def test_unix_permissions():
    ...

@pytest.mark.xfail(reason="Known bug #123")
def test_known_issue():
    """Expected to fail."""
    ...
```

### Test Classes

```python
class TestUserService:
    """Group related tests."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Run before each test in this class."""
        self.service = UserService(db)
        self.db = db

    def test_create_user(self):
        user = self.service.create(name="Alice")
        assert user.id is not None

    def test_get_user(self):
        user = self.service.create(name="Bob")
        found = self.service.get(user.id)
        assert found.name == "Bob"

    def test_delete_user(self):
        user = self.service.create(name="Charlie")
        self.service.delete(user.id)
        assert self.service.get(user.id) is None
```

### Custom Assertions

```python
# conftest.py
def assert_user_equal(actual: User, expected: User) -> None:
    """Custom assertion with better error messages."""
    assert actual.id == expected.id, f"ID mismatch: {actual.id} != {expected.id}"
    assert actual.name == expected.name, f"Name mismatch: {actual.name} != {expected.name}"
    assert actual.email == expected.email, f"Email mismatch: {actual.email} != {expected.email}"

# In tests
def test_user_copy(sample_user):
    copy = sample_user.copy()
    assert_user_equal(copy, sample_user)
```

### Snapshot Testing

```python
# Using pytest-snapshot or syrupy

def test_api_response(snapshot):
    """Compare against saved snapshot."""
    response = get_user_response("1")
    assert response == snapshot

def test_error_message(snapshot):
    """Snapshot for error messages."""
    with pytest.raises(ValidationError) as exc_info:
        validate_user({})
    assert str(exc_info.value) == snapshot
```

### Coverage Configuration

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = ["*/tests/*", "*/__init__.py"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80
```

Run with: `pytest --cov=src --cov-report=term-missing`
