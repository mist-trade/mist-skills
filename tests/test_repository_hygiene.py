from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 compatibility
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_python_files_do_not_mutate_sys_path():
    roots = [REPO_ROOT / "skills", REPO_ROOT / "tests"]
    needle = "sys.path" + ".insert"
    offenders = []
    for root in roots:
        for path in sorted(root.rglob("*.py")):
            text = path.read_text(encoding="utf-8")
            if needle in text:
                offenders.append(str(path.relative_to(REPO_ROOT)))

    assert offenders == []


def test_quality_tools_are_configured():
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text())
    dev_deps = pyproject["project"]["optional-dependencies"]["dev"]

    assert any(dep.startswith("ruff") for dep in dev_deps)
    assert any(dep.startswith("pyright") for dep in dev_deps)
    assert any(dep.startswith("black") for dep in dev_deps)
    assert "ruff" in pyproject["tool"]
    assert "pyright" in pyproject["tool"]
    assert "black" in pyproject["tool"]


def test_ci_runs_quality_gates_before_tests():
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()

    assert "ruff check" in workflow
    assert "pyright" in workflow
    assert "black --check" in workflow
    assert "pytest" in workflow
