import ast
import subprocess
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from app.database.base import Base


def test_alembic_config_loads_without_credentials() -> None:
    """Verify that alembic.ini loads correctly and contains no database credentials."""
    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"

    assert ini_path.exists(), "alembic.ini must exist in backend root"

    cfg = Config(str(ini_path))
    url = cfg.get_main_option("sqlalchemy.url")
    assert not url or url.strip() == "", "sqlalchemy.url in alembic.ini must remain empty/unset"


def test_alembic_target_metadata_references_base() -> None:
    """Verify that alembic/env.py specifies target_metadata = Base.metadata."""
    backend_dir = Path(__file__).resolve().parent.parent
    env_py_path = backend_dir / "alembic" / "env.py"

    assert env_py_path.exists(), "alembic/env.py must exist"

    content = env_py_path.read_text(encoding="utf-8")
    assert "target_metadata = Base.metadata" in content
    assert Base.metadata is not None


def test_baseline_migration_exists_and_is_empty() -> None:
    """Verify that the baseline revision exists and contains no DDL operations."""
    backend_dir = Path(__file__).resolve().parent.parent
    ini_path = backend_dir / "alembic.ini"
    cfg = Config(str(ini_path))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    script_dir = ScriptDirectory.from_config(cfg)
    revisions = list(script_dir.walk_revisions())

    baseline_rev = next((r for r in revisions if "baseline_database" in (r.doc or "")), None)
    assert baseline_rev is not None, "baseline_database revision must exist in Alembic history"

    # Inspect the python AST of the baseline migration file
    migration_file = Path(baseline_rev.path)
    assert migration_file.exists()

    tree = ast.parse(migration_file.read_text(encoding="utf-8"))

    forbidden_calls = {
        "create_table",
        "drop_table",
        "add_column",
        "drop_column",
        "create_index",
        "drop_index",
        "execute",
    }

    found_forbidden = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in forbidden_calls:
                found_forbidden.append(node.func.attr)

    assert not found_forbidden, f"Baseline migration must contain no DDL calls, found: {found_forbidden}"


def test_env_file_is_ignored_by_git() -> None:
    """Verify that backend/.env is properly ignored by Git."""
    backend_dir = Path(__file__).resolve().parent.parent
    repo_root = backend_dir.parent

    result = subprocess.run(
        ["git", "check-ignore", "backend/.env"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "backend/.env must be ignored by git"
    assert "backend/.env" in result.stdout.strip()
