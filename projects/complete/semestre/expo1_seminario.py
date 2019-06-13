import scipy.integrate
from big_ol_pile_of_manim_imports import *

USE_ALMOST_FOURIER_BY_DEFAULT = False
NUM_SAMPLES_FOR_FFT = 1000
DEFAULT_COMPLEX_TO_REAL_FUNC = lambda z : z.real

def get_fourier_transform(
    func, t_min, t_max, 
    complex_to_real_func = DEFAULT_COMPLEX_TO_REAL_FUNC,
    use_almost_fourier = USE_ALMOST_FOURIER_BY_DEFAULT,
    **kwargs ##Just eats these
    ):
    scalar = 1./(t_max - t_min) if use_almost_fourier else 1.0/np.sqrt(2*PI)
    def fourier_transform(f):
        z = scalar*scipy.integrate.quad(
            lambda t : func(t)*np.exp(complex(0, -TAU*f*t)),
            t_min, t_max
        )[0]
        return complex_to_real_func(z)
    return fourier_transform

class FourierMachineScene(Scene):
    CONFIG = {
        "time_axes_config" : {
            "x_min" : 0,
            "x_max" : 4.4,
            "x_axis_config" : {
                "unit_size" : 3,
                "tick_frequency" : 0.25,
                "numbers_with_elongated_ticks" : [1, 2, 3],
            },
            "y_min" : -1.5,
            "y_max" : 1.5,
            "y_axis_config" : {"unit_size" : 1},
        },
        "time_label_t" : 4.4,
        "circle_plane_config" : {
            "x_radius" : 2.1,
            "y_radius" : 2.1,
            "x_unit_size" : 1,
            "y_unit_size" : 1,
        },
        "frequency_axes_config" : {
            "number_line_config" : {
                "color" : BLUE_B,
            },
            "x_min" : 0,
            "x_max" : 5.0,
            "x_axis_config" : {
                "unit_size" : 1.4,
                "numbers_to_show" : list(range(1, 6)),
            },
            "y_min" : -1.0,
            "y_max" : 1.0,
            "y_axis_config" : {
                "unit_size" : 1,
                "tick_frequency" : 1,
                "label_direction" : LEFT,
            },
            "color" : TEAL,
        },
        "frequency_axes_box_color" : BLUE_B,
        "text_scale_val" : 0.75,
        "default_graph_config" : {
            "num_graph_points" : 100,
            "color" : YELLOW,
        },
        "equilibrium_height" : 1,
        "default_y_vector_animation_config" : {
            "run_time" : 5,
            "rate_func" : None,
            "remover" : True,
        },
        "default_time_sweep_config" : {
            "rate_func" : None,
            "run_time" : 5,
        },
        "default_num_v_lines_indicating_periods" : 20,
    }

    def get_time_axes(self):
        time_axes = Axes(**self.time_axes_config)
        time_axes.x_axis.add_numbers()
        time_label = TextMobject("$t$")
        intensity_label = TextMobject("dB")
        labels = VGroup(time_label, intensity_label)
        for label in labels:
            label.scale(self.text_scale_val)
        time_label.next_to(
            time_axes.coords_to_point(self.time_label_t,0), 
            DOWN
        )
        intensity_label.next_to(time_axes.y_axis[0].get_end(), RIGHT)
        time_axes.labels = labels
        time_axes.add(labels)
        time_axes.to_corner(UP+LEFT)
        time_axes.x_axis[3][0].fade(1)
        self.time_axes = time_axes
        return time_axes

    def get_circle_plane(self):
        circle_plane = NumberPlane(**self.circle_plane_config)
        circle_plane.to_corner(DOWN+LEFT)
        circle = DashedLine(ORIGIN, TAU*UP).apply_complex_function(np.exp)
        circle.scale(circle_plane.x_unit_size)
        circle.move_to(circle_plane.coords_to_point(0, 0))
        circle_plane.circle = circle
        circle_plane.add(circle)
        circle_plane.fade()
        self.circle_plane = circle_plane
        return circle_plane

    def get_frequency_axes(self):
        frequency_axes = Axes(**self.frequency_axes_config)
        frequency_axes.x_axis.add_numbers()
        frequency_axes.y_axis.add_numbers(
            *frequency_axes.y_axis.get_tick_numbers()
        )
        box = SurroundingRectangle(
            frequency_axes,
            buff = MED_SMALL_BUFF,
            color = self.frequency_axes_box_color,
        )
        frequency_axes.box = box
        frequency_axes.add(box)
        frequency_axes.to_corner(DOWN+RIGHT, buff = MED_SMALL_BUFF)

        frequency_label = TexMobject("\\omega")
        frequency_y_label = TexMobject("{\\tt FFT}(\\omega)")
        frequency_y_label.scale(self.text_scale_val)
        frequency_label.scale(self.text_scale_val)
        frequency_label.next_to(
            frequency_axes.x_axis.get_right(), DOWN, 
            buff = MED_LARGE_BUFF,
            aligned_edge = RIGHT,
        )
        frequency_y_label.next_to(
            frequency_axes.y_axis[0].get_end(), RIGHT, 
            buff = MED_LARGE_BUFF,
        )
        frequency_axes.label = frequency_label
        frequency_axes.add(frequency_label)
        frequency_axes.add(frequency_y_label)

        self.frequency_axes = frequency_axes
        return frequency_axes

    def get_time_graph(self, func, **kwargs):
        if not hasattr(self, "time_axes"):
            self.get_time_axes()
        config = dict(self.default_graph_config)
        config.update(kwargs)
        graph = self.time_axes.get_graph(func, **config)
        return graph

    def get_cosine_wave(self, freq = 1, shift_val = 0, scale_val = 0.9):
        return self.get_time_graph(
            lambda t : shift_val + scale_val*np.cos(TAU*freq*t)
        )

    def get_fourier_transform_graph(self, time_graph, **kwargs):
        if not hasattr(self, "frequency_axes"):
            self.get_frequency_axes()
        func = time_graph.underlying_function
        t_axis = self.time_axes.x_axis
        t_min = t_axis.point_to_number(time_graph.points[0])
        t_max = t_axis.point_to_number(time_graph.points[-1])
        f_max = self.frequency_axes.x_max
        # result = get_fourier_graph(
        #     self.frequency_axes, func, t_min, t_max,
        #     **kwargs
        # )
        # too_far_right_point_indices = [
        #     i
        #     for i, point in enumerate(result.points)
        #     if self.frequency_axes.x_axis.point_to_number(point) > f_max
        # ]
        # if too_far_right_point_indices:
        #     i = min(too_far_right_point_indices)
        #     prop = float(i)/len(result.points)
        #     result.pointwise_become_partial(result, 0, prop)
        # return result
        return self.frequency_axes.get_graph(
            get_fourier_transform(func, t_min, t_max, **kwargs),
            color = self.center_of_mass_color,
            **kwargs
        )

    def get_polarized_mobject(self, mobject, freq = 1.0):
        if not hasattr(self, "circle_plane"):
            self.get_circle_plane()
        polarized_mobject = mobject.copy()
        polarized_mobject.apply_function(lambda p : self.polarize_point(p, freq))
        # polarized_mobject.make_smooth()
        mobject.polarized_mobject = polarized_mobject
        polarized_mobject.frequency = freq
        return polarized_mobject

    def polarize_point(self, point, freq = 1.0):
        t, y = self.time_axes.point_to_coords(point)
        z = y*np.exp(complex(0, -2*np.pi*freq*t))
        return self.circle_plane.coords_to_point(z.real, z.imag)

    def get_polarized_animation(self, mobject, freq = 1.0):
        p_mob = self.get_polarized_mobject(mobject, freq = freq)
        def update_p_mob(p_mob):
            Transform(
                p_mob, 
                self.get_polarized_mobject(mobject, freq = freq)
            ).update(1)
            mobject.polarized_mobject = p_mob
            return p_mob
        return UpdateFromFunc(p_mob, update_p_mob)

    def animate_frequency_change(self, mobjects, new_freq, **kwargs):
        kwargs["run_time"] = kwargs.get("run_time", 3.0)
        added_anims = kwargs.get("added_anims", [])
        self.play(*[
            self.get_frequency_change_animation(mob, new_freq, **kwargs)
            for mob in mobjects
        ] + added_anims)

    def get_frequency_change_animation(self, mobject, new_freq, **kwargs):
        if not hasattr(mobject, "polarized_mobject"):
            mobject.polarized_mobject = self.get_polarized_mobject(mobject)
        start_freq = mobject.polarized_mobject.frequency
        def update(pm, alpha):
            freq = interpolate(start_freq, new_freq, alpha)
            new_pm = self.get_polarized_mobject(mobject, freq)
            Transform(pm, new_pm).update(1)
            mobject.polarized_mobject = pm
            mobject.polarized_mobject.frequency = freq
            return pm
        return UpdateFromAlphaFunc(mobject.polarized_mobject, update, **kwargs)

    def get_time_graph_y_vector_animation(self, graph, **kwargs):
        config = dict(self.default_y_vector_animation_config)
        config.update(kwargs)
        vector = Vector(UP, color = WHITE)
        graph_copy = graph.copy()
        x_axis = self.time_axes.x_axis
        x_min = x_axis.point_to_number(graph.points[0])
        x_max = x_axis.point_to_number(graph.points[-1])
        def update_vector(vector, alpha):
            x = interpolate(x_min, x_max, alpha)
            vector.put_start_and_end_on(
                self.time_axes.coords_to_point(x, 0),
                self.time_axes.input_to_graph_point(x, graph_copy)
            )
            return vector
        return UpdateFromAlphaFunc(vector, update_vector, **config)

    def get_polarized_vector_animation(self, polarized_graph, **kwargs):
        config = dict(self.default_y_vector_animation_config)
        config.update(kwargs)
        vector = Vector(RIGHT, color = WHITE)
        origin = self.circle_plane.coords_to_point(0, 0)
        graph_copy = polarized_graph.copy()
        def update_vector(vector, alpha):
            # Not sure why this is needed, but without smoothing 
            # out the alpha like this, the vector would occasionally
            # jump around
            point = center_of_mass([
                graph_copy.point_from_proportion(alpha+d)
                for d in np.linspace(-0.001, 0.001, 5)
            ])
            vector.put_start_and_end_on_with_projection(origin, point)
            return vector
        return UpdateFromAlphaFunc(vector, update_vector, **config)

    def get_vector_animations(self, graph, draw_polarized_graph = True, **kwargs):
        config = dict(self.default_y_vector_animation_config)
        config.update(kwargs)
        anims = [
            self.get_time_graph_y_vector_animation(graph, **config),
            self.get_polarized_vector_animation(graph.polarized_mobject, **config),
        ]
        if draw_polarized_graph:
            new_config = dict(config)
            new_config["remover"] = False
            anims.append(ShowCreation(graph.polarized_mobject, **new_config))
        return anims

    def animate_time_sweep(self, freq, n_repeats = 1, t_max = None, **kwargs):
        added_anims = kwargs.pop("added_anims", [])
        config = dict(self.default_time_sweep_config)
        config.update(kwargs)
        circle_plane = self.circle_plane
        time_axes = self.time_axes
        ctp = time_axes.coords_to_point
        t_max = t_max or time_axes.x_max
        v_line = DashedLine(
            ctp(0, 0), ctp(0, time_axes.y_max),
            stroke_width = 6,
        )
        v_line.set_color(RED)

        for x in range(n_repeats):
            v_line.move_to(ctp(0, 0), DOWN)
            self.play(
                ApplyMethod(
                    v_line.move_to, 
                    ctp(t_max, 0), DOWN
                ),
                self.get_polarized_animation(v_line, freq = freq),
                *added_anims,
                **config
            )
            self.remove(v_line.polarized_mobject)
        self.play(FadeOut(VGroup(v_line, v_line.polarized_mobject)))

    def get_v_lines_indicating_periods(self, freq, n_lines = None):
        if n_lines is None:
            n_lines = self.default_num_v_lines_indicating_periods
        period = np.divide(1., max(freq, 0.01))
        v_lines = VGroup(*[
            DashedLine(ORIGIN, 1.5*UP).move_to(
                self.time_axes.coords_to_point(n*period, 0),
                DOWN
            )
            for n in range(1, n_lines + 1)
        ])
        v_lines.set_stroke(LIGHT_GREY)
        return v_lines

    def get_period_v_lines_update_anim(self):
        def update_v_lines(v_lines):
            freq = self.graph.polarized_mobject.frequency
            Transform(
                v_lines,
                self.get_v_lines_indicating_periods(freq)
            ).update(1)
        return UpdateFromFunc(
            self.v_lines_indicating_periods, update_v_lines
        )

class EscenaSumaFrecuencias(FourierMachineScene):
    CONFIG = {
        "high_freq_color": YELLOW,
        "low_freq_color": TEAL,
        "sum_color": GREEN,
        "low_freq" : 1.0,
        "high_freq" : 2.0,
        "circle_plane_config" : {
            "x_radius" : 2.5,
            "y_radius" : 2.7,
            "x_unit_size" : 0.8,
            "y_unit_size" : 0.8,
        },
        "camera_config":{"background_color":BLACK}
    }
    def construct(self):
        self.show_sum_of_signals()
        self.realiza_transformada()
        self.muestra_transformada()
        self.show_winding_with_sum_graph()
        self.wait(6)

    def show_sum_of_signals(self):
        low_freq, high_freq = self.low_freq, self.high_freq
        axes = self.get_time_axes()
        axes_copy = axes.copy()
        low_freq_graph, high_freq_graph = [
            self.get_cosine_wave(
                freq = freq, 
                scale_val = amp,
                shift_val =0,
            )
            for freq,amp in [(low_freq,0.5),(high_freq,1)]
        ]
        sum_graph = self.get_time_graph(
            lambda t : sum([
                low_freq_graph.underlying_function(t),
                high_freq_graph.underlying_function(t),
            ])
        )
        VGroup(axes_copy, high_freq_graph).next_to(
            axes, DOWN, MED_LARGE_BUFF
        )

        low_freq_label = TexMobject("0.5\\cdot\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(low_freq)).scale(1.3)
        high_freq_label = TexMobject("\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(high_freq)).scale(1.3)
        sum_label = VGroup(TexMobject(
            "0.5\\cdot\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(low_freq)), TexMobject("+"),
            TexMobject("\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(high_freq))
        ).scale(1.3)
        sum_label_water=TexMobject("0.5\\cdot\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(low_freq),"+","\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(high_freq)).scale(1.3)
        for cont in range(len(sum_label)):
        	sum_label[cont].move_to(sum_label_water[cont])
        trips = [
            (low_freq_label, low_freq_graph, self.low_freq_color), 
            (high_freq_label, high_freq_graph, self.high_freq_color),
            (sum_label, sum_graph, self.sum_color),
        ]
        for label, graph, color in trips:
            label.next_to(graph, UP)
            graph.set_color(color)
            label.set_color(color)
        sum_label[0].match_color(low_freq_graph)
        sum_label[2].match_color(high_freq_graph)

        self.play(FadeIn(axes),ShowCreation(low_freq_graph))
        self.play(
            FadeIn(axes_copy),
            ShowCreation(high_freq_graph),
        )
        self.play(LaggedStart(
            FadeIn, VGroup(low_freq_label,high_freq_label)
        ))
        self.wait(7.7)
        axes_copy2=axes.copy()
        VGroup(sum_label,axes_copy2,sum_graph).shift(UP*2.3)
        self.play(
            ReplacementTransform(axes_copy, axes_copy2),
            ReplacementTransform(axes, axes_copy2),
            ReplacementTransform(high_freq_graph, sum_graph),
            ReplacementTransform(low_freq_graph, sum_graph),
            ReplacementTransform(
                high_freq_label,
                sum_label[2]
            ),
            Write(sum_label[1]),
            ReplacementTransform(
                low_freq_label,
                sum_label[0]
            )
        )
        self.wait(2.5)
        self.graph = sum_graph
        self.sum_label=sum_label

    def realiza_transformada(self):
    	transformada=VGroup(TexMobject("\\mathcal{F}\\{\\}"),
    		TexMobject("0.5\\cdot\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(1),color=self.low_freq_color),
    		TexMobject("+"),
    		TexMobject("\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(2),color=self.high_freq_color),
    		TexMobject("\\{\\}")).scale(1.3)
    	transformada_water=TexMobject("\\mathcal{F}\\{\\}",
    		"0.5\\cdot\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(1),
    		"+",
    		"\\cos(%d[{\\rm Hz}]\\cdot(2\\pi\\cdot t))"%int(2),
    		"\\{\\}").scale(1.3)
    	for cont in range(len(transformada)):
    		transformada[cont].move_to(transformada_water[cont])
    	transformada[0][-1].fade(1)
    	transformada[0].next_to(transformada[1],LEFT,buff=-0.2)
    	transformada[-1][-2].fade(1)
    	transformada[-1].next_to(transformada[3],RIGHT,buff=-0.2)
    	self.play(ReplacementTransform(self.sum_label.copy(),transformada[1:-1]))
    	self.play(Write(transformada[0]),Write(transformada[-1]))
    	self.wait()
    	formula=VGroup(TexMobject("\\hat{f}(\\omega)="),
    		TexMobject("\\sqrt{\\frac{\\pi}{8}}\\delta(\\omega-1\\cdot 2\\pi)"),
    		TexMobject("+"),
    		TexMobject("\\sqrt{\\frac{\\pi}{2}}\\delta(\\omega-2\\cdot 2\\pi)")).scale(1.5).set_color(WHITE)
    	formula.arrange_submobjects(RIGHT)
    	formula[1].set_color(self.low_freq_color)
    	formula[-1].set_color(self.high_freq_color)
    	aclaracion=TextMobject("(S\\'olo parte positiva)").scale(1.3).next_to(formula,DOWN)
    	self.play(*[ReplacementTransform(transformada[j],formula[j])for j in range(len(formula))],
    		FadeOut(transformada[-1]))
    	self.play(FadeInFrom(aclaracion,UP))
    	self.wait(2)
    	self.play(aclaracion.shift,RIGHT*10)
    	self.wait(3)
    	self.formula=formula

    def muestra_transformada(self):
        formula_c=self.formula[0].copy()
        formula_transformada=VGroup(TexMobject("\\hat{f}(\\omega)="),
                                    TexMobject("\\sqrt{\\frac{\\beta}{2\\pi}}"),
                                    TexMobject("\\int^","{\\infty}_","{-\\infty}"),
                                    TexMobject("f(t)","e^","{-i\\beta\\omega t}"),
                                    TexMobject("dt")).set_color(WHITE)
        formula_transformada[2].set_color(ORANGE)
        formula_transformada.arrange_submobjects(RIGHT)
        formula_transformada.shift(UP*1.5)
        transformada_discreta=VGroup(
                                        TexMobject("{\\tt FFT}(\\omega)="),
                                        TexMobject("\\sum^","{T-1}_","{t=0}"),
                                        TexMobject("f(t)","e^","{-i2\\pi \\omega\\frac{t}{T}}")
                                    ).set_color(WHITE)
        transformada_discreta[1].set_color(ORANGE)
        transformada_discreta.arrange_submobjects(RIGHT)
        transformada_discreta.next_to(formula_transformada,DOWN,buff=MED_LARGE_BUFF*2)
        VGroup(formula_transformada,transformada_discreta).scale(1.69).move_to(ORIGIN)
        formula_transformada[-1].shift(LEFT*0.2)
        nota_td=TexMobject("\\left(t=0,\\dots,T-1\\right)")
        nota_td.next_to(transformada_discreta,DOWN,buff=0.3)
        self.add_foreground_mobject(formula_c)
        cuadro=Rectangle(height=FRAME_HEIGHT*3,width=FRAME_WIDTH*3,color=BLACK).set_fill(opacity=0.85)
        self.play(FadeIn(cuadro))
        self.wait()
        self.play(ReplacementTransform(formula_c,formula_transformada[0]))
        self.play(Escribe(formula_transformada[1:],rate_func=linear))
        self.wait(6)
        self.play(
                    *[ReplacementTransform(formula_transformada[i].copy(),transformada_discreta[j])
                      for i,j in [(0,0),(2,1),(3,2)]],
                )
        self.play(FadeInFrom(nota_td,UP))
        self.wait(6)
        self.play(FadeOut(cuadro),
            FadeOut(formula_transformada),
            FadeOut(nota_td),
            FadeOut(transformada_discreta[1:]),
            FadeOut(transformada_discreta[0][-1])
            )
        self.etiqueta=transformada_discreta[0][0:-1]




    def show_winding_with_sum_graph(self):
        graph = self.graph
        circle_plane = self.get_circle_plane()
        frequency_axes = self.get_frequency_axes()
        pol_graph = self.get_polarized_mobject(graph, freq = 0.0)

        self.center_of_mass_color=RED

        fourier_graph = self.get_fourier_transform_graph(graph)
        VGroup(fourier_graph,frequency_axes).move_to(ORIGIN).scale(1.7).shift(3.5*DOWN)
        frequency_axes[2][0].fade(1)
        fa=frequency_axes
        fa[4].scale(1.3).shift(LEFT*0.3)
        self.play(LaggedStart(FadeIn,VGroup(fa[0],fa[1],fa[2],fa[3])),
                    self.etiqueta.move_to,fa[4])
        self.play(ReplacementTransform(graph.copy(),fourier_graph))
        p1=Dot(frequency_axes.coords_to_point(1,0.45),color=self.low_freq_color)
        p2=Dot(frequency_axes.coords_to_point(2,0.85),color=self.high_freq_color)
        self.play(ShowCreation(VGroup(p1,p2)))
        self.wait(2)
            

class PentagramaArmonicos(CheckSVG):
    CONFIG={
    "svg_type": "text",
    "stroke_width":0,
    "show_numbers":False,
    "direction_numbers": RIGHT,
    }
    def import_text(self):
        partitura=TikzMobject("""
            \\begin{music}
            \\parindent10mm
            \\instrumentnumber{1}
            \\setname1{} 
            \\setstaffs1{2}
            \\setclef16
            \\startextract
            \\NOtes\\wh{C}|\\en
            \\NOtes\\wh{'C}\\en
            \\NOtes\\wh{'G}\\en
            \\NOtes\\wh{c}\\en
            \\NOtes|\\wh{e}|\\en
            \\NOtes|\\wh{g}|\\en
            \\NOtes|\\wh{'_b}|\\en
            \\NOtes|\\wh{'c}|\\en
            \\NOtes|\\wh{'d}|\\en
            \\NOtes|\\wh{'e}|\\en
            \\NOtes|\\wh{'^f}|\\en
            \\NOtes|\\wh{'g}|\\en
            \\NOtes|\\wh{''a}|\\en
            \\NOtes|\\wh{''_b}|\\en
            \\NOtes|\\wh{''=b}|\\en
            \\NOtes|\\wh{''c}|\\en
            \\endextract
            \\end{music}
            """)
        numbers=VGroup()
        num_inicial=TexMobject("1").next_to(partitura[16],DOWN,buff=0.3)
        numbers.add(num_inicial)
        pos_y=num_inicial.get_center()[1]
        contador=2
        for n in [17,18,20,21,22,24,25,26,27,29,30,32,35,38,40]:
            pos_x=partitura[n].get_center()[0]
            numero=TexMobject("%d"%contador).move_to(np.array([pos_x,pos_y,0]))
            contador=contador+1
            numbers.add(numero)

        fin=VGroup(partitura,numbers)
        return fin[0]

class Soporte(CheckSVG):
    CONFIG={
    "file":"soporte",
    "set_size":"height",
    }


class Armonicos(MusicalScene):
    CONFIG={
    "camera_config":{"background_color":BLACK}
    }
    def setup(self):
        pass

    def construct(self):
        conjunto_lineas,particiones=self.Armonics(20,amplitud=2,tamanho=12)
        conjunto_lineas.shift(DOWN*3)
        particiones.shift(DOWN*3)
        lineas_planas=conjunto_lineas[2]
        lineas_down=conjunto_lineas[1]
        lineas_up=conjunto_lineas[0]
        soporte=ImageMobject("soporte").scale(0.9)
        soporte_espejo=soporte.copy().flip()
        soporte.move_to(lineas_planas[0][0].get_start()).shift(LEFT*soporte.get_width()*0.9/2)
        soporte_espejo.move_to(lineas_planas[0][0].get_end()).shift(RIGHT*soporte.get_width()*0.9/2)

        partitura=self.importa_partitura()
        partitura.shift(UP*3).scale(0.67)
        VGroup(*[partitura[0][j]for j in range(14,42)]).set_submobject_colors_by_gradient(TEAL,GREEN,YELLOW)
        VGroup(*[partitura[1][j]for j in range(len(partitura[1]))]).set_submobject_colors_by_gradient(TEAL,GREEN,YELLOW)

        frecuencias=VGroup()
        armonicos_texto=VGroup()
        do1=65.4064
        for freq in range(1,17):
            frecuencias.add(TextMobject("Frecuencia: ","%.3f"%(float(freq)*do1),"[Hz]"))
            armonicos_texto.add(TextMobject("Armónico","%d"%freq,":","${\\rm C}_1\\times$","%d"%freq))
        frecuencias.set_submobject_colors_by_gradient(TEAL,GREEN,YELLOW)
        armonicos_texto.set_submobject_colors_by_gradient(TEAL,GREEN,YELLOW)

        for freq in range(len(frecuencias)):
            armonicos_texto[freq].to_edge(LEFT)
            frecuencias[freq].next_to(armonicos_texto[freq],DOWN,aligned_edge=LEFT)
            armonicos_texto[freq][2:].next_to(armonicos_texto[freq][:2],RIGHT,buff=0.1)

        piano=self.definir_teclado_piano(7,1,1)
        piano.move_to(ORIGIN).shift(UP*FRAME_WIDTH/2+DOWN*piano.get_height()*2.5/2)
        octavas=7
        do=[*[3+12*n for n in range(octavas)]]
        do_s=[*[3+1+12*n for n in range(octavas)]]
        re=[*[3+2+12*n for n in range(octavas)]]
        re_s=[*[3+3+12*n for n in range(octavas)]]
        mi=[*[3+4+12*n for n in range(octavas)]]
        fa=[*[3+5+12*n for n in range(octavas)]]
        fa_s=[*[3+6+12*n for n in range(octavas)]]
        sol=[*[3+7+12*n for n in range(octavas)]]
        sol_s=[*[3+8+12*n for n in range(octavas)]]
        la=[0,*[3+9+12*n for n in range(octavas)]]
        la_s=[1,*[3+10+12*n for n in range(octavas)]]
        si=[2,*[3+11+12*n for n in range(octavas)]]
        progresion_piano=[do[0+1],
                          do[1+1],
                          sol[1+1],
                          do[2+1],
                          mi[2+1],
                          sol[2+1],
                          la_s[2+1+1],
                          do[3+1],
                          re[3+1],
                          mi[3+1],
                          fa_s[3+1],
                          sol[3+1],
                          la[3+1+1],
                          la_s[3+1+1],
                          si[3+1+1],
                          do[4+1]
                        ]
        teclas_coloreadas=VGroup(*[piano[i].copy()for i in progresion_piano])
        teclas_coloreadas.set_submobject_colors_by_gradient(TEAL,GREEN,YELLOW)




        self.play(GrowFromCenter(soporte),GrowFromCenter(soporte_espejo))
        self.play(ShowCreation(lineas_planas[0]))
        lista=[*range(12),42]
        teclas_coloreadas.set_stroke(BLACK,0.5)
        self.mandar_frente_sostenido_piano(piano)
        self.play(*[LaggedStart(GrowFromCenter,partitura[0][i])for i in lista],LaggedStart(FadeIn,piano))
        self.play(*[FadeIn(partitura[0][i])for i in [12,13]])

        for i in range(16):
            if i==0:
                    self.play(*[Write(partitura[0][u])for u in [14,15,16]],
                        Write(partitura[1][0]),
                        Escribe(frecuencias[0],color_orilla=TEAL),
                        Escribe(armonicos_texto[0],color_orilla=TEAL),
                        ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                        )
                    self.wait(2)
            if i==1:
                self.play(ReplacementTransform(partitura[0][16].copy(),partitura[0][17]),
                    Write(partitura[1][1]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ShowCreation(particiones[i-1])
                    )
                self.wait(2)
            if i==2:
                self.play(ReplacementTransform(partitura[0][17].copy(),partitura[0][18]),
                    Write(partitura[1][2]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==3:
                self.play(ReplacementTransform(partitura[0][18].copy(),partitura[0][20]),
                    Write(partitura[1][3]),
                    Write(partitura[0][19]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==4:
                self.play(ReplacementTransform(partitura[0][20].copy(),partitura[0][21]),
                    Write(partitura[1][4]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==5:
                self.play(ReplacementTransform(partitura[0][21].copy(),partitura[0][22]),
                    Write(partitura[1][5]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==6:
                self.play(ReplacementTransform(partitura[0][22].copy(),partitura[0][24]),
                    Write(partitura[1][6]),
                    Write(partitura[0][23]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==7:
                self.play(ReplacementTransform(partitura[0][24].copy(),partitura[0][25]),
                    Write(partitura[1][7]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==8:
                self.play(ReplacementTransform(partitura[0][25].copy(),partitura[0][26]),
                    Write(partitura[1][8]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==9:
                self.play(ReplacementTransform(partitura[0][26].copy(),partitura[0][27]),
                    Write(partitura[1][9]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==10:
                self.play(ReplacementTransform(partitura[0][27].copy(),partitura[0][29]),
                    Write(partitura[1][10]),
                    Write(partitura[0][28]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==11:
                self.play(ReplacementTransform(partitura[0][29].copy(),partitura[0][30]),
                    Write(partitura[1][11]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==12:
                self.play(ReplacementTransform(partitura[0][30].copy(),partitura[0][32]),
                    Write(partitura[1][12]),
                    Write(partitura[0][31]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==13:
                self.play(ReplacementTransform(partitura[0][32].copy(),partitura[0][35]),
                    Write(partitura[1][13]),
                    Write(partitura[0][33:35]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==14:
                self.play(ReplacementTransform(partitura[0][35].copy(),partitura[0][38]),
                    Write(partitura[1][14]),
                    Write(partitura[0][36:38]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            if i==15:
                self.play(ReplacementTransform(partitura[0][38].copy(),partitura[0][41]),
                    Write(partitura[1][15]),
                    Write(partitura[0][39:41]),
                    *[ReplacementTransform(frecuencias[i-1][j],frecuencias[i][j])for j in range(len(frecuencias[i]))],
                    *[ReplacementTransform(armonicos_texto[i-1][j],armonicos_texto[i][j])for j in range(len(armonicos_texto[i]))],
                    ReplacementTransform(piano[progresion_piano[i]],teclas_coloreadas[i]),
                    ReplacementTransform(particiones[i-2],particiones[i-1])
                    )
            self.mandar_frente_sostenido_piano(piano)
            if i<4:
                self.wait(4)
                lpr=lineas_planas[i].copy()
                for w in range(4):
                    self.play(Transform(lineas_planas[i],lineas_up[i]))
                    self.play(Transform(lineas_planas[i],lineas_down[i]))
                self.play(ReplacementTransform(lineas_planas[i],lpr),run_time=0.7)
                self.remove(lpr)
                self.add(lineas_planas[i+1])
            if i>=4:
                self.wait(0.5)

        self.wait()

    def Armonics(self,numero_armonicos,disminucion=False,amplitud=5,tamanho=12):
        conjunto_lineas=VGroup()
        particiones=VGroup()
        lineas_up=VMobject()
        contador_particiones=0
        lineas_down=VMobject()
        lineas_planas=VMobject()
        punto_referencia=ORIGIN+LEFT*tamanho/2
        for linea_v in [lineas_up,lineas_down,lineas_planas]:
            for i in range(numero_armonicos):
                cuerda=VGroup()
                for j in range(i+1):
                    particion=tamanho/(i+1)
                    punto_inicio=punto_referencia+RIGHT*j*particion
                    punto_final=punto_referencia+RIGHT*(j+1)*particion
                    linea=Line(punto_inicio,punto_final,buff=0)
                    for k in range(3):
                        linea.points[0]=linea.get_start()
                        if linea_v==lineas_up:
                            if disminucion==True:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,amplitud*np.sin(PI/2+PI*j)*0.5**i,0])
                            else:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,amplitud*np.sin(PI/2+PI*j),0])
                        if linea_v==lineas_down:
                            if disminucion==True:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,-amplitud*np.sin(PI/2+PI*j)*0.5**i,0])
                            else:
                                linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2+np.array([0,-amplitud*np.sin(PI/2+PI*j),0])
                        if linea_v==lineas_planas:
                            linea.points[1]=linea.points[0]+RIGHT*linea.get_length()/2
                        linea.points[2]=linea.get_end()
                    cuerda.add(linea)
                linea_v.add(cuerda)
                if i>0 and contador_particiones==0:
                    particion_parcial=VGroup()
                    for j in range(len(linea_v)-1):
                        linea_particion=DashedLine(cuerda[j].get_end(),cuerda[j].get_end()+UP)
                        linea_particion.shift(DOWN*linea_particion.get_length()/2)
                        particion_parcial.add(linea_particion)
                    particiones.add(particion_parcial)
            conjunto_lineas.add(linea_v)
            contador_particiones=contador_particiones+1
        return conjunto_lineas,particiones

    def importa_partitura(self):
        partitura=TikzMobject("""
            \\begin{music}
            \\parindent10mm
            \\instrumentnumber{1}
            \\setname1{} 
            \\setstaffs1{2}
            \\setclef16
            \\startextract
            \\NOtes\\wh{C}|\\en
            \\NOtes\\wh{'C}\\en
            \\NOtes\\wh{'G}\\en
            \\NOtes\\wh{c}\\en
            \\NOtes|\\wh{e}|\\en
            \\NOtes|\\wh{g}|\\en
            \\NOtes|\\wh{'_b}|\\en
            \\NOtes|\\wh{'c}|\\en
            \\NOtes|\\wh{'d}|\\en
            \\NOtes|\\wh{'e}|\\en
            \\NOtes|\\wh{'^f}|\\en
            \\NOtes|\\wh{'g}|\\en
            \\NOtes|\\wh{''a}|\\en
            \\NOtes|\\wh{''_b}|\\en
            \\NOtes|\\wh{''=b}|\\en
            \\NOtes|\\wh{''c}|\\en
            \\endextract
            \\end{music}
            """,stroke_width=0,fill_opacity=1,color=WHITE)
        numbers=VGroup()
        num_inicial=TexMobject("1").next_to(partitura[16],DOWN,buff=0.3)
        numbers.add(num_inicial)
        pos_y=num_inicial.get_center()[1]
        contador=2
        for n in [17,18,20,21,22,24,25,26,27,29,30,32,35,38,40]:
            pos_x=partitura[n].get_center()[0]
            numero=TexMobject("%d"%contador).move_to(np.array([pos_x,pos_y,0]))
            contador=contador+1
            numbers.add(numero)

        return VGroup(partitura,numbers)
        

class LogoUnam(Scene):
    CONFIG={
    "camera_config":{"background_color":BLACK}
    }
    def construct(self):
        Logo=SVGMobject("unam")
        Logo.set_height(FRAME_HEIGHT*1.6)
        self.play(DrawBorderThenFill(Logo,rate_func=linear,lag_ratio=0.1,run_time=4))
        self.wait(2)

class Presentacion(Scene):
    CONFIG={"camera_config":{"background_color":BLACK}}
    def construct(self):
        universidad=TextMobject("\\sc Universidad Nacional Autónoma de México",color=GOLD)
        asignatura=TextMobject("Seminario de Ingeniería")
        semestre=TextMobject("\\sf Semestre 2019-2")
        alumno=TextMobject("\\it Vázquez Zaldívar Daniel Alexander",color=YELLOW_B)
        nombre=TextMobject("\\tt ANÁLISIS DE ARMÓNICOS MUSICALES","USANDO LA TRANSFORMADA DE FOURIER").set_color(RED)
        ingenieria=TextMobject("Ingeniería Mecánica",color=BLUE)
        datos=VGroup(
                        universidad,
                        asignatura,
                        nombre[0],
                        nombre[1],
                        alumno,
                        semestre,
                        ingenieria
            )
        datos.arrange_submobjects(DOWN,buff=0.5)
        datos[0].shift(UP*3).scale(1.2)
        datos[1].shift(UP*2).scale(1.4)
        datos[2:4].shift(UP*0.7).scale(1.5)
        datos[4].shift(DOWN).scale(1.6)
        datos[5].shift(DOWN*2).scale(1.7)
        datos[6].shift(DOWN*3).scale(1.7)
        linea1=Line(nombre[0].get_corner(DL),nombre[0].get_corner(DR)).set_color(RED).shift(DOWN*0.1)
        linea2=Line(nombre[1].get_corner(DL),nombre[1].get_corner(DR)).set_color(RED).shift(DOWN*0.1)

        self.play(*[LaggedStart(Escribe,datos[i],rate_func=linear,color_orilla=datos[i].get_color())for i in range(len(datos))],
            )
        self.wait(7.7)
        self.play(GrowFromCenter(linea1),GrowFromCenter(linea2))
        self.wait(3)

class Pendiente(Scene):
    CONFIG={"camera_config":{"background_color":BLACK}}
    def construct(self):
        puntos=VGroup(*[Dot(color=WHITE)for i in range(5)])
        puntos.arrange_submobjects(RIGHT)
        puntos.to_corner(DOWN+LEFT).shift(DOWN*3.4)
        puntos.fade(0.7)
        self.play(FadeIn(puntos))
        for i in range(len(puntos)):
            self.play(Uncreate(puntos[-i-1]),run_time=1)
            self.wait()
        self.wait()

class Referencias(Scene):
    CONFIG={"camera_config":{"background_color":BLACK}}
    def construct(self):
        self.wait(2)
        datos=VGroup(
                        TextMobject("Referencias:"),
                        TextMobject("[1] {\\sc Dennis Zill}, {\\it Matemáticas avanzadas para Ingeniería}, 4ta Edición."),
                        TextMobject("[2] {\\sc Claudio Gabis}, {\\it Armonía Funcional}, 1ra Edición."),
                        TextMobject("[3] {\\sc Grant Sanderson}, {\\it Pero ¿qué es la Transformada de Fourier?}, Código."),
                        TextMobject("Programas utilizados:"),
                        TextMobject("[A] Adobe Audition CC."),
                        TextMobject("[B] Kdenlive."),
                        TextMobject("[C] Manim (Python 3, Cario, \\LaTeX, FFmpeg, SoX)."),

            ).scale(0.8)
        datos.arrange_submobjects(DOWN,buff=0.5,aligned_edge=LEFT)

        self.play(*[LaggedStart(Escribe,datos[i],rate_func=linear,color_orilla=datos[i].get_color())for i in range(len(datos))],
            )
        self.wait(5)
