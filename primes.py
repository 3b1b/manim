from helpers import *
from mobject import Mobject
from mobject.vectorized_mobject import *
from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from scene import Scene
from camera import *
from topics.number_line import *
from topics.three_dimensions import *
from topics.light import *
from topics.characters import *
from topics.numerals import *

def is_prime(n):

    for i in primes(n**0.5):
        if n % i == 0:
            return False

    return True

def primes(max_n):

    if max_n < 2:
        return []

    numbers = range(2, int(max_n) + 1)
    p = []

    while len(numbers) > 0:
        q = numbers[0]
        p.append(q)
        numbers = [x for x in numbers if x % q != 0]

    return p

def prime_factors(n):

    if is_prime(n):
        return [n]

    i = 0
    primes_list = primes(n/2)

    factors = []
    r = n

    while r >= 2:
        p = primes_list[i]
        if r % p == 0:
            factors.append(p)
            r = r/p
        else:
            i += 1

    return factors


RUN_TIME = 0.5
DOWN_SHIFT = 0.0 * DOWN

class Primes(Scene):

    def construct(self):
        
        N = 100

        primes_list = np.array(primes(N))

        palette = ["#FBA125", "#76CD42", "#30CCF5", "#9377C4", "#F95137", 
        #                 2         3       5            7      11
                  "#1B442E", TEAL_E, MAROON_A, DARK_BROWN, PINK,
        #            13        17      19        23         29
                  "#9C25FB", GREEN_E, MAROON_E, GOLD_E, GREEN_E,
        #            31      37       41       43      47 # last prime to occur in a factorization
                  LIGHT_BROWN, DARK_BLUE, GREY_BROWN, GREEN_C, BLUE_C,
        #            53           59           61        67      71
                  PURPLE_C, RED_C, YELLOW_E, TEAL_C, MAROON_C]
        #            73      79      83        89       97

        nb_primes = len(primes_list)
        print nb_primes

        prime_points_radius = 3.2
        angles = np.arange(TAU/4, -3*TAU/4, -TAU/float(nb_primes))
        print len(angles), angles
        prime_points = [prime_points_radius * (np.cos(theta) * RIGHT
                         + np.sin(theta) * UP)
                            for theta in angles]
        print len(prime_points)

        wheel = Wheel()
        
        angles = [TAU]
        colors = [LIGHT_GREY]

        wheel.update_sectors(angles, colors)
        wheel.rotate(-TAU/4).shift(DOWN_SHIFT)
        self.add(wheel)

        number = DecimalNumber(1, num_decimal_points = 0).scale(2).shift(DOWN_SHIFT)
        self.add(number)
        self.wait(RUN_TIME)

        j = 0

        for i in range(2,N+1):

            factors = prime_factors(i)
            factor_indices = [np.where(primes_list == x)[0][0] for x in factors]

            nb_sectors = float(len(factor_indices))
            new_angles = np.ones(nb_sectors) / nb_sectors * TAU

            new_colors = []
            for index in factor_indices:
                new_colors.append(palette[index])
        
            self.play(
                UpdateAngles(wheel, new_angles = new_angles, new_colors = new_colors,
                    run_time = RUN_TIME),
                ChangeDecimalToValue(number, i, run_time = RUN_TIME)
            )
            self.wait(RUN_TIME)

            if is_prime(i):
                full_wheel = VGroup(wheel,number).copy()
                full_wheel_copy = full_wheel.copy()
                full_wheel_copy.scale(0.15).move_to(prime_points[j])
                print j
                j += 1
                self.play(
                    Transform(full_wheel, full_wheel_copy)
                )




class Wheel(VMobject):

    CONFIG = {
        "inner_radius" : 1.2,
        "outer_radius" : 2.4,
        "nb_sectors" : 25,
        "colors" : [BLACK] * 25
    }

    def generate_points(self):

        angle = TAU/self.nb_sectors
        angle_range = np.arange(0,TAU,angle)
        for j in range(self.nb_sectors - len(angle_range)):
            angle_range = np.append(angle_range, TAU)
            self.colors.append(BLACK)

        for (i,theta) in enumerate(angle_range):
            if theta != TAU:
                use_angle = angle
            else:
                use_angle = 0
            sector = AnnularSector(
                inner_radius = self.inner_radius,
                outer_radius = self.outer_radius,
                angle = use_angle,
                start_angle = theta,
                fill_color = self.colors[i],
                fill_opacity = 1,
                stroke_color = WHITE,
                stroke_width = 5
            ).rotate_about_origin(TAU/2, axis = UP).shift(DOWN_SHIFT)
            self.add(sector)

    def update_sectors(self, new_angles, new_colors):

        if len(new_angles) > self.nb_sectors:
            raise "More angles than sectors!"
        
        for i in range(len(new_angles), self.nb_sectors):
            new_angles = np.append(new_angles, 0)
            new_colors.append(BLACK)

        self.colors = new_colors

        new_start_angles = -np.cumsum(new_angles) + new_angles

        for (i,sector) in enumerate(self.submobjects):
            sector.angle = new_angles[i]
            sector.start_angle = new_start_angles[i]
            sector.set_fill(color = new_colors[i])
            sector.generate_points()
            sector.rotate_about_origin(TAU/2, axis = UP).shift(DOWN_SHIFT)





class UpdateAngles(Animation):

    def __init__(self,mobject,**kwargs):

        self.old_angles = []
        for (i, sector) in enumerate(mobject.submobjects):
            self.old_angles.append(sector.angle)

        self.old_angles = np.array(self.old_angles)
        self.old_start_angles = np.cumsum(self.old_angles) - self.old_angles + TAU/4
        
        digest_config(self, kwargs)
        Animation.__init__(self,mobject,**kwargs)

    def update_submobject(self, submobject, starting_submobject, alpha):

        i = 0
        for submob in self.mobject.submobjects:
            if submobject == submob:
                break
            else:
                i += 1

        for j in range(len(self.new_angles), self.mobject.nb_sectors):

            self.new_angles = np.append(self.new_angles, 0)
            self.new_colors.append(BLACK)

        self.new_start_angles = np.cumsum(self.new_angles) - self.new_angles + TAU/4
        # this should be in __init__!
        # but has no effect there

        submobject.angle = interpolate(
            self.old_angles[i], self.new_angles[i], alpha
        )
        submobject.start_angle = interpolate(
            self.old_start_angles[i],
            self.new_start_angles[i], alpha
        )


        interpolated_color = interpolate_color(
            self.mobject.colors[i],
            self.new_colors[i],
            alpha
        )

        submobject.set_fill(color = interpolated_color)
        submobject.generate_points()
        submobject.rotate_about_origin(TAU/2, axis = UP).shift(DOWN_SHIFT)

        if alpha > 0.95:
            self.mobject.colors[i] = self.new_colors[i]














