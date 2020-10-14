LaTeX
=================================

.. manim:: Example1LaTeX
    :save_last_frame:

    class Example1LaTeX(Scene):
        def construct(self):
            tex = Tex(r'$\xrightarrow{Hello}$ \LaTeX').scale(3)
            self.add(tex)

.. manim:: Example2LaTeX
    :save_last_frame:

    class Example2LaTeX(Scene):
        def construct(self):
            tex = Tex(r'$\mathtt{Hello}$ \LaTeX', color=BLUE).scale(3)
            self.add(tex)


.. manim:: Example3LaTeX
    :save_last_frame:

    class Example3LaTeX(Scene):
        def construct(self):
            myTemplate = TexTemplate()
            myTemplate.add_to_preamble(r"\usepackage{mathrsfs}")
            tex = Tex(r'$\mathscr{H}ello$ \LaTeX}', tex_template=myTemplate).scale(3)
            self.add(tex)


.. manim:: Example4LaTeX
    :save_last_frame:

    class Example4LaTeX(Scene):
        def construct(self):
            tex = Tex('Hello', '$\\bigstar$', '\LaTeX').scale(3)
            tex.set_color_by_tex('igsta', RED)
            self.add(tex)

.. manim:: Example5LaTeX
    :save_last_frame:

    class Example5LaTeX(Scene):
        def construct(self):
            tex = Tex('Hello \LaTeX', tex_template=TexFontTemplates.french_cursive).scale(3)
            self.add(tex)

.. manim:: Example5bLaTeX
    :save_last_frame:

    class Example5bLaTeX(Scene):
        def construct(self):
            templateForFrenchCursive = TexTemplate(
                preamble=r"""
    \usepackage[english]{babel}
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage[T1]{fontenc}
    \usepackage[default]{frcursive}
    \usepackage[eulergreek,noplusnominus,noequal,nohbar,nolessnomore,noasterisk]{mathastext}
    """)
            tex = Tex('Hello \LaTeX', tex_template=templateForFrenchCursive).scale(3)
            self.add(tex)

.. manim:: Example6LaTeX
    :save_last_frame:

    class Example6LaTeX(Scene):
        def construct(self):
            tex = Tex('Hello 你好 \LaTeX', tex_template=TexTemplateLibrary.ctex).scale(3)
            self.add(tex)


