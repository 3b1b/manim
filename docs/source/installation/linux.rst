Linux
=====

Ubuntu
------

Install system libraries::

    # apt install sox ffmpeg libcairo2 libcairo2-dev

Install Latex distribution::

    # apt install texlive-full

Install manim via pypi::

    # pip3 install manimlib

OR Install manim via the git repository with venv::

    $ git clone https://github.com/3b1b/manim
    $ cd manim
    $ python3 -m venv ./
    $ source bin/activate
    $ pip3 install -r requirement.txt

To use manim in virtual environment you need to activate the environment with
the ``activate`` binary by doing ``source bin/activate``, to exit use the ``deactivate`` command.

.. note:: The git repository is updated first before the one on pypi. The git repository also
          includes project files used to produce 3b1b videos. Some of the old projects might not
          work as due to api changes.


.. note:: The required latex packages are dictated by
          ``manimlib/tex_template.tex`` which ``texlive-full`` will satisfy. The download size
          can be quite large. If you wish to install only the packages required to use
          manim, substitude ``texlive-full`` with::

            texlive texlive-latex-extra texlive-fonts-extra
            texlive-latex-recommended texlive-science texlive-fonts-extra tipa
