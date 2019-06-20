from manimlib.imports import *

class Birthday(Scene):

    def construct(self):

        sidelength = 6.0
        corner = np.array([-sidelength/2,-sidelength/2,0])
        nb_days_left = 365.0
        toggle = False

        def probability():
            width = rect.get_width()
            height = rect.get_height()
            return width * height / sidelength**2

        rect = Square().scale(sidelength/2)

        while probability() > 0.5:

            self.add(rect.copy())
            nb_days_left -= 1

            if toggle:
                dim = 0
            else:
                dim = 1
            
            rect.stretch_about_point(nb_days_left / 365, dim, corner)

            toggle = not toggle

