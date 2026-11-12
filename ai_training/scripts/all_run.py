from __future__ import annotations

import runpy
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
YUNET_RUN = SCRIPTS_DIR / "yunet" / "run.py"
SFACE_RUN = SCRIPTS_DIR / "sface" / "run.py"


def main() -> int:
    print("[1/2] Running YuNet...")
    yunet_code = _run_script(YUNET_RUN)
    if yunet_code != 0:
        return yunet_code

    if not SFACE_RUN.exists():
        print("[2/2] SFace is not ready yet. Skip.")
        return 0

    print("[2/2] Running SFace...")
    return _run_script(SFACE_RUN)


def _run_script(script_path: Path) -> int:
    script_dir = str(script_path.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    try:
        runpy.run_path(str(script_path), run_name="__main__")
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
