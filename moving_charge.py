from big_ol_pile_of_manim_imports import *
import math
class MovingCharges(Scene):
    CONFIG = {"plane_kwargs" : {"color" : RED_B},
              "point_charge_loc" : 0.5*RIGHT-1.5*UP,
        }
    
    class Positron(Circle):
        CONFIG = {
        "radius" : 0.2,
        "stroke_width" : 3,
        "color" : RED,
        "fill_color" : RED,
        "fill_opacity" : 0.5,
        }
        def __init__(self, **kwargs):
            Circle.__init__(self, **kwargs)
            plus = TexMobject("+")
            plus.scale(0.7)
            plus.move_to(self)
            self.add(plus)

    def calc_field(self,point):
        x,y = point[:2]
        Rx,Ry = self.point_charge_loc[:2]
        r = math.sqrt((x-Rx)**2 + (y-Ry)**2)
        efield = (point - self.point_charge_loc)/r**3
        return Vector(efield).shift(point)

    def moving_charge(self):
        numb_charges=4
        possible_points = [v.get_start() for v in self.field]
        points = random.sample(possible_points, numb_charges)
        particles = VGroup(*[
            self.Positron().move_to(point)
            for point in points
        ])
        for particle in particles:
            particle.velocity = np.array((0,0,0))

        self.play(FadeIn(particles))
        self.moving_particles = particles
        self.add_foreground_mobjects(self.moving_particles )
        self.always_continually_update = True
        self.wait(10)

    def field_at_point(self,point):
        x,y = point[:2]
        Rx,Ry = self.point_charge_loc[:2]
        r = math.sqrt((x-Rx)**2 + (y-Ry)**2)
        efield = (point - self.point_charge_loc)/r**3
        return efield

    def continual_update(self, *args, **kwargs): # updates the screen for each frame during the entire scene
        if hasattr(self, "moving_particles"):
            dt = self.frame_duration
            for p in self.moving_particles:
                accel = self.field_at_point(p.get_center())
                p.velocity = p.velocity + accel*dt
                p.shift(p.velocity*dt)

    def construct(self):
        plane = NumberPlane(**self.plane_kwargs)
        plane.main_lines.fade(.9)
        plane.add(plane.get_axis_labels())
        self.add(plane)

        field = VGroup(*[self.calc_field(x*RIGHT+y*UP)
            for x in np.arange(-9,9,1)
            for y in np.arange(-5,5,1)
            ])

        # self.field=field | Don't need it?
        source_charge = self.Positron().move_to(self.point_charge_loc)
        self.play(FadeIn(source_charge))
        self.play(ShowCreation(field))
        self.moving_charge()

