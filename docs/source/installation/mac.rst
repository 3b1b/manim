Mac
===

First, you need to install Homebrew.  Homebrew is a package manager similar to
``apt`` or ``pacman`` on linux that allows you to install packages easily.  If
it is not installed, please install it with this command:

.. code-block:: bash

   ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null

To install cairo:

.. code-block:: bash

   brew install cairo

To install Pango and it dependencies:

.. code-block:: bash

   brew install pkg-config
   brew install libffi
   brew install pango
   brew install glib


To install ffmpeg:

.. code-block:: bash

   brew install ffmpeg

To install LaTeX:

.. code-block:: bash

   brew cask install mactex

.. warning:: Note that MacTeX will require at least 4.5GB of hard disk space.
	     This is due to the fact that it installs every LaTeX addon package
	     offered by `CTAN <https://ctan.org/>`_.  Only a few of these
	     packages are required by Manim.  If you would like a smaller LaTeX
	     install which only contains the packages needed by Manim alone,
	     consider installing BasicTeX with the instructions below. This
	     will require only about 1.5GB of space.  If you have installed
	     MacTeX and are comfortable with it, do not install BasicTeX.

(Alternative) To install BasicTeX:

.. code-block:: bash

   brew cask install basictex

Ensure that the TeXLiveManager tool ``tlmgr`` works, by running ``tlmgr
--version`` in the terminal.  Now run

.. code-block:: bash

   sudo tlmgr install standalone preview doublestroke relsize fundus-calligra \
   wasysym physics dvisvgm.x86_64-darwin dvisvgm rsfs wasy cm-super


Certifying a clean install
**************************

To check that all dependencies have been installed properly, you can execute
the commands ``ffmpeg -version`` and ``latex`` (regardless of whether you
installed MacTeX or BasicTeX).  If LaTeX is installed properly, you will be
taken to a command-line program that captures your cursor. Press CTRL+C to
exit.

After making sure you have a clean install, you can go back to
:ref:`installing-manim`.
