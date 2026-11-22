# SPDX-FileCopyrightText: foundata GmbH <https://foundata.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise a live weekly-to-daily migration on the disposable Debian 13 VM."""

import shutil
import subprocess
import tempfile
import time
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path

TIMERS = ("apt-daily-upgrade.timer", "auto-update-reboot.timer")


def systemctl(*args):
    return subprocess.check_output(["systemctl", *args], text=True).strip()


def calendar(timestamp, *, weekly=False):
    condition = "%a *-*-*" if weekly else "*-*-*"
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime(
        condition + " %H:%M:%S UTC"
    )


def schedule(calendars, delay):
    return "\n".join(
        [
            "[Timer]",
            "OnCalendar=",
            *("OnCalendar=" + entry for entry in calendars),
            "OnClockChange=false",
            "OnTimezoneChange=false",
            "Persistent=false",
            "AccuracySec=1us",
            f"RandomizedDelaySec={delay}",
            "",
        ]
    )


def events(work, name):
    return [int(line) for line in (work / name).read_text().splitlines()]


def wait_for(predicate, deadline, description):
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(0.1)
    raise AssertionError(description)


def exercise(work, overrides):
    # Isolate PATH so a broken or missing recorder cannot reach a real shutdown.
    for name in ("sh", "grep", "date", "logger", "busctl", "systemd-analyze"):
        (work / name).symlink_to(shutil.which(name))
    for name in ("updates", "checks", "shutdowns"):
        (work / name).touch()
    for name, body in {
        "record-update": f"date +%s >> {work}/updates",
        "record-check": f"date +%s >> {work}/checks",
        "shutdown": f"date +%s >> {work}/shutdowns",
        "zypper": "exit 102",  # Force a reboot requirement on every invocation.
    }.items():
        script = work / name
        script.write_text(f"#!/bin/sh\n{body}\n")
        script.chmod(0o755)

    def dropin(unit):
        directory = Path("/run/systemd/system") / (unit + ".d")
        if not directory.exists():
            directory.mkdir()
            overrides.callback(directory.rmdir)
        target = directory / "zz-molecule-active-timers.conf"
        target.touch(exist_ok=False)
        overrides.callback(target.unlink)
        return target

    dropin("apt-daily-upgrade.service").write_text(
        f"[Service]\nExecStartPre=\nExecStart=\nExecStart={work}/record-update\n"
    )
    dropin("auto-update-reboot.service").write_text(
        f'[Service]\nEnvironment="PATH={work}"\nExecStartPre={work}/record-check\n'
    )
    timers = [dropin(unit) for unit in TIMERS]
    weekly = int(time.time()) + 6
    for timer in timers:
        timer.write_text(schedule([calendar(weekly, weekly=True)], 0))
    systemctl("daemon-reload")
    systemctl("start", *TIMERS)
    wait_for(
        lambda: all(
            any(t >= weekly for t in events(work, name))
            for name in ("updates", "shutdowns")
        ),
        weekly + 15,
        "Both weekly timers must run before the migration",
    )
    invocations = [
        systemctl("show", "-p", "InvocationID", "--value", unit) for unit in TIMERS
    ]
    baseline = {
        name: len(events(work, name)) for name in ("updates", "checks", "shutdowns")
    }

    # The daily slot must fall after the last weekly trigger but its entire
    # randomized window must have expired by the time the units are reloaded.
    missed = int(time.time()) + 2
    delay = 8
    time.sleep(max(0, missed + delay + 1 - time.time()))
    upcoming = int(time.time()) + 18
    # Overlap two legitimate slots. Even a randomized expiry very near the
    # end of the first slot leaves time for the oneshot to start in the second.
    following = upcoming + delay // 2
    for timer in timers:
        timer.write_text(
            schedule([calendar(t) for t in (missed, upcoming, following)], delay)
        )
    systemctl("daemon-reload")
    # Some systemd versions immediately catch up. Either behavior is safe
    # provided the out-of-window activation cannot schedule a shutdown.
    time.sleep(max(0, upcoming - 2 - time.time()))
    for name, previous in baseline.items():
        print(f"Live reload: {len(events(work, name)) - previous} {name}", flush=True)
    assert len(events(work, "shutdowns")) == baseline["shutdowns"], (
        "Out-of-window shutdown requested"
    )
    assert invocations == [
        systemctl("show", "-p", "InvocationID", "--value", unit) for unit in TIMERS
    ]
    wait_for(
        lambda: len(events(work, "shutdowns")) > baseline["shutdowns"],
        following + delay + 5,
        "Expected a shutdown request from the following real timer event",
    )
    assert all(
        upcoming <= timestamp <= following + delay
        for timestamp in events(work, "shutdowns")[baseline["shutdowns"] :]
    )


if __name__ == "__main__":
    for timer in TIMERS:
        assert systemctl("is-active", timer) == "active"
    with tempfile.TemporaryDirectory(dir="/opt") as directory:
        systemctl("stop", *TIMERS)
        try:
            with ExitStack() as overrides:
                try:
                    exercise(Path(directory), overrides)
                finally:
                    systemctl(
                        "stop",
                        *TIMERS,
                        *(unit.replace(".timer", ".service") for unit in TIMERS),
                    )
        finally:
            systemctl("daemon-reload")
            systemctl("start", *TIMERS)
