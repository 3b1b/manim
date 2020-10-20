Linux
=====

The following instructions are given for different linux distributions that use
different package managers.  After executing the instructions corresponding to
your distribution, go to `Certifying a clean install`_ to check whether the
dependencies are installed correctly.  All distributions will follow the same
instructions in `Certifying a clean install`_.

The two necessary dependencies are cairo and ffmpeg.  LaTeX is strongly
recommended, as it is necessary to have access to the ``Tex`` and ``MathTex`` classes.

Ubuntu/Mint/Debian
******************

Before installing anything, make sure that your system is up to date.

.. code-block:: bash

   sudo apt update
   sudo apt upgrade

To install cairo:

.. code-block:: bash

   sudo apt install libcairo2-dev

To install ffmpeg:

.. code-block:: bash

   sudo apt install ffmpeg

To install LaTeX:

.. code-block:: bash

   sudo apt install texlive texlive-latex-extra texlive-fonts-extra \
   texlive-latex-recommended texlive-science texlive-fonts-extra tipa

If you don't have python3-pip installed, install it:

.. code-block:: bash
   
   sudo apt install python3-pip
  
.. note:: These instructions are also valid for other Debian-based
          distributions or distributions that use the ``apt`` package manager.


Fedora/CentOS/RHEL
******************

To install cairo:

.. code-block:: bash

  sudo dnf install cairo-devel

To install ffmpeg, you have to add RPMfusion repository (If it's not already added). Please follow the instructions for your specific distribution in the following URL:

https://rpmfusion.org/Configuration/

Install ffmpeg from RPMfusion repository:

.. code-block:: bash

   sudo dnf install ffmpeg

Install python development headers in order to successfully build pycairo wheel:

.. code-block:: bash

   sudo dnf install python3-devel

To install LaTeX:

.. code-block:: bash

   sudo dnf install texlive-scheme-medium


Arch/Manjaro
************

Before installing anything, make sure that your system is up to date.

.. code-block:: bash

   sudo pacman -Syu

To install cairo:

.. code-block:: bash

   sudo pacman -S cairo


To install ffmpeg:

.. code-block:: bash

   sudo pacman -S ffmpeg

To install LaTeX:

.. code-block:: bash

   sudo pacman -S texlive-most

If you don't have python-pip installed, install it:

.. code-block:: bash
   
   sudo pacman -S python-pip


.. note:: These instructions are also valid for other Arch-based
          distributions or distributions that use the ``pacman`` package
          manager.


Certifying a clean install
**************************

To check that all dependencies have been installed properly, you can execute
the commands ``ffmpeg -version`` and ``latex``.  (If LaTeX is installed
properly, you will be taken to a command-line program that captures your
cursor. Press CTRL+C to exit.)

.. note:: Note the LaTeX installation may take up a lot of space.  The manim
          community developers are currently working on providing a simpler,
          lighter LaTeX package for you to install.

After making sure you have a clean install, you can go back to
:ref:`installing-manim`.
