MCP server
==========

ManimGL ships a native `Model Context Protocol
<https://modelcontextprotocol.io/>`_ (MCP) server, ``manimlib.mcp``, that
gives LLM coding assistants ground truth about *this* library instead of
letting them guess. Almost all Manim material an LLM has been trained on
describes `ManimCommunity <https://github.com/ManimCommunity/manim>`_,
which shares a name and a common ancestor with ManimGL but has diverged:
``Create``, ``MathTex``, ``config``, ``MovingCameraScene``, and the
``-ql``/``-qh`` CLI flags do not exist here. This server exposes the
*installed* version's real classes, signatures, and constants by
reflection, so there is nothing to hallucinate.

Installing
----------

The server is an optional extra -- it depends on the
`mcp <https://pypi.org/project/mcp/>`_ package (``mcp>=2.0``), which pulls
in ``pydantic``, ``starlette``, and ``uvicorn`` that ManimGL itself has no
use for, so it is never installed by default.

.. code-block:: sh

    pip install -e ".[mcp]"

Running it
----------

.. code-block:: sh

    python -m manimlib.mcp

or, equivalently, the console script installed alongside ``manimgl``:

.. code-block:: sh

    manimgl-mcp

**Both must be invoked with no additional command-line arguments.**
Importing ``manimlib`` (which happens automatically, before either entry
point's own code runs, since Python always imports a package before its
submodules) parses the process's command-line arguments through
ManimGL's own CLI parser. Any extra argument -- even one meant for the
MCP server itself -- gets fed to that parser and raises an error before
the server can start. Configure the server with the environment
variables below instead of flags.

A typical MCP client configuration:

.. code-block:: json

    {
      "mcpServers": {
        "manimgl": {
          "command": "python",
          "args": ["-m", "manimlib.mcp"]
        }
      }
    }

Environment variables
----------------------

- ``MANIMGL_MCP_ENABLE_RENDER``
    Set to ``1`` to enable the ``render_scene`` tool. It is **disabled by
    default**: rendering executes submitted Python code in a subprocess
    with the server's own filesystem and network privileges. Only enable
    it for a trusted, local client.

- ``MANIMGL_MCP_MAX_CONCURRENT``
    Maximum number of renders to run at once. Defaults to ``1`` -- each
    render creates its own GPU adapter and device, so unbounded
    concurrency can exhaust GPU memory.

Tools
-----

- ``list_manim_classes(kind, query)``
    List ManimGL classes (``kind`` is ``"mobject"``, ``"animation"``,
    ``"scene"``, or ``"all"``), optionally filtered by a name substring.

- ``get_class_signature(name)``
    A class's real constructor signature, flattened across its base
    classes, with its docstring and any inline parameter comments found
    in the source. Most ManimGL constructors take almost all of their
    real configuration through keyword arguments forwarded up their base
    classes, so this is normally far more useful than the class's own
    local ``__init__``.

- ``list_scene_methods(name)``
    Public methods available on a class (for example, the verbs on
    ``Scene`` -- ``play``, ``add``, ``wait``, and so on -- or on
    ``Mobject``), with signatures and docstrings.

- ``get_manim_constants(category)``
    The real, currently configured values of ManimGL's constants
    (``category`` is ``"colors"``, ``"vectors"``, ``"angles"``,
    ``"sizes"``, or ``"all"``) -- these reflect your own
    ``custom_config.yml``, not a static list.

- ``search_examples(query, limit)``
    Search a small corpus of known-good example scenes (a curated,
    headless-safe set, plus this repository's own example scenes when
    running from a checkout) by name and source substring.

- ``validate_scene(code)``
    Statically check submitted scene code for syntax errors and unknown
    names -- in particular, ManimCommunity-only names it recognizes by
    name (``Create``, ``MathTex``, ...) and suggests a ManimGL
    replacement for. Instant and needs no GPU.

- ``check_environment()``
    Report whether rendering will actually work: the installed manimgl
    version, whether ``ffmpeg``/``latex``/``dvisvgm`` are on ``PATH``,
    and the currently configured font, resolution, and output directory.

- ``probe_gpu()``
    Check whether a working graphics adapter can be created, without
    risking the server itself (the probe runs in a subprocess, since a
    driver fault during device creation aborts the whole process).

- ``render_scene(code, scene_name, output, timeout)``
    Render submitted scene code in a sandboxed subprocess and return a
    PNG of the last frame (default, returned inline for a vision-capable
    client to inspect) or an MP4 of the full animation (``output="video"``,
    returned as a file path). Disabled unless
    ``MANIMGL_MCP_ENABLE_RENDER=1`` is set -- see above.

Security
--------

``render_scene`` executes arbitrary submitted Python. It runs in a
subprocess with no stdin, a fresh temporary working directory, and a
timeout, but otherwise with the server's own filesystem and network
access -- this is process isolation for reliability (a crashed or hung
render must not take the server down with it), not a security sandbox.
Do not enable ``MANIMGL_MCP_ENABLE_RENDER`` for a server any untrusted
client can reach.
