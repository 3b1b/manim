Animations
============


Transformations
#################

Some more examples will come soon here!

Updaters
##########

.. manim:: Updater1Example

    class Updater1Example(Scene):
        def construct(self):
            def my_rotation_updater(mobj,dt):
                mobj.rotate_about_origin(dt)
            line_reference = Line(ORIGIN, LEFT).set_color(WHITE)
            line_moving = Line(ORIGIN, LEFT).set_color(BLUE)
            line_moving.add_updater(my_rotation_updater)
            self.add(line_reference, line_moving)
            self.wait(PI)

.. manim:: Updater2Example

    class Updater2Example(Scene):
        def construct(self):
            def updater_forth(mobj, dt):
                mobj.rotate_about_origin(dt)
            def updater_back(mobj, dt):
                mobj.rotate_about_origin(-dt)
            line_reference = Line(ORIGIN, LEFT).set_color(WHITE)
            line_moving = Line(ORIGIN, LEFT).set_color(YELLOW)
            line_moving.add_updater(updater_forth)
            self.add(line_reference, line_moving)
            self.wait(2)
            line_moving.remove_updater(updater_forth)
            line_moving.add_updater(updater_back)
            self.wait(2)
            line_moving.remove_updater(updater_back)
            self.wait(0.5)

.. manim:: Example3

    class Example3(Scene):
        def construct(self):
            number_line = NumberLine()  ##with all your parameters and stuff
            pointer = Vector(DOWN)
            label = MathTex("x").add_updater(lambda m: m.next_to(pointer, UP))

            pointer_value = ValueTracker(0)
            pointer.add_updater(
                lambda m: m.next_to( number_line.n2p(pointer_value.get_value()), UP)
            )
            self.add(number_line, pointer, label)
            self.play(pointer_value.set_value, 5)
            self.wait()
            self.play(pointer_value.set_value, 3)

.. manim:: Example4

    class Example4(Scene):
        def construct(self):
            path = VMobject()
            dot = Dot()
            path.set_points_as_corners([dot.get_center(), dot.get_center()])
            def update_path(path):
                previus_path = path.copy()
                previus_path.add_points_as_corners([dot.get_center()])
                path.become(previus_path)
            path.add_updater(update_path)
            self.add(path, dot)
            self.play(Rotating(dot, radians=PI, about_point=RIGHT, run_time=2))
            self.wait()
            self.play(dot.shift, UP)
            self.play(dot.shift, LEFT)
            self.wait()

.. manim:: Example1ValTracker

    class Example1ValTracker(Scene):
        def construct(self):
            dot_disp = Dot().set_color(RED)
            self.add(dot_disp)
            tick_start = 1
            tick_end = 2
            val_tracker = ValueTracker(tick_start)
            def dot_updater(mob):
                mob.set_y(val_tracker.get_value())
            dot_disp.add_updater(dot_updater)
            self.play(val_tracker.set_value, tick_end, rate_func=linear)
            self.wait()

.. manim:: Example2ValTracker

    class Example2ValTracker(Scene):
        def construct(self):
            tick_start = 0
            tick_end = 2 * PI
            val_tracker = ValueTracker(tick_start)
            def my_rotation_updater(mobj):
                mobj.rotate_about_origin(1 / 30) # be careful: This is framerate dependent!
            line_reference = Line(ORIGIN, LEFT).set_color(WHITE)
            line_moving = Line(ORIGIN, LEFT).set_color(ORANGE)
            line_moving.add_updater(my_rotation_updater)
            self.add(line_reference, line_moving)
            self.play(val_tracker.set_value, tick_end, run_time=PI)

.. manim:: PlaneFadeOut
      
    class PlaneFadeOut(Scene):
        
        def construct(self):
            
            sq2= Square()
            
            sq1= Square()
            sq1.next_to(sq2,LEFT)
            
            sq3= Square()
            sq3.next_to(sq2,RIGHT)
            
            circ = Circle()
            circ.next_to(sq2,DOWN)
            
            self.add(sq1,sq2,sq3,circ)
            self.wait()
            
            self.play(FadeOut(sq1),FadeOut(sq2),FadeOut(sq3))
            self.wait()

.. manim:: AnimationFadeInAndOut
    
    class AnimationFadeInAndOut(Scene):
        def construct(self):
            square = Square(color=BLUE).shift(2*UP)
            
            annotation = Text('Fade In', height=.8)
            self.add(annotation)
            self.play(FadeIn(square))
            
            annotation.become(Text('Fade Out', height=.8))
            self.add(annotation)
            self.play(FadeOut(square))


