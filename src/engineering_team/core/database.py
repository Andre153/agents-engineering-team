"""SQLite database handling for engineering-team."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional

from .schema import StackItem

DB_FILE_NAME = "engineering-team.db"
CURRENT_SCHEMA_VERSION = 1


def get_db_path(project_dir: Optional[Path] = None) -> Path:
    """Get the path to the database file."""
    if project_dir is None:
        project_dir = Path.cwd()
    return project_dir / DB_FILE_NAME


def db_exists(project_dir: Optional[Path] = None) -> bool:
    """Check if a database file exists."""
    return get_db_path(project_dir).exists()


@contextmanager
def get_connection(project_dir: Optional[Path] = None) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    db_path = get_db_path(project_dir)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database(project_dir: Optional[Path] = None) -> Path:
    """Initialize the database with schema. Returns path to database file."""
    db_path = get_db_path(project_dir)

    with get_connection(project_dir) as conn:
        cursor = conn.cursor()

        # Create tables
        cursor.executescript("""
            -- Core project info
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            -- Project tech stack (languages, frameworks, versions)
            CREATE TABLE IF NOT EXISTS project_stack (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                stack_type TEXT NOT NULL,
                name TEXT NOT NULL,
                version TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                UNIQUE(project_id, stack_type, name)
            );

            -- Installed agents
            CREATE TABLE IF NOT EXISTS installed_agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                agent_name TEXT NOT NULL,
                installed_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                UNIQUE(project_id, agent_name)
            );

            -- Installed skills
            CREATE TABLE IF NOT EXISTS installed_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                installed_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                UNIQUE(project_id, skill_name)
            );

            -- Schema version tracking
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            );
        """)

        # Set schema version if not exists
        cursor.execute("SELECT version FROM schema_version LIMIT 1")
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (CURRENT_SCHEMA_VERSION,)
            )

        conn.commit()

    return db_path


def get_schema_version(project_dir: Optional[Path] = None) -> Optional[int]:
    """Get the current schema version."""
    if not db_exists(project_dir):
        return None

    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT version FROM schema_version LIMIT 1")
            row = cursor.fetchone()
            return row["version"] if row else None
        except sqlite3.OperationalError:
            return None


def set_schema_version(version: int, project_dir: Optional[Path] = None) -> None:
    """Set the schema version."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schema_version")
        cursor.execute(
            "INSERT INTO schema_version (version) VALUES (?)",
            (version,)
        )
        conn.commit()


# =============================================================================
# Project Repository
# =============================================================================

def create_project(
    path: Path,
    name: Optional[str] = None,
    project_dir: Optional[Path] = None
) -> int:
    """Create a new project record. Returns the project ID."""
    now = datetime.now().isoformat()

    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects (path, name, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (str(path), name, now, now)
        )
        conn.commit()
        return cursor.lastrowid


def get_project(project_dir: Optional[Path] = None) -> Optional[dict]:
    """Get the project record for the given directory."""
    if project_dir is None:
        project_dir = Path.cwd()

    if not db_exists(project_dir):
        return None

    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM projects WHERE path = ?",
            (str(project_dir),)
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_or_create_project(project_dir: Optional[Path] = None) -> int:
    """Get existing project or create new one. Returns project ID."""
    if project_dir is None:
        project_dir = Path.cwd()

    project = get_project(project_dir)
    if project:
        return project["id"]

    return create_project(project_dir, name=project_dir.name, project_dir=project_dir)


def update_project_timestamp(project_id: int, project_dir: Optional[Path] = None) -> None:
    """Update the project's updated_at timestamp."""
    now = datetime.now().isoformat()

    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE projects SET updated_at = ? WHERE id = ?",
            (now, project_id)
        )
        conn.commit()


# =============================================================================
# Stack Repository
# =============================================================================

def add_stack_item(
    project_id: int,
    stack_type: str,
    name: str,
    version: Optional[str] = None,
    project_dir: Optional[Path] = None
) -> None:
    """Add a stack item to the project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO project_stack (project_id, stack_type, name, version)
            VALUES (?, ?, ?, ?)
            """,
            (project_id, stack_type, name, version)
        )
        conn.commit()


def get_stack(project_id: int, project_dir: Optional[Path] = None) -> List[StackItem]:
    """Get all stack items for a project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT stack_type, name, version FROM project_stack WHERE project_id = ?",
            (project_id,)
        )
        return [
            StackItem(stack_type=row["stack_type"], name=row["name"], version=row["version"])
            for row in cursor.fetchall()
        ]


def clear_stack(project_id: int, project_dir: Optional[Path] = None) -> None:
    """Remove all stack items for a project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM project_stack WHERE project_id = ?",
            (project_id,)
        )
        conn.commit()


# =============================================================================
# Agent Repository
# =============================================================================

def add_agent(
    project_id: int,
    agent_name: str,
    project_dir: Optional[Path] = None
) -> None:
    """Add an agent to the project."""
    now = datetime.now().isoformat()

    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO installed_agents (project_id, agent_name, installed_at)
            VALUES (?, ?, ?)
            """,
            (project_id, agent_name, now)
        )
        conn.commit()


def get_agents(project_id: int, project_dir: Optional[Path] = None) -> List[str]:
    """Get all agent names for a project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT agent_name FROM installed_agents WHERE project_id = ?",
            (project_id,)
        )
        return [row["agent_name"] for row in cursor.fetchall()]


def remove_agent(
    project_id: int,
    agent_name: str,
    project_dir: Optional[Path] = None
) -> None:
    """Remove an agent from the project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM installed_agents WHERE project_id = ? AND agent_name = ?",
            (project_id, agent_name)
        )
        conn.commit()


def clear_agents(project_id: int, project_dir: Optional[Path] = None) -> None:
    """Remove all agents for a project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM installed_agents WHERE project_id = ?",
            (project_id,)
        )
        conn.commit()


# =============================================================================
# Skill Repository
# =============================================================================

def add_skill(
    project_id: int,
    skill_name: str,
    project_dir: Optional[Path] = None
) -> None:
    """Add a skill to the project."""
    now = datetime.now().isoformat()

    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO installed_skills (project_id, skill_name, installed_at)
            VALUES (?, ?, ?)
            """,
            (project_id, skill_name, now)
        )
        conn.commit()


def get_skills(project_id: int, project_dir: Optional[Path] = None) -> List[str]:
    """Get all skill names for a project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT skill_name FROM installed_skills WHERE project_id = ?",
            (project_id,)
        )
        return [row["skill_name"] for row in cursor.fetchall()]


def remove_skill(
    project_id: int,
    skill_name: str,
    project_dir: Optional[Path] = None
) -> None:
    """Remove a skill from the project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM installed_skills WHERE project_id = ? AND skill_name = ?",
            (project_id, skill_name)
        )
        conn.commit()


def clear_skills(project_id: int, project_dir: Optional[Path] = None) -> None:
    """Remove all skills for a project."""
    with get_connection(project_dir) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM installed_skills WHERE project_id = ?",
            (project_id,)
        )
        conn.commit()


# =============================================================================
# Bulk Operations
# =============================================================================

def set_agents(
    project_id: int,
    agent_names: List[str],
    project_dir: Optional[Path] = None
) -> None:
    """Set the agents for a project, replacing any existing ones."""
    clear_agents(project_id, project_dir)
    for name in agent_names:
        add_agent(project_id, name, project_dir)


def set_skills(
    project_id: int,
    skill_names: List[str],
    project_dir: Optional[Path] = None
) -> None:
    """Set the skills for a project, replacing any existing ones."""
    clear_skills(project_id, project_dir)
    for name in skill_names:
        add_skill(project_id, name, project_dir)


def set_stack(
    project_id: int,
    stack_items: List[StackItem],
    project_dir: Optional[Path] = None
) -> None:
    """Set the stack for a project, replacing any existing items."""
    clear_stack(project_id, project_dir)
    for item in stack_items:
        add_stack_item(project_id, item.stack_type, item.name, item.version, project_dir)
