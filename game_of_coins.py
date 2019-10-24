import random
from manimlib.imports import *
from manimlib.mobject.three_dimensions import Cube, Prism
from manimlib.mobject.types.vectorized_mobject import VMobject
from math import sqrt



class Coin(VGroup):
    CONFIG = {
        "fill_opacity": 0.45,
        "fill_color": YELLOW_D,
        "stroke_width": 0.7,
        "side_length": 2,
    }
    def generate_points(self):
        for ln in np.arange(0, 0.5, 0.1):
            face = Circle(
                radius=1,
                shade_in_3d=True,
                color = YELLOW_D,
            )
            face.flip()
            face.shift( ln*OUT / 2.0)
            face.apply_matrix(z_to_vector(OUT))
            self.add(face)

class Ellipsoid(ParametricSurface):
    CONFIG = {
        "resolution": (12, 24),
        "radius": 1,
        "u_min": 0.001,
        "u_max": PI - 0.001,
        "v_min": 0,
        "v_max": TAU,
        "fill_color": RED_C,
    }

    def __init__(self, **kwargs):
        ParametricSurface.__init__(
            self, self.func, **kwargs
        )
        self.scale(self.radius)

    def func(self, u, v):
        return np.array([
            np.cos(u),
            0.6*np.cos(v) * np.sin(u),
            0.6*np.sin(v) * np.sin(u),
        ])

class RocketBody(ParametricSurface):
    CONFIG = {
        "resolution": (12, 24),
        "radius": 1,
        "u_min": 0.01,
        "u_max": PI,
        "v_min": 0,
        "v_max": TAU,
        "height":2,
    }

    def __init__(self, **kwargs):
        ParametricSurface.__init__(
            self, self.func, **kwargs
        )
        self.scale(self.radius)

    def func(self, u, v):
        # print("TAU", TAU)
        
        if(u<PI/2):
            return np.array([
                0.6*np.cos(v) * np.sin(u),
                0.6*np.sin(v) * np.sin(u),
                np.cos(u),
            ])
        
        else:
            return np.array([
                0.6*np.cos(v) * np.sin(u),
                0.6*np.sin(v) * np.sin(u),
                1.5*np.cos(u),
            ])

class RocketBase(ParametricSurface):
    CONFIG = {
        "resolution": (12, 24),
        "radius": 1,
        "u_min": (PI/2)-0.5,
        "u_max": PI/2+0.2,
        "v_min": 0,
        "v_max": TAU,
        "fill_opacity": 0.9,
        "fill_color": BLUE_D,
        
    }

    def __init__(self, **kwargs):
        ParametricSurface.__init__(
            self, self.func, **kwargs
        )
        self.scale(self.radius)

    def func(self, u, v):
        # print("TAU", TAU)
        if(u<PI/2):
            return np.array([
                0.8*np.cos(v) * np.sin(u),
                0.8*np.sin(v) * np.sin(u),
                np.cos(u),
            ])
        elif(u>(PI/2-0.1)):
            return np.array([
                0.8*np.cos(v) * np.sin(u),
                0.8*np.sin(v) * np.sin(u),
                0.1*np.cos(u),
            ])
        else:
            return np.array([
                0.8*np.cos(v) * np.sin(u),
                0.8*np.sin(v) * np.sin(u),
                *np.cos(u),
            ])
'''
class CuemathRocket(VGroup):
    CONFIG = {
        "fill_opacity": 0.9,
        "fill_color": BLUE_D,
        "stroke_width": 0,
        "label": "A",
    }
    def generate_points(self):
        body2 = RocketBody()
        body2.flip()
        body2.scale(1)
        self.add(body2)

'''
class Observer(VGroup):
    CONFIG = {
        "fill_opacity": 0.45,
        "fill_color": BLUE_D,
        "stroke_width": 0,
        "side_length": 2,
        "label": "A",
    }
    def generate_points(self):
        face = Sphere(
                radius=1,
                shade_in_3d=True,
                color = PURPLE_E,
            )
        face.flip()
        face.scale(0.5)
        face.shift(1.5*LEFT)
        body = Ellipsoid()
        body.flip()
        body.scale(1)
        body.add(face)
        hand1 = Ellipsoid()
        hand1.scale(0.3)
        hand1.shift(-0.8*RIGHT+0.6*UP)
        #hand1.apply_matrix(np.matrix([[1.0, 0, 0.0], [0, 1.0, 0.0], [0.0, 1.0, 0.6]])*np.cos(PI/3))
        body.add(hand1)
        hand2 = Ellipsoid()
        hand2.scale(0.3)
        hand2.shift(-0.8*RIGHT-0.6*UP)
        #hand2.apply_matrix(np.matrix([[0.0, 0, 1.0], [0, 1.0, 0.0], [0.0, 1.0, 0.6]])*np.sin(PI/6))
        body.add(hand2)
        body.apply_matrix(z_to_vector(TOP))
        self.add(body)


class TestScene2(ThreeDScene):
    CONFIG = {
    "plane_kwargs" : {
    "color" : RED_B
        },
    "point_charge_loc" : 0.5*RIGHT-1.5*UP,
    }
    def construct(self):
        self.coin_size = 0.25
        # my_plane = NumberPlane(**self.plane_kwargs)
        # my_plane.add(my_plane.get_axis_labels())
        # self.add(my_plane)
        self.set_camera_orientation(0.1, -np.pi/2)
        self.move_camera(0.8*np.pi/2, -0.45*np.pi)        
        # rocket = CuemathRocket()
        base = RocketBase()
        # base.shift(LEFT)
        # rocket.add(base)
        self.play(ShowCreation(base))
        self.wait(1)
        self.move_camera(-0.8*np.pi/2, -0.45*np.pi)        
        self.wait(2)

#this is test class  for first scene        
class rule(ThreeDScene):
    CONFIG = {
        "color" : RED_B,
        "fill_color" : RED_B
        }
        
    def construct(self):
        self.coin_size = 0.25
        # my_plane = NumberPlane(**self.plane_kwargs)
        # my_plane.add(my_plane.get_axis_labels())
        # self.add(my_plane)
        # self.set_camera_orientation(0.1, -np.pi/2)
        table = Circle(color=RED_B, fill_color = RED_B )
        table.scale(3.80)
        
        obs = Observer()
        obs.shift( UP + 2* TOP - 0.5*LEFT )
        obs2 = Observer(fill_color = YELLOW_D)
        obs2.shift( DOWN + 2*BOTTOM - 0.5*LEFT )
        obs_label=TextMobject("A")
        obs_label.next_to(obs, LEFT)
        self.add(obs)
        self.add(obs2)        
        self.add(table)
        for i in range(1,4):
            if i%2==0:
                self.move_camera(0.8*np.pi/2, -0.45*np.pi)
                
            else:   
                self.move_camera(0.8*np.pi/2, 0.45*np.pi)
        #point_list = self.get_pts_on_tables
        self.move_camera(0.1, -np.pi/2)


class endtest(ThreeDScene):
    CONFIG = {
    "plane_kwargs" : {
    "color" : RED_B
        },
    "point_charge_loc" : 0.5*RIGHT-1.5*UP,
    }
    import math

    '''def rotate_via_numpy(self, xy, radians):
    """Use numpy to build a rotation matrix and take the dot product."""
        x, y = xy
        c, s = np.cos(radians), np.sin(radians)
        j = np.matrix([[c, s], [-s, c]])
        m = np.dot(j, [x, y])

        return float(m.T[0]), float(m.T[1])'''
    def translate_D(self, old_pt,vec, mag):
        pt = old_pt + mag*vec
        return pt

    def calculate_D(self,D,angle):
        qx = D*math.cos(angle);
        qy = D*math.sin(angle);
        return (qx, qy, 0)
    def get_ordered_list(self,points):
        points.sort(key = lambda p: sqrt((p[0] )**2 + (p[1])**2))
        return points

    def get_pts_on_table(self):
        r = 0.25
        R = 3.80
        n_l = math.floor((1/2)*((R/r)+1))
        origin = np.array([0, 0, 0])
        list_pts = []
        old_vec = np.matrix([[1, 0, 0]])
        for layer in range(1, n_l):
            last_pt = np.array(self.translate_D(origin, old_vec , layer*2*r))
            # old_theta = 0
            theta = 2*np.pi/3 
            for k in range(1, 7):
                rotation_matr = np.matrix([[np.cos(theta), -np.sin(theta), 0],
                                            [np.sin(theta), np.cos(theta), 0], 
                                            [0, 0, 1],
                                        ])
                new_vec = np.dot(old_vec, rotation_matr)
                theta = np.pi/3
                # print(theta, old_vec, new_vec)
                for i in range(layer):
                    pt_to_append = list(last_pt[0])
                    #print(pt_to_append)
                    list_pts.append(pt_to_append)
                    pt = np.array(self.translate_D(last_pt, new_vec, 2*r))
                    last_pt = pt
                old_vec = new_vec
        # print(list_pts)
        new_D = (n_l-1)*2*r 
        theta_new = np.pi/6;
        change = np.pi/3
        for i in range(1,7):
            list_pts.append(self.calculate_D(new_D,theta_new))
            theta_new = theta_new+change
        origin_l = [0,0,0]
        list_pts.append(origin_l)  
        return(self.get_ordered_list(list_pts))
            
    

    def construct(self):
        self.coin_size = 0.25
        # my_plane = NumberPlane(**self.plane_kwargs)
        # my_plane.add(my_plane.get_axis_labels())
        # self.add(my_plane)
        # self.set_camera_orientation(0.1, -np.pi/2)
        table = Circle(color=RED_B, fill_color = RED_B )
        table.scale(3.80)
        #my_first_text=TextMobject("Writing with manim is fun")
        #second_line=TextMobject("and easy to do!")
        #second_line.next_to(my_first_text,DOWN)
        #third_line=TextMobject("for me and you!")
        #third_line.next_to(my_first_text,DOWN)
        obs = Observer()
        #print("values of direction",UP ,TOP ,LEFT)
        #print("hellworld", UP + 1.5* TOP - 0.5*LEFT)
        obs.shift( UP + 2* TOP - 0.5*LEFT )
        obs2 = Observer(fill_color = YELLOW_D)
        obs2.shift( DOWN + 2*BOTTOM - 0.5*LEFT )
        obs_label=TextMobject("A")
        obs_label.next_to(obs, LEFT)
        
        self.add(obs)
        self.add(obs2)        
        self.add(table)
        #point_list = self.get_pts_on_tables
        point_list = self.get_pts_on_table()
        #random.shuffle(point_list)
        reversed(point_list)
        '''for idx, point in enumerate(point_list[]):
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            total_vect=point
            print("total_vect", total_vect)
            coin.shift(total_vect)
            self.play(GrowFromCenter(coin));'''        
        self.wait(2)
        self.remove(obs)
        self.move_camera(0.1, -np.pi/2)
        for idx, i in enumerate(point_list[::-1]):
            print("Loop2", i)
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                #self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                #self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            coin.shift(i);
            self.play(GrowFromCenter(coin));
        #self.add(my_first_text, second_line)
        self.wait(2)
        self.wait(2)
        #self.play(Transform(second_line,third_line))
        

class TestScene(ThreeDScene):
    CONFIG = {
    "plane_kwargs" : {
    "color" : RED_B
        },
    "point_charge_loc" : 0.5*RIGHT-1.5*UP,
    }
    import math

    '''def rotate_via_numpy(self, xy, radians):
    """Use numpy to build a rotation matrix and take the dot product."""
        x, y = xy
        c, s = np.cos(radians), np.sin(radians)
        j = np.matrix([[c, s], [-s, c]])
        m = np.dot(j, [x, y])

        return float(m.T[0]), float(m.T[1])'''
    def translate_D(self, old_pt,vec, mag):
        pt = old_pt + mag*vec
        return pt

    def calculate_D(self,D,angle):
        qx = D*math.cos(angle);
        qy = D*math.sin(angle);
        return (qx, qy, 0)
    def get_ordered_list(self,points):
        points.sort(key = lambda p: sqrt((p[0] )**2 + (p[1])**2))
        return points

    def get_pts_on_table(self):
        r = 0.25
        R = 3.80
        n_l = math.floor((1/2)*((R/r)+1))
        origin = np.array([0, 0, 0])
        list_pts = []
        old_vec = np.matrix([[1, 0, 0]])
        for layer in range(1, n_l):
            last_pt = np.array(self.translate_D(origin, old_vec , layer*2*r))
            # old_theta = 0
            theta = 2*np.pi/3 
            for k in range(1, 7):
                rotation_matr = np.matrix([[np.cos(theta), -np.sin(theta), 0],
                                            [np.sin(theta), np.cos(theta), 0], 
                                            [0, 0, 1],
                                        ])
                new_vec = np.dot(old_vec, rotation_matr)
                #print("new_vec", new_vec)
                theta = np.pi/3
                # print(theta, old_vec, new_vec)
                for i in range(layer):
                    pt_to_append = list(last_pt[0])
                    #print(pt_to_append)
                    list_pts.append(pt_to_append)
                    pt = np.array(self.translate_D(last_pt, new_vec, 2*r))
                    last_pt = pt
                old_vec = new_vec
        # print(list_pts)
        new_D = (n_l-1)*2*r 
        theta_new = np.pi/6;
        change = np.pi/3
        for i in range(1,7):
            list_pts.append(self.calculate_D(new_D,theta_new))
            theta_new = theta_new+change
        origin_l = [0,0,0]
        list_pts.append(origin_l)  
        return(self.get_ordered_list(list_pts))
            
    

    def construct(self):
        self.coin_size = 0.25
        # my_plane = NumberPlane(**self.plane_kwargs)
        # my_plane.add(my_plane.get_axis_labels())
        # self.add(my_plane)
        # self.set_camera_orientation(0.1, -np.pi/2)
        table = Circle(color=RED_B, fill_color = RED_B )
        table.scale(3.80)
        '''my_first_text=TextMobject("Writing with manim is fun")
        second_line=TextMobject("and easy to do!")
        second_line.next_to(my_first_text,DOWN)
        third_line=TextMobject("for me and you!")
        third_line.next_to(my_first_text,DOWN)'''
        obs = Observer()
        #print("values of direction",UP ,TOP ,LEFT)
        #print("hellworld", UP + 1.5* TOP - 0.5*LEFT)
        obs.shift( UP + 2* TOP - 0.5*LEFT )
        obs2 = Observer(fill_color = YELLOW_D)
        obs2.shift( DOWN + 2*BOTTOM - 0.5*LEFT )
        obs_label=TextMobject("A")
        obs_label.next_to(obs, LEFT)
        
        self.add(obs)
        self.add(obs2)        
        self.add(table)
        #point_list = self.get_pts_on_tables
        point_list = self.get_pts_on_table()
        #random.shuffle(point_list)
        '''for idx, point in enumerate(point_list[:8]):
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            total_vect=point
            #print("total_vect", total_vect)
            coin.shift(total_vect)
            self.play(GrowFromCenter(coin)); '''       
        self.wait(2)
        self.remove(obs)
        self.move_camera(0.1, -np.pi/2)
        for idx, i in enumerate(point_list[:]):
            print("Loop2", i)
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                #self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                #self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            coin.shift(i);
            self.play(GrowFromCenter(coin));
        #self.add(my_first_text, second_line)
        self.wait(2)
        #self.play(Transform(second_line,third_line))
        #self.wait(2)
        #second_line.shift(3*DOWN)
        #self.play(ApplyMethod(my_first_text.shift,3*UP))

class rules(ThreeDScene):
    CONFIG = {
    "plane_kwargs" : {
    "color" : RED_B
        },
    "point_charge_loc" : 0.5*RIGHT-1.5*UP,
    }
    import math

    '''def rotate_via_numpy(self, xy, radians):
    """Use numpy to build a rotation matrix and take the dot product."""
        x, y = xy
        c, s = np.cos(radians), np.sin(radians)
        j = np.matrix([[c, s], [-s, c]])
        m = np.dot(j, [x, y])

        return float(m.T[0]), float(m.T[1])'''
    def translate_D(self, old_pt,vec, mag):
        pt = old_pt + mag*vec
        return pt

    def calculate_D(self,D,angle):
        qx = D*math.cos(angle);
        qy = D*math.sin(angle);
        return (qx, qy, 0)
    def get_ordered_list(self,points):
        points.sort(key = lambda p: sqrt((p[0] )**2 + (p[1])**2))
        return points

    def get_pts_on_table(self):
        r = 0.25
        R = 3.80
        n_l = math.floor((1/2)*((R/r)+1))
        origin = np.array([0, 0, 0])
        list_pts = []
        old_vec = np.matrix([[1, 0, 0]])
        for layer in range(1, n_l):
            last_pt = np.array(self.translate_D(origin, old_vec , layer*2*r))
            # old_theta = 0
            theta = 2*np.pi/3 
            for k in range(1, 7):
                rotation_matr = np.matrix([[np.cos(theta), -np.sin(theta), 0],
                                            [np.sin(theta), np.cos(theta), 0], 
                                            [0, 0, 1],
                                        ])
                new_vec = np.dot(old_vec, rotation_matr)
                #print("new_vec", new_vec)
                theta = np.pi/3
                # print(theta, old_vec, new_vec)
                for i in range(layer):
                    pt_to_append = list(last_pt[0])
                    #print(pt_to_append)
                    list_pts.append(pt_to_append)
                    pt = np.array(self.translate_D(last_pt, new_vec, 2*r))
                    last_pt = pt
                old_vec = new_vec
        # print(list_pts)
        new_D = (n_l-1)*2*r 
        theta_new = np.pi/6;
        change = np.pi/3
        for i in range(1,7):
            list_pts.append(self.calculate_D(new_D,theta_new))
            theta_new = theta_new+change
        origin_l = [0,0,0]
        list_pts.append(origin_l)  
        return(self.get_ordered_list(list_pts))
            
    

    def construct(self):
        self.coin_size = 0.25
        # my_plane = NumberPlane(**self.plane_kwargs)
        # my_plane.add(my_plane.get_axis_labels())
        # self.add(my_plane)
        # self.set_camera_orientation(0.1, -np.pi/2)
        table = Circle(color=RED_B, fill_color = RED_B )
        table.scale(3.80)
        '''my_first_text=TextMobject("Writing with manim is fun")
        second_line=TextMobject("and easy to do!")
        second_line.next_to(my_first_text,DOWN)
        third_line=TextMobject("for me and you!")
        third_line.next_to(my_first_text,DOWN)'''
        obs = Observer()
        #print("values of direction",UP ,TOP ,LEFT)
        #print("hellworld", UP + 1.5* TOP - 0.5*LEFT)
        obs.shift( UP + 2* TOP - 0.5*LEFT )
        obs2 = Observer(fill_color = YELLOW_D)
        obs2.shift( DOWN + 2*BOTTOM - 0.5*LEFT )
        obs_label=TextMobject("A")
        obs_label.next_to(obs, LEFT)
        
        self.add(obs)
        self.add(obs2)        
        self.add(table)
        #point_list = self.get_pts_on_tables
        point_list = self.get_pts_on_table()
        random.shuffle(point_list)
        for idx, point in enumerate(point_list[:8]):
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            total_vect=point
            #print("total_vect", total_vect)
            coin.shift(total_vect)
            self.play(GrowFromCenter(coin));        
        self.wait(2)
        self.remove(obs)
        self.move_camera(0.1, -np.pi/2)
        for idx, i in enumerate(point_list[8:]):
            print("Loop2", i)
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                #self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                #self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            coin.shift(i);
            self.play(GrowFromCenter(coin));
        #self.add(my_first_text, second_line)
        self.wait(2)
        #self.play(Transform(second_line,third_line))
        #self.wait(2)
        #second_line.shift(3*DOWN)
        #self.play(ApplyMethod(my_first_text.shift,3*UP))
        
class solution(ThreeDScene):
    CONFIG = {
    "plane_kwargs" : {
    "color" : RED_B
        },
    "point_charge_loc" : 0.5*RIGHT-1.5*UP,
    }
    import math
    import numpy as np

    def rotate_via_numpy(self, xy, radians):
        """Use numpy to build a rotation matrix and take the dot product."""
        x, y, z = xy
        c, s = np.cos(radians), np.sin(radians)
        j = np.matrix([[c, s,0], [-s, c,0]])
        m = np.dot(j, [x, y,z])
        return float(m.T[0]), float(m.T[1]), 0

    def translate_D(self, old_pt,vec, mag):
        pt = old_pt + mag*vec
        return pt

    def calculate_D(self,D,angle):
        qx = D*math.cos(angle);
        qy = D*math.sin(angle);
        return (qx, qy, 0)
    def get_ordered_list(self,points):
        points.sort(key = lambda p: sqrt((p[0] )**2 + (p[1])**2))
        return points

    def get_pts_on_table(self):
        r = 0.25
        R = 3.80
        n_l = math.floor((1/2)*((R/r)+1))
        origin = np.array([0, 0, 0])
        list_pts = []
        origin_l = [0,0,0]
        # list_pts.append(origin_l)  
        old_vec = np.matrix([[1, 0, 0]])
        for layer in range(1, n_l):
            last_pt = np.array(self.translate_D(origin, old_vec , layer*2*r))
            # old_theta = 0
            theta = 2*np.pi/3 
            for k in range(1, 7):
                rotation_matr = np.matrix([[np.cos(theta), -np.sin(theta), 0],
                                            [np.sin(theta), np.cos(theta), 0], 
                                            [0, 0, 1],
                                        ])
                new_vec = np.dot(old_vec, rotation_matr)
                #print("new_vec", new_vec)
                theta = np.pi/3
                # print(theta, old_vec, new_vec)
                for i in range(layer):
                    pt_to_append = list(last_pt[0])
                    #print(pt_to_append)
                    list_pts.append(pt_to_append)
                    pt = np.array(self.translate_D(last_pt, new_vec, 2*r))
                    last_pt = pt
                old_vec = new_vec
        # print(list_pts)
        new_D = (n_l-1)*2*r 
        theta_new = np.pi/6;
        change = np.pi/3
        for i in range(1,7):
            list_pts.append(self.calculate_D(new_D,theta_new))
            theta_new = theta_new+change
        return(self.get_ordered_list(list_pts))
            
    def get_pts_on_table2(self):
        lists_of_points = self.get_pts_on_table()
        print(len(lists_of_points))
        new_list = list()
        for i in lists_of_points:
            if (i[1]>=0):
                new_list.append(i)
        
        for i in lists_of_points:
            if(i[1]==0 and i[0]<=0):
                new_list.remove(i)
        random.shuffle(new_list)
        new_list2 = list()
        flag = 175
        for i in new_list:
            if(flag%3==0):
                new_list2.append(i) 
                new_list2.append(self.rotate_via_numpy(i,PI))
            else:
                new_list2.append(self.rotate_via_numpy(i,PI))
                new_list2.append(i)    
            flag-=1      
        print(len(new_list2))    
        return new_list2



    def construct(self):
        self.coin_size = 0.25
        # my_plane = NumberPlane(**self.plane_kwargs)
        # my_plane.add(my_plane.get_axis_labels())
        # self.add(my_plane)
        # self.set_camera_orientation(0.1, -np.pi/2)
        table = Circle(color=RED_B, fill_color = RED_B )
        table.scale(3.80)
        #my_first_text=TextMobject("Writing with manim is fun")
        #second_line=TextMobject("and easy to do!")
        #second_line.next_to(my_first_text,DOWN)
        #third_line=TextMobject("for me and you!")
        #third_line.next_to(my_first_text,DOWN)
        obs = Observer()
        #print("values of direction",UP ,TOP ,LEFT)
        #print("hellworld", UP + 1.5* TOP - 0.5*LEFT)
        obs.shift( UP + 2* TOP - 0.5*LEFT )
        obs2 = Observer(fill_color = YELLOW_D)
        obs2.shift( DOWN + 2*BOTTOM - 0.5*LEFT )
        obs_label=TextMobject("A")
        obs_label.next_to(obs, LEFT)
        
        self.add(obs)
        self.add(obs2)        
        self.add(table)
        #point_list = self.get_pts_on_tables
        point_list = self.get_pts_on_table2()
        #random.shuffle(point_list)
        print(len(point_list))
        '''for idx, point in enumerate(point_list):
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            total_vect=point
            print("total_vect", total_vect, idx)
            coin.shift(total_vect)
            self.play(GrowFromCenter(coin));   '''
        coin = Coin()
        origin1 = [0,0,0]
        coin.scale(self.coin_size)
        coin.shift(origin1)
        self.play(GrowFromCenter(coin)) 
#here this coin will generate from  the center and it is yellow

        self.wait(2)
        self.remove(obs)
        self.move_camera(0.1, -np.pi/2)
        for idx, i in enumerate(point_list):
            print("Loop2", i)
            if(idx % 2 == 0):
                coin = Coin(fill_color= BLUE)
                #self.move_camera(0.8*np.pi/2, -0.45*np.pi)
            else:
                coin = Coin()
                #self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            coin.scale(self.coin_size)
            coin.shift(i);
            #self.add(coin)
            self.play(GrowFromCenter(coin));
        #self.add(my_first_text, second_line)
        self.wait(2)


class ColorCounter(ThreeDScene):
    # self.coin_size=0.25
    def get_points(self):
        pt=np.array([0.4,3,0])
        point = list()
        point.append(pt)
        for i in range(1,4):
            for j in range(i):
                pt+=np.array([1.2,0,0])
                point.append(pt)  
            pt +=np.array([0,-1,0])
        return point
    def construct(self):
        point = self.get_points()
        print(point)
        for i in point: 
            coin = Coin(radius=0.5)
                #self.move_camera(0.8*np.pi/2, 0.45*np.pi)
            # coin.scale(self.coin_size)
            coin.shift(i);
            #self.add(coin)
            self.play(GrowFromCenter(coin));



