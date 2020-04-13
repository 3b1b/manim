from manimlib.imports import *

class Grid(VGroup):
    CONFIG = {
        "height": 6.0,
        "width": 6.0,
    }

    def __init__(self, rows, columns, **kwargs):
        digest_config(self, kwargs, locals())
        super().__init__(**kwargs)

        x_step = self.width / self.columns
        y_step = self.height / self.rows

        for x in np.arange(0, self.width + x_step, x_step):
            self.add(Line(
                [x - self.width / 2., -self.height / 2., 0],
                [x - self.width / 2., self.height / 2., 0],
            ))
        for y in np.arange(0, self.height + y_step, y_step):
            self.add(Line(
                [-self.width / 2., y - self.height / 2., 0],
                [self.width / 2., y - self.height / 2., 0]
            ))


class ScreenGrid(VGroup):
    CONFIG = {
        "rows": 16,
        "columns": 28,
        "height": FRAME_Y_RADIUS * 2,
        "width": 14,
        "grid_stroke": 0.5,
        "grid_color": WHITE,
        "axis_color": RED,
        "axis_stroke": 2,
        "labels_scale": 0.25,
        "labels_buff": 0,
        "number_decimals": 2
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rows = self.rows
        columns = self.columns
        grid = Grid(width=self.width, height=self.height, rows=rows, columns=columns)
        grid.set_stroke(self.grid_color, self.grid_stroke)

        vector_ii = ORIGIN + np.array((- self.width / 2, - self.height / 2, 0))
        vector_si = ORIGIN + np.array((- self.width / 2, self.height / 2, 0))
        vector_sd = ORIGIN + np.array((self.width / 2, self.height / 2, 0))

        axes_x = Line(LEFT * self.width / 2, RIGHT * self.width / 2)
        axes_y = Line(DOWN * self.height / 2, UP * self.height / 2)

        axes = VGroup(axes_x, axes_y).set_stroke(self.axis_color, self.axis_stroke)

        divisions_x = self.width / columns
        divisions_y = self.height / rows

        directions_buff_x = [UP, DOWN]
        directions_buff_y = [RIGHT, LEFT]
        dd_buff = [directions_buff_x, directions_buff_y]
        vectors_init_x = [vector_ii, vector_si]
        vectors_init_y = [vector_si, vector_sd]
        vectors_init = [vectors_init_x, vectors_init_y]
        divisions = [divisions_x, divisions_y]
        orientations = [RIGHT, DOWN]
        labels = VGroup()
        set_changes = zip([columns, rows], divisions, orientations, [0, 1], vectors_init, dd_buff)
        for c_and_r, division, orientation, coord, vi_c, d_buff in set_changes:
            for i in range(1, c_and_r):
                for v_i, directions_buff in zip(vi_c, d_buff):
                    ubication = v_i + orientation * division * i
                    coord_point = round(ubication[coord], self.number_decimals)
                    label = TextMobject(f"{coord_point}",font="Arial",stroke_width=0).scale(self.labels_scale)
                    label.next_to(ubication, directions_buff, buff=self.labels_buff)
                    labels.add(label)

        self.add(grid, axes, labels)

        
class Floors(MovingCameraScene):
    def construct(self):
        # self.play(
        #     self.camera_frame.scale(2),0.5            
        # )        
        self.camera_frame.scale(-2.5)
        # grid = ScreenGrid()
        # self.add(grid)      
        ground = Line((-8,-8,0),(8,-8,0),stroke_color=BLUE_E) 
        self.play(GrowFromCenter(ground))       
        c_rectangle = Rectangle(width=16, height=2,stroke_color=BLUE_E)
        c_rectangle.rotate(PI/2)
        c_rectangle.move_to([-2,0,0])
        l_rectangle = c_rectangle.copy()        
        l_rectangle.move_to([2,0,0])
        self.play(
            ShowCreation(c_rectangle),
            ShowCreation(l_rectangle)
            )
        s = [(i,i) for i in range(-3, 3, 1)]
        print(s)
        self.play(
            *[
                ShowCreation(Line((-3,i,0),(-1,i,0),stroke_color=BLUE_E))
                for i in range(-8, 8)
            ]
        )
        self.play(
            *[
                ShowCreation(Line((1,i,0),(3,i,0),stroke_color=BLUE_E))
                for i in range(-8, 8)
            ]
        )        
        self.wait()
        c_array = [i for i in range(1, 17)]
        l_array = [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16, 17, 18, 19]        
        for i in range(16):
            c_level_num = TextMobject(str(int(c_array[i])))
            c_level_num.move_to([-2,-7.5+i,0]) 
            l_level_num = TextMobject(str(int(l_array[i])))
            l_level_num.move_to([2,-7.5+i,0])                        
            self.add(c_level_num, l_level_num)
            self.wait(0.2)
        self.play(ShowCreation(l_rectangle))
        self.wait()
        unlucky_floors = [4, 13, 14] 
        unlucky_offset = 8.5
        red_rectangles = []
        for i in range(3):
            red_rectangle = Rectangle(stroke_color=RED_E,width=1, height=2)
            red_rectangle.rotate(PI/2)
            red_rectangle.move_to([-2,unlucky_floors[i] - unlucky_offset,0])
            red_rectangles.append(red_rectangle)
        self.play(
            *[
                ShowCreation(red_rectangles[i])
                for i in range(3)
            ]          
        )        
        self.wait()
        self.camera_frame.move_to([10,0,0])

        # num_str = [i for i in range(1, 17)]
        formula = TexMobject(
            "if \\text{ 4 } or \\text{ and } B)",
            tex_to_color_map={"if": YELLOW, "B": BLUE},
        )
        formula.arrange(RIGHT)
        formula.scale(1.5)
        formula.to_edge(UP)
        s = TextMobject("This is a regular text")                       
        # check_number_text = Text('if "4" in num_str or "13" in num_str:', t2c={'if':RED_E})
        formula.move_to([10,0,0])
        self.play(ShowCreation(formula))
        # self.play(Write(s))
        self.wait()

class MyText(Text):
    CONFIG = {
        'font': 'Helvetica',
        'size': 0.4
    }

class DPScene(LinearTransformationScene):
    CONFIG = {
        "include_background_plane": True,
        "include_foreground_plane": True,
        "foreground_plane_kwargs": {
            "x_radius": FRAME_WIDTH,
            "y_radius": FRAME_HEIGHT,
            "secondary_line_ratio": 0
        },
        "background_plane_kwargs": {
            "color": GREY,
            "secondary_color": DARK_GREY,
            "axes_color": GREY,
            "stroke_width": 2,
        },
        "show_coordinates": False,
        "show_basis_vectors": True,
        "basis_vector_stroke_width": 6,
        "i_hat_color": X_COLOR,
        "j_hat_color": Y_COLOR,
        "leave_ghost_vectors": False,
    }    
    def construct(self):                
        s1 = Square(side_length=0.5)
        n1 = MyText("7",size=0.5)
        n1.add_updater(lambda d: d.next_to(s1, ORIGIN, buff=SMALL_BUFF))
        self.play(
            ShowCreation(s1),
            ShowCreation(n1)
        )
        self.wait()        
        self.play(s1.shift, LEFT*5)        
        self.wait()

        for i in range(5):
            if i == 0:
                self.play(
                    ShowCreation(self.draw_column(-3))
                )
                self.wait()
            else:
                self.play(
                    self.draw_column(-3).shift, RIGHT * i * 2
                )
        self.wait()
            
    def draw_column(self, x_shift):
        return VGroup(
            *[ 
                VGroup(
                    Square(side_length=0.5)
                    .move_to(
                        [x_shift, 3-i*0.75, 0] if i < 4 else [x_shift, 3-(i-1)*0.75, 0]
                    ), 
                    MyText(str(i))
                    .move_to(
                        [x_shift, 3-i*0.75, 0] if i < 4 else [x_shift, 3-(i-1)*0.75, 0]
                    ),
                ) for i in range(10) if i != 4           
            ]
        )

                          

        
                

        