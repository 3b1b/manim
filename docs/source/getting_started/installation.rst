Installation
============

Manim runs on Python 3.10 or higher.

System requirements are:

- `FFmpeg <https://ffmpeg.org/>`__
- `OpenGL <https://www.opengl.org/>`__ (included in python package ``PyOpenGL``)
- `LaTeX <https://www.latex-project.org>`__ (optional, if you want to use LaTeX)
- `Pango <https://pango.org>`__ (only for Linux)


Install FFmpeg
--------------

Follow the instructions for your platform, then run ``ffmpeg -version`` to check
that the installation succeeded.

Windows
^^^^^^^

.. code-block:: bat

   choco install ffmpeg

Linux
^^^^^

.. code-block:: sh

   sudo apt update
   sudo apt install ffmpeg

macOS
^^^^^

.. code-block:: sh

   brew install ffmpeg


Directly
--------

.. code-block:: sh

   # Install manimgl
   pip install manimgl

   # Try it out
   manimgl

If you want to hack on manimlib itself, clone this repository and in
that directory execute:

.. code-block:: sh

   # Install python requirements
   pip install -e .

   # Try it out
   manimgl example_scenes.py OpeningManimExample
   # or
   manim-render example_scenes.py OpeningManimExample

If you run the above command and no error message appears,
then you have successfully installed all the environments required by manim.

Directly (Windows)
------------------

1. `Install
   FFmpeg <https://www.wikihow.com/Install-FFmpeg-on-Windows>`__, and make sure that its path is in the PATH environment variable.
2. Install a LaTeX distribution.
   `TeXLive-full <http://tug.org/texlive/>`__ is recommended.
3. Install the remaining Python packages.

.. code-block:: sh

   git clone https://github.com/3b1b/manim.git
   cd manim
   pip install -e .
   manimgl example_scenes.py OpeningManimExample

For Anaconda
------------

-  Install FFmpeg and LaTeX as above.
-  Clone the repository and set up the environment using

.. code-block:: sh

   git clone https://github.com/3b1b/manim.git
   cd manim
   conda create -n manim python=3.10
   conda activate manim
   pip install -e .
