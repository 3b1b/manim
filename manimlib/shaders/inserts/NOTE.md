WGSL has no preprocessor, and no analog to #include. So the way manim shares code between
shaders is to replace any line which looks like

#INSERT <file_name>

with the code from one of the files in this folder, see utils/shaders.get_shader_code_from_file.
An inserted file may insert others, and may declare bindings of its own, so nothing should
re-declare those in the surrounding context.

One shader is one file, both stages of it together, sitting beside this folder and named for
the kind of mobject it draws. A mobject says which by its shader_file, which may be any path.

Three of the lines in these files are replaced in turn with code generated from the mobject
being drawn: what its records hold, what it holds for the whole of itself, and which binding
each image it named is at. Those are marked with a comment rather than a #INSERT, since there
is no file behind them.
