Plotting with manim
=================================

.. manim:: ParamFunc1
    :quality: medium
    :save_last_frame:

    class ParamFunc1(Scene):
       def func(self,t):
           return np.array((np.sin(2*t), np.sin(3*t),0))
       def construct(self):
           func=ParametricFunction(self.func, t_max=TAU, fill_opacity=0).set_color(RED)
           self.add(func.scale(3))

