Mac
===

First, you need to install Homebrew.  Homebrew is a package manager similar to
``apt`` or ``pacman`` on linux that allows you to install packages easily.  If
it is not installed, please install it with this command (for Apple Silicon useres, please read the tip first):

.. code-block:: bash

   ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)" < /dev/null 2> /dev/null


.. tip:: 

    As of February 2020, the installation with ``brew`` has some issues with scipy and cairo packages in Apple Silicon mode. This can be solved by installing brew in the rosetta2 mode.
    Therefore, a rosetta terminal needs to be created (see here: https://5balloons.info/correct-way-to-install-and-use-homebrew-on-m1-macs/). In case you installed ``brew`` in the normal terminal before, you have to make sure you are using the correct brew when installing packages. On default, the rosetta brew is located at "/usr/local/bin/brew" and the Apple Silicon brew is located at "/opt/homebrew/bin/brew" (For more details on this, visit 
 https://stackoverflow.com/questions/64882584/how-to-run-the-homebrew-installer-under-rosetta-2-on-m1-macbook ). Next, install cairo, ffmpeg and mactex as described below with the rosetta brew. If not already there, install python 3.9 with ``brew install python@3.9``. Finally, make sure that you are using the right pip version to install manim, for example by running ``/usr/local/opt/python@3.9/bin/python3.9 -m pip install manim``.




To install cairo:

.. code-block:: bash

   brew install cairo

To install ffmpeg:

.. code-block:: bash

   brew install ffmpeg

To install LaTeX:

.. code-block:: bash

   brew install --cask mactex

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

   brew install --cask basictex

Ensure that the TeXLiveManager tool ``tlmgr`` works by running ``tlmgr
--version`` in the terminal (a reboot might be necessary). Now update ``tlmgr``

.. code-block:: bash
   
   sudo tlmgr update --self

Finally, run

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
