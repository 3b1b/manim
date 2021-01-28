.. _plugins:

=======
Plugins
=======

Plugins are features that extend Manim's core functionality. Since Manim is
extensible and not everything belongs in its core, we'll go over how to
install, use, and create your own plugins.

.. note:: 

    The standard naming convention for plugins is to prefix the plugin with
    ``manim-``. This makes them easy for users to find on package
    repositories such as PyPI.

.. WARNING::

    The plugin feature is new and under active development. Expect updates
    for the best practices on installing, using, and creating plugins; as
    well as new subcommands/flags for ``manim plugins``

Installing Plugins
******************
Plugins can be easily installed via the ``pip``
command:

.. code-block:: bash

    pip install manim-*

After installing a plugin, you may use the ``manim plugins`` command to list
your available plugins, see the following help output:

.. code-block:: bash

    manim plugins -h
    usage: manim plugins -h -l

    Utility command for managing plugins

    optional arguments:
    -h, --help    show this help message and exit
    -l, --list    Lists all available plugins

    Made with <3 by the ManimCommunity devs

You can list plugins as such:

.. code-block:: bash

    manim plugins -l
    Plugins:
    • manim_plugintemplate

Using Plugins in Projects
*************************
Plugins specified in ``plugins/__init__.py`` are imported automatically by
manim's ``__init__.py``. As such, writing:

.. code-block:: python

    from manim import *

in your projects will import any of the plugins imported in
``plugins/__init__.py``.

By default, ``plugins/__init__.py`` is not provided; although, there are
plans to support subcommands that would manage this file. It is especially
useful to create this file for projects that involve usage of the same
plugins. Alternatively, you may manually specify the plugins in your project
scripts.

.. code-block:: python

    import manim_cool_plugin
    # or
    from manim_cool_plugin import feature_x, feature_y, ...

Creating Plugins
****************
Plugins are intended to extend Manim's core functionality. If you aren't sure
whether a feature should be included in Manim's core, feel free to ask over
on the `Discord server <https://discord.gg/mMRrZQW>`_. Visit
`manim-plugintemplate <https://pypi.org/project/manim-plugintemplate/>`_
on PyPI.org which serves as an in-depth tutorial for creating plugins.

.. code-block:: bash

    pip install manim-plugintemplate

The only requirement of manim plugins is that they specify an entry point
with the group, ``"manim.plugins"``. This allows Manim to discover plugins
available in the user's environment. Everything regarding the plugin's
directory structure, build system, and naming are completely up to your
discretion as an author. The aforementioned template plugin, is only a model
using Poetry since this is the build system Manim uses. The plugin's `entry
point <https://packaging.python.org/specifications/entry-points/>`_ can be
specified in poetry as:

.. code-block:: toml

    [tool.poetry.plugins."manim.plugins"]
    "name" = "object_reference"