#!/usr/bin/env python3
"""Create the minimal macOS process isolation used by the M1 harness."""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path


SANDBOX_EXEC = Path("/usr/bin/sandbox-exec")


def _quote(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace('"', '\\"')


def require_backend() -> Path:
    if os.uname().sysname != "Darwin" or not SANDBOX_EXEC.is_file():
        raise RuntimeError("isolation_backend_unavailable")
    return SANDBOX_EXEC


def copy_regular_file(
    source: Path,
    destination: Path,
    *,
    error: str,
    max_bytes: int | None = None,
) -> tuple[os.stat_result, int]:
    """Copy from a no-follow descriptor and bind the copy to the lstat object."""
    try:
        source_stat = source.lstat()
    except OSError as cause:
        raise ValueError(error) from cause
    if not stat.S_ISREG(source_stat.st_mode):
        raise ValueError(error)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(source, flags)
    except OSError as cause:
        raise ValueError(error) from cause
    try:
        observed = os.fstat(descriptor)
        if not stat.S_ISREG(observed.st_mode) or (
            observed.st_dev,
            observed.st_ino,
        ) != (source_stat.st_dev, source_stat.st_ino):
            raise ValueError(error)
        destination.parent.mkdir(parents=True, exist_ok=True)
        copied = 0
        with os.fdopen(descriptor, "rb", closefd=False) as source_handle, destination.open("xb") as target:
            while chunk := source_handle.read(1024 * 1024):
                copied += len(chunk)
                if max_bytes is not None and copied > max_bytes:
                    raise ValueError(error)
                target.write(chunk)
        return observed, copied
    finally:
        os.close(descriptor)


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
        Path("/private/var/select"),
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
            "(deny process-info*)",
            "(allow process-info* (target self))",
            "(allow process-info-codesignature)",
            '(deny process-exec (literal "/bin/ps") (literal "/usr/bin/pgrep")',
            '  (literal "/usr/sbin/lsof") (literal "/usr/sbin/sysctl"))',
            f"(allow file-read* {read_rules})",
            f"(allow file-write* {write_rules})",
            '(allow file-read* (literal "/dev/null") (literal "/dev/urandom"))',
            '(allow file-write* (literal "/dev/null"))',
            "(deny network*)",
            "",
        ]
    )


def copy_adapter(source: Path, run_root: Path) -> Path:
    source = source.absolute()
    try:
        source_stat = source.lstat()
    except OSError as error:
        raise ValueError("producer_adapter_must_be_regular_file") from error
    if not stat.S_ISREG(source_stat.st_mode):
        raise ValueError("producer_adapter_must_be_regular_file")
    destination = run_root / "input" / "producer-adapter"
    copy_regular_file(source, destination, error="producer_adapter_changed_or_unreadable")
    destination.chmod(0o555)
    return destination
