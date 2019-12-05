
from manimlib.imports import *
from once_useful_constructs.combinatorics import *

nb_levels = 5

dev_x_step = 2
dev_y_step = 5

GRADE_COLOR_1 = RED
GRADE_COLOR_2 = BLUE



def graded_square(n,k):
    return Square(
        side_length = 1, 
        fill_color = graded_color(n,k), 
        fill_opacity = 1, 
        stroke_width = 1
    )

def graded_binomial(n,k):
    return Integer(
        choose(n,k), 
        color = graded_color(n,k)
    )

def split_square(n,k):
    width = 1
    height = 1

    proportion = float(choose(n,k)) / 2**n
    
    lower_height = proportion * height
    upper_height = (1 - proportion) * height
    lower_rect = Rectangle(
        width = width,
        height = lower_height,
        fill_color = RED,
        fill_opacity = 1.0,
        stroke_color = WHITE,
        stroke_width = 3
    )
    upper_rect = Rectangle(
        width = width,
        height = upper_height,
        fill_color = BLUE,
        fill_opacity = 1.0,
        stroke_color = WHITE,
        stroke_width = 3
    )
    upper_rect.next_to(lower_rect,UP,buff = 0)
    square = VGroup(lower_rect, upper_rect).move_to(ORIGIN)
    return square


class BuildNewPascalRow(Transform):

    def __init__(self,mobject, duplicate_row = None, **kwargs):
        if mobject.__class__ != GeneralizedPascalsTriangle and mobject.__class__ != PascalsTriangle:
            raise("Transform BuildNewPascalRow only works on members of (Generalized)PascalsTriangle!")

        n = mobject.nrows - 1
        lowest_row_copy1 = mobject.get_lowest_row()
        lowest_row_copy2 = duplicate_row

        start_mob = VGroup(lowest_row_copy1, lowest_row_copy2)

        new_pt = mobject.copy()
        new_pt.nrows += 1
        new_pt.generate_points()
        # align with original (copy got centered on screen)
        c1 = new_pt.coords_to_mobs[0][0].get_center()
        c2 = mobject.coords_to_mobs[0][0].get_center()
        print(c1, c2)
        v = c2 - c1
        new_pt.shift(v)

        new_row_left_copy = VGroup(*[
            new_pt.coords_to_mobs[n+1][k]
            for k in range(0,n+1)
        ])

        new_row_right_copy = VGroup(*[
            new_pt.coords_to_mobs[n+1][k]
            for k in range(1,n+2)
        ]).copy()

        target_mob = VGroup(new_row_left_copy, new_row_right_copy)

        Transform.__init__(self, start_mob, target_mob, **kwargs)

        



class SimplePascal(Scene):

    def build_new_pascal_row(self,old_pt):

        lowest_row_copy = old_pt.get_lowest_row().copy()
        self.add(lowest_row_copy)

        n = old_pt.nrows - 1
        lowest_row_copy1 = old_pt.get_lowest_row()
        lowest_row_copy2 = lowest_row_copy1.copy()


        start_mob = VGroup(lowest_row_copy1, lowest_row_copy2)
        self.add(start_mob)

        new_pt = old_pt.copy()
        cell_height = old_pt.height / old_pt.nrows
        cell_width = old_pt.width / old_pt.nrows
        new_pt.nrows += 1
        new_pt.height = new_pt.nrows * cell_height
        new_pt.width = new_pt.nrows * cell_width

        new_pt.generate_points()
        # align with original (copy got centered on screen)
        c1 = new_pt.coords_to_mobs[0][0].get_center()
        c2 = old_pt.coords_to_mobs[0][0].get_center()
        v = c2 - c1
        new_pt.shift(v)

        new_row_left_copy = VGroup(*[
            new_pt.coords_to_mobs[n+1][k]
            for k in range(0,n+1)
        ])

        new_row_right_copy = VGroup(*[
            new_pt.coords_to_mobs[n+1][k]
            for k in range(1,n+2)
        ]).copy()

        target_mob = VGroup(new_row_left_copy, new_row_right_copy)
        self.play(Transform(start_mob, target_mob))

        return new_pt



    def construct(self):

        cell_height = 1
        cell_width = 1
        nrows = 1
        pt = GeneralizedPascalsTriangle(
            nrows = nrows, 
            height = nrows * cell_height, 
            width = nrows * cell_width, 
            submob_class = graded_square,
            portion_to_fill = 0.9
        )
        pt.shift(3 * UP)
        self.add(pt)
        lowest_row_copy = pt.get_lowest_row().copy()
        self.add(lowest_row_copy)
        #self.play(BuildNewPascalRow(pt, duplicate_row = lowest_row_copy))
        for i in range(7):
            pt = self.build_new_pascal_row(pt)
        




class PascalNetScene(Scene):

    def construct(self):

        unit_width = 0.25
        top_height = 4.0
        level_height = 2.0 * top_height / nb_levels

        start_points = np.array([top_height * UP])

        dev_start = start_points[0]

        j = 0

        for n in range(nb_levels):

            half_width = 0.5 * (n + 0.5) * unit_width

            stop_points_left = start_points.copy()
            stop_points_left[:,0] -= 0.5 * unit_width
            stop_points_left[:,1] -= level_height

            stop_points_right = start_points.copy()
            stop_points_right[:,0] += 0.5 * unit_width
            stop_points_right[:,1] -= level_height
            
            for (p,q) in zip(start_points,stop_points_left):
                alpha = np.abs((p[0]+q[0])/2) / half_width
                color = rainbow_color(alpha)
                line = Line(p,q, stroke_color = color)
                self.add(line)

            for (i,(p,q)) in enumerate(zip(start_points,stop_points_right)):
                alpha = np.abs((p[0]+q[0])/2) / half_width
                color = rainbow_color(alpha)
                line = Line(p,q, stroke_color = color)
                self.add(line)

            if (n + 1) % dev_y_step == 0 and n != 1:
                j += dev_x_step
                dev_stop = stop_points_left[j]
                line = Line(dev_start,dev_stop,stroke_color = WHITE)
                self.add(line)
                dot = Dot(dev_stop, fill_color = WHITE)
                self.add_foreground_mobject(dot)
                dev_start = dev_stop

            start_points = np.append(stop_points_left,[stop_points_right[-1]], axis = 0)


        self.wait()



class RescaledPascalNetScene(Scene):

    def construct(self):

        half_width = 3.0
        top_height = 4.0
        level_height = 2.0 * top_height / nb_levels

        start_points = np.array([top_height * UP])
        left_edge = top_height * UP + half_width * LEFT
        right_edge = top_height * UP + half_width * RIGHT

        dev_start = start_points[0]

        j = 0

        for n in range(nb_levels):

            if n == 0:
                start_points_left_shift = np.array([left_edge])
            else:
                start_points_left_shift = start_points[:-1]
                start_points_left_shift = np.insert(start_points_left_shift,0,left_edge, axis = 0)
            stop_points_left = 0.5 * (start_points + start_points_left_shift)
            stop_points_left += level_height * DOWN

            
            if n == 0:
                start_points_right_shift = np.array([right_edge])
            else:
                start_points_right_shift = start_points[1:]
                start_points_right_shift = np.append(start_points_right_shift,np.array([right_edge]), axis = 0)
            stop_points_right = 0.5 * (start_points + start_points_right_shift)
            stop_points_right += level_height * DOWN

            
            for (i,(p,q)) in enumerate(zip(start_points,stop_points_left)):
                
                color = LIGHT_GRAY 

                if n % 2 == 0 and i <= n/2:
                    m = n/2 + 0.25
                    jj = i
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)

                elif n % 2 == 0 and i > n/2:
                    m = n/2 + 0.25
                    jj = n - i + 0.5
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)

                elif n % 2 == 1 and i <= n/2:
                    m = n/2 + 0.75
                    jj = i
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)

                elif n % 2 == 1 and i > n/2:
                    m = n/2 + 0.75
                    jj = n - i + 0.5
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)

                line = Line(p,q, stroke_color = color)
                self.add(line)

            for (i,(p,q)) in enumerate(zip(start_points,stop_points_right)):
                
                color = LIGHT_GRAY

                if n % 2 == 0 and i < n/2:
                    m = n/2 + 0.25
                    jj = i + 0.5
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)

                elif n % 2 == 0 and i >= n/2:
                    m = n/2 + 0.25
                    jj = n - i
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)

                elif n % 2 == 1 and i <= n/2:
                    m = n/2 + 0.75
                    jj = i + 0.5
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)

                elif n % 2 == 1 and i > n/2:
                    m = n/2 + 0.75
                    jj = n - i
                    alpha = 1 - float(jj)/m
                    color = rainbow_color(alpha)


                line = Line(p,q, stroke_color = color)
                self.add(line)

            if (n + 1) % dev_y_step == 0 and n != 1:
                j += dev_x_step
                dev_stop = stop_points_left[j]
                line = Line(dev_start,dev_stop,stroke_color = WHITE)
                self.add(line)
                dot = Dot(dev_stop, fill_color = WHITE)
                self.add_foreground_mobject(dot)
                dev_start = dev_stop



            start_points = np.append(stop_points_left,[stop_points_right[-1]], axis = 0)
            
            left_edge += level_height * DOWN
            right_edge += level_height * DOWN


        self.wait()









