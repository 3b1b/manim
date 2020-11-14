Installation
============

Manim has a few dependencies that need to be installed before it.  The
following pages have instructions that are specific to your system.  Once you
are done installing the dependencies, come back to this page to install manim
itself.

Installing dependencies
***********************

.. toctree::

   installation/win
   installation/mac
   installation/linux
   installation/troubleshooting
   installation/for_dev


.. _installing-manim:

Installing Manim
****************

Manim-Community runs on Python 3.6+. If you'd like to just use the library, you
can install it from PyPI via pip:

.. code-block:: bash

   pip install manimce

You can replace ``pip`` with ``pip3`` if you need to in your system.

Alternatively, you can work with Manim using our Docker image that can be
found at `Docker Hub <https://hub.docker.com/r/manimcommunity/manim>`_.

If you'd like to contribute to and/or help develop ``manim-community``, you can
clone this repository to your local device.  To do this, first make sure you
have ``git`` installed. Then, clone this repo by executing either

.. code-block:: bash

   git clone git@github.com:ManimCommunity/manim.git

or

.. code-block:: bash

   git clone https://github.com/ManimCommunity/manim.git

depending on whether you want to use HTTPS or SSH.  Finally, after having
cloned this repo, run the following:

.. code-block:: bash

   python3 -m pip install .

Please see :doc:`contributing` for more details about contributing to Manim.

.. warning::

   If you want to contribute to ``manim-community`` and have cloned the
   repository to your local device, please uninstall the pip-installed version
   of ``manim-community``, if you had installed it previously.
   This is to avoid any accidental usage of the pip-installed version when developing
   and testing on your local copy of the repository. This warning doesn't apply for
   users who use `poetry <https://python-poetry.org>`_.
