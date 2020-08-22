Windows
=======

First, you need to install Chocolatey, which is a package manager for Windows
systems.  Please refer to `this link <https://chocolatey.org/install>`_ for
instructions.


Cairo installation
******************

1. Visit the `Download Page
   <https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo>`_.

2. Select the download that corresponds to your PC's architechture and Python
   Version

   .. image:: ../_static/installation/windows_cairo.png
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

2. Add SoX to your PATH: Find the directory where SoX is installed.  This is
   probably ``C:\Program Files (x86)\sox-(version_number)`` or ``C:\Program
   Files\sox-(version_number)``.  Open a command prompt window by hitting the
   Win key and typing ``cmd``. Run this command to update your PATH:

   .. code-block::

      setx PATH %PATH%;C:\Program Files (x86)\sox-(version_number)

   Check whether you did it right by running ``refreshenv`` to update your environment
   variable and running ``sox``.


LaTeX Installation
******************

1. Download the MiKTex installer from `this page
   <https://miktex.org/download>`_ and execute it.

   .. image:: ../_static/installation/windows_miktex.png
       :align: center
       :width: 500px
       :alt: windows latex download page

2. You can check if you did it right by running ``refreshenv`` to update your
   environment variable and running ``latex``.


Certifying a clean install
**************************

After making sure you have a clean install following the instructions for each
dependency above, you can go back to :ref:`installing-manim`.
