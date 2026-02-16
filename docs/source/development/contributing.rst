Contributing
============

We welcome and appreciate any contributions you make to Manim! :)

Contributing to the Source Code
-------------------------------

- **Fork the repository** to your own GitHub account.
- Make your changes locally.
- Submit a **pull request** to the main repository.
- Fill in the **motivation for your change** following the instructions in the provided template.

.. note::

    Pull requests will be reviewed in detail. This process may take some time, so please be patient.

Contributing to the Documentation
---------------------------------

- Make edits to the documentation files in your fork.
- Submit a **pull request** describing the main changes you made.

Reporting Bugs
--------------

If you find a bug in the code:

1. Open a new **issue** in the repository.
2. Describe the problem clearly.
3. Include details about your **environment** (Python version, OS, Manim version, etc.) according to the issue template.

.. note::

    If you suspect the problem is local to your setup rather than the source code, it is recommended to ask a question in the
    `Q&A category <https://github.com/3b1b/manim/discussions/categories/q-a>`_ of the discussion page.

Sharing Your Work
-----------------

- You are welcome to share content you created using Manim.
- Post it in the `Show and Tell category <https://github.com/3b1b/manim/discussions/categories/show-and-tell>`_ of the discussion page.

Sharing Ideas and Suggestions
-----------------------------

- Suggestions, feature requests, and ideas are encouraged!
- Post them in the `Ideas category <https://github.com/3b1b/manim/discussions/categories/ideas>`_ of the discussion page.

How to Build the Documentation
------------------------------

Follow these steps to build the Manim documentation locally:

1. **Clone the repository**

.. code-block:: sh

    git clone https://github.com/3b1b/manim.git
    # Or clone your own fork
    # git clone https://github.com/<your-username>/manim.git
    cd manim

2. **Install Python package dependencies**

.. code-block:: sh

    pip install -r docs/requirements.txt

3. **Navigate to the docs folder and build HTML**

.. code-block:: sh

    cd docs/
    make html

4. **Find the built documentation**

    The output HTML files will be located in::

        docs/build/html/