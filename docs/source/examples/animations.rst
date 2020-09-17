Animations
============


Transformations
#################

Some more examples will come soon here!

Updaters
##########

.. manim:: Updater1Example
    :quality: medium

    class Updater1Example(Scene):
        def construct(self):
            curve_reference = Line(ORIGIN, LEFT).set_color(GREEN)
            self.add(curve_reference)

            def update_curve(mob, dt):
                mob.rotate_about_origin(dt)

            curve2 = Line(ORIGIN, LEFT)
            curve2.add_updater(update_curve)
            self.add(curve_reference, curve2)
            self.wait(PI)
