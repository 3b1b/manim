custom_config
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
        :emphasize-lines: 9, 11

            manim/
            ├── manimlib/
            │   ├── animation/
            │   ├── ...
            │   ├── default_config.yml
            │   └── window.py
            ├── output/
            │   ├── images
            │   │   └── Scene1.png
            │   └── videos
            │       └── Scene1.mp4
            ├── code.py
            └── custom_config.yml

    But if you set ``mirror_module_path`` to ``True``, the directory structure will be:

    .. code-block:: text
        :emphasize-lines: 8

            manim/
            ├── manimlib/
            │   ├── animation/
            │   ├── ...
            │   ├── default_config.yml
            │   └── window.py
            ├── output/
            │   └── code/
            │       ├── images
            │       │   └── Scene1.png
            │       └── videos
            │           └── Scene1.mp4
            ├── code.py
            └── custom_config.yml

- ``raster_images`` 
    The directory for storing raster images to be used in the code (including 
    ``.jpg``, ``.jpeg``, ``.png`` and ``.gif``), which will be read by ``ImageMobject``.

- ``vector_images``
    The directory for storing vector images to be used in the code (including 
    ``.svg`` and ``.xdv``), which will be read by ``SVGMobject``.

- ``sounds``
    The directory for storing sound files to be used in ``Scene.add_sound()`` (
    including ``.wav`` and ``.mp3``).

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

- ``text_alignment``
    Default text alignment for LaTeX

- ``background_color``
    Default background color

``window_position``
-------------------

The relative position of the playback window on the display (two characters, 
the first character means upper(U) / middle(O) / lower(D), the second character 
means left(L) / middle(O) / right(R)).

``window_monitor``
------------------

The number of the monitor you want the preview window to pop up on. (default is 0)

``full_screen``
---------------

Whether open the window in full screen. (default is false)

``break_into_partial_movies``
-----------------------------

If this is set to ``True``, then many small files will be written corresponding 
to each ``Scene.play`` and ``Scene.wait`` call, and these files will then be combined
to form the full scene.  

Sometimes video-editing is made easier when working with the broken up scene, which
effectively has cuts at all the places you might want.

``camera_resolutions``
----------------------

Export resolutions

- ``low``
    Low resolutions (default is 480p)

- ``medium``
    Medium resolutions (default is 720p)

- ``high``
    High resolutions (default is 1080p)

- ``ultra_high``
    Ultra high resolutions (default is 4K)

- ``default_resolutions``
    Default resolutions (one of the above four, default is high)

``fps``
-------

Export frame rate. (default is 30)