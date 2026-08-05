"""
That every frame drawn reaches the file, and reaches it unaltered.

Frames are copied off the gpu a frame behind the drawing of them, see camera.FrameStream, so
the last ones drawn are still on their way off when the file is closed. A frame going missing
that way would leave nothing about the picture looking wrong, only the video a frame short.

So: render a scene of a known length, count what came out, and check the last frame of it
against the same frame written straight to a png.

    python tests/readback.py
    python tests/readback.py --quality hd
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image


TESTS = Path(__file__).parent
SCENES = TESTS / "scenes.py"
# What the scene below animates for, at the fps a render uses, which is how many frames a
# file of it has to hold
RUN_TIME = 0.5
FPS = 30
EXPECTED_FRAMES = int(RUN_TIME * FPS)

SCENE = f'''
from manimlib import *


class ReadbackScene(Scene):
    """
    Something whose every frame differs from the last, so that a frame arriving twice or not
    at all cannot go unnoticed, and which ends where it can also be reached with -s.
    """

    def construct(self):
        dots = Group(*(
            Dot(radius=0.2).set_color(color)
            for color in [RED, GREEN, BLUE, YELLOW]
        )).arrange(RIGHT, buff=0.5)
        label = Text("readback", font_size=48).next_to(dots, DOWN)
        self.add(dots, label)
        self.play(
            dots.animate.shift(2 * UP).set_color(WHITE),
            run_time={RUN_TIME},
        )
'''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quality", default="l", choices=["l", "m", "hd", "uhd"])
    parser.add_argument("--out", default="/tmp/manimgl-readback")
    args = parser.parse_args()

    work = Path(args.out)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    scene_file = work / "readback_scene.py"
    scene_file.write_text(SCENE)
    config = work / "lossless.yml"
    # Whatever a frame is compared against has to be the frame, not an encoding of it
    config.write_text(
        'file_writer:\n  video_codec: "libx264rgb"\n  pixel_format: "rgb24"\n  crf: 0\n'
    )

    def render(*extra) -> None:
        subprocess.run(
            ["manimgl", str(scene_file), "ReadbackScene", "-w", f"-{args.quality}"
             if args.quality in "lm" else f"--{args.quality}",
             "--config_file", str(config), "--video_dir", str(work), *extra],
            check=True, capture_output=True, text=True,
        )

    render()
    render("-s")
    movie = work / "ReadbackScene.mp4"
    still = work / "ReadbackScene.png"

    frames = work / "frames"
    frames.mkdir()
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(movie), str(frames / "%05d.png")],
        check=True,
    )
    written = sorted(frames.glob("*.png"))

    failures = []
    if len(written) != EXPECTED_FRAMES:
        failures.append(
            f"{len(written)} frames in the file, against the {EXPECTED_FRAMES} drawn"
        )

    if written:
        last = np.asarray(Image.open(written[-1]).convert("RGB"), dtype=int)
        end = np.asarray(Image.open(still).convert("RGB"), dtype=int)
        if last.shape != end.shape:
            failures.append(f"last frame is {last.shape}, the still is {end.shape}")
        else:
            difference = np.abs(last - end)
            if difference.max() > 0:
                failures.append(
                    f"the last frame written differs from the same frame drawn straight to "
                    f"a png: max {int(difference.max())} on "
                    f"{int((difference.max(axis=2) > 0).sum())} pixels"
                )

    # And that no two frames came out the same, which is what a frame arriving twice, or a
    # buffer being read before its copy landed, would look like
    seen = {}
    for path in written:
        digest = Image.open(path).convert("RGB").tobytes()
        if digest in seen:
            failures.append(f"frames {seen[digest]} and {path.name} are identical")
        seen[digest] = path.name

    print(f"  {len(written)} frames written, {EXPECTED_FRAMES} expected")
    for failure in failures:
        print(f"  FAIL: {failure}")
    if not failures:
        print("  every frame arrived, once, unaltered")
    return 1 if failures else 0


sys.exit(main())
