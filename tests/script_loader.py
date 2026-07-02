import importlib.util
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_skill_script(skill_name: str, script_name: str) -> ModuleType:
    module_name = f"mist_skill_{skill_name.replace('-', '_')}_{script_name}"
    script_path = REPO_ROOT / "skills" / skill_name / "scripts" / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {script_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
