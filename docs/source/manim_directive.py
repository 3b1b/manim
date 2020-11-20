r"""
A directive for including Manim videos in a Sphinx document
===========================================================

When rendering the HTML documentation, the ``.. manim::`` directive
implemented here allows to include rendered videos.

Its basic usage that allows processing **inline content**
looks as follows::

    .. manim:: MyScene

        class MyScene(Scene):
            def construct(self):
                ...

It is required to pass the name of the class representing the
scene to be rendered to the directive.

As a second application, the directive can also be used to
render scenes that are defined within doctests, for example::

    .. manim:: DirectiveDoctestExample
        :ref_classes: Dot

        >>> dot = Dot(color=RED)
        >>> dot.color
        <Color #fc6255>
        >>> class DirectiveDoctestExample(Scene):
        ...     def construct(self):
        ...         self.play(ShowCreation(dot))


Options
-------

Options can be passed as follows::

    .. manim:: <Class name>
        :<option name>: <value>

The following configuration options are supported by the
directive:

    hide_source
        If this flag is present without argument,
        the source code is not displayed above the rendered video.

    quality : {'low', 'medium', 'high', 'fourk'}
        Controls render quality of the video, in analogy to
        the corresponding command line flags.

    save_as_gif
        If this flag is present without argument,
        the scene is rendered as a gif.

    save_last_frame
        If this flag is present without argument,
        an image representing the last frame of the scene will
        be rendered and displayed, instead of a video.

    ref_classes
        A list of classes, separated by spaces, that is
        rendered in a reference block after the source code.

    ref_functions
        A list of functions and methods, separated by spaces,
        that is rendered in a reference block after the source code.

"""
from docutils.parsers.rst import directives, Directive

import jinja2
import os
from os.path import relpath
from pathlib import Path
from typing import List

import shutil

from manim import QUALITIES

classnamedict = {}


def process_name_list(option_input: str, reference_type: str) -> List[str]:
    r"""Reformats a string of space separated class names
    as a list of strings containing valid Sphinx references.

    Tests
    -----

    ::

        >>> process_name_list("Tex TexTemplate", "class")
        [":class:`~.Tex`", ":class:`~.TexTemplate`"]
        >>> process_name_list("Scene.play Mobject.rotate", "func")
        [":func:`~.Scene.play`", ":func:`~.Mobject.rotate`"]
    """
    return [f":{reference_type}:`~.{name}`" for name in option_input.split()]


class ManimDirective(Directive):
    r"""The manim directive, rendering videos while building
    the documentation.

    See the module docstring for documentation.
    """
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "hide_source": bool,
        "quality": lambda arg: directives.choice(
            arg, ("low", "medium", "high", "fourk")
        ),
        "save_as_gif": bool,
        "save_last_frame": bool,
        "ref_modules": lambda arg: process_name_list(arg, "mod"),
        "ref_classes": lambda arg: process_name_list(arg, "class"),
        "ref_functions": lambda arg: process_name_list(arg, "func"),
    }
    final_argument_whitespace = True

    def run(self):
        from manim import config

        global classnamedict

        clsname = self.arguments[0]
        if clsname not in classnamedict:
            classnamedict[clsname] = 1
        else:
            classnamedict[clsname] += 1

        hide_source = "hide_source" in self.options
        save_as_gif = "save_as_gif" in self.options
        save_last_frame = "save_last_frame" in self.options
        assert not (save_as_gif and save_last_frame)

        ref_content = (
            self.options.get("ref_modules", [])
            + self.options.get("ref_classes", [])
            + self.options.get("ref_functions", [])
        )
        if ref_content:
            ref_block = f"""
.. admonition:: Example References
    :class: example-reference

    {' '.join(ref_content)}"""
        else:
            ref_block = ""

        if "quality" in self.options:
            quality = f'{self.options["quality"]}_quality'
        else:
            quality = "example_quality"
        frame_rate = QUALITIES[quality]["frame_rate"]
        pixel_height = QUALITIES[quality]["pixel_height"]
        pixel_width = QUALITIES[quality]["pixel_width"]
        qualitydir = f"{pixel_height}p{frame_rate}"

        state_machine = self.state_machine
        document = state_machine.document

        source_file_name = document.attributes["source"]
        source_rel_name = relpath(source_file_name, setup.confdir)
        source_rel_dir = os.path.dirname(source_rel_name)
        while source_rel_dir.startswith(os.path.sep):
            source_rel_dir = source_rel_dir[1:]

        dest_dir = os.path.abspath(
            os.path.join(setup.app.builder.outdir, source_rel_dir)
        )
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        source_block = [
            ".. code-block:: python",
            "",
            *["    " + line for line in self.content],
        ]
        source_block = "\n".join(source_block)

        config.media_dir = Path(setup.confdir) / "media"
        config.images_dir = "{media_dir}/images"
        config.video_dir = "{media_dir}/videos/{quality}"
        output_file = f"{clsname}-{classnamedict[clsname]}"
        config.assets_dir = Path("_static")

        config_code = [
            f'config["frame_rate"] = {frame_rate}',
            f'config["pixel_height"] = {pixel_height}',
            f'config["pixel_width"] = {pixel_width}',
            f'config["save_last_frame"] = {save_last_frame}',
            f'config["save_as_gif"] = {save_as_gif}',
            f'config["output_file"] = r"{output_file}"',
        ]

        user_code = self.content
        if user_code[0].startswith(">>> "):  # check whether block comes from doctest
            user_code = [
                line[4:] for line in user_code if line.startswith((">>> ", "... "))
            ]

        code = [
            "from manim import *",
            *config_code,
            *user_code,
            f"{clsname}().render()",
        ]
        exec("\n".join(code), globals())

        # copy video file to output directory
        if not (save_as_gif or save_last_frame):
            filename = f"{output_file}.mp4"
            filesrc = config.get_dir("video_dir") / filename
            destfile = os.path.join(dest_dir, filename)
            shutil.copyfile(filesrc, destfile)
        elif save_as_gif:
            filename = f"{output_file}.gif"
            filesrc = config.get_dir("video_dir") / filename
        elif save_last_frame:
            filename = f"{output_file}.png"
            filesrc = config.get_dir("images_dir") / filename
        else:
            raise ValueError("Invalid combination of render flags received.")

        rendered_template = jinja2.Template(TEMPLATE).render(
            clsname=clsname,
            clsname_lowercase=clsname.lower(),
            hide_source=hide_source,
            filesrc_rel=os.path.relpath(filesrc, setup.confdir),
            output_file=output_file,
            save_last_frame=save_last_frame,
            save_as_gif=save_as_gif,
            source_block=source_block,
            ref_block=ref_block,
        )
        state_machine.insert_input(
            rendered_template.split("\n"), source=document.attributes["source"]
        )

        return []


def setup(app):
    import manim

    setup.app = app
    setup.config = app.config
    setup.confdir = app.confdir
    app.add_directive("manim", ManimDirective)

    metadata = {"parallel_read_safe": False, "parallel_write_safe": True}
    return metadata


TEMPLATE = r"""
{% if not hide_source %}
.. raw:: html

    <div class="manim-example">

{% endif %}

{% if not (save_as_gif or save_last_frame) %}
.. raw:: html

    <video id="{{ clsname_lowercase }}" class="manim-video" controls loop autoplay src="./{{ output_file }}.mp4"></video>
{% elif save_as_gif %}
.. image:: /{{ filesrc_rel }}
    :align: center
    :name: {{ clsname_lowercase }}
{% elif save_last_frame %}
.. image:: /{{ filesrc_rel }}
    :align: center
    :name: {{ clsname_lowercase }}
{% endif %}
{% if not hide_source %}
.. raw:: html

    <h5 class="example-header">{{ clsname }}<a class="headerlink" href="#{{ clsname_lowercase }}">¶</a></h5>

{{ source_block }}
{{ ref_block }}
{% endif %}

.. raw:: html

    </div>
"""
