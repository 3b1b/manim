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

Cairo Installation
------------------

Running the command below installs ``pycairo``. This needs to be an
elevated command prompt like Powershell.

.. code:: powershell

    (Invoke-WebRequest -Uri https://raw.githubusercontent.com/ManimCommunity/manim/master/scripts/pycairoinstall.py -UseBasicParsing).Content | py -3

If the above one Fails, here is the alternative for it below. 1. Visit
the `Download
Page <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo>`__ 2. Select
the download that corresponds to your PC's architechture and Python
Version

::

    cp38 corresponds to Python 3.8, cp37 corresponds to Python 3.7, etc 
    win_amd64 corresponds to 64-bit machines, win32 corresponds to 32-bit machines

Open up your command prompt by hitting the Win key and typing ``cmd``

Enter the directory where you install cairo by typing ``cd C:\path\to\cairo`` with the path being where you downloaded the ``.whl`` file. 
Alternatively, ``shift+Right Click`` will open an option for opening in powershell window.

Finally, run ``pip3 install (cairo-file).whl``, where the file the appropriate name of the ``.whl`` file.

Grab the pycairo wheel binary ``pycairo‑1.18.0‑cp37‑cp37m‑win32.whl`` from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo
and install it via ``python -m pip install C:\absolute\path\to\the\whl\file``

clone the manim repository if you have git ``git clone https://github.com/3b1b/manim`` or download the zip file from
the repository page with ``Clone or download`` button and unzip it.

Open the commandline within the manim directory with ``Shift + Right click`` on an empty space in the folder and select ``open command window here``

Install manim python dependencies with ``pip install -r requirements.txt``

Test the installation
---------------------

Type in ``python -m manim -h`` and if nothing went wrong during the installation process you should see the help text.

Use ``python -m manim example_scenes.py SquareToCircle -pl`` to render the example scene and the file should play after rendering. The movie file should be
in ``media/videos/example_scenes/480p15``
