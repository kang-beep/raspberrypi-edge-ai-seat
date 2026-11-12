from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable

from config import YUNET_DIR

_MODULE_NAMES = ("config", "download_model", "detector")


def load_yunet_api() -> tuple[Callable[[], Path], type]:
    saved = {name: sys.modules.pop(name, None) for name in _MODULE_NAMES}
    inserted = False
    if str(YUNET_DIR) not in sys.path:
        sys.path.insert(0, str(YUNET_DIR))
        inserted = True

    try:
        _load_yunet_module("config", "config.py")
        download_model = _load_yunet_module("download_model", "download_model.py")
        detector = _load_yunet_module("detector", "detector.py")
        return download_model.ensure_yunet_model, detector.YuNetDetector
    finally:
        for name in _MODULE_NAMES:
            sys.modules.pop(name, None)
        for name, module in saved.items():
            if module is not None:
                sys.modules[name] = module
        if inserted and sys.path and sys.path[0] == str(YUNET_DIR):
            sys.path.pop(0)


def _load_yunet_module(module_name: str, filename: str) -> ModuleType:
    module_path = YUNET_DIR / filename
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load YuNet module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module
