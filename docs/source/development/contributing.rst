Contributing
============

Accept any contribution you make :)

- **Contribute to the manim source code**: 

Please fork to your own repository and make changes, submit a pull request, and fill in 
the motivation for the change following the instructions in the template. We will check 
your pull request in detail (this usually takes a while, please be patient)

- **Contribute to the documentation**: 

Also submit a pull request and write down the main changes.

- **If you find a bug in the code**: 

Please open an issue and fill in the found problem and your environment according 
to the template. (But please note that if you think this problem is just a problem 
of yourself, rather than a problem of source code, it is recommended that you ask a 
question in the `Q&A category <https://github.com/3b1b/manim/discussions/categories/q-a>`_ 
of the discussion page)

- **You are welcome to share the content you made with manim**: 

Post it in the `show and tell category <https://github.com/3b1b/manim/discussions/categories/show-and-tell>`_
of the discussion page.

- **You are also welcome to share some of your suggestions and ideas**: 

Post them in the `ideas category <https://github.com/3b1b/manim/discussions/categories/ideas>`_ 
of the discussion page.

How to build this documentation
-------------------------------

- Clone the 3b1b/manim repository

.. code-block:: sh

    git clone https://github.com/3b1b/manim.git
    # or your own repo
    # git clone https://github.com/<your user name>/manim.git
    cd manim

- Install python package dependencies

.. code-block:: sh

    pip install -r docs/requirements.txt

- Go to the ``docs/`` folder and build

.. code-block:: sh

    cd docs/
    make html

- The output document is located in ``docs/build/html/``