Installation
============

ManimGL runs on **Python 3.7 or higher**.

System Requirements
-------------------
- `FFmpeg <https://ffmpeg.org/>`__  
- `OpenGL <https://www.opengl.org/>`__ (included in Python package ``PyOpenGL``)  
- `LaTeX <https://www.latex-project.org/>`__ (optional, only if you want to render LaTeX)  
- `Pango <https://pango.org>`__ (required only for Linux)  

---

Install FFmpeg
--------------------------

Windows
----------------
.. code-block:: cmd

   choco install ffmpeg

.. admonition:: 💡 Note
    :class: tip

    Make sure FFmpeg is added to your PATH environment variable.

Linux
--------
.. code-block:: sh

   sudo apt update
   sudo apt install ffmpeg
   ffmpeg -version

MacOS
------
- Download the FFmpeg ZIP archive from:  
  `FFmpeg Builds <https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z>`__  

.. admonition:: 💡 Note
    :class: tip

    If the link is not working, you can download FFmpeg from the official website: `https://ffmpeg.org/download.html`__

---

Direct Installation via pip
---------------------------

.. code-block:: sh

   # Install ManimGL
   pip install manimgl

   # Test the installation
   manimgl

.. admonition:: 💡 Note
    :class: tip

    If no error appears, the installation was successful.

---

Clone & Editable Installation
------------------------------

If you want to hack on ManimGL itself:

.. code-block:: sh

   # Clone the repository
   git clone https://github.com/3b1b/manim.git
   cd manim

   # Install in editable mode
   pip install -e .

   # Test an example scene
   manimgl example_scenes.py OpeningManimExample
   # or
   manim-render example_scenes.py OpeningManimExample

---

Linux (Debian-based distributions)
-----------------------------------
These instructions apply to Debian-based systems such as **Ubuntu, Linux Mint, Pop!_OS**, etc.

1. Install system dependencies:

    .. code-block:: sh

        sudo apt update
        sudo apt install ffmpeg texlive-latex-base texlive-latex-recommended texlive-fonts-recommended
        sudo apt install texlive-science texlive-fonts-extra texlive-latex-extra
        sudo apt install libpango1.0-dev pkg-config python3-dev

    .. admonition:: 💡 Note
        :class: tip

        These packages provide a lightweight LaTeX setup (~1.5GB).  
        If you want the full LaTeX distribution (~6GB), you can install:

        .. code-block:: sh

            sudo apt install texlive-full

---

Directly (Windows)
------------------
1. Install `FFmpeg <https://www.wikihow.com/Install-FFmpeg-on-Windows>`__ and ensure its path is in the PATH environment variable.  
2. Install a LaTeX distribution: `TeXLive-full <http://tug.org/texlive/>`__ is recommended.  
3. Clone and install ManimGL:

    .. code-block:: sh  

       git clone https://github.com/3b1b/manim.git
       cd manim  
       pip install -e . 
       manimgl example_scenes.py OpeningManimExample

---

For Anaconda Users
-------------------
- **Install FFmpeg and LaTeX** as described above.  
- **Create a conda environment and install ManimGL:**

  .. code-block:: sh

     # Clone the repository
     git clone https://github.com/3b1b/manim.git
     cd manim

     # Create a conda environment (choose your Python version)
     conda create -n manim python=<your_python_version>  # e.g., python=3.8 or python=3.12
     conda activate manim

     # Install Manim in editable mode (choose version if needed)
     pip install -e .[dev]

.. admonition:: 💡 Note
    :class: tip

    Replace `<your_python_version>` with the Python version you want (>=3.7).  
    The `[dev]` option installs optional dependencies useful for development and examples.

---

Quick Test
----------
.. code-block:: sh

   manimgl example_scenes.py OpeningManimExample

.. admonition:: 💡 Note
    :class: tip

    If a window pops up playing a scene, your installation is ready.  
    If you encounter errors, check FFmpeg, Python version, or LaTeX installation.