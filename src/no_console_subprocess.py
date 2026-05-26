"""Hide transient console windows spawned by subprocesses on Windows."""

from __future__ import annotations

import subprocess
import sys


_PATCHED = False


def install_no_console_subprocess_patch() -> None:
    """Ensure child console apps such as ffmpeg do not flash over the GUI."""
    global _PATCHED
    if _PATCHED or sys.platform != "win32":
        return

    original_popen = subprocess.Popen
    create_no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    startupinfo_class = getattr(subprocess, "STARTUPINFO", None)
    startf_use_showwindow = getattr(subprocess, "STARTF_USESHOWWINDOW", 1)
    sw_hide = 0

    class HiddenPopen(original_popen):
        def __init__(self, *args, **kwargs):
            kwargs["creationflags"] = kwargs.get("creationflags", 0) | create_no_window

            startupinfo = kwargs.get("startupinfo")
            if startupinfo is None and startupinfo_class is not None:
                startupinfo = startupinfo_class()
                kwargs["startupinfo"] = startupinfo

            if startupinfo is not None:
                startupinfo.dwFlags |= startf_use_showwindow
                startupinfo.wShowWindow = sw_hide

            super().__init__(*args, **kwargs)

    subprocess.Popen = HiddenPopen
    _PATCHED = True
