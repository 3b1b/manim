# General Contribution Guidelines

Please take what follows into consideration when contributing to this repository (repo).

1. If code changes are being made, please include documentation **following the guidelines in the Wiki** (typings are also welcome, but we can probably do them for you, given the documentation).
2. (For the maintainers of this repo) Label PRs appropriately.
3. Link relevant issues.
4. Ensure compatibility with the latest changes in the repo.

## Contributing to the Manim Community Fork - General instructions

As this is a Fork of [Manim from 3b1b](https://github.com/3b1b/manim), contributing can be a bit confusing. So here is a small guide on it. 

1. First, make a fork of either this Repository.
2. Then clone the repository you forked by the command below.

 ```sh
   git clone <your-fork-url>
   cd manim
 ```

3. Now that you have cloned the Repo, before making any changes, you have to enter the commands below to contribute to Manim Community.

   ```sh
   git remote add fork https://github.com/ManimCommunity/manim.git
   git fetch fork
   git checkout -b <your-branch-name> fork/master
   ```

   The first command tells `git` that you are going to make a Pull Request for Manim Community. 
   Then the second command pulls all the commits from the Fork ( Community Fork ).
   The third one changes your current working branch even with Manim Community Fork master.

   Now there are three repositories that git is keeping track of: the manim community repo (referred to as "fork"), your own fork of the manim  community repo (referred to by git as "origin"), and your local  repository).

4. After that, you can make your changes to contents inside the `manim` directory. Then, you can commit the changes.

5. Finally, before typing in `git push` enter the command below.

   ```sh
   git push -u origin <your-branch-name>
   ```

   Doing this creates a new branch with the updated contents in your fork on GitHub.

   Then you can make a Pull Request to the Manim Community Repo from your fork, through GitHub. Make sure to select `ManimCommunity/manim` instead of `3b1b/manim` as `base repository` and your fork and branch as `head repository`. See the picture below.

   ![pull-requests-example-manim-community](./readme-assets/pull-requests.PNG)

Also make sure to pull from upstream/master right before making a Pull Request, resolving merge conflicts locally and only then submitting the Pull Request.
