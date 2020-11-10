Manim Installation For Developers
=================================

	This documentation is for developers who want to contribute to ``ManimCommunity/manim``.

Installing Poetry
*****************

Poetry can be easily installed in any OS by just running the below command.

If your system has the ``curl`` program installed, which is usually true in Linux and Mac,

.. code-block:: bash
	
	  curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python


If you are a Windows developer and want to use PowerShell, you can use the below command.

.. code-block:: bash
	
	  (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python

.. note:: Poetry can be installed by other ways also, such as with ``pip``. See `<https://python-poetry.org/docs/#alternative-installation-methods-not-recommended>`_. If you are using MacOS with the Homebrew package manager, you can also install poetry with ``brew install poetry``.

It will add it to ``PATH`` variable automatically. In order to make sure you have poetry installed correctly, try running:

.. code-block:: bash

	poetry --version


.. note:: You may need to restart your shell in order for the changes to take effect.

See the `docs on installation python poetry for more information
<https://python-poetry.org/docs/>`_.

Installing System Dependencies
******************************

Please follow the instructions under :ref:`installing-manim` to install all dependencies. Then come back to this page to continue with the installation.

.. important:: Windows Users can skip the steps to install Pycairo.


Additionally, ``git`` has to be installed. For instructions see `Documentation
<https://git-scm.com/>`_.

.. _install-manim-poetry:

Installing Manim using Poetry
*****************************

1.  First, clone the Manim repo locally using git.

    .. code-block:: bash
		
		git clone https://github.com/ManimCommunity/manim.git

    or

    .. code-block:: bash
		
		git clone git@github.com:ManimCommunity/manim.git

2.  Open a Terminal/Powershell/Command Prompt and cd into the cloned directory.

    .. code-block:: bash
		
		cd path/to/manim
    

    .. note:: This path should contain a file called ``pyproject.toml`` if it doesn't contain it, you would need to go a level up.

3.  Use the below command to install python dependencies. This will use the default python version installed.

    .. code-block:: bash
	
         poetry install


    .. note:: Poetry will create a virtual environment rooted at the current directory.
    
    You can select the desired python version using 

    .. code-block:: bash
	
         poetry env use <python version you need>

    For example you can use for python 3.7.

    .. code-block:: bash
	
         poetry env use 3.7
     
    For more information about this you can visit the `docs
    <https://python-poetry.org/docs/managing-environments/>`_.

4.  Now you can activate the virtual environment ``Poetry`` has created by using the command below.

    .. code-block:: bash

       poetry shell
    
    Or if you want to run a single command use

    .. code-block:: bash

       poetry run manim -h

Now you are free to start developing on the Manim Repository.

Running the Tests Using Poetry
******************************

Once you are done with :ref:`install-manim-poetry`, you can run manim's test suite by activating a shell using ``poetry shell`` command and then running the command ``pytest`` to run the tests. 

.. code-block:: bash

   poetry shell
   pytest

.. important:: You should always run the test suite before making a PR. For other contributing guidelines, see `the guide for contributions to manim <../contributing.html>`_.


Code Formatting and Linting Using Poetry
****************************************

Once you are done with :ref:`install-manim-poetry`, you can run the code formatter ``black`` by activating a shell using ``poetry shell`` and then running the command ``black manim``. Or alternatively just use the command ``poetry run black manim``.

You can see linting information for a given file or directory by either running ``poetry shell`` followed by ``pylint <path>`` or with ``poetry run pylint <path>``. Note that unlike ``black``, ``pylint`` cannot make code changes automatically.

.. code-block:: bash

   poetry shell
   black manim
   pylint manim

.. note:: Here, the word ``manim``, as used in the commands ``black manim`` or ``poetry run black manim``, refers to the folder which ``black`` is to format. You can also reformat the files containing the test suite by running the command ``black tests``.

For example, if you have written some new example and want to format it and see lint information use the commands below.

.. code-block:: bash

    poetry run black example_scenes

