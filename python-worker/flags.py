import os
from pathlib import Path
import yaml

_flags = {}


def load_flags(path: str = "config/flags.yaml") -> None:
    global _flags
    config_path = Path(path)
    if not config_path.exists():
        _flags = {}
        return
    with config_path.open('r', encoding='utf-8') as handle:
        data = yaml.safe_load(handle) or {}
    items = (data.get('flags') or {})
    _flags = {key: bool(value.get('default', False)) for key, value in items.items()}


def is_enabled(name: str) -> bool:
    env_key = f"FLAG_{name.upper()}"
    if env_key in os.environ:
        return os.environ[env_key].lower() == 'true'
    return _flags.get(name, False)


load_flags()
