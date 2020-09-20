# Contributing

Thank you for contributing to Manim!  However you have decided to contribute or
interact with the community, please always be civil and respect other members
of the community.  Manim is a free open source software for mathematical
animations, and as such we welcome **everyone** who is interested in
mathematics, pedagogy, computer animations, open-source, software development,
and beyond.  Manim accepts contributions of many kinds, detailed below.

Many ways of contributing will involve writing, reading, testing, or
refactoring code.  As our repository is a Fork of [Manim by
3b1b](https://github.com/3b1b/manim), contributing in this way can be a bit
confusing.  Here is a short guide on how to do it.

1. Make a fork of this repository on Github.

   You will need an account with Github. This will allow you to make pull requests (PR)
   to the ManimCommunity repo later on.

2. Clone your fork.

   You can clone your Github fork by running:
   ```sh
     git clone <your-fork-url>
     cd manim
   ```
   GitHub will provide both a SSH (`git@github.com:<your-username>/manim.git`) and
   HTTPS (`https://github.com/<your-username>/manim.git`) URL for cloning the repo.
   You can use whichever one you are setup for.

   Note: Do not `git clone` the original ManimCommunity repository.  You must
    clone your own fork.  After this step, there are three different
    repositories to keep track of: the original ManimCommunity repo, your own
    fork of it, and your local repository.

3. Make `git` aware of the ManimCommunity repo.

   ```sh
   git remote add upstream https://github.com/ManimCommunity/manim.git
   git fetch upstream
   ```

	After these commands, your local repository can keep track of your fork
    (referred to as 'origin') as well as the main ManimCommunity repository
    (referred to as 'upstream').

4. Choose the branch for your changes.

   To work on the ManimCommunity master branch, you can change to it with:
   ```sh
   git checkout -b master upstream/master
   ```

   If you are starting a new branch, execute
   ```sh
   git checkout -b <new_branch-name>
   ```
5. Install manim.

   Install the required packages and manim itself:
   ```sh
   pip install -e .
   ```

   Manim has other requirements that you will need to install,
   explained in the [Installation](installation) instructions.


6. Write some awesome code!

   You're ready to make changes in your local repository, add them, and commit
   them.

7. Update docstrings and documentation.

   You should update the docstrings (the text in triple quotation marks) of any functions
   or classes you change and include them with any new functions you add.
   There is a [Wiki Entry for
   Documentation](https://github.com/ManimCommunity/manim/wiki//Documentation-guidelines-(WIP))
   with more information about how we prefer our code to be documented.

   You must check that the command `make doctest`, executed from the `docs/` folder
   terminates without problems after your changes.

8. Add/update tests.

   Depending on the changes you are making you will need to update or add new tests.
   If you have added a new feature or bug fix, it is strongly
   preferred that you include tests with your PR.
   Please check out the [Wiki Entry for Testing](https://github.com/ManimCommunity/manim/wiki/Testing)
   to learn how our tests work.

9. Check for merge conflicts.

   If you want your changes to be incorporated to the main ManimCommunity
   repository, you need to make sure that there are no merge conflicts between
   the current upstream/master and the changes you are trying to make.  To do this
   you will need to update your local repo with any changes that have
   been made to the ManimCommunity repo while you've been working with
   `git pull upstream master`.
   This will probably generate merge conflicts that you will need to resolve.

10. Run the `black` autoformatter.

    You can run black on a file or directory with `black <file_or_directory>` to
    format your code to the same standard as the rest of ManimCommunity.
    This will make changes to your code, so you will need to add/commit those changes
    if you commit before running it. Most python IDE/text editors have packages for
    running black after every save if you would like to keep formatting consistent while
    you work.

11. Run `pytest`.

    You can check that everything is still working properly after your modifications
    with `pytest`. Make sure that you run the tests locally and that they all pass
    before submitting a PR.  `pytest` should be run from the main `manim/`
    folder (Not the `manim/manim` subfolder).

12. Update your GitHub fork with local changes.

    To make your changes visible in your GitHub fork, instead of typing in `git
    push` as usual, you need to enter the command below.

    ```sh
    git push -u origin <branch-name>
    ```

    Doing so creates a new branch with the updated contents of your fork on
    GitHub (the 'origin').

13. Make a Pull Request on Github.

    To request the ManimCommunity dev team to incorporate the changes in your
    fork into the main repository, you can make a Pull Request to the Manim
    Community repo from your fork. Make sure to select `ManimCommunity/manim`
    instead of `3b1b/manim` as the `base repository` and your fork and branch as
    `head repository` - see the screenshot below.

    ![pull-requests-example-manim-community](./_static/pull-requests.PNG)

	  Please make sure you follow the template (this is the default
    text you are shown when first opening the 'New Pull Request' page)

14. Wait for feedback and make any requested changes.

    Thank you for contributing! Once your PR is submitted, it will require at least
    two approving code reviews from community developers. It will also be automatically
    tested. These tests must all pass for the PR to be merged.
    You will likely be asked to edit or modify your PR in one way or
    another during this process.  This is not an indictment of your work, but
    rather a strong signal that the dev community wants to merge your changes!

    Note: To open a PR, you do not need to have everything
    (documentation/tests) complete and ready to go.  However, the more complete
    your PR is, the easier it will be for community devs to review it, and the
    quicker it will be merged.  If you open a PR that is still under development
    and you want a quick overview or start some discussion about planned
    yet-to-be-implemented changes, please mark your PR as a draft.


## Other guidelines

1. When submitting a PR, please make special note of whether your proposed
   changes will result in breaking changes.

2. When submitting a PR, make sure that your proposed changes are as general as
   possible, and ready to be taken advantage of by all of manim's users.  In
   particular, leave out any machine-specific configurations, or any personal
   information it may contain.

3. If you are a maintainer, please label issues and PRs appropriately and
   frequently.

4. When opening a new issue, if there are old issues that are related, link
   them in your new issue (even if the old ones are closed).

5. When submitting a code review, it is highly recommended that you adhere to
   [these general guidelines](https://conventionalcomments.org/).  Similarly,
   when crafting commit messages, it is highly recommended that you adhere to
   [these guidelines](https://www.conventionalcommits.org/en/v1.0.0/).

6. If you find stale or inactive issues that seem to be irrelevant, please post
   a comment saying 'This issue should be closed', and a community developer
   will take a look.

7. Please do as much as possible to keep issues, PRs, and development in
   general as tidy as possible.
