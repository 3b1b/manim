Troubleshooting
===============

List of known installation problems.

(Windows) OSError: dlopen() failed to load a library: pango?
------------------------------------------------------------

If your manual installation of Manim (or even the installation using
Chocolatey) fails with the error

.. code-block::

  OSError: dlopen() failed to load a library: pango / pango-1 / pango-1.0 / pango-1.0-0

possibly combined with alerts warning about procedure entry points
``"deflateSetHeader"`` and ``"inflateReset2"`` that could not be
located, you might run into an issue with a patched version of ``zlib1.dll``
shipped by Intel, `as described here <https://github.com/msys2/MINGW-packages/issues/813>`_.

To resolve this issue, you can copy ``zlib1.dll`` from the directory
provided for the Pango binaries to the directory Manim is installed to.

For a more global solution (try at your own risk!), try renaming the
file ``zlib1.dll`` located at ``C:\Program Files\Intel\Wifi\bin`` to
something like ``zlib1.dll.bak`` -- and then try installing Manim again
(either using ``pip install manimce`` or with Chocolatey). Ensure that
you are able to revert this name change in case you run into troubles
with your WiFi (we did not get any reports about such a problem, however).


Some letters are missing from TextMobject/TexMobject output?
------------------------------------------------------------

If you have recently installed TeX you may need to build the fonts it
uses. Which can be done by running:

.. code-block:: bash

  fmtutil -sys --all


.. _dvisvgm-troubleshoot:

Installation does not support converting PDF to SVG?
----------------------------------------------------

First, make sure your ``dvisvgm`` version is at least 2.4:

.. code-block:: bash

  dvisvgm --version


If you do not know how to update ``dvisvgm``, please refer to your operating system's documentation.

Second, check whether your ``dvisvgm`` supports PostScript specials. This is needed in order to convert from PDF to SVG.

.. code-block:: bash

  dvisvgm -l


If the output to this command does **not** contain ``ps  dvips PostScript specials``, this is a bad sign.
In this case, run

.. code-block:: bash

  dvisvgm -h


If the output does **not** contain ``--libgs=filename``, this means your ``dvisvgm`` does not currently support PostScript. You must get another binary.

If, however, ``--libgs=filename`` appears in the help, that means that your ``dvisvgm`` needs the Ghostscript library in order to support PostScript. Search for ``libgs.so`` (on Linux, probably in ``/usr/local/lib`` or ``/usr/lib``) or ``gsdll32.dll`` (on 32-bit Windows, probably in ``C:\windows\system32``) or ``gsdll64.dll`` (on 64-bit Windows, probably in ``c:\windows\system32`` -- yes 32) or ``libgsl.dylib`` (on Mac OS, probably in ``/usr/local/lib`` or ``/opt/local/lib``). Please look carefully, as the file might be located elsewhere, e.g. in the directory where Ghostscript is installed.

As soon as you have found the library, try (on Mac OS or Linux)

.. code-block:: bash

  export LIBGS=<path to your library including the file name>
  dvisvgm -l

or (on Windows)

.. code-block:: bat

  set LIBGS=<path to your library including the file name>
  dvisvgm -l


You should now see ``ps    dvips PostScript specials`` in the output. Refer to your operating system's documentation in order to find out how you can set or export the environment variable ``LIBGS`` automatically whenever you open a shell.

As a last check, you can run

.. code-block:: bash

  dvisvgm -V1

while still having ``LIBGS`` set to the correct path, of course. If ``dvisvgm`` can find your Ghostscript installation, it will be shown in the output together with the version number.

If you do not have the necessary library on your system, please refer to your operating system's documentation in order to find out where you can get it and how you have to install it.

If you are unable to solve your problem, check out the `dvisvgm FAQ <https://dvisvgm.de/FAQ/>`_.
