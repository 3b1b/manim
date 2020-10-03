Text
=================================

.. manim:: Example1Text
    :save_last_frame:

    class Example1Text(Scene):
        def construct(self):
            text = Text('Hello world').scale(3)
            self.add(text)

.. manim:: Example2Text
    :save_last_frame:

    class Example2Text(Scene):
        def construct(self):
            text = Text('Hello world', color=BLUE).scale(3)
            self.add(text)


.. manim:: Example3Text
    :save_last_frame:

    class Example3Text(Scene):
        def construct(self):
            text = Text('Hello world', gradient=(BLUE, GREEN)).scale(3)
            self.add(text)


.. manim:: Example4Text
    :save_last_frame:

    class Example4Text(Scene):
        def construct(self):
            text = Text('Hello world', t2g={'world':(BLUE, GREEN)}).scale(3)
            self.add(text)

.. manim:: Example5Text
    :save_last_frame:

    class Example5Text(Scene):
        def construct(self):
            text = Text('Hello world', font='Source Han Sans').scale(3)
            self.add(text)

.. manim:: Example5bText
    :save_last_frame:

    class Example5bText(Scene):
        def construct(self):
            text = Text('Hello world', t2f={'world':'Forte'}).scale(3)
            self.add(text)

.. manim:: Example6Text
    :save_last_frame:

    class Example6Text(Scene):
        def construct(self):
            text = Text('Hello world', slant=ITALIC).scale(3)
            self.add(text)

.. manim:: Example7Text
    :save_last_frame:

    class Example7Text(Scene):
        def construct(self):
            text = Text('Hello world!', t2s={'world':ITALIC}).scale(3)
            self.add(text)

.. manim:: Example8Text
    :save_last_frame:

    class Example8Text(Scene):
        def construct(self):
            text = Text('Hello world', weight=BOLD).scale(3)
            self.add(text)

.. manim:: Example9Text
    :save_last_frame:

    class Example9Text(Scene):
        def construct(self):
            text = Text('Hello world', t2w={'world':BOLD}).scale(3)
            self.add(text)

.. manim:: Example10Text
    :save_last_frame:

    class Example10Text(Scene):
        def construct(self):
            text = Text('Hello', size=0.3).scale(3)
            self.add(text)

.. manim:: Example11Text
    :save_last_frame:

    class Example11Text(Scene):
        def construct(self):
            text = Text('Hello\nWorld', lsh=1.5).scale(3)
            self.add(text)

.. manim:: Example12Text
    :save_last_frame:

    class Example12Text(Scene):
        def construct(self):
            text = Text(
                'Google',
                t2c={'[:1]':'#3174f0', '[1:2]':'#e53125',
                     '[2:3]':'#fbb003', '[3:4]':'#3174f0',
                     '[4:5]':'#269a43', '[5:]':'#e53125', }).scale(3)
            self.add(text)

`Text` works also with other languages like `你好` or  `こんにちは` or `안녕하세요` or `مرحبا بالعالم`.
Be sure you have the font that supports those languages!

