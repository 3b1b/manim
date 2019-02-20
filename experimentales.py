from big_ol_pile_of_manim_imports import *

class Perturbacion(ContinualAnimation):
    CONFIG = {
        "amplitude": 0.4,
        "jiggles_per_second": 1,
    }

    def __init__(self, group, **kwargs):
        for submob in group.submobjects:
            submob.jiggling_direction = rotate_vector(
                RIGHT, np.random.random() * TAU *1.5,
            )
            submob.jiggling_phase = np.random.random() * TAU *1.5
        ContinualAnimation.__init__(self, group, **kwargs)

    def update_mobject(self, dt):
        for submob in self.mobject.submobjects:
            submob.jiggling_phase += dt * self.jiggles_per_second * TAU
            submob.shift(
                self.amplitude *
                submob.jiggling_direction *
                np.sin(submob.jiggling_phase) * dt
            )

class Particula(Scene):
    def construct(self):
        punto=VGroup(Dot(radius=0.6).shift(LEFT+UP),Dot(radius=0.6).shift(RIGHT+DOWN),Dot(radius=0.6))
        punto2=punto.copy().shift(LEFT*2)
        self.play(GrowFromCenter(punto),GrowFromCenter(punto2))
        self.add(Perturbacion(punto),Perturbacion(punto2))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(Perturbacion(punto,amplitude=0.6),Perturbacion(punto2,amplitude=0.6))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(Perturbacion(punto,amplitude=0.8),Perturbacion(punto2,amplitude=0.8))
        self.wait(5)
        self.remove(Perturbacion(punto),Perturbacion(punto2))
        self.add(punto,punto2)
        self.wait(5)

class PerTexto(Scene):
    def construct(self):
        texto=Texto("Q","u","é","\\_","o","n","d","a","\\_","g","e","n","t","e")
        for i in [3,8]:
            texto[i].fade(1)
        texto_base=Texto("Qué\\_onda\\_gente")
        for i in range(len(texto)):
            texto[i].move_to(texto_base[i])
        self.play(Escribe(texto))
        self.add(*[Perturbacion(texto[i])for i in range(len(texto))])
        self.wait(5)

class Dimensiones(Scene):
    def construct(self):
        rectangulo=Rectangle(width=5,height=3)
        rectangulo.rotate(30*DEGREES)
        linea=Line(LEFT*1.5,RIGHT*1.5)
        linea.rotate(20*DEGREES)
        linea.shift(LEFT*2)
        v_medicion=Medicion(linea,color=BLUE,dashed=False)
        self.play(ShowCreation(linea))
        self.play(GrowFromCenter(v_medicion))
        def update(grupo):
            angulo=linea.get_angle()
            tam_med=grupo[1].get_length()/2
            vu=linea.get_unit_vector()
            mr=rotation_matrix(PI/2,OUT)
            #grupo.rotate(angulo)
            grupo[0].put_start_and_end_on(linea.get_start(),linea.get_end())
            direccion=np.matmul(mr,vu)
            grupo[0].shift(direccion*0.3)
            origen1=grupo[0].get_end()
            fin1_1=origen1+direccion*tam_med
            fin1_2=origen1-direccion*tam_med
            grupo[1].put_start_and_end_on(fin1_1,fin1_2)

            origen2=grupo[0].get_start()
            fin2_1=origen2+direccion*tam_med
            fin2_2=origen2-direccion*tam_med
            grupo[2].put_start_and_end_on(fin2_1,fin2_2)


        self.play(linea.scale,2,linea.rotate,PI/8,linea.shift,RIGHT*3,
            UpdateFromFunc(
            v_medicion,update))
        self.wait(2)

class Dimensiones2(Scene):
    def construct(self):
        rectangulo=Rectangle(width=5,height=3)
        rectangulo.rotate(30*DEGREES)
        linea=Line(LEFT*1.5,RIGHT*1.5)
        linea.rotate(20*DEGREES)
        linea.shift(LEFT*2)
        v_medicion=Medicion(linea).add_tips().add_letter("x",buff=2)
        self.play(ShowCreation(linea))
        self.play(GrowFromCenter(v_medicion))
        def update(grupo):
            nueva_medicion=Medicion(linea).add_tips().add_letter("x",buff=2)
            for i in range(len(grupo)-1):
                grupo[i].put_start_and_end_on(nueva_medicion[i].get_start(),nueva_medicion[i].get_end())
            grupo[-1].move_to(nueva_medicion[-1])


        self.play(linea.scale,2,linea.rotate,PI/8,linea.shift,RIGHT*3,
            UpdateFromFunc(
            v_medicion,update))
        self.wait(2)

class Temperatura(GraphScene):
    CONFIG = {
        "x_min" : 0,
        "x_axis_label" : "$t$",
        "y_axis_label" : "Temperature",
        "T_room" : 4,
        "include_solution" : False,
    }
    def construct(self):
        self.setup_axes()
        graph = self.get_graph(
            lambda t : 3*np.exp(-0.3*t) + self.T_room,
            color = RED
        )
        h_line = DashedLine(*[
            self.coords_to_point(x, self.T_room)
            for x in (self.x_min, self.x_max)
        ])
        T_room_label = TexMobject("T_{\\text{room}}")
        T_room_label.next_to(h_line, LEFT)

        ode = TexMobject(
            "\\frac{d\\Delta T}{dt} = -k \\Delta T"
        )
        ode.to_corner(UP+RIGHT)

        solution = TexMobject(
            "\\Delta T(", "t", ") = e", "^{-k", "t}"
        )
        solution.next_to(ode, DOWN, MED_LARGE_BUFF)
        solution.set_color_by_tex("t", YELLOW)
        solution.set_color_by_tex("Delta", WHITE)

        delta_T_brace = Brace(graph, RIGHT)
        delta_T_label = TexMobject("\\Delta T")
        delta_T_group = VGroup(delta_T_brace, delta_T_label)
        def update_delta_T_group(group):
            brace, label = group
            v_line = Line(
                graph.points[-1],
                graph.points[-1][0]*RIGHT + h_line.get_center()[1]*UP
            )
            brace.set_height(v_line.get_height())
            brace.next_to(v_line, RIGHT, SMALL_BUFF)
            label.set_height(min(
                label.get_height(),
                brace.get_height()
            ))
            label.next_to(brace, RIGHT, SMALL_BUFF)

        self.add(ode)
        self.play(
            Write(T_room_label),
            ShowCreation(h_line, run_time = 2)
        )
        if self.include_solution:
            self.play(Write(solution))
        graph_growth = ShowCreation(graph, rate_func = None)
        delta_T_group_update = UpdateFromFunc(
            delta_T_group, update_delta_T_group
        )
        self.play(
            GrowFromCenter(delta_T_brace),
            Write(delta_T_label),
        )
        self.play(graph_growth, delta_T_group_update, run_time = 15)
        self.wait(2)

