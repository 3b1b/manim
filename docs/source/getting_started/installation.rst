Installation
============

This guide is for ManimGL (the ``manimgl`` package), not Manim Community.
Use `uv <https://docs.astral.sh/uv/getting-started/installation/>`__ to manage
this repository's Python environment and dependencies.

System dependencies
-------------------

Before rendering, install `FFmpeg <https://ffmpeg.org/download.html>`__ and
ensure it is on ``PATH``. A compatible GPU and graphics drivers are also needed.

On macOS:

.. code-block:: sh

   brew install ffmpeg cairo pango pkg-config

On Ubuntu/Debian:

.. code-block:: sh

   sudo apt update
   sudo apt install ffmpeg libpango1.0-dev pkg-config

On Windows, follow the FFmpeg download instructions and add its binaries to
``PATH``.

Scenes using ``Tex`` or ``TexText`` also need LaTeX and ``dvisvgm``. Use
`MacTeX or BasicTeX <https://www.tug.org/mactex/>`__ on macOS,
``texlive-science``, ``texlive-fonts-extra``, and ``texlive-latex-extra`` on
Ubuntu/Debian, or a distribution such as `MiKTeX <https://miktex.org/download>`__
on Windows.

Create the uv environment
-------------------------

Install uv using its instructions linked above, then run:

.. code-block:: sh

   git clone https://github.com/3b1b/manim.git
   cd manim
   uv sync --locked
   uv run --locked manimgl --version
   uv run --locked manimgl example_scenes.py OpeningManimExample

The ``.python-version`` file selects Python 3.12 for development. uv downloads
that interpreter if needed, creates ``.venv``, and installs the checkout in
editable mode. The package's supported Python range remains 3.10 and newer.

Python dependencies are declared in ``pyproject.toml`` and locked in
``uv.lock``. Native system dependencies such as FFmpeg and LaTeX are managed
separately. No manual environment activation is needed when using ``uv run``.

Render and test
---------------

To render a video without opening a preview window:

.. code-block:: sh

   uv run --locked manimgl example_scenes.py OpeningManimExample -w -l

To run the unit tests:

.. code-block:: sh

   uv run --locked pytest

Use ``uv add`` to change runtime dependencies or ``uv add --dev`` for development
tools, and commit both ``pyproject.toml`` and ``uv.lock``. To deliberately update
locked versions, run ``uv lock --upgrade``. Other standard Python build frontends
can still install the package using its setuptools backend.
