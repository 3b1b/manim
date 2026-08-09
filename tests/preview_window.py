"""
That a scene shown in a window reaches the screen.

Every other test here renders with -w, which never opens a window, so the whole of window.py
goes untried: configuring a surface for a device, and the pass which puts a finished frame onto
it. Worse, the canvas catches whatever a draw raises and logs it, so a window which throws on
every frame still exits 0 and still writes the file it was asked for. A rename which missed one
line of Window.present survived the whole harness that way.

    python tests/preview_window.py

Needs a display; without one there is nothing to test rather than anything to report. What a
surface actually showed cannot be read back, so what is checked is that every frame went
through present without raising, that nothing which looks like a traceback reached the log, and
that the scene drew through the window's own device.

That last is what a surface being configurable for one device only comes to. Asking for several
scenes at once used to give the first of them a device of its own and then point the surface at
the last one's, so every frame of it failed validation and the preview stayed black. Note that
only the first of several is shown either way, a scene destroying its window as it tears down.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


WORK = Path("/tmp/manimgl-preview-window")
# What the canvas says when there is no display to open a window on
NO_DISPLAY = ("glfw", "GLFW", "display")
# What a frame drawn by one device and presented on a surface belonging to another comes to
DEVICE_MISMATCH = "doesn't match Device"
# Long enough for a scene to be built and shown, short enough that a window left open is
# reported rather than waited on
TIMEOUT = 180

SCENES = '''
from manimlib import *
from manimlib.window import Window

# Whatever a draw raises is caught and logged by the canvas, so it is noted here on the way
# past as well, there being no exit code to read it from
FAILURES = []
PRESENTS = [0]

present_original = Window.present


def present(self, target_view):
    try:
        result = present_original(self, target_view)
    except BaseException as error:
        FAILURES.append(f"{type(error).__name__}: {error}")
        raise
    PRESENTS[0] += 1
    return result


Window.present = present


class Shown(Scene):
    """Enough frames to be sure the presenting pass runs more than once"""

    def construct(self):
        self.add(NumberPlane())
        dot = Dot(color=YELLOW)
        self.add(dot)
        self.play(dot.animate.shift(RIGHT * 2), run_time=0.3)
        own = self.camera.gpu is self.window.gpu
        print(f"WINDOW|{type(self).__name__}|{PRESENTS[0]}|{own}|"
              f"{'; '.join(FAILURES[:1])}")
        # Ends the loop Scene.run enters after construct, which otherwise waits to be
        # closed by hand
        self.quit_interaction = True


class ShownSecond(Shown):
    """Named after the first so that both are asked for at once"""
'''


def run(*scenes: str) -> str:
    """
    Those scenes in one process. Given a deadline, a window which never comes down being a
    hang rather than an answer.
    """
    try:
        result = subprocess.run(
            ["manimgl", str(WORK / "scenes.py"), *scenes, "-l",
             "--config_file", str(WORK / "empty.yml")],
            capture_output=True, text=True, timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired as expired:
        return (expired.stdout or "") + (expired.stderr or "") + "\nTIMED OUT"
    return result.stdout + result.stderr


def check(what: str, *scenes: str) -> list[str]:
    """One run, reported on and judged by what its first scene managed"""
    output = run(*scenes)
    reports = [line for line in output.splitlines() if line.startswith("WINDOW|")]
    if not reports:
        if any(word in output for word in NO_DISPLAY):
            print(f"  {what}: SKIPPED, no display to open a window on")
            return []
        if "TIMED OUT" in output:
            return [f"{what}: the window never came down, so the scene waited on it"]
        tail = "\n".join(output.strip().splitlines()[-8:])
        return [f"{what}: nothing reached a window at all\n{tail}"]

    _, name, presents, own_device, raised = reports[0].split("|")
    presents = int(presents)
    print(f"  {what}: {presents} frames presented, "
          f"drawn by the window's own device: {own_device}")

    failures = []
    if raised:
        failures.append(f"{what}: presenting raised: {raised}")
    if presents < 2:
        failures.append(f"{what}: only {presents} frames were presented, wanted at least 2")
    if own_device != "True":
        failures.append(
            f"{what}: the scene drew through a device of its own while the surface is "
            f"configured for the window's, so nothing it draws can be presented"
        )
    if DEVICE_MISMATCH in output:
        failures.append(f"{what}: a frame was presented on a surface belonging to another device")
    # A traceback the canvas logged rather than raised, which is the whole reason for this file
    if "Draw error" in output:
        logged = [line for line in output.splitlines() if "Error" in line][:3]
        failures.append(f"{what}: something was logged while drawing:\n    "
                        + "\n    ".join(logged))
    return failures


def main() -> int:
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "scenes.py").write_text(SCENES)
    (WORK / "empty.yml").write_text("")

    failures = check("one scene", "Shown")
    # Several at once is what used to hand the first scene a device the surface was not
    # configured for, every scene built before any of them ran
    failures += check("first of two", "Shown", "ShownSecond")

    for failure in failures:
        print(f"  FAIL: {failure}")
    if not failures:
        print("  frames drawn for a window reach it")
    return 1 if failures else 0


sys.exit(main())
