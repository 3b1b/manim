import configparser
from pathlib import Path

from manimlib.mobject.svg.text_mobject import MarkupText, Text


def test_setup_cfg_includes_av_dependency():
    repo_root = Path(__file__).resolve().parents[1]
    cfg = configparser.ConfigParser()
    cfg.read(repo_root / "setup.cfg")
    install_requires = [
        line.strip().split(";")[0].split(">=")[0].strip()
        for line in cfg["options"]["install_requires"].splitlines()
        if line.strip()
    ]
    assert "av" in install_requires


def test_text_forwards_isolate_and_deduplicates_spans():
    mob = Text("Learn from data!")
    substrings = mob.get_specified_substrings()
    assert substrings == ["Learn", "from", "data", "data!"]
    group_words = [substr for substr, _ in mob.get_group_part_items()]
    assert group_words == ["Learn", "from", "data", "!"]


def test_arabic_rtl_tashkeel_isolation_and_spatial_order():
    mob = Text("تعلّم بلا تعقيد!")
    substrings = mob.get_specified_substrings()
    assert "تعلّم" in substrings
    assert "تعل" not in substrings
    assert "بلا" in substrings
    assert "تعقيد" in substrings

    # In RTL layout, the first logical word ('تعلّم') is positioned to the right (+x)
    # of the middle word ('بلا') and the last word ('تعقيد').
    x_first = float(mob["تعلّم"].get_center()[0])
    x_mid = float(mob["بلا"].get_center()[0])
    x_last = float(mob["تعقيد"].get_center()[0])
    assert x_first > x_mid > x_last

    group_words = [substr for substr, _ in mob.get_group_part_items()]
    assert all(word != "" for word in group_words)
    assert set(group_words) == {"تعلّم", "بلا", "تعقيد", "!"}


def test_markuptext_forwards_custom_isolate():
    mob = MarkupText("alpha beta", isolate=["alpha", "beta"])
    assert mob.get_specified_substrings() == ["alpha", "beta"]
