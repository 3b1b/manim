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
NOTE : Make sure that the python version you are using is python3.7 because manim works only for that version . If not, you will get errors when running the old_projects.If the python3 version is not 3.7 then upgrade your version usimg the following steps:
     
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install build-essential libpq-dev libssl-dev openssl libffi-dev zlib1g-dev
sudo apt-get install python3-pip python3.7-dev
sudo apt-get install python3.7

Then use python3.7 command for 3.7 version and python3 for pre installed version.


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
