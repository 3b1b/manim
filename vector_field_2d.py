from big_ol_pile_of_manim_imports import *
import math

class DrawAnAxis(Scene):
    CONFIG = { "plane_kwargs" : { "x_line_frequency" : 1, "y_line_frequency" :1 }}
    
    def construct(self):
        my_plane = NumberPlane(**self.plane_kwargs)
        my_plane.add(my_plane.get_axis_labels())

        self.play(ShowCreation(my_plane))
        self.wait(2)

class SimpleField(Scene):
    CONFIG = {"plane_kwargs" : {"color" : RED} }

    def construct(self):
        plane = NumberPlane(**self.plane_kwargs) #Create axes and grid
        plane.add(plane.get_axis_labels())  #add x and y label
        self.play(ShowCreation(plane))  #Place grid on screen

        points = [x*RIGHT+y*UP  # RIGHT=np.array(1,0,0) and UP=np.array(0,1,0)
            for x in np.arange(-5,5,1)
            for y in np.arange(-5,5,1)
            ]     #List of vectors pointing to each grid point
        print(points)

        vec_field = []  #Empty list to use in for loop
        for point in points:
            field = 0.5*RIGHT + 0.5*UP   #Constant field up and to right
            result = Vector(field).shift(point)   #Create vector and shift it to grid point
            vec_field.append(result)   #Append to list
            #self.add(VGroup(vec_field))
            #self.wait(1)

        draw_field = VGroup(*vec_field)   #Pass list of vectors to create a VGroup
        self.play(ShowCreation(draw_field)) #Draw VGroup on screen


class FieldWithAxes(Scene):
    CONFIG = {"plane_kwargs" : {"color" : RED_B}, "point_charge_loc" : 0.5*RIGHT-1.5*UP}  # RIGHT=np.array(1,0,0) and UP=np.array(0,1,0)

    def calc_field(self,point):
        '''
        Calculates the field at a single point.
        '''
        # [:2] because the original array (RIGHT, UP) is 3D, and we only need two dimensional components
        x,y = point[:2];                                  print("xy: {}".format((x,y)))
        # Rx,Ry = self.point_charge_loc[:2];                print("RxRy: {}".format((Rx,Ry)))
        # r = math.sqrt((x-Rx)**2 + (y-Ry)**2);             print("r: {}".format(r))
        # efield = (point - self.point_charge_loc)/r**3   ; print("EField = {}".format(efield))
        efield = np.array((-y,x,0))/math.sqrt(x**2+y**2)  #Try one of these two fields
        # efield = np.array(( -2*(y%2)+1 , -2*(x%2)+1 , 0 ))/3  #Try one of these two fields
        return Vector(efield).shift(point)

    def construct(self):
        plane = NumberPlane(**self.plane_kwargs)
        plane.main_lines.fade(.9)
        plane.add(plane.get_axis_labels())
        self.play(ShowCreation(plane))

        field = VGroup(*[self.calc_field(x*RIGHT+y*UP)
            for x in np.arange(-9,9,1)
            for y in np.arange(-5,5,1)
            ])

        self.play(ShowCreation(field))




"""
class NumberPlane(VMobject):
    CONFIG = {
        "color": BLUE_D,
        "secondary_color": BLUE_E,
        "axes_color": WHITE,
        "secondary_stroke_width": 1,
        "x_radius": None,
        "y_radius": None,
        "x_unit_size": 1,
        "y_unit_size": 1,
        "center_point": ORIGIN,
        "x_line_frequency": 1, #cg=hange spacing of gridlines in x dir
        "y_line_frequency": 1, #cg=hange spacing of gridlines in y dir
        "secondary_line_ratio": 1,
        "written_coordinate_height": 0.2,
        "propagate_style_to_family": False,
        "make_smooth_after_applying_functions": True,
    }


class DrawAnAxis(Scene):
    CONFIG = { "plane_kwargs":{"x_line_frequency" : 2,  "y_line_frequency" :2} }
 
    def construct(self):
        my_plane = NumberPlane(**self.plane_kwargs)
        my_plane.add(my_plane.get_axis_labels())
        self.add(my_plane)
        self.wait(5)
"""