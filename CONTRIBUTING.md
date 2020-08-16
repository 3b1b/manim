# Contributing

1. If code changes are being made, please include documentation **following the guidelines in the Wiki** (typings are also welcome, but we can probably do them for you, given the documentation).
2. (For the maintainers of this repo) Label PRs appropriately.
3. Link relevant issues.
4. Ensure compatibility with the latest changes in the repo.
5. After you've made your changes, please test them out thoroughly. If the repository has any example code or code exclusively used for testing, please test your changes against those. If you have added new features, consider writing and contributing to a test for that feature to ensure it works properly.

## General instructions

As this is a Fork of [Manim by 3b1b](https://github.com/3b1b/manim), contributing can be a bit confusing. Because of that, here is a small guide on it. 

1. First, make a fork of this repository.
2. Then clone the repository you forked using the command below (bash/zsh).

 ```sh
   git clone <your-fork-url>
   cd manim
 ```

3. Now that you have cloned the repo, before making any changes, you have to enter the commands below in order to be able to contribute to Manim Community.

   ```sh
   git remote add fork https://github.com/ManimCommunity/manim.git
   git fetch fork
   git checkout -b <your-branch-name> fork/master
   ```

   The first command tells `git` that you are going to make a Pull Request to Manim Community. 
   The second command pulls all the commits from the aforementioned fork.
   Finally, the third one makes your current working branch up-to-date with Manim Community's master branch.

    Now there are three repositories that git is keeping track of: the manim community repo (referred to as "fork"), your own fork of it (referred to by git as "origin"), and your local repository.

4. After that, you can make your changes to the repo's files (the code is in the `manim` directory). Then, you can commit said changes.

> As stated in the General Contribution Guidelines, make sure to test your changes against the example scenes in the `example_scenes` directory and test scenes in the `tests` directory, and add a new test in the `tests` directory for your new feature if you've made one.

5. Finally, instead of  typing in `git push`, enter the command below.

   ```sh
   git push -u origin <your-branch-name>
   ```

   Doing so creates a new branch with the updated contents of your fork on GitHub.

   Then you can make a Pull Request to the Manim Community Repo from your fork, through GitHub. Make sure to select `ManimCommunity/manim` instead of `3b1b/manim` as the `base repository` and your fork and branch as `head repository` - see the picture below.

   ![pull-requests-example-manim-community](./readme-assets/pull-requests.PNG)

Also make sure to pull from upstream/master right before making a Pull Request, resolve merge conflicts locally and only then submit the Pull Request.
