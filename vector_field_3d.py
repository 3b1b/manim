from big_ol_pile_of_manim_imports import *
import math

class ExampleThreeD(ThreeDScene):
    CONFIG = {"plane_kwargs" : { "color" : RED_B },
              "point_charge_loc" : 0.5*RIGHT-1.5*UP,
    }

    def construct(self):
        plane = NumberPlane(**self.plane_kwargs)
        plane.main_lines.fade(.9)
        plane.add(plane.get_axis_labels())
        field2D = VGroup(*[self.calc_field2D(x*RIGHT+y*UP)
            for x in np.arange(-9,9,1)
            for y in np.arange(-5,5,1)
        ])

        # animations
        '''
        keyword arguments for set_camera_position() are phi, theta, distance, center_x, center_y, and center_z. 
        https://commons.wikimedia.org/wiki/File:3D_Spherical_2.svg#/media/File:3D_Spherical_2.svg
       
        The point that the camera is pointing towards is given by center_x, center_y, center_z.
        The other three arguments correspond to phi, \theta, and r in the figure below. 
        Notice that the center point corresponds to the origin of the graph, with the camera located at the 'x', looking back towards the origin.
        This is why phi = 0 and \theta = -pi/2 corresponds to the normal 2D orientation with the x-axis pointing right and the y-axis pointing up on the screen. 
        If you set \theta = pi/2 we flip the screen over.
        '''
        self.set_camera_position(0, -np.pi/2, center_x = 5, center_y = 5, center_z = 1)
        self.wait(1)
        self.move_camera(0.8*np.pi/2, -0.45*np.pi)
        self.play(ShowCreation(plane))
        self.play(ShowCreation(field2D))
        self.wait()
        self.begin_ambient_camera_rotation()
        self.wait(6)

    def calc_field2D(self,point):
        x,y = point[:2]
        Rx,Ry = self.point_charge_loc[:2]
        r = math.sqrt((x-Rx)**2 + (y-Ry)**2)
        efield = (point - self.point_charge_loc)/r**3
        return Vector(efield).shift(point)

class EFieldInThreeD(ThreeDScene):
    CONFIG = {"plane_kwargs" : {"color" : RED_B},
              "point_charge_loc" : 0.5*RIGHT-1.5*UP,
        }
    '''
    def calc_field2D(self,point):
        x,y = point[:2]
        # Rx,Ry = self.point_charge_loc[:2]
        # r = math.sqrt((x-Rx)**2 + (y-Ry)**2)
        # efield = (point - self.point_charge_loc)/r**3
        efield = np.array((-y,x,0))/math.sqrt(x**2+y**2)
        return Vector(efield).shift(point)
    '''
    def calc_field3D(self,point):
        x,y,z = point
        # Rx,Ry,Rz = self.point_charge_loc
        # r = math.sqrt((x-Rx)**2 + (y-Ry)**2+(z-Rz)**2)
        # efield = (point - self.point_charge_loc)/r**3
        efield = np.array((-y,x,z))/math.sqrt(x**2+y**2+z**2)
        #efield = np.array((-y,x,z))/math.sqrt(x**2+y**2+z**2)
        return Vector(efield).shift(point)

    def construct(self):
        self.set_camera_position(0.1, -np.pi/2, 8)
        plane = NumberPlane(**self.plane_kwargs)
        plane.main_lines.fade(.9)
        plane.add(plane.get_axis_labels())
        self.add(plane)
        '''
        field2D = VGroup(*[self.calc_field2D(x*RIGHT+y*UP)
            for x in np.arange(-9,9,2)
            for y in np.arange(-5,5,2)
            ])
        '''

        field3D = VGroup(*[self.calc_field3D(x*RIGHT+y*UP+z*OUT)
            for x in np.arange(-9,9,2)
            for y in np.arange(-5,5,2)
            for z in np.arange(-5,5,2)])



        self.play(ShowCreation(field3D))
        self.wait()
        self.move_camera(0.8*np.pi/2, -0.45*np.pi)
        self.begin_ambient_camera_rotation()
        self.wait(6)