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

   .. code-block:: powershell

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

LaTeX Installation
******************
You can install latex by either of the two methods below. MiKTex is very large (2 GB) while TinyTex is small  (500Mb).

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

Using TinyTex
-------------

1. Save the batch file `install-windows.bat
<https://yihui.org/gh/tinytex/tools/install-windows.bat>`_. (open this link and press Ctrl + S).

.. note:: Please note that it requires PowerShell (at least version 3.0).

2. Double click the file and it opens a command prompt. There might be an error 
dialog or two about ``luatex.dll`` during the installation `(like this)
<https://db.yihui.org/images/install-tl-win-lua.png>`_, but that does not seem to hurt, and click “OK”. The installation directory is ``%APPDATA%/TinyTeX``, where APPDATA is an environment variable that typically points to the path ``C:\Users\Your Name\AppData\Roaming``

3.Finally, close the terminal and open a new one and type the below commands.

.. code-block:: powershell

      tlmgr install standalone preview doublestroke ms setspace rsfs relsize ragged2e fundus-calligra microtype wasysym physics dvisvgm jknapltx wasy cm-super babel-english

4. Finally, check whether it installed properly by running an example scene.

Certifying a clean install
**************************

After making sure you have a clean install following the instructions for each
dependency above, you can go back to :ref:`installing-manim`.
