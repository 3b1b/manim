Windows
=======

First, you need to install Chocolatey, which is a package manager for Windows
systems.  Please refer to `this link <https://chocolatey.org/install>`_ for
instructions.

Installing using Chocolatey
***************************

You can install manim very easily using chocolatey, by typing the following command.

.. code-block:: powershell

      choco install manimce


And then you can skip all the other steps and move to installing :ref:`latex-installation`.
Please see :doc:`troubleshooting` section for details about OSError.

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
                  It is possible to have installed ``x86`` python installed on ``x64`` PC.

2. Extract the zip file using File Explorer or 7z to the loaction you want to install.

   .. code-block:: bash

      7z x pango-windows-binaires-x64.zip -oC:\Pango

3. Finally, add it `PATH variable
   <https://www.computerhope.com/issues/ch000549.htm>`_.


FFmpeg installation
*******************

1. To install ``ffmpeg`` and add it to your PATH, install `Chocolatey
   <https://chocolatey.org/>`_ and run ``choco install ffmpeg``.

2. You can check if you did it right by running ``refreshenv`` to update your
   environment variable and running ``ffmpeg``.


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
