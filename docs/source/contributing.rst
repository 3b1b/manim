############
Contributing
############

Thank you for contributing to Manim!  However you have decided to contribute or
interact with the community, please always be civil and respect other members
of the community.  Manim is a free open source software for mathematical
animations, and as such we welcome **everyone** who is interested in
mathematics, pedagogy, computer animations, open-source, software development,
and beyond.  Manim accepts contributions of many kinds, detailed below.

Many ways of contributing will involve writing, reading, testing, or
refactoring code.  As our repository is a Fork of `Manim by
3b1b <https://github.com/3b1b/manim>`_, contributing in this way can be a bit
confusing.  Here is a short guide on how to do it.


Setup Manim and version control
===============================

#. *Make a fork of this repository on Github.*
   You will need an account with Github. This will allow you to make pull requests (PR)
   to the ManimCommunity repo later on.

#. *Clone your fork.*
   You can clone your Github fork by running:

   .. code-block:: shell

      git clone <your-fork-url>
      cd manim

   GitHub will provide both a SSH (``git@github.com:<your-username>/manim.git``) and
   HTTPS (``https://github.com/<your-username>/manim.git``) URL for cloning the repo.
   You can use whichever one you are setup for.

   .. WARNING::

      Do not ``git clone`` the original ManimCommunity repository.  You must
      clone your own fork.  After this step, there are three different
      repositories to keep track of: the original ManimCommunity repo, your own
      fork of it, and your local repository.

#. Make ``git`` aware of the ManimCommunity repo.

   .. code-block:: shell

      git remote add upstream https://github.com/ManimCommunity/manim.git
      git fetch upstream

   After these commands, your local repository can keep track of your fork
   (referred to as 'origin') as well as the main ManimCommunity repository
   (referred to as 'upstream').

#. *Install manim.*
   See the :doc:`installation instructions for developers <installation/for_dev>` for
   details.

You are now ready to work on manim!


Changing manim's source code
============================

#. *Choose the branch for your changes.*
   To work on the ManimCommunity master branch, you can change to it with:

   .. code-block:: shell

      git checkout -b master upstream/master

   If you are starting a new branch, execute

   .. code-block:: shell

      git checkout -b <new branch name>

#. *Write some awesome code!*
   You're ready to make changes in your local repository, add them, and commit
   them.

#. *Update docstrings and documentation.*
   Update the docstrings (the text in triple quotation marks) of any functions
   or classes you change and include them with any new functions you add.
   There is a `Wiki Entry for
   Documentation <https://github.com/ManimCommunity/manim/wiki/Documentation-guidelines-(WIP)>`_
   with more information about how we prefer our code to be documented. The content
   of the docstrings will be rendered in the :doc:`reference manual <reference>`.

   .. tip::

      Use the :mod:`manim directive for Sphinx <.manim_directive>` to add examples
      to the documentation!

      .. autosummary::
         :toctree: reference

         manim_directive

#. *Add new or update existing tests.*
   Depending on the changes you are making you will need to update or add new tests.
   It is strongly preferred that you include tests with your PR. Details of our testing
   system are explained in the
   `corresponding Wiki Entry <https://github.com/ManimCommunity/manim/wiki/Testing>`_.

As far as development on your local machine goes, these are the main steps you
should follow.

Polishing your changes and submitting them for review
=====================================================

As soon as you are ready to share your local changes with the community
so that they can be discussed, go through the following steps to open a
pull request.

.. NOTE::

   To open a pull request (PR), you do not need to have everything
   (code / documentation / tests) complete and ready to go.  However, the more complete
   your PR is, the easier it will be for community developers to review it, and the
   quicker it will be merged.  If you open a PR that is still under development
   and you want a quick overview or start some discussion about planned
   yet-to-be-implemented changes, please mark your PR as a draft.

#. *Update your GitHub fork with local changes.*
   To make your changes visible in your GitHub fork, instead of typing in
   ``git push`` as usual, you need to enter the command below.

   .. code-block:: shell

      git push -u origin <branch name>

   Doing so creates a new branch with the updated contents of your fork on
   GitHub (the 'origin').

#. *Make a Pull Request on Github.*
   In order to make the ManimCommunity development team aware of your changes,
   you can make a Pull Request to the Manim Community repository from your fork.

   .. WARNING::

      Make sure to select ``ManimCommunity/manim`` instead of ``3b1b/manim``
      as the base repository!

   Choose the branch with your changes from your fork as the head
   repository - see the screenshot below.

   .. image:: /_static/pull-requests.PNG
      :align: center

   Please make sure you follow the template (this is the default
   text you are shown when first opening the 'New Pull Request' page).


Your changes are eligible to be merged, if

#. there are no merge conflicts,
#. and if the tests in our pipeline passes.

You can check for merge conflicts between the current upstream/master and
your branch by executing ``git pull upstream master`` locally. If this
generates any merge conflicts, you need to resolve them and push an
updated version of the branch to your fork of the repository.

Our pipeline consists of a series of different tests that ensure
that manim still works as intended and that the code you added
sticks to our coding conventions.

- *Code style*: We use the code style imposed
  by `Black <https://black.readthedocs.io/en/stable/>`_. The pipeline
  makes sure that the (Python) files changed in your pull request
  also adhere to this code style. If this step of the pipeline fails,
  fix your code style by running ``black <file or directory>`` to
  automatically format your files.

- *Tests*: The pipeline runs manim's test suite on different operating systems
  (the latest versions of Ubuntu, MacOS, and Windows) for different versions of Python.
  The test suite consists of two different kinds of tests: integration tests
  and doctests. You can run them locally by executing ``poetry run pytest``
  and ``poetry run pytest --doctest-modules manim``, respectively, from the
  root directory of your cloned fork.

- *Documentation*: We also build a version of the documentation corresponding
  to your pull request. Make sure not to introduce any Sphinx errors, and have
  a look at the built HTML files to see whether the formatting of the documentation
  you added looks like you intended. You can build the documentation locally
  by running ``make html`` from the ``docs`` directory.

Finally, if the pipeline passes and you are satisfied with your changes: wait for
feedback and iterate over requested changes. You will likely be asked to edit or
modify your PR in one way or another during this process.
This is not an indictment of your work, but rather a strong signal that the
community wants to merge your changes! Overall, in order for your PR to be merged
at least two approving code reviews from core community developers are required.


Further useful guidelines
=========================

#. When submitting a PR, please make special note of whether your proposed
   changes will result in breaking changes.

#. When submitting a PR, make sure that your proposed changes are as general as
   possible, and ready to be taken advantage of by all of manim's users.  In
   particular, leave out any machine-specific configurations, or any personal
   information it may contain.

#. If you are a maintainer, please label issues and PRs appropriately and
   frequently.

#. When opening a new issue, if there are old issues that are related, link
   them in your new issue (even if the old ones are closed).

#. When submitting a code review, it is highly recommended that you adhere to
   `these general guidelines <https://conventionalcomments.org/>`_.  Similarly,
   when crafting commit messages, it is highly recommended that you adhere to
   `these guidelines <https://www.conventionalcommits.org/en/v1.0.0/>`_.

#. If you find stale or inactive issues that seem to be irrelevant, please post
   a comment saying 'This issue should be closed', and a community developer
   will take a look.

#. Please do as much as possible to keep issues, PRs, and development in
   general as tidy as possible.


**Thank you for contributing!**