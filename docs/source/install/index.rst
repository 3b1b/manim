Installation
============

Manim runs on Python 3.8.

System requirements are `FFmpeg <https://ffmpeg.org/>`__,
`OpenGL <https://www.opengl.org//>`__ and
`latex <https://www.latex-project.org>`__ (optional, if you want to use
LaTeX).

Directly
--------

If you want to hack on manimlib itself, clone this repository and in
that directory execute:

.. code:: sh

   # Install python requirements
   pip install -r requirements.txt

   # Try it out
   python -m manim example_scenes.py OpeningManimExample

Directly (Windows)
------------------

1. `Install
   FFmpeg <https://www.wikihow.com/Install-FFmpeg-on-Windows>`__.
2. Install a LaTeX distribution.
   `MiKTeX <https://miktex.org/download>`__ is recommended.
3. Install the remaining Python packages.

.. code:: sh  

   git clone https://github.com/3b1b/manim.git
   cd manim  
   pip install -r requirements.txt  
   python manim.py example_scenes.py OpeningManimExample

For Anaconda
----------------

-  Install latex as above.
-  Create a conda environment using
   ``conda env create -f environment.yml``

Using virtualenv and virtualenvwrapper
----------------------------------------------

After installing virtualenv and virtualenvwrapper

.. code:: sh

   git clone https://github.com/3b1b/manim.git
   mkvirtualenv -a manim -r requirements.txt manim
   python -m manim example_scenes.py OpeningManimExample