"""Tests for the database module."""

import tempfile
from pathlib import Path

import pytest

from engineering_team.core.database import (
    CURRENT_SCHEMA_VERSION,
    add_agent,
    add_skill,
    add_stack_item,
    clear_agents,
    clear_skills,
    clear_stack,
    create_project,
    db_exists,
    get_agents,
    get_db_path,
    get_or_create_project,
    get_project,
    get_schema_version,
    get_skills,
    get_stack,
    init_database,
    remove_agent,
    remove_skill,
    set_agents,
    set_schema_version,
    set_skills,
    set_stack,
    update_project_timestamp,
)
from engineering_team.core.schema import StackItem


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestDatabaseConnection:
    """Tests for database connection and initialization."""

    def test_get_db_path(self, temp_dir: Path):
        """Test getting the database path."""
        path = get_db_path(temp_dir)
        assert path == temp_dir / "engineering-team.db"

    def test_db_exists_false(self, temp_dir: Path):
        """Test db_exists returns False when no database."""
        assert db_exists(temp_dir) is False

    def test_init_database(self, temp_dir: Path):
        """Test database initialization."""
        db_path = init_database(temp_dir)
        assert db_path.exists()
        assert db_exists(temp_dir) is True

    def test_schema_version(self, temp_dir: Path):
        """Test schema version tracking."""
        # Before init, version should be None
        assert get_schema_version(temp_dir) is None

        # After init, version should be current
        init_database(temp_dir)
        assert get_schema_version(temp_dir) == CURRENT_SCHEMA_VERSION

        # Can update version
        set_schema_version(2, temp_dir)
        assert get_schema_version(temp_dir) == 2


class TestProjectRepository:
    """Tests for project CRUD operations."""

    def test_create_and_get_project(self, temp_dir: Path):
        """Test creating and retrieving a project."""
        init_database(temp_dir)

        project_id = create_project(temp_dir, name="test-project", project_dir=temp_dir)
        assert project_id is not None
        assert project_id > 0

        project = get_project(temp_dir)
        assert project is not None
        assert project["path"] == str(temp_dir)
        assert project["name"] == "test-project"
        assert project["created_at"] is not None
        assert project["updated_at"] is not None

    def test_get_project_not_found(self, temp_dir: Path):
        """Test getting a project that doesn't exist."""
        init_database(temp_dir)
        project = get_project(temp_dir)
        assert project is None

    def test_get_or_create_project_creates(self, temp_dir: Path):
        """Test get_or_create creates new project."""
        init_database(temp_dir)

        project_id = get_or_create_project(temp_dir)
        assert project_id is not None
        assert project_id > 0

        project = get_project(temp_dir)
        assert project is not None

    def test_get_or_create_project_gets_existing(self, temp_dir: Path):
        """Test get_or_create returns existing project."""
        init_database(temp_dir)

        project_id1 = get_or_create_project(temp_dir)
        project_id2 = get_or_create_project(temp_dir)
        assert project_id1 == project_id2

    def test_update_project_timestamp(self, temp_dir: Path):
        """Test updating project timestamp."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        project_before = get_project(temp_dir)
        update_project_timestamp(project_id, temp_dir)
        project_after = get_project(temp_dir)

        # Timestamps should be different (or at least not earlier)
        assert project_after["updated_at"] >= project_before["updated_at"]


class TestStackRepository:
    """Tests for stack item CRUD operations."""

    def test_add_and_get_stack(self, temp_dir: Path):
        """Test adding and retrieving stack items."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_stack_item(project_id, "language", "Python", "3.12", temp_dir)
        add_stack_item(project_id, "framework", "FastAPI", "0.109", temp_dir)

        stack = get_stack(project_id, temp_dir)
        assert len(stack) == 2

        python = next((s for s in stack if s.name == "Python"), None)
        assert python is not None
        assert python.stack_type == "language"
        assert python.version == "3.12"

        fastapi = next((s for s in stack if s.name == "FastAPI"), None)
        assert fastapi is not None
        assert fastapi.stack_type == "framework"
        assert fastapi.version == "0.109"

    def test_add_stack_item_without_version(self, temp_dir: Path):
        """Test adding stack item without version."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_stack_item(project_id, "cloud", "AWS", None, temp_dir)

        stack = get_stack(project_id, temp_dir)
        assert len(stack) == 1
        assert stack[0].name == "AWS"
        assert stack[0].version is None

    def test_clear_stack(self, temp_dir: Path):
        """Test clearing all stack items."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_stack_item(project_id, "language", "Python", "3.12", temp_dir)
        add_stack_item(project_id, "framework", "FastAPI", None, temp_dir)

        clear_stack(project_id, temp_dir)

        stack = get_stack(project_id, temp_dir)
        assert len(stack) == 0

    def test_set_stack(self, temp_dir: Path):
        """Test replacing all stack items."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        # Add initial items
        add_stack_item(project_id, "language", "Python", "3.12", temp_dir)

        # Replace with new items
        new_stack = [
            StackItem(stack_type="language", name="TypeScript", version="5.0"),
            StackItem(stack_type="framework", name="React", version="18"),
        ]
        set_stack(project_id, new_stack, temp_dir)

        stack = get_stack(project_id, temp_dir)
        assert len(stack) == 2
        assert all(s.name in ["TypeScript", "React"] for s in stack)


class TestAgentRepository:
    """Tests for agent CRUD operations."""

    def test_add_and_get_agents(self, temp_dir: Path):
        """Test adding and retrieving agents."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_agent(project_id, "backend-architect", temp_dir)
        add_agent(project_id, "code-reviewer", temp_dir)

        agents = get_agents(project_id, temp_dir)
        assert len(agents) == 2
        assert "backend-architect" in agents
        assert "code-reviewer" in agents

    def test_remove_agent(self, temp_dir: Path):
        """Test removing an agent."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_agent(project_id, "backend-architect", temp_dir)
        add_agent(project_id, "code-reviewer", temp_dir)

        remove_agent(project_id, "backend-architect", temp_dir)

        agents = get_agents(project_id, temp_dir)
        assert len(agents) == 1
        assert "code-reviewer" in agents

    def test_clear_agents(self, temp_dir: Path):
        """Test clearing all agents."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_agent(project_id, "backend-architect", temp_dir)
        add_agent(project_id, "code-reviewer", temp_dir)

        clear_agents(project_id, temp_dir)

        agents = get_agents(project_id, temp_dir)
        assert len(agents) == 0

    def test_set_agents(self, temp_dir: Path):
        """Test replacing all agents."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        # Add initial agent
        add_agent(project_id, "backend-architect", temp_dir)

        # Replace with new agents
        set_agents(project_id, ["frontend-dev", "devops"], temp_dir)

        agents = get_agents(project_id, temp_dir)
        assert len(agents) == 2
        assert "frontend-dev" in agents
        assert "devops" in agents
        assert "backend-architect" not in agents

    def test_add_agent_idempotent(self, temp_dir: Path):
        """Test adding same agent twice doesn't duplicate."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_agent(project_id, "backend-architect", temp_dir)
        add_agent(project_id, "backend-architect", temp_dir)

        agents = get_agents(project_id, temp_dir)
        assert len(agents) == 1


class TestSkillRepository:
    """Tests for skill CRUD operations."""

    def test_add_and_get_skills(self, temp_dir: Path):
        """Test adding and retrieving skills."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_skill(project_id, "typescript", temp_dir)
        add_skill(project_id, "flutter", temp_dir)

        skills = get_skills(project_id, temp_dir)
        assert len(skills) == 2
        assert "typescript" in skills
        assert "flutter" in skills

    def test_remove_skill(self, temp_dir: Path):
        """Test removing a skill."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_skill(project_id, "typescript", temp_dir)
        add_skill(project_id, "flutter", temp_dir)

        remove_skill(project_id, "typescript", temp_dir)

        skills = get_skills(project_id, temp_dir)
        assert len(skills) == 1
        assert "flutter" in skills

    def test_clear_skills(self, temp_dir: Path):
        """Test clearing all skills."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_skill(project_id, "typescript", temp_dir)
        add_skill(project_id, "flutter", temp_dir)

        clear_skills(project_id, temp_dir)

        skills = get_skills(project_id, temp_dir)
        assert len(skills) == 0

    def test_set_skills(self, temp_dir: Path):
        """Test replacing all skills."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        # Add initial skill
        add_skill(project_id, "typescript", temp_dir)

        # Replace with new skills
        set_skills(project_id, ["python", "rust"], temp_dir)

        skills = get_skills(project_id, temp_dir)
        assert len(skills) == 2
        assert "python" in skills
        assert "rust" in skills
        assert "typescript" not in skills

    def test_add_skill_idempotent(self, temp_dir: Path):
        """Test adding same skill twice doesn't duplicate."""
        init_database(temp_dir)
        project_id = get_or_create_project(temp_dir)

        add_skill(project_id, "typescript", temp_dir)
        add_skill(project_id, "typescript", temp_dir)

        skills = get_skills(project_id, temp_dir)
        assert len(skills) == 1
