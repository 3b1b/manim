Troubleshooting
===============

List of known installation problems.

Some letters are missing from TextMobject/TexMobject output?
------------------------------------------------------------

If you have recently installed TeX you may need to build the fonts it
uses. Which can be done by running:

.. code-block:: bash

  fmtutil -sys --all
