custom_default
==============

``directories``
---------------

- ``mirror_module_path``
    (``True`` or ``False``) Whether to create a folder named the name of the 
    running file under the ``output`` path, and save the output (``images/`` 
    or ``videos/``) in it.

- ``output``
    Output file path, the videos will be saved in the ``videos/`` folder under it, 
    and the pictures will be saved in the ``images/`` folder under it.

    For example, if you set ``output`` to ``"/.../manim/output"`` and 
    ``mirror_module_path`` to ``False``, then you exported ``Scene1`` in the code 
    file and saved the last frame, then the final directory structure will be like:

    .. code-block:: text
        :emphasize-lines: 8, 10

            manim/
            ├── manimlib/
            │   ├── animation/
            │   ├── ...
            │   └── window.py
            ├── output/
            │   ├── images
            │   │   └── Scene1.png
            │   └── videos
            │       └── Scene1.mp4
            ├── code.py
            ├── custom_default.yml
            └── manim.py

    But if you set ``mirror_module_path`` to ``True``, the directory structure will be:

    .. code-block:: text
        :emphasize-lines: 7

            manim/
            ├── manimlib/
            │   ├── animation/
            │   ├── ...
            │   └── window.py
            ├── output/
            │   └── code/
            │       ├── images
            │       │   └── Scene1.png
            │       └── videos
            │           └── Scene1.mp4
            ├── code.py
            ├── custom_default.yml
            └── manim.py

- ``raster_images`` 
    The directory for storing raster images to be used in the code (including 
    ``.jpg``, ``.png`` and ``.gif``), which will be read by ``ImageMobject``.

- ``vector_images``
    The directory for storing vector images to be used in the code (including 
    ``.svg`` and ``.xdv``), which will be read by ``SVGMobject``.

- ``temporary_storage``
    The directory for storing temporarily generated cache files, including 
    ``Tex`` cache, ``Text`` cache and storage of object points.

``tex``
-------

- ``executable``
    The executable program used to compile LaTeX (``latex`` or ``xelatex -no-pdf``
    is recommended)

- ``template_file``
    LaTeX template used, in ``manimlib/tex_templates``

- ``intermediate_filetype``
    The type of intermediate vector file generated after compilation (``dvi`` if 
    ``latex`` is used, ``xdv`` if ``xelatex`` is used)
    
- ``text_to_replace``
    The text to be replaced in the template (needn't to change)

``universal_import_line``
-------------------------

Import line that need to execute when entering interactive mode directly.

``style``
---------

- ``font`` 
    Default font of Text

- ``background_color``
    Default background color

``window_position``
-------------------

The relative position of the playback window on the display (two characters, 
the first character means upper(U) / middle(O) / lower(D), the second character 
means left(L) / middle(O) / right(R)).

``camera_qualities``
--------------------

Export quality

- ``low``
    Low quality (default is 480p15)

- ``medium``
    Medium quality (default is 720p30)

- ``high``
    High quality (default is 1080p30)

- ``ultra_high``
    Ultra high quality (default is 4K60)

- ``default_quality``
    Default quality (one of the above four)