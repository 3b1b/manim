Windows
=======

Install System Libraries
------------------------

Make sure you have *Python 3* for Windows installed first:

https://www.python.org/downloads/windows/

Install ffmpeg:

https://ffmpeg.org/download.html#build-windows

Install sox:

http://sox.sourceforge.net/Main/HomePage

Install a latex distribution. On Windows MikTex is commonly used:

https://miktex.org/howto/install-miktex

Path configuration
------------------

To invoke commandline without supplying path to the binary
the PATH environment needs to be configured. Below are template examples, please change
the path according to your username and specific python version. Assuming all the
softwares are installed with no alteration to the installation paths::

  C:\Users\$username\AppData\local\Programs\Python\Python$version\
  C:\Users\$username\AppData\local\Programs\Python\Python$version\Scripts\
  C:\MikTex\miktex\bin\x64\
  C:\ffmpeg\bin\

The path entries should be separated by semicolon.

Installing python packages and manim
------------------------------------

Make sure you can start pip using ``pip`` in your commandline. Then do
``pip install pyreadline`` for the ``readline`` package.

Grab the pycairo wheel binary ``pycairo‑1.18.0‑cp37‑cp37m‑win32.whl`` from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo
and install it via ``python -m pip install C:\absolute\path\to\the\whl\file``

clone the manim repository if you have git ``git clone https://github.com/3b1b/manim`` or download the zip file from
the repository page with ``Clone or download`` button and unzip it.

Open the commandline within the manim directory with ``Shift + Right click`` on an empty space in the folder and select ``open command window here``

Install manim python dependencies with ``pip install -r requirement.txt``

Test the installation
---------------------

Type in ``python -m manim -h`` and if nothing went wrong during the installtion process you should see the help text.

Use ``python -m manim example_scenes.py SquareToCircle -pl`` to render the example scene and the file should play after rendering. The movie file should be
in ``media/videos/example_scenes/480p15``
