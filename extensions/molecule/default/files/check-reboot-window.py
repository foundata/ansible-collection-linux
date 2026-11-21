# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Check the installed helper with a shutdown recorder and systemd calendars."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def check(helper, service, work):
    # Only these executables are visible to the helper, even when run as root.
    for name in ("sh", "grep", "systemd-analyze"):
        (work / name).symlink_to(shutil.which(name))
    for name, body in {
        "logger": "exit 0",
        "zypper": "exit 102",  # A reboot is required on every test platform.
        "shutdown": 'printf "%s\\n" "$*" >> shutdown.calls',
        "busctl": "echo lookup >> bus.calls\nexec /bin/cat timer.json",
    }.items():
        executable = work / name
        executable.write_text(f"#!/bin/sh\n{body}\n")
        executable.chmod(0o755)

    def run(args, *, requests, lookups, status=0):
        for log in ("shutdown.calls", "bus.calls"):
            (work / log).write_text("")
        result = subprocess.run(
            [helper, *args],
            cwd=work,
            env={**os.environ, "PATH": str(work)},
            check=False,
        )
        assert result.returncode == status, (args, result.returncode)
        assert (work / "shutdown.calls").read_text().splitlines() == [
            "-r +1 Reboot required after automatic updates"
        ] * requests, args
        assert len((work / "bus.calls").read_text().splitlines()) == lookups, args

    command = next(
        line.removeprefix("ExecStart=").split()
        for line in service.read_text().splitlines()
        if line.startswith("ExecStart=")
    )
    assert command == [helper, "--respect-timer-window"], command
    guarded = command[1:]
    # Independently of the timer or its availability, a direct call still works.
    run([], requests=1, lookups=0)
    run(["--typo"], requests=0, lookups=0, status=2)
    run([*guarded, "extra"], requests=0, lookups=0, status=2)
    run(guarded, requests=0, lookups=1, status=1)

    now = int(time.time())
    expired = ["OnCalendar", f"@{now - 7200}", 0]
    in_window = ["OnCalendar", f"@{now - 300}", 0]
    future = ["OnCalendar", f"@{now + 7200}", 0]
    timer = {
        "TimersCalendar": [expired, future],
        "TimersMonotonic": [],
        "Persistent": False,
        "OnClockChange": False,
        "OnTimezoneChange": False,
        "RandomizedDelayUSec": 3600_000_000,
    }
    for overrides, requests, status in (
        ({}, 0, 0),  # Both an early and a late firing fall outside a window.
        ({"TimersCalendar": [expired, in_window]}, 1, 0),
        (
            {
                "TimersCalendar": [["OnCalendar", "*-*-* *:*:00/0.1 UTC", 0]],
                "RandomizedDelayUSec": 200_000,
            },
            1,
            0,
        ),
        ({"Persistent": True}, 1, 0),
        ({"TimersMonotonic": [["OnBootUSec", 100, 0]]}, 1, 0),
        ({"OnTimezoneChange": True}, 1, 0),
        ({"OnClockChange": True}, 1, 0),
        ({"RandomizedOffsetUSec": 100}, 1, 0),
        ({"RandomizedDelayUSec": 0}, 1, 0),
        ({"TimersCalendar": []}, 0, 1),
        ({"TimersCalendar": [["OnCalendar", "invalid calendar", 0]]}, 0, 1),
    ):
        properties = {k: {"data": v} for k, v in {**timer, **overrides}.items()}
        (work / "timer.json").write_text(json.dumps({"data": [properties]}))
        run(guarded, requests=requests, lookups=1, status=status)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        check(sys.argv[1], Path(sys.argv[2]), Path(directory))
