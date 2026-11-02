import io
import subprocess

import pytest

from manimlib.config import manim_config
from manimlib.utils import tex_file_writing
from manimlib.utils.tex_file_writing import LatexError
from manimlib.utils.tex_file_writing import get_full_tex


# Skip the on-disk cache
full_tex_to_svg = tex_file_writing.full_tex_to_svg.__wrapped__


@pytest.fixture
def latex_cache(monkeypatch, tmp_path):
    # Behave like Windows with a non-UTF-8 code page (cp1252, cp932, ...),
    # where text files opened without an explicit encoding use that code page
    monkeypatch.setattr(
        io, "text_encoding", lambda encoding, stacklevel=2: encoding or "cp1252"
    )
    monkeypatch.setitem(manim_config.directories, "latex_cache", str(tmp_path))
    return tmp_path


def test_tex_file_is_written_as_utf8(latex_cache, monkeypatch):
    written = []

    def fake_run(command, **kwargs):
        if command[0] == "dvisvgm":
            return subprocess.CompletedProcess(command, 0, b"<svg></svg>", b"")
        written.append((latex_cache / "working.tex").read_bytes())
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    svg = full_tex_to_svg(get_full_tex("caf\u00e9 \u4e2d\u6587"))

    assert svg == "<svg></svg>"
    assert "caf\u00e9 \u4e2d\u6587".encode("utf-8") in written[0]


def test_latex_error_message_is_read_as_utf8(latex_cache, monkeypatch):
    def fake_run(command, **kwargs):
        log = "This is pdfTeX\n! Undefined control sequence.\nl.7 caf\u00e9 \\foo\n"
        (latex_cache / "working.log").write_bytes(log.encode("utf-8"))
        return subprocess.CompletedProcess(command, 1, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(LatexError, match="l.7 caf\u00e9"):
        full_tex_to_svg(get_full_tex("caf\u00e9 \\foo"))
