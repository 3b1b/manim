Text and LaTeX
===============


Text
--------------
The simplest way to add text to you animation is to use the :class:`~.Text` class. It uses the Cairo library to render text.
A newer addition to manim is the :class:`~.PangoText` class, which uses the Pango library.

The Text() mobject
+++++++++++++++++++

.. manim:: HelloWorld
    :save_last_frame:

    class HelloWorld(Scene):
        def construct(self):
            text = Text('Hello world').scale(3)
            self.add(text)

For more examples, see: :class:`~.Text`.

The PangoText() mobject
+++++++++++++++++++++++

The :class:`~.PangoText` mobject uses the Pango library to render text. Use this whenever you want to use non-English alphabets like `你好` or  `こんにちは` or `안녕하세요` or `مرحبا بالعالم`.


LaTeX
-------------------

The Tex() mobject
+++++++++++++++++++
Just as you can use :class:`~.Text` to add text to your videos, you can use :class:`~.Tex` to insert LaTeX.

.. manim:: HelloLaTeX
    :save_last_frame:

    class HelloLaTeX(Scene):
        def construct(self):
            tex = Tex(r'\LaTeX').scale(3)
            self.add(tex)

Note that we are using a raw string (``r'---'``) instead of a regular string (``'---'``).
This is because TeX code uses a lot of special characters - like ``\`` for example - 
that have special meaning within a regular python string. An alternative would have
been to write ``\\`` as in ``Tex('\\LaTeX')``.

The MathTex() mobject
++++++++++++++++++++++
Anything enclosed in ``$`` signs is interpreted as maths-mode:

.. manim:: HelloTex
    :save_last_frame:

    class HelloTex(Scene):
        def construct(self):
            tex = Tex(r'$\xrightarrow{Hello}$ \LaTeX').scale(3)
            self.add(tex)

Whereas in a :class:`~.MathTex` mobject everything is math-mode by default and you would use ``\text{}`` to
insert regular text:

.. manim:: HelloMathTex
    :save_last_frame:

    class HelloMathTex(Scene):
        def construct(self):
            tex = MathTex(r'\xrightarrow{Hello}\text{ \LaTeX}').scale(3)
            self.add(tex)

LaTeX commands and keyword arguments
+++++++++++++++++++++++++++++++++++++
We can use any standard LaTeX commands in the AMS maths packages. For example the ``mathtt`` text type.

.. manim:: AMSLaTeX
    :save_last_frame:

    class AMSLaTeX(Scene):
        def construct(self):
            tex = Tex(r'$\mathtt{Hello}$ \LaTeX').scale(3)
            self.add(tex)

On the manim side, the :class:`~.Tex` class also accepts attributes to change the appearance of the output. 
This is very similar to the :class:`~.Text` class. For example, the ``color`` keyword changes the color of the TeX mobject:

.. manim:: LaTeXAttributes
    :save_last_frame:

    class LaTeXAttributes(Scene):
        def construct(self):
            tex = Tex(r'Hello \LaTeX', color=BLUE).scale(3)
            self.add(tex)

Extra LaTeX Packages
+++++++++++++++++++++
Some commands require special packages to be loaded into the TeX template. For example, 
to use the ``mathscr`` script, we need to add the ``mathrsfs`` package. Since this package isn't loaded
into manim's tex template by default, we add it manually:

.. manim:: AddPackageLatex
    :save_last_frame:

    class AddPackageLatex(Scene):
        def construct(self):
            myTemplate = TexTemplate()
            myTemplate.add_to_preamble(r"\usepackage{mathrsfs}")
            tex = Tex(r'$\mathscr{H} \rightarrow \mathbb{H}$}', tex_template=myTemplate).scale(3)
            self.add(tex)

Substrings and parts
+++++++++++++++++++++
The TeX mobject can accept multiple strings as arguments. Afterwards you can refer to the individual
parts either by their index (like ``tex[1]``), or you can look them up by (parts of) the tex code like
in this example where we set the color of the ``\bigstar`` using :func:`~.set_color_by_tex`:

.. manim:: LaTeXSubstrings
    :save_last_frame:

    class LaTeXSubstrings(Scene):
        def construct(self):
            tex = Tex('Hello', r'$\bigstar$', r'\LaTeX').scale(3)
            tex.set_color_by_tex('igsta', RED)
            self.add(tex)

LaTeX Maths Fonts - The Template Library
++++++++++++++++++++++++++++++++++++++++++++
Changing fonts in LaTeX when typesetting mathematical formulae is a little bit more tricky than 
with regular text. It requires changing the template that is used to compile the tex code.
Manim comes with a collection of :class:`~.TexFontTemplates` ready for you to use. These templates will all work
in maths mode:

.. manim:: LaTeXMathFonts
    :save_last_frame:

    class LaTeXMathFonts(Scene):
        def construct(self):
            tex = Tex(r'$f: A \rightarrow B$', tex_template=TexFontTemplates.french_cursive).scale(3)
            self.add(tex)

Manim also has a :class:`~.TexTemplateLibrary` containing the TeX templates used by 3Blue1Brown. One example 
is the ctex template, used for typesetting Chinese. For this to work, the ctex LaTeX package
must be installed on your system. Furthermore, if you are only typesetting Text, you probably do not
need :class:`~.Tex` at all, and should use :class:`~.Text` or :class:`~.PangoText` instead. 

.. manim:: LaTeXTemplateLibrary
    :save_last_frame:

    class LaTeXTemplateLibrary(Scene):
        def construct(self):
            tex = Tex('Hello 你好 \\LaTeX', tex_template=TexTemplateLibrary.ctex).scale(3)
            self.add(tex)


Aligning formulae
++++++++++++++++++
A :class:`~.MathTex` mobject is typeset in the LaTeX  ``align*`` environment. This means you can use the ``&`` alignment
character when typesetting multiline formulae:

.. manim:: LaTeXAlignEnvironment
    :save_last_frame:

    class LaTeXAlignEnvironment(Scene):
        def construct(self):
            tex = MathTex(r'f(x) &= 3 + 2 + 1\\ &= 5 + 1 \\ &= 6').scale(2)
            self.add(tex)
