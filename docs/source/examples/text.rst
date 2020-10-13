Text
=================================

.. manim:: Example1Text
    :save_last_frame:

    class Example1Text(Scene):
        def construct(self):
            text = Text('Hello world').scale(3)
            self.add(text)

This is an example that illustrates how to use the :class:`~.Text` class.

In case you want to use other alphabets like `你好` or  `こんにちは` or `안녕하세요` or `مرحبا بالعالم`, you can have a look at :class:`~.PangoText` 
