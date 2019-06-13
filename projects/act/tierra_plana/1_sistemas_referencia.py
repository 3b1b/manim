from big_ol_pile_of_manim_imports import *
from numpy import linalg as LA

class Soporte(Dot):
    CONFIG = {
        "color": RED
    }
    def __init__(self, ** kwargs):
        Dot.__init__(self,** kwargs)
        self.velocity = np.array((2, 0, 0))

class ContinualPendulumAnimation(ContinualAnimation):
    def __init__(self, pendulo, soporte, cuerda):
        self.pendulo = pendulo
        self.soporte = soporte
        self.cuerda  = cuerda
        ContinualAnimation.__init__(self, cuerda)

    def update_mobject(self, dt):
    	linea_ref=Line(UP,DOWN)
    	#angulo=angle_between_vectors(linea_ref.get_vector(),cuerda.get_vector())
    	self.soporte.acceleration=np.array([3,0,0])
    	self.soporte.velocity= self.soporte.velocity + self.soporte.acceleration * dt
    	self.soporte.shift(self.soporte.velocity*dt)
    	mag_aceleracion=LA.norm(self.soporte.acceleration)
    	ang_alpha=np.arctan(LA.norm(self.soporte.acceleration)/dt)
    	self.cuerda.rotate(ang_alpha,
            about_point=self.soporte.get_center(),
            about_edge=self.soporte.get_center())
    	self.pendulo.move_to(self.cuerda.get_end())


class MovimientoTren(Scene):
	def construct(self):
		soporte=Soporte().to_edge(LEFT)
		pendulo=Dot(color=YELLOW).next_to(soporte,DOWN,buff=1.5)
		cuerda=Line(soporte,pendulo)

		conjunto=VGroup(soporte,pendulo,cuerda)
		self.add(conjunto)

		self.add(ContinualPendulumAnimation(pendulo,soporte,cuerda))
		self.wait(4)
		self.remove(ContinualPendulumAnimation(pendulo,soporte,cuerda))
		self.wait()


class Ball(Circle):
    CONFIG = {
        "radius": 0.4,
        "fill_color": BLUE,
        "fill_opacity": 1,
        "color": BLUE
    }

    def __init__(self, ** kwargs):
        Circle.__init__(self, ** kwargs)
        self.velocity = np.array((2, 0, 0))

    def get_top(self):
        return self.get_center()[1] + self.radius

    def get_bottom(self):
        return self.get_center()[1] - self.radius

    def get_right_edge(self):
        return self.get_center()[0] + self.radius

    def get_left_edge(self):
        return self.get_center()[0] - self.radius


class Box(Rectangle):
    CONFIG = {
        "height": 6,
        "width": FRAME_WIDTH - 2,
        "color": GREEN_C
    }

    def __init__(self, ** kwargs):
        Rectangle.__init__(self, ** kwargs)  # Edges
        self.top = 0.5 * self.height
        self.bottom = -0.5 * self.height
        self.right_edge = 0.5 * self.width
        self.left_edge = -0.5 * self.width


class ContinualBallUpdate(ContinualAnimation):
    def __init__(self, ball, box):
        self.ball = ball
        self.box = box
        ContinualAnimation.__init__(self, ball)

    def update_mobject(self, dt):
        self.ball.acceleration = np.array((0, -5, 0))
        self.ball.velocity = self.ball.velocity + self.ball.acceleration * dt
        self.ball.shift(self.ball.velocity * dt)  # Bounce off ground and roof
        if self.ball.get_bottom() <= self.box.bottom or \
                self.ball.get_top() >= self.box.top:
            self.ball.velocity[1] = -self.ball.velocity[1]

        # Bounce off walls
        if self.ball.get_left_edge() <= self.box.left_edge or \
                self.ball.get_right_edge() >= self.box.right_edge:
            self.ball.velocity[0] = -self.ball.velocity[0]


class Bouncing_Ball(Scene):
    def construct(self):

        self.box = Box()

        ball = Ball()

        self.play(FadeIn(self.box))
        self.play(FadeIn(ball))
        self.ball = ball

        self.add(ContinualBallUpdate(ball, self.box))
        text1 = TextMobject("This is a bouncing ball")
        text2 = TextMobject("Enjoy watching!")
        self.wait(1)
        self.play(FadeIn(text1))

        self.wait(2)
        self.play(Transform(text1, text2))

        self.wait(10)