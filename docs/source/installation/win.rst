Windows
=======

First, you need to install Chocolatey, which is a package manager for Windows
systems.  Please refer to `this link <https://chocolatey.org/install>`_ for
instructions.

Installing using Chocolatey
***************************

You can install manim very easily using chocolatey, by typing the following command.


.. code-block:: powershell

      choco install manim


And then you can skip all the other steps and move to installing :ref:`latex-installation`.

Pango Installation
******************
These steps would get you `libpango-1.0-0.dll` to your ``PATH`` along 
with other dependencies. You may probably have them before itself if 
you have installed `GTK <https://www.gtk.org/>`_ or any ``GTK`` 
based app like emacs. If you have it you can just add it to your 
path and skip these steps.

1. Go to `Release Page
   <https://github.com/ManimCommunity/manim-windows/releases/latest>`_ 
   and download the one according to your PC architechture.

	.. important:: Please download the ``zip`` file for architechture of python installed.
                  It is possible to have installed ``x86`` python on ``x64`` PC.

2. Extract the zip file using File Explorer or 7z to the loaction you want to install.

   .. code-block:: powershell
      
      7z x pango-windows-binaires-x64.zip -oC:\Pango

3. Finally, add it `PATH variable
   <https://www.computerhope.com/issues/ch000549.htm>`_.


Cairo installation
******************

1. Visit the `Download Page
   <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo>`_.

2. Select the download that corresponds to your PC's architechture and Python
   Version

   .. image:: ../_static/windows_cairo.png
       :align: center
       :width: 400px
       :alt: windows cairo download page

   .. note:: ``cp38`` corresponds to Python 3.8, ``cp37`` corresponds to Python
             3.7, etc. ``win_amd64`` corresponds to 64-bit machines, ``win32``
             corresponds to 32-bit machines.

3. Open up your command prompt by hitting the Win key and typing ``cmd``.

4. Enter the directory where you want to install cairo by typing ``cd
   C:\path\to\cairo`` with the path being where you downloaded the ``.whl``
   file in step 2.

5. Finally, run ``pip(pyversion) install (cairo-file).whl``, where
   ``pyversion`` is the python version you are using.  For example, if you are
   using python3.7, you should run ``pip3.7 install (cairo-file).whl``.


6. Alternatively, running the command below installs pycairo.  This needs to be
   run in an elevated command prompt like Powershell.

   .. code-block:: bash

      (Invoke-WebRequest -Uri https://raw.githubusercontent.com/ManimCommunity/manim/master/scripts/pycairoinstall.py -UseBasicParsing).Content | py -3


FFmpeg installation
*******************

1. To install ``ffmpeg`` and add it to your PATH, install `Chocolatey
   <https://chocolatey.org/>`_ and run ``choco install ffmpeg``.

2. You can check if you did it right by running ``refreshenv`` to update your
   environment variable and running ``ffmpeg``.


Sox installation (optional)
***************************

1. To install Sox, execute ``choco install sox.portable``.

2. You can check if you did it right by running ``refreshenv`` to update your
   environment variable and running ``sox``.

.. _latex-installation:

LaTeX Installation
******************
You can install latex by either of the two methods below. MiKTex is very large (2 GB) while ManimLaTeX is small  (500Mb).

Using a custom distribution for Manim based on Texlive
------------------------------------------------------

This is the smallest latex distribution just enough to run Manim. Extra latex packages for fonts can be
installed using ``tlmgr``. See https://www.tug.org/texlive/tlmgr.html for more information.

1. Install chocolatey if you haven't already.

2. Run the following command

   .. code-block:: powershell
      
      choco install manim-latex

3. Finally, check whether it installed properly by running an example scene.

Using MiKTex
------------
1. Download the MiKTex installer from `this page
   <https://miktex.org/download>`_ and execute it.

   .. image:: ../_static/windows_miktex.png
       :align: center
       :width: 500px
       :alt: windows latex download page

2. You can check if you did it right by running ``refreshenv`` to update your
   environment variable and running ``latex``.

Certifying a clean install
**************************

After making sure you have a clean install following the instructions for each
dependency above, you can go back to :ref:`installing-manim`.
