"""
Renders a fixed list of scenes and compares them against references rendered earlier.

There is no way to unit test a renderer. What there is, is the frame it drew last time.
So: capture references from a tree known to be good, then compare against them after every
change which has any business leaving the picture alone.

    python tests/render_compare.py capture --refs <dir>
    python tests/render_compare.py compare --refs <dir>

Any case which differs is reported with how far off it is, how much of that is away from any
edge of any shape, and, for the worst frame, an image written to the output directory showing
the two side by side over their difference. The count away from an edge is the one to read: two
rasterizers will never agree along an edge, and are expected to everywhere else.

A tolerance may be given for comparing renders which have no business being identical to the
byte, as across a change of graphics api. Within one renderer, leave it at zero.

Videos are written losslessly, see LOSSLESS_CONFIG, since otherwise what is compared is what
an encoder made of a frame rather than the frame.

    --only NAME [NAME ...]   just these cases
    --tolerance N            allow a per channel difference of up to N out of 255
    --quality l|m|hd|uhd     what to render at, low by default
    --twice                  (capture) render everything twice and report anything unstable
    --no-bundling            draw every frame afresh rather than replaying a render bundle
    --no-merging             draw every mobject on its own rather than gathering runs

Both of those are meant to be invisible, so capturing with one and comparing without it is a
test of that, animations included. With one exception: gathering anti-aliases a fill against
the whole run's winding rather than one mobject's, so an edge pixel between two close glyphs
may land differently. A render made without gathering is judged by what differs away from an
edge, see run.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Sequence

import numpy as np
from PIL import Image
from scipy import ndimage


TESTS = Path(__file__).parent
SCENES = TESTS / "scenes.py"
EXAMPLES = TESTS.parent / "example_scenes.py"

# Every case is a scene, the file holding it, and whether one frame of it is enough. The
# stills are quick and cover how a frame is drawn; the videos cover everything which only
# goes wrong once a mobject changes between frames.
CASES = [
    (SCENES, "Fills", "still"),
    (SCENES, "Strokes", "still"),
    (SCENES, "PartialDraws", "still"),
    (SCENES, "TextAndTex", "still"),
    (SCENES, "ClipPlanes", "still"),
    (SCENES, "ClippedInThree", "still"),
    (SCENES, "Surfaces", "still"),
    (SCENES, "TransparentSurfaces", "still"),
    (SCENES, "TexturedAndImages", "still"),
    (SCENES, "DotsAndVectors", "still"),
    (SCENES, "FixedInFrame", "still"),
    (SCENES, "Zoomed", "still"),
    (SCENES, "ByCode", "still"),
    (SCENES, "DrawnTogether", "still"),
    (SCENES, "AnimWrite", "video"),
    (SCENES, "AnimTransform", "video"),
    (SCENES, "AnimShapes", "video"),
    (SCENES, "AnimUpdaters", "video"),
    (SCENES, "AnimCamera", "video"),
    (SCENES, "AnimSorted", "video"),
    (SCENES, "AnimTextTransform", "video"),
    # The example scenes are the closest thing to real content in the repository, and
    # between them they exercise most of what a video would
    (EXAMPLES, "OpeningManimExample", "still"),
    (EXAMPLES, "AnimatingMethods", "still"),
    (EXAMPLES, "TextExample", "still"),
    (EXAMPLES, "TexTransformExample", "still"),
    (EXAMPLES, "TexIndexing", "still"),
    (EXAMPLES, "UpdatersExample", "still"),
    (EXAMPLES, "CoordinateSystemExample", "still"),
    (EXAMPLES, "GraphExample", "still"),
    (EXAMPLES, "SurfaceExample", "still"),
    (EXAMPLES, "TexAndNumbersExample", "still"),
    (EXAMPLES, "ControlsExample", "still"),
]

QUALITY_FLAGS = {"l": "-l", "m": "-m", "hd": "--hd", "uhd": "--uhd"}

# A video written the way one meant for watching is written comes back nothing like the
# frames that went in: a smooth gradient beside a sharp edge lands a hundred values out of
# 255 away, which is far more than any difference worth noticing here. So the cases which
# are videos are written losslessly, which costs disk and nothing else.
LOSSLESS_CONFIG = """
file_writer:
  video_codec: "libx264rgb"
  pixel_format: "rgb24"
  crf: 0
"""
# What a render is told when asked to draw the plain way rather than by replaying a bundle
# or gathering mobjects into runs, both of which are meant to come out to the same picture,
# see Renderer
PLAIN_DRAWING = {"bundle_draws": "--no-bundling", "draw_together": "--no-merging"}


def render(case, into: Path, quality: str, plainly: Sequence[str] = ()) -> Path | None:
    """One case into a directory of its own, coming back with what it wrote"""
    path, scene, kind = case
    into.mkdir(parents=True, exist_ok=True)
    config = into / "lossless.yml"
    settings = "".join(f"  {name}: False\n" for name in plainly)
    config.write_text(LOSSLESS_CONFIG + (f"camera:\n{settings}" if settings else ""))
    command = ["manimgl", str(path), scene, "-w", QUALITY_FLAGS[quality],
               "--video_dir", str(into), "--config_file", str(config)]
    if kind == "still":
        command.append("-s")
    result = subprocess.run(command, capture_output=True, text=True)
    written = list(into.glob(f"{scene}.*"))
    if not written:
        tail = "\n".join(result.stderr.strip().splitlines()[-6:])
        print(f"  {scene:28s} FAILED TO RENDER\n{tail}")
        return None
    return written[0]


def frames_of(path: Path, into: Path) -> list[np.ndarray]:
    """Every frame of what was rendered, whether that is a still or a video"""
    if path.suffix == ".png":
        return [np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)]
    into.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(path), str(into / "%05d.png")],
        check=True,
    )
    return [
        np.asarray(Image.open(frame).convert("RGB"), dtype=np.int16)
        for frame in sorted(into.glob("*.png"))
    ]


# What counts as being where a reference's own color is changing, and how far around a pixel
# to look for that. Two rasterizers fill a triangle from different sample points, so the
# pixels along a shape's edge are the ones they were never going to agree about; a pixel in
# the middle of a flat region is not, and a difference there is worth a closer look.
EDGE_CONTRAST = 8
EDGE_REACH = 2


def edges_of(reference: np.ndarray) -> np.ndarray:
    """Which pixels of a reference sit where its own color is changing"""
    size = 2 * EDGE_REACH + 1
    spread = np.zeros(reference.shape[:2])
    for channel in range(3):
        plane = reference[:, :, channel].astype(float)
        spread = np.maximum(
            spread,
            ndimage.maximum_filter(plane, size) - ndimage.minimum_filter(plane, size),
        )
    return spread > EDGE_CONTRAST


def compare_frames(new: list[np.ndarray], old: list[np.ndarray]) -> dict:
    """How far apart two renders are, and which frame is the worst of it"""
    if len(new) != len(old):
        return {"error": f"{len(new)} frames against {len(old)}"}
    worst = {"frame": 0, "max": 0, "pixels": 0, "inside": 0, "inside_max": 0}
    differing = 0
    for index, (a, b) in enumerate(zip(new, old)):
        if a.shape != b.shape:
            return {"error": f"{a.shape} against {b.shape}"}
        diff = np.abs(a - b).max(axis=2)
        pixels = int((diff > 0).sum())
        if pixels:
            differing += 1
        inside = (diff > 0) & ~edges_of(b)
        result = {
            "frame": index,
            "max": int(diff.max()),
            "pixels": pixels,
            "inside": int(inside.sum()),
            "inside_max": int(diff[inside].max()) if inside.any() else 0,
        }
        # The frame to report is the one differing most where it has least excuse to, and
        # failing that the one differing most anywhere
        if (result["inside_max"], result["max"]) > (worst["inside_max"], worst["max"]):
            worst = result
    return {"frames": len(new), "differing": differing, **worst}


def write_diff_image(new: np.ndarray, old: np.ndarray, path: Path) -> None:
    """The reference over the new render over their difference, brightened to be visible"""
    diff = np.abs(new - old)
    amplified = np.clip(diff * max(1, 255 // max(1, int(diff.max()))), 0, 255)
    rule = np.full((4, new.shape[1], 3), 128)
    stack = np.vstack([old, rule, new, rule, amplified]).astype(np.uint8)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(stack).save(path)


def run(args) -> int:
    cases = [case for case in CASES if not args.only or case[1] in args.only]
    if args.only:
        missing = set(args.only) - {case[1] for case in cases}
        if missing:
            print(f"No such case: {', '.join(sorted(missing))}")
            return 2

    plainly = [
        setting for setting, flag in PLAIN_DRAWING.items()
        if getattr(args, flag.lstrip("-").replace("-", "_"))
    ]
    refs = Path(args.refs).expanduser()
    work = refs / "_work"
    if work.exists():
        shutil.rmtree(work)

    failures = []
    for case in cases:
        _, scene, kind = case
        if args.command == "capture":
            rendered = render(case, refs / "render", args.quality, plainly)
            if rendered is None:
                failures.append(scene)
                continue
            kept = refs / rendered.name
            shutil.move(str(rendered), kept)
            note = ""
            if args.twice:
                again = render(case, work / "again", args.quality, plainly)
                same = again is not None and compare_frames(
                    frames_of(again, work / "frames_a"),
                    frames_of(kept, work / "frames_b"),
                ).get("max") == 0
                note = "  stable" if same else "  NOT STABLE between runs"
                if not same:
                    failures.append(scene)
            print(f"  {scene:28s} captured{note}")
            continue

        reference = next((refs / f"{scene}.{ext}" for ext in ["png", "mp4"]
                          if (refs / f"{scene}.{ext}").exists()), None)
        if reference is None:
            print(f"  {scene:28s} NO REFERENCE")
            failures.append(scene)
            continue
        rendered = render(case, work / "render", args.quality, plainly)
        if rendered is None:
            failures.append(scene)
            continue
        new = frames_of(rendered, work / "frames_new")
        old = frames_of(reference, work / "frames_old")
        report = compare_frames(new, old)
        if "error" in report:
            print(f"  {scene:28s} SHAPE MISMATCH: {report['error']}")
            failures.append(scene)
            continue
        # Gathering can only move a pixel where a fill meets its own edge, so a render made
        # without it is allowed to differ from a gathered reference exactly there
        edges_only = "draw_together" in plainly and report["pixels"] and not report["inside"]
        if report["max"] <= args.tolerance or edges_only:
            within = ""
            if edges_only:
                within = f" (differs on {report['pixels']} px, all along an edge)"
            elif report["max"]:
                within = f" (within tolerance, max {report['max']})"
            print(f"  {scene:28s} matches{within}")
            continue
        where = "" if report["frames"] == 1 else \
            f", {report['differing']}/{report['frames']} frames, worst {report['frame'] + 1}"
        inside = "none away from an edge" if not report["inside"] else \
            f"{report['inside']} away from an edge, max {report['inside_max']} there"
        print(f"  {scene:28s} DIFFERS: max {report['max']} on {report['pixels']} px, "
              f"{inside}{where}")
        out = Path(args.out) / f"{scene}.png"
        write_diff_image(new[report["frame"]], old[report["frame"]], out)
        failures.append(scene)

    if work.exists():
        shutil.rmtree(work)
    print()
    if failures:
        print(f"{len(failures)} of {len(cases)}: {', '.join(failures)}")
        if args.command == "compare":
            print(f"Diff images in {args.out}")
        return 1
    print(f"All {len(cases)} cases {'captured' if args.command == 'capture' else 'match'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["capture", "compare", "list"])
    parser.add_argument("--refs", default="~/.cache/manimgl-render-refs")
    parser.add_argument("--out", default="/tmp/manimgl-render-diffs")
    parser.add_argument("--only", nargs="+", default=[])
    parser.add_argument("--tolerance", type=int, default=0)
    parser.add_argument("--quality", choices=list(QUALITY_FLAGS), default="l")
    parser.add_argument("--twice", action="store_true")
    parser.add_argument("--no-bundling", action="store_true")
    parser.add_argument("--no-merging", action="store_true")
    args = parser.parse_args()
    if args.command == "list":
        for path, scene, kind in CASES:
            print(f"  {scene:28s} {kind:6s} {path.name}")
        return 0
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
