from helpers import *
from mobject import Mobject
from mobject.vectorized_mobject import *
from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from scene import Scene
from camera import *
from topics.characters import *
from topics.numerals import *

RADIUS = 2
RADIUS_BUFF_HOR = 1.3
RADIUS_BUFF_VER = 0.5
RADIUS_COLOR = BLUE
CIRCUM_COLOR = YELLOW
DECIMAL_WIDTH = 0.5


class ArcLengthChange(Animation):

    def __init__(self, mobject = None, new_angle = TAU/3, **kwargs):

        self.old_angle = mobject.angle
        self.start_angle = mobject.start_angle
        self.new_angle = new_angle
        Animation.__init__(self,mobject,**kwargs)

    def update_mobject(self,alpha):
        angle = interpolate(self.old_angle, self.new_angle, alpha)
        self.mobject.angle = angle
        self.mobject.generate_points()


class LabelTracksLine(Animation):

    def __init__(self, mobject = None, line = None, buff = 0.2, **kwargs):

        self.line = line
        self.buff = buff
        Animation.__init__(self,mobject,**kwargs)

    def update_mobject(self,alpha):
        line_center = self.line.get_center()
        line_end = self.line.points[-1]
        v = line_end - line_center
        v = v/np.linalg.norm(v)
        w = np.array([-v[1],v[0],0])
        self.mobject.move_to(line_center + self.buff * w)




        
class CircleConstants(Scene):

    def radial_label_func(self,a,b,theta):

        theta2 = theta % TAU
        slope = (a-b)/(TAU/4)

        if theta2 < TAU/4:
            x = a - slope * theta2
        elif theta < TAU/2:
            x = b + slope * (theta2 - TAU/4)
        elif theta < 3*TAU/4:
            x = a - slope * (theta2 - TAU/2)
        else:
            x = b + slope * (theta2 - 3*TAU/4)
        return x

	
    def construct(self):
        self.setup_circle()
        self.change_arc_length(0.004)
        self.pi_equals.next_to(self.decimal, LEFT)
        self.wait()
        self.change_arc_length(TAU/2)
        self.wait()
        self.change_arc_length(TAU)
        self.wait()
        self.change_arc_length(TAU/4)
        self.wait()
        self.change_arc_length(TAU/2)
        self.wait()




    def setup_circle(self):


        self.circle_arc = Arc(angle = 0.004, radius = RADIUS)
        self.radius = Line(ORIGIN, RADIUS * RIGHT)
        self.radius.highlight(RADIUS_COLOR)
        self.circle_arc.highlight(CIRCUM_COLOR)

        self.pi_equals = TexMobject("\pi\\approx", color = CIRCUM_COLOR)
        self.decimal = DecimalNumber(0, color = CIRCUM_COLOR)
        self.decimal.next_to(self.pi_equals, RIGHT, buff = 0.25)
        self.circum_label = VGroup(self.pi_equals, self.decimal)
        self.circum_label.next_to(self.radius, RIGHT, buff = RADIUS_BUFF_HOR)

            
        self.one = TexMobject("1", color = RADIUS_COLOR)
        self.one.next_to(self.radius, UP)

        self.play(ShowCreation(self.radius), FadeIn(self.one))
        self.play(
            ShowCreation(self.circle_arc),
            Write(self.pi_equals),
            Write(self.decimal)
        )


    def change_arc_length(self, new_angle):

        def decimal_position_update_func(decimal):

            angle = decimal.number
            max_radius = RADIUS + RADIUS_BUFF_HOR
            min_radius = RADIUS + RADIUS_BUFF_VER
            label_radius = self.radial_label_func(max_radius, min_radius, angle)
            label_center = label_radius * np.array([np.cos(angle), np.sin(angle),0])
            label_center += 0.5 * RIGHT
            # label_center += pi_eq_stencil.get_width() * RIGHT
            # print "label_center = ", label_center
            decimal.move_to(label_center)


        self.play(
            Rotate(self.radius, new_angle - self.circle_arc.angle, about_point = ORIGIN),
            ArcLengthChange(self.circle_arc,new_angle),
            ChangeDecimalToValue(
                self.decimal, new_angle, 
                position_update_func = decimal_position_update_func
            ),
            #MaintainPositionRelativeTo(self.one, self.radius),
            MaintainPositionRelativeTo(self.pi_equals, self.decimal),
            LabelTracksLine(self.one,self.radius, buff = 0.5),
            run_time = 3,
        )
        self.wait(2)
















