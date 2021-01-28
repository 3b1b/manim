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

.. tip::

    See https://plugins.manim.community/ for the list of plugins available.

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
For enabling a plugin ``manim.cfg`` or command line parameters should be used.

.. important::

    The plugins should be module name of the plugin and not PyPi name.

Enabling plugins through ``manim.cfg`` 

.. code-block:: ini

    [CLI]
    plugins = manim_rubikscube

For specifing multiple plugins, command separated values must be used.

.. code-block:: ini

    [CLI]
    plugins = manim_rubikscube, manim_plugintemplate

Enabling Plugins through CLI

.. code-block:: bash

    manim basic.py --plugins=manim_plugintemplate

For multiple plugins

.. code-block:: bash

    manim basic.py --plugins=manim_rubikscube,manim_plugintemplate

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

Here ``name`` is the name of the module of the plugin.

Here ``object_reference`` can point to either a function in a module or a module
itself. For example,

.. code-block:: toml

    [tool.poetry.plugins."manim.plugins"]
    "manim_plugintemplate" = "manim_plugintemplate"

Here a module is used as ``object_reference``, and when this plugin is enabled,
Manim will look for ``__all__`` keyword defined in ``manim_plugintemplate`` and
everything as a global variable one by one.

If ``object_reference`` is a function, Manim calls the function and expects the
function returns a list of modules or functions that needs to defined globally and
it defined it.

For example,

.. code-block:: toml

    [tool.poetry.plugins."manim.plugins"]
    "manim_plugintemplate" = "manim_awesomeplugin.imports:setup_things"

Here, Manim will call the function ``setup_things`` defined in
``manim_awesomeplugin.imports`` and calls that. It returns a list of function or
modules which will be imported globally.
