# see more documentation guidelines online here: https://github.com/ManimCommunity/manim/wiki/Documentation-guidelines-(WIP)


class SomeClass:
    """A one line description of the Class.

    A short paragraph providing more details.

    Deprecation warning

    Extended Summary

    Parameters
    ----------
    scale_factor : :class:`float`
        The factor used for scaling.

    Returns
    -------
    :class:`~.VMobject`
        Returns the modified :class:`~.VMobject`.

    Tests
    -----

    Yields
    -------

    Receives
    ----------

    Other Parameters
    -----------------

    Raises
    ------
    :class:`TypeError`
        If one element of the list is not an instance of VMobject

    Warns
    -----

    Warnings
    --------

    Notes
    -----

    Examples
    --------
    .. manim:: AddTextLetterByLetterScene
        :save_last_frame:

        class AddTextLetterByLetterScene(Scene):
            def construct(self):
                t = Text("Hello World word by word")
                self.play(AddTextWordByWord(t))



    See Also
    --------
    :class:`ShowCreation`, :class:`~.ShowPassingFlash`

    References
    ----------


    Other useful directives:

    .. tip::

        This is currently only possible for class:`~.Text` and not for class:`~.MathTex`.

    .. note::

        This is something to note.

    """
