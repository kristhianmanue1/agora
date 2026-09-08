#!/usr/bin/env python3
"""Create the minimal macOS process isolation used by the M1 harness."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


SANDBOX_EXEC = Path("/usr/bin/sandbox-exec")


def _quote(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')


def require_backend() -> Path:
    if os.uname().sysname != "Darwin" or not SANDBOX_EXEC.is_file():
        raise RuntimeError("isolation_backend_unavailable")
    return SANDBOX_EXEC


def sanitized_environment(run_root: Path) -> dict[str, str]:
    home = run_root / "producer" / "home"
    temporary = run_root / "producer" / "tmp"
    workspace = run_root / "producer" / "workspace"
    instructions = run_root / "input" / "instructions"
    record = workspace / ".agora-execution-record.json"
    for path in (home, temporary, workspace, instructions):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "PATH": "/usr/bin:/bin",
        "HOME": str(home),
        "TMPDIR": str(temporary),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "AGORA_INPUT_DIR": str(instructions),
        "AGORA_WORKSPACE": str(workspace),
        "AGORA_EXECUTION_RECORD": str(record),
    }


def seatbelt_profile(run_root: Path) -> str:
    readable = [
        Path("/System"),
        Path("/usr"),
        Path("/bin"),
        Path("/Library"),
        Path("/private/var/db/timezone"),
        run_root / "input",
        run_root / "producer" / "workspace",
        run_root / "producer" / "home",
        run_root / "producer" / "tmp",
    ]
    writable = [
        run_root / "producer" / "workspace",
        run_root / "producer" / "home",
        run_root / "producer" / "tmp",
    ]
    read_rules = " ".join(f'(subpath "{_quote(path)}")' for path in readable)
    write_rules = " ".join(f'(subpath "{_quote(path)}")' for path in writable)
    return "\n".join(
        [
            "(version 1)",
            "(deny default)",
            '(import "system.sb")',
            "(allow process*)",
            '(deny process-exec (literal "/bin/ps") (literal "/usr/bin/pgrep")',
            '  (literal "/usr/sbin/lsof") (literal "/usr/sbin/sysctl"))',
            "(allow file-read-metadata)",
            f"(allow file-read* {read_rules})",
            f"(allow file-write* {write_rules})",
            '(allow file-read* (literal "/dev/null") (literal "/dev/urandom"))',
            '(allow file-write* (literal "/dev/null"))',
            "(deny network*)",
            "",
        ]
    )


def copy_adapter(source: Path, run_root: Path) -> Path:
    source = source.resolve()
    if not source.is_file() or source.is_symlink():
        raise ValueError("producer_adapter_must_be_regular_file")
    destination = run_root / "input" / "producer-adapter"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    destination.chmod(0o555)
    return destination
