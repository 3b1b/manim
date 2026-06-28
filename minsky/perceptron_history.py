from manimlib import *
import numpy as np
# para ejecutar manimgl minsky/perceptron_history.py 
# para guardar el video manimgl minsky/perceptron_history.py ATimelinePerceptron --hd --write_file --file_name perceptron_high.mp4
# 1) LÍNEA DE TIEMPO DEL PERCEPTRÓN

class ATimelinePerceptron(Scene):
    def construct(self):
        # ========= PARÁMETROS =========
        TITLE_SIZE = 40
        SUBTITLE_SIZE = 26
        YEAR_FONT_SIZE = 21       # año grande debajo de la línea
        LABEL_FONT_SIZE = 18      # texto corto debajo del año
        DETAIL_TITLE_SIZE = 22    # título en la caja inferior
        DETAIL_BODY_SIZE = 18     # cuerpo en la caja inferior
        LINE_LENGTH = 10
        LINE_BUFF = 1.4
        LABEL_BUFF = 0.45
        DOT_RADIUS = 0.06
        # ==============================

        # ---------- TÍTULO ----------
        title = Text(
            "Del Perceptrón a las Redes Profundas",
            font_size=TITLE_SIZE
        ).to_edge(UP)

        subtitle = Text(
            "Rosenblatt, Minsky–Papert, CNN y Transformers",
            font_size=SUBTITLE_SIZE
        ).next_to(title, DOWN, buff=0.25)

        timeline_label = Text(
            "Línea de tiempo",
            font_size=22
        ).next_to(subtitle, DOWN, buff=0.25)

        self.wait(5.0)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN))
        self.play(FadeIn(timeline_label, shift=DOWN))
        self.wait(0.8)

        # ---------- LÍNEA DE TIEMPO ----------
        line = Line(
            ORIGIN - RIGHT * LINE_LENGTH / 2,
            ORIGIN + RIGHT * LINE_LENGTH / 2
        )
        line.next_to(timeline_label, DOWN, buff=LINE_BUFF)
        self.play(ShowCreation(line))

        # ---------- EVENTOS SOBRE LA LÍNEA ----------
        short_events = [
            ("1943",        "McCulloch &\nPitts"),
            ("1949",        "Donald Hebb"),
            ("1957–1962",   "Frank\nRosenblatt"),
            ("1969",        "Minsky &\nPapert"),
            ("1973",        "AI Winter\nLighthill"),
            ("1989",        "Cybenko &\nHornik"),
            ("1980s–2010s", "MLP,\nCNN"),
            ("2017",        "Vaswani\net al."),
        ]

        detail_titles = [
            "1943 – McCulloch & Pitts",
            "1949 – Donald O. Hebb",
            "1957–1962 – Frank Rosenblatt",
            "1969 – Marvin Minsky & Seymour Papert",
            "1973 – ‘AI Winter’ (Informe Lighthill)",
            "1989 – Teoremas de aproximación universal",
            "Años 1980–2010s",
            "2017 – Vaswani et al.",
        ]

        detail_bodies = [
            "“A Logical Calculus of the Ideas\n"
            "Immanent in Nervous Activity”.\n"
            "McCulloch & Pitts proponen el primer modelo\n"
            "matemático de la neurona basado en lógica booleana\n y disparo binario.",

            "“The Organization of Behavior:\n"
            "A Neuropsychological Theory”.\n"
            "Hebb propone que las conexiones entre neuronas\n"
            "se fortalecen con la experiencia y el aprendizaje.\nInspirando muchos métodos de ajuste de parámetros.",

            "Perceptron y “Principles of Neurodynamics”.\n"
            "Rosenblatt formaliza el perceptrón como máquina\n"  
            "de aprendizaje con pesos.\n"
            "Es una de las primeras redes neuronales \n"
            "capaces de aprender patrones a partir\n"
            "de ejemplos etiquetados.",

            "“Perceptrons: An Introduction to\n"
            "Computational Geometry”.\n"
            "Minsky y Papert demuestran las limitaciones\n"
            "de un modelo particular de perceptrón\n"
            "en la resolución de problemas no lineales.",

            "Informe de Sir James Lighthill para el\n"
            "Parlamento británico.\n"
            "Recortes de financiación y caída del interés\n"
            "por redes y sistemas de IA.",

            "Cybenko: “Approximation by superpositions\n"
            "of a sigmoidal function”.\n"
            "Hornik et al.: “Multilayer feedforward\n"
            "networks are universal approximators”.",

            "MLP profundos, Retropropagation,\n"
            "CNN y deep learning moderno.",

            "“Attention Is All You Need”.\n"
            "Transformers y comienzo de la era\n"
            "de los LLM modernos.",
        ]

        n = len(short_events)
        dots = VGroup()
        labels = VGroup()

        for i, (year_text, label_text) in enumerate(short_events):
            alpha = i / (n - 1)
            pos = line.get_left() + RIGHT * alpha * line.get_length()

            dot = Dot(pos, radius=DOT_RADIUS)
            dots.add(dot)

            year = Text(year_text, font_size=YEAR_FONT_SIZE)
            label = Text(label_text, font_size=LABEL_FONT_SIZE)

            label_group = VGroup(year, label).arrange(
                DOWN, aligned_edge=UP, buff=0.10
            )
            label_group.move_to(
                dot.get_center() + DOWN * LABEL_BUFF + DOWN * 0.2
            )

            labels.add(label_group)

        # puntos + etiquetas aparecen
        for d in dots:
            self.play(FadeIn(d), run_time=0.2)
        for lg in labels:
            self.play(Write(lg), run_time=1.0)

        self.wait(2.0)

        # ---------- CAJA DE DETALLE INFERIOR ----------
        detail_box = RoundedRectangle(
            width=10.5,
            height=2.6,
            corner_radius=0.15,
            color=WHITE,
            stroke_width=1.5,
        )
        detail_box.to_edge(DOWN, buff=0.4)

        # placeholders iniciales para título + abstract (lado derecho)
        detail_title = Text(" ", font_size=DETAIL_TITLE_SIZE, color=BLUE)
        detail_body = Text(" ", font_size=DETAIL_BODY_SIZE)

        detail_group = VGroup(detail_title, detail_body).arrange(
            DOWN, aligned_edge=LEFT, buff=0.15
        )
        detail_group.move_to(detail_box.get_center() + RIGHT * 2.0)

        # referencia (copia de la etiqueta) en el lado izquierdo del rectángulo
        ref_holder = [None]

        self.play(ShowCreation(detail_box))
        self.play(FadeIn(detail_group))
        self.wait(0.9)

        def show_detail(idx, color=WHITE):
            """Resalta un evento, baja una copia al rectángulo y muestra título+abstract."""
            nonlocal detail_group

            # Resaltar evento en la línea
            self.play(
                ApplyMethod(labels[idx].set_color, color),
                Indicate(labels[idx], scale_factor=1.03),
                run_time=1.0
            )

            # --- nueva referencia (copia de la etiqueta del timeline) ---
            new_ref = labels[idx].copy().scale(0.9)
            left_target = detail_box.get_left() + RIGHT * 1.6
            new_ref.move_to(
                np.array([left_target[0],
                          detail_box.get_center()[1],
                          0.0])
            )

            # --- nuevo título y abstract ---
            new_title = Text(
                detail_titles[idx],
                font_size=DETAIL_TITLE_SIZE,
                color=BLUE
            )
            new_body = Text(
                detail_bodies[idx],
                font_size=DETAIL_BODY_SIZE
            )
            new_group = VGroup(new_title, new_body).arrange(
                DOWN, aligned_edge=LEFT, buff=0.15
            )
            new_group.move_to(detail_box.get_center() + RIGHT * 2.0)

            # Animaciones acopladas:
            if ref_holder[0] is None:
                # Primera vez: copia que baja desde el timeline
                ref_holder[0] = new_ref
                self.add(ref_holder[0])
                self.play(
                    TransformFromCopy(labels[idx], ref_holder[0]),
                    Transform(detail_group, new_group),
                    run_time=10.0 # adjusted run_time for smoother transition abstract
                )
            else:
                # Siguientes veces: solo se transforma la referencia existente
                self.play(
                    Transform(ref_holder[0], new_ref),
                    Transform(detail_group, new_group),
                    run_time=10.0 # adjusted run_time for smoother transition abstract
                )

            self.wait(3.0)

        # ---------- RECORRER TODOS LOS EVENTOS ----------
        for idx in range(n):
            show_detail(idx)

        # ---------- LIMPIEZA (CAJA + REFERENCIA) ----------
        fade_anims = [FadeOut(detail_box), FadeOut(detail_group)]
        if ref_holder[0] is not None:
            fade_anims.append(FadeOut(ref_holder[0]))

        self.play(*fade_anims, run_time=1.2)
        self.wait(0.5)

        # ---------- ZOOM GEOMÉTRICO A 1957–1989 ----------
        # Grupos de interés:
        # Rosenblatt (2), Minsky–Papert (3), AI Winter (4), 1989 (5)
        focus_labels = VGroup(
            labels[2], labels[3], labels[4], labels[5]
        )
        focus_dots = VGroup(
            dots[2], dots[3], dots[4], dots[5]
        )
        focus_group = VGroup(line, focus_labels, focus_dots)

        # Resto de la línea para desvanecerlo
        rest_labels = VGroup(
            labels[0], labels[1], labels[6], labels[7]
        )
        rest_dots = VGroup(
            dots[0], dots[1], dots[6], dots[7]
        )
        rest_group = VGroup(rest_labels, rest_dots)

        # 1) Apagar lo que no es el tramo central
        self.play(FadeOut(rest_group), run_time=0.8)
        self.wait(0.3)

        # 2) Zoom "real": escalar y centrar el tramo de interés
        self.play(
            ApplyMethod(focus_group.scale, 1.6),
            ApplyMethod(focus_group.move_to, DOWN * 0.5),
            run_time=2.0,
            rate_func=smooth
        )
        self.wait(0.5)

        # ---------- RESALTADO FINAL ----------
        # Rosenblatt (2), Minsky–Papert (3),
        # AI Winter (4), 1989 (5), 2017 (7)
        self.play(
            ApplyMethod(labels[2].set_color, YELLOW),
            ApplyMethod(labels[3].set_color, RED),
            ApplyMethod(labels[4].set_color, ORANGE),
            ApplyMethod(labels[5].set_color, GREEN),
            #ApplyMethod(labels[7].set_color, BLUE),
            run_time=1.5
        )
        self.wait(2.0)


# 2) COMPARACIÓN ROSENBLATT vs MINSKY–PAPERT (según Block)
class BRosenblattVsMinskySplit(Scene):
    def construct(self):
        # ---------- TÍTULO ----------
        title = Text(
            "Dos concepciones de Perceptrón",
            font_size=40
        ).to_edge(UP)

        self.play(Write(title))
        self.wait(0.5)

        # ---------- CAJAS ----------
        left_box = RoundedRectangle(
            width=6.4,
            height=4.6,
            corner_radius=0.25
        )
        right_box = left_box.copy()

        left_box.shift(LEFT * 3.4 + DOWN * 0.1)
        right_box.shift(RIGHT * 3.4 + DOWN * 0.1)

        self.play(ShowCreation(left_box), ShowCreation(right_box))
        self.wait(0.3)

        # ======================================================
        #   SUBESCENARIO 1: COMPARACIÓN CONCEPTUAL (SOLO TEXTO)
        # ======================================================

        # --- Contenido conceptual Rosenblatt ---
        left_title_1 = Text(
            "Perceptron de Rosenblatt",
            font_size=28
        )

        left_bullets_1 = VGroup(
            Text("• Modelo de cerebro (capas A–B–C)", font_size=24),
            Text("• Varias capas, feedback", font_size=24),
            Text("• Aprendizaje y plasticidad", font_size=24),
            Text("• Conexiones aleatorias viables", font_size=24),
            Text("• Funciones perceptuales humanas", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        left_content_1 = VGroup(
            left_title_1,
            left_bullets_1
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.30)

        # --- Contenido conceptual Minsky–Papert ---
        right_title_1 = Text(
            "Perceptron de Minsky–Papert",
            font_size=28
        )

        right_bullets_1 = VGroup(
            Text("• Máquina fija de una capa", font_size=24),
            Text("• Predicados locales sobre la retina", font_size=24),
            Text("• Análisis de capacidad, no de aprendizaje", font_size=24),
            Text("• Predicados globales: paridad, conectividad", font_size=24),
            Text("• Parte de una 'Geometría computacional'", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        right_content_1 = VGroup(
            right_title_1,
            right_bullets_1
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.30)

        # Función para ajustar contenido a cada caja
        def fit_content_in_box(content, box, top_shift=0.1, margin=0.5):
            base_pos = box.get_center() + UP * top_shift
            content.move_to(base_pos)

            max_width = box.get_width() - 2 * margin
            max_height = box.get_height() - 2 * margin

            cur_width = content.get_width()
            cur_height = content.get_height()

            scale_factor = min(
                max_width / cur_width if cur_width > 0 else 1.0,
                max_height / cur_height if cur_height > 0 else 1.0,
                1.0
            )
            if scale_factor < 1.0:
                content.scale(scale_factor)
                content.move_to(base_pos)

        # Ajustar contenido conceptual
        fit_content_in_box(left_content_1, left_box)
        fit_content_in_box(right_content_1, right_box)

        # Mostrar contenido conceptual
        self.play(
            Write(left_content_1),
            Write(right_content_1),
            run_time=1.6
        )
        self.wait(0.8)

        # Texto y flecha de Block SOLO para esta primera parte
        quote_1 = Text(
            "Block (1970): el libro estudia\n"
            "un subconjunto muy restringido\n"
            "de los Perceptrons de Rosenblatt.",
            font_size=22,
        )
        quote_1.next_to(VGroup(left_box, right_box), DOWN, buff=0.8)

        arrow_1 = Arrow(
            start=quote_1.get_top() + UP * 0.05,
            end=right_box.get_bottom() + DOWN * 0.3,
            buff=0.2
        )

        self.play(FadeIn(quote_1, shift=UP), ShowCreation(arrow_1))
        self.wait(2.5)

        # ===========================================
        #   TRANSICIÓN: SE DESAPARECE ESCENARIO 1
        # ===========================================
        self.play(
            FadeOut(left_content_1),
            FadeOut(right_content_1),
            FadeOut(quote_1),
            FadeOut(arrow_1),
            run_time=1.2
        )
        self.wait(0.4)

        # ======================================================
        #   SUBESCENARIO 2: MODELOS MATEMÁTICOS + DESCRIPCIÓN
        # ======================================================

        # Subtítulo nuevo para marcar el cambio de nivel
        subtitle_2 = Text(
            "Formulación matemática de los modelos",
            font_size=28
        ).next_to(title, DOWN, buff=0.3)

        self.play(FadeIn(subtitle_2, shift=DOWN))
        self.wait(0.4)

        # --- Contenido matemático Rosenblatt ---
        left_title_2 = Text(
            "Perceptron de Rosenblatt",
            font_size=26
        )

        left_math_text = VGroup(
            Text("Capas A–B–C (sensores, asociadores, respuesta)", font_size=22),
            Text("Salida binaria con umbral:", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)

        left_formula_C = Tex(
            r"C = \mathbf{1}\Big\{\sum_j w_j a_j \ge \theta\Big\}",
            font_size=26
        )

        left_learning = VGroup(
            Text("Regla de aprendizaje (refuerzo):", font_size=22),
            Tex(r"w_j \leftarrow w_j + \eta\, a_j", font_size=26),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)

        left_content_2 = VGroup(
            left_title_2,
            left_math_text,
            left_formula_C,
            left_learning
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        # --- Contenido matemático Minsky–Papert ---
        right_title_2 = Text(
            "Perceptron de Minsky–Papert",
            font_size=26
        )

        right_math_text = VGroup(
            Text("Predicados locales φ_i(X) de orden finito", font_size=22),
            Text("Sin aprendizaje: pesos a_i fijos", font_size=22),
            Text("Salida binaria con umbral sobre predicados:", font_size=22),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.10)

        right_formula_psi = Tex(
            r"\psi(X) = \mathbf{1}\Big\{\sum_i a_i\,\phi_i(X) > \theta\Big\}",
            font_size=26
        )

        right_comment = Text(
            "Paridad y conectividad no son representables\n"
            "bajo estas restricciones.",
            font_size=22
        )

        right_content_2 = VGroup(
            right_title_2,
            right_math_text,
            right_formula_psi,
            right_comment
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)

        # Ajustar contenido matemático a las cajas
        fit_content_in_box(left_content_2, left_box)
        fit_content_in_box(right_content_2, right_box)

        # Mostrar contenido matemático
        self.play(
            Write(left_content_2),
            Write(right_content_2),
            run_time=1.8
        )
        self.wait(3)


# ------------------------------------------------------
#  ESCENA 1: PERCEPTRON DE ROSENBLATT (VISUAL + SIMPLE)
# ------------------------------------------------------

class RosenblattPerceptronVisual(Scene):
    def construct(self):
        # ---------- Título ----------
        title = Text(
            "Perceptron de Rosenblatt",
            font_size=46
        ).to_edge(UP, buff=0.1)

        subtitle = Text(
            "Modelo de cerebro S → A → R",
            font_size=30
        ).next_to(title, DOWN, buff=0.1)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=DOWN))
        self.wait(0.8)

        # ---------- DIAGRAMA S–A–R ----------
        S_neurons = VGroup(
            *[Circle(radius=0.15, color=RED) for _ in range(5)]
        ).arrange(DOWN, buff=0.35)
        S_neurons.shift(LEFT * 4 + DOWN * 1.0)

        A_neurons = VGroup(
            *[Circle(radius=0.17, color=RED) for _ in range(4)]
        ).arrange(DOWN, buff=0.45)
        A_neurons.shift(LEFT * 1.3 + DOWN * 1.0)

        R_neuron = Circle(radius=0.22, color=RED).shift(RIGHT * 2.5 + DOWN * 1.0)

        SA_lines = VGroup()
        for s in S_neurons:
            for a in A_neurons:
                SA_lines.add(Line(s.get_right(), a.get_left(), stroke_width=1.5))

        AR_lines = VGroup()
        for a in A_neurons:
            AR_lines.add(Line(a.get_right(), R_neuron.get_left(), stroke_width=2))

        S_label = Text("S-units\n(retina)", font_size=24).next_to(S_neurons, UP, buff=0.1)
        A_label = Text("A-units\n(asociación)", font_size=24).next_to(A_neurons, UP, buff=0.1)
        R_label = Text("R-unit\n(respuesta)", font_size=24).next_to(R_neuron, UP, buff=0.1)

        self.play(
            LaggedStart(*[FadeIn(n, scale=1.2) for n in S_neurons], lag_ratio=0.15),
            run_time=0.8
        )
        self.play(
            LaggedStart(*[FadeIn(n, scale=1.2) for n in A_neurons], lag_ratio=0.15),
            FadeIn(R_neuron, scale=1.2),
            run_time=1.0
        )
        self.play(
            ShowCreation(SA_lines),
            ShowCreation(AR_lines),
            FadeIn(S_label), FadeIn(A_label), FadeIn(R_label),
            run_time=1.2
        )
        self.wait(0.5)

        # ---------- BULLETS ----------
        bullets = VGroup(
            Text("• Red S → A → R inspirada en el córtex visual", font_size=20),
            Text("• S-units fijos; A→R con pesos modificables", font_size=20),
            Text("• R-unit decide la clase del estímulo", font_size=20),
            Text("• Aprendizaje por refuerzo corrige wᵢ", font_size=20),
        ).arrange(DOWN, buff=0.25)

        bullets.shift(UP * 0.3)
        bullets.to_corner(UR, buff=1.5)

        self.play(LaggedStart(*[Write(b) for b in bullets], lag_ratio=0.15))
        self.wait(0.6)

        # ---------- ECUACIÓN (versión LaTeX simplificada) ----------
        eq_main = Tex(
            r"f(S) = \text{sign}\Big(\sum_i w_i a_i\Big),"
            r"\quad a_i = \mathbf{1}\Big( \sum_j v_{ij} S_j \ge \theta_A \Big)"
        ).scale(0.5)

        eq_main.to_edge(DOWN, buff=0.7)

        # ----- EXPLICACIÓN DEL INDICADOR -----
        indicator_expl = Tex(
            r"\mathbf{1}(\text{condición}) = "
            r"\begin{cases}"
            r"1 & \text{si la condición es verdadera}\\"
            r"0 & \text{si la condición es falsa}"
            r"\end{cases}",
        ).scale(0.4)


        indicator_expl.next_to(eq_main, DOWN, buff=0.01)

        self.play(Write(eq_main))
        self.play(FadeIn(indicator_expl, shift=UP))
        self.wait(2.0)

#  ESCENA 2: PERCEPTRON DE MINSKY–PAPERT (VISUAL + SIMPLE)
#        TRANSICIÓN DESDE LA ESCENA ANTERIOR
# ------------------------------------------------------




###############################################################
# todo lo que sigue es nuevo y no esta revisado adecuadamente

###################################################
class MinskyPerceptronPhilosophy(Scene):
    def construct(self):
        # ================== TÍTULO GENERAL ==================
        title = Text(
            "Filosofía y Limitaciones del Perceptrón de Minsky–Papert",
            font_size=40
        ).to_edge(UP, buff=0.3)

        subtitle = Text(
            "Predicados locales, capacidad geométrica y límites globales",
            font_size=26
        ).next_to(title, DOWN, buff=0.15)

        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=DOWN))
        self.wait(0.6)

        # ----------------------------------------------------
        # Helper para dibujar una mini-retina cuadriculada
        # active_positions: lista de pares (i,j), 0..2
        # ----------------------------------------------------
        def build_mini_retina(center, active_positions):
            retina = Square(side_length=1.7, stroke_width=2.0)
            retina.move_to(center)

            grid_lines = VGroup()
            step = retina.get_width() / 3.0

            # líneas verticales y horizontales
            for k in range(1, 3):
                x = retina.get_left()[0] + k * step
                grid_lines.add(Line(
                    np.array([x, retina.get_bottom()[1], 0]),
                    np.array([x, retina.get_top()[1], 0]),
                    stroke_width=1.0
                ))
                y = retina.get_bottom()[1] + k * step
                grid_lines.add(Line(
                    np.array([retina.get_left()[0], y, 0]),
                    np.array([retina.get_right()[0], y, 0]),
                    stroke_width=1.0
                ))

            dots = VGroup()
            for (i, j) in active_positions:
                px = retina.get_left()[0] + (i + 0.5) * step
                py = retina.get_bottom()[1] + (j + 0.5) * step
                dots.add(Dot(np.array([px, py, 0]), radius=0.06))

            return VGroup(retina, grid_lines, dots)

        # ================== TEOREMA 3.1 – PARIDAD ==================
        t3_title = Text("Teorema 3.1 – Paridad", font_size=30)
        t3_title.next_to(subtitle, DOWN, aligned_edge=LEFT, buff=0.5)

        t3_text = Text(
            "Ningún perceptrón Σ aᵢ φᵢ(X) > θ puede decidir\n"
            "si el número de puntos activos en X es impar\n"
            "usando sólo predicados locales φᵢ(X).",
            font_size=24
        )
        t3_text.next_to(t3_title, DOWN, aligned_edge=LEFT, buff=0.25)

        # Dos patrones: uno impar (3 puntos), otro par (4 puntos)
        retina_odd = build_mini_retina(
            center=np.array([2.5, 0.6, 0]),
            active_positions=[(0, 0), (1, 1), (2, 2)]
        )
        retina_even = build_mini_retina(
            center=np.array([4.5, 0.6, 0]),
            active_positions=[(0, 0), (2, 0), (0, 2), (2, 2)]
        )

        label_odd = Tex(r"X_1:\ n(X_1)=3\ \text{(impar)}").scale(0.6)
        label_even = Tex(r"X_2:\ n(X_2)=4\ \text{(par)}").scale(0.6)
        label_odd.next_to(retina_odd, DOWN, buff=0.2)
        label_even.next_to(retina_even, DOWN, buff=0.2)

        # Caja de perceptrón local
        perc_box = Rectangle(width=2.4, height=1.2, stroke_width=2.0)
        perc_box.move_to(np.array([3.5, -1.2, 0]))
        perc_label = Tex(r"\text{Perceptrón local}").scale(0.75)
        perc_label.move_to(perc_box.get_center())

        arrow_odd = Arrow(retina_odd.get_bottom(), perc_box.get_top() + LEFT * 0.4,
                          buff=0.2, stroke_width=1.8)
        arrow_even = Arrow(retina_even.get_bottom(), perc_box.get_top() + RIGHT * 0.4,
                           buff=0.2, stroke_width=1.8)

        out_q = Tex(r"?").scale(1.1)
        out_q.next_to(perc_box, RIGHT, buff=0.3)

        eq_parity = Tex(
            r"\sum_i a_i\,\varphi_i(X) > \theta"
            r"\quad\text{no puede decidir }[n(X)\text{ es impar}]"
        ).scale(0.75)
        eq_parity.next_to(t3_text, DOWN, aligned_edge=LEFT, buff=0.75)

        t3_group = VGroup(
            t3_title, t3_text,
            retina_odd, retina_even, label_odd, label_even,
            perc_box, perc_label, arrow_odd, arrow_even, out_q,
            eq_parity
        )

        # Animación teorema 3.1
        self.play(Write(t3_title))
        self.play(Write(t3_text))
        self.play(
            FadeIn(retina_odd, shift=RIGHT),
            FadeIn(retina_even, shift=RIGHT),
            FadeIn(label_odd), FadeIn(label_even)
        )
        self.play(
            ShowCreation(perc_box),
            Write(perc_label),
            ShowCreation(arrow_odd),
            ShowCreation(arrow_even),
            Write(out_q)
        )
        self.play(Write(eq_parity))
        self.wait(3.0)

        self.play(FadeOut(t3_group), run_time=1.0)
        self.wait(0.4)

        # ================== TEOREMA 4.0 – AND/OR ==================
        t4_title = Text("Teorema 4.0 – And/Or", font_size=30)
        t4_title.next_to(subtitle, DOWN, aligned_edge=LEFT, buff=0.5)

        t4_text = Text(
            "Existen predicados ψ₁ y ψ₂ de orden 1 tales que\n"
            "ψ₁ ∧ ψ₂ y ψ₁ ∨ ψ₂ no son de orden finito.",
            font_size=24
        )
        t4_text.next_to(t4_title, DOWN, aligned_edge=LEFT, buff=0.25)

        # Cajitas ψ1 y ψ2
        psi1_box = Rectangle(width=1.7, height=0.7, stroke_width=2.0)
        psi2_box = psi1_box.copy()

        psi1_box.move_to(np.array([-1.0, 0.4, 0]))
        psi2_box.move_to(np.array([-1.0, -0.4, 0]))

        psi1_label = Tex(r"\psi_1(X)").scale(0.8).move_to(psi1_box.get_center())
        psi2_label = Tex(r"\psi_2(X)").scale(0.8).move_to(psi2_box.get_center())

        ord1_label = Text("orden 1", font_size=20)
        ord1_label.next_to(psi2_box, DOWN, buff=0.15)

        # Nodo AND y OR
        and_circle = Circle(radius=0.35, stroke_width=2.0).move_to(np.array([1.0, 0.5, 0]))
        or_circle = Circle(radius=0.35, stroke_width=2.0).move_to(np.array([1.0, -0.5, 0]))
        and_label = Tex(r"\land").scale(0.8).move_to(and_circle.get_center())
        or_label = Tex(r"\lor").scale(0.8).move_to(or_circle.get_center())

        arrow1_and = Arrow(psi1_box.get_right(), and_circle.get_left(), buff=0.15, stroke_width=1.8)
        arrow2_and = Arrow(psi2_box.get_right(), and_circle.get_left() + DOWN * 0.2,
                           buff=0.15, stroke_width=1.2)

        arrow1_or = Arrow(psi1_box.get_right(), or_circle.get_left() + UP * 0.2,
                          buff=0.15, stroke_width=1.2)
        arrow2_or = Arrow(psi2_box.get_right(), or_circle.get_left(), buff=0.15, stroke_width=1.8)

        # Salidas: ψ1∧ψ2 y ψ1∨ψ2 con aviso "orden infinito"
        out_and = Tex(r"\psi_1 \land \psi_2").scale(0.8)
        out_or = Tex(r"\psi_1 \lor \psi_2").scale(0.8)
        out_and.next_to(and_circle, RIGHT, buff=0.3)
        out_or.next_to(or_circle, RIGHT, buff=0.3)

        inf_label = Text("no de orden finito", font_size=22)
        inf_label.next_to(VGroup(out_and, out_or), DOWN, buff=0.2)

        t4_group = VGroup(
            t4_title, t4_text,
            psi1_box, psi2_box, psi1_label, psi2_label, ord1_label,
            and_circle, or_circle, and_label, or_label,
            arrow1_and, arrow2_and, arrow1_or, arrow2_or,
            out_and, out_or, inf_label
        )

        t4_group.shift(DOWN * 0.2)  # un poco más al centro

        # Animación teorema 4.0
        self.play(Write(t4_title))
        self.play(Write(t4_text))
        self.play(
            ShowCreation(psi1_box), ShowCreation(psi2_box),
            Write(psi1_label), Write(psi2_label), Write(ord1_label)
        )
        self.play(
            ShowCreation(and_circle), ShowCreation(or_circle),
            Write(and_label), Write(or_label)
        )
        self.play(
            ShowCreation(arrow1_and), ShowCreation(arrow2_and),
            ShowCreation(arrow1_or), ShowCreation(arrow2_or)
        )
        self.play(Write(out_and), Write(out_or), Write(inf_label))
        self.wait(3.0)

        self.play(FadeOut(t4_group), run_time=1.0)
        self.wait(0.4)

        # ================== TEOREMA 5.1 / 0.8 – CONECTIVIDAD ==================
        t5_title = Text("Teorema 5.1 / 0.8 – Conectividad", font_size=30)
        t5_title.next_to(subtitle, DOWN, aligned_edge=LEFT, buff=0.5)

        t5_text = Text(
            "El predicado ψ_CONNECTED(X) = “X es conexo”\n"
            "no es de orden finito; su orden crece con |R|.",
            font_size=24
        )
        t5_text.next_to(t5_title, DOWN, aligned_edge=LEFT, buff=0.25)

        # Retina con ejemplo conexo y no conexo
        retina_big = Square(side_length=2.4, stroke_width=2.0)
        retina_big.move_to(np.array([-2.3, -0.1, 0]))

        # componente conexa: un camino curvo
        conn_curve = VMobject(stroke_width=3.0)
        conn_curve.set_points_smoothly([
            retina_big.get_left() + RIGHT * 0.2 + UP * 0.3,
            retina_big.get_center() + UP * 0.4,
            retina_big.get_right() + LEFT * 0.2 + DOWN * 0.2
        ])

        # no conexo: dos discos
        d1 = Circle(radius=0.15, stroke_width=3.0).move_to(retina_big.get_center() + LEFT * 0.4 + DOWN * 0.4)
        d2 = Circle(radius=0.15, stroke_width=3.0).move_to(retina_big.get_center() + RIGHT * 0.5 + DOWN * 0.1)

        conn_label = Text("X conexo", font_size=20)
        disc_label = Text("X desconexo", font_size=20)
        conn_label.next_to(conn_curve, UP, buff=0.2)
        disc_label.next_to(d2, DOWN, buff=0.15)

        # Caja ψ_CONNECTED
        psi_box = Rectangle(width=2.3, height=1.0, stroke_width=2.0)
        psi_box.move_to(np.array([1.0, -0.1, 0]))
        psi_label = Tex(r"\psi_{\text{CONNECTED}}(X)").scale(0.8).move_to(psi_box.get_center())

        arrow_retina = Arrow(retina_big.get_right(), psi_box.get_left(), buff=0.2, stroke_width=1.8)

        grow_text = Text(
            "orden necesario ↑ cuando |R| crece",
            font_size=22
        )
        grow_text.next_to(psi_box, DOWN, buff=0.2)

        # Pequeño toro para sugerir la retina como variedad
        outer = Ellipse(width=2.2, height=1.3, stroke_width=2.0)
        inner = Ellipse(width=1.0, height=0.55, stroke_width=2.0)
        torus_grid = VGroup()
        for x in np.linspace(-0.8, 0.8, 3):
            torus_grid.add(Line(
                np.array([x, -0.5, 0]),
                np.array([x, 0.5, 0]),
                stroke_width=1.0
            ))
        for y in np.linspace(-0.3, 0.3, 2):
            torus_grid.add(Line(
                np.array([-1.0, y, 0]),
                np.array([1.0, y, 0]),
                stroke_width=1.0
            ))
        torus = VGroup(outer, inner, torus_grid)
        torus.scale(0.9)
        torus.move_to(np.array([3.7, -0.1, 0]))

        torus_label = Text(
            "Retina R como toro:\n"
            "propiedades globales viven\n"
            "en un espacio geométrico mayor.",
            font_size=20
        )
        torus_label.next_to(torus, DOWN, buff=0.2)

        t5_group = VGroup(
            t5_title, t5_text,
            retina_big, conn_curve, d1, d2,
            conn_label, disc_label,
            psi_box, psi_label, arrow_retina,
            grow_text,
            torus, torus_label
        )

        # Animación teorema 5.1 / 0.8
        self.play(Write(t5_title))
        self.play(Write(t5_text))
        self.play(ShowCreation(retina_big))
        self.play(ShowCreation(conn_curve), ShowCreation(d1), ShowCreation(d2))
        self.play(Write(conn_label), Write(disc_label))
        self.play(ShowCreation(psi_box), Write(psi_label), ShowCreation(arrow_retina))
        self.play(Write(grow_text))
        self.play(FadeIn(torus), FadeIn(torus_label, shift=UP))
        self.wait(3.0)

        self.play(FadeOut(t5_group), FadeOut(title), FadeOut(subtitle), run_time=1.5)
        self.wait(0.5)




# material descartado o extra
#################
# 3) PERCEPTRÓN SIMPLE (MODELO MATEMÁTICO)
class CSimplePerceptron(Scene):
    def construct(self):
        title = Text("Perceptrón simple", font_size=40).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Entradas x1, x2, x3
        x_labels = VGroup(
            Tex("x_1"),
            Tex("x_2"),
            Tex("x_3"),
        ).arrange(DOWN, buff=0.6)
        x_labels.shift(LEFT * 4)

        # Neurona
        neuron = Circle(radius=0.7)
        neuron.shift(RIGHT * 0.5)

        y_label = Tex("y = \\text{sign}(w \\cdot x + b)")\
            .next_to(neuron, RIGHT, buff=1.0)

        # Conexiones
        lines = VGroup()
        for xl in x_labels:
            lines.add(Line(xl.get_right(), neuron.get_left()))

        for x in x_labels:
            self.play(Write(x), run_time=0.2)

        for l in lines:
            self.play(ShowCreation(l), run_time=0.2)

        self.play(ShowCreation(neuron), Write(y_label))
        self.wait(1)

        # Mostrar pesos y suma
        w_text = Tex("w = (w_1, w_2, w_3)").to_edge(DOWN).shift(LEFT * 2)
        b_text = Tex("b").next_to(w_text, RIGHT, buff=1.5)
        dot_text = Tex("w \\cdot x + b").next_to(neuron, UP, buff=0.8)

        self.play(Write(w_text), Write(b_text))
        self.play(Write(dot_text))
        self.wait(2)

        # Animación con valores concretos
        example = Tex(
            "w = (1, -2, 1),\\ x=(1,1,0) \\Rightarrow "
            "w\\cdot x + b = -1 + b"
        ).scale(0.7).next_to(w_text, UP, buff=0.4)

        self.play(Write(example))
        self.wait(3)

# 3.1 Timeline de la vida de Minsky

class MinskyLifeTimeline(Scene):
    def construct(self):
        # Título
        title = Text(
            "Marvin Minsky – Vida e influencia",
            font_size=40
        ).to_edge(UP)

        subtitle = Text(
            "Breve cronología personal e intelectual",
            font_size=26
        ).next_to(title, DOWN, buff=0.25)

        self.play(Write(title), FadeIn(subtitle, shift=DOWN))
        self.wait(1)

        # Línea de tiempo
        line = Line(LEFT * 5, RIGHT * 5)
        line.next_to(subtitle, DOWN, buff=1.2)
        self.play(ShowCreation(line))

        # Eventos clave (puedes ajustar años/texto)
        events = [
            "1927\nNace en Nueva York",
            "1951\nPhD en Princeton",
            "1959\nCo-funda el MIT AI Lab",
            "1969\nPublica Perceptrons",
            "1986\nThe Society of Mind",
            "2016\nFallece en Boston",
        ]

        n = len(events)
        dots = VGroup()
        labels = VGroup()

        for i, text in enumerate(events):
            alpha = i / (n - 1)
            pos = line.get_left() + RIGHT * alpha * line.get_length()
            dot = Dot(pos)
            dots.add(dot)

            label = Text(text, font_size=22)\
                .next_to(dot, DOWN, buff=0.35)
            labels.add(label)

        # Aparecen puntos y etiquetas
        for d in dots:
            self.play(FadeIn(d), run_time=0.2)
        for l in labels:
            self.play(Write(l), run_time=0.25)

        self.wait(1.5)

        # Resaltar "Perceptrons" y "Society of Mind"
        perceptrons_label = labels[3]
        society_label = labels[4]

        self.play(
            ApplyMethod(perceptrons_label.set_color, YELLOW),
            Indicate(perceptrons_label)
        )
        self.wait(1)

        self.play(
            ApplyMethod(society_label.set_color, BLUE),
            Indicate(society_label)
        )
        self.wait(2)


# 3.2 Grafo de influencias de Minsky

class MinskyInfluenceGraph(Scene):
    def construct(self):
        title = Text(
            "Constelación intelectual de Minsky",
            font_size=40
        ).to_edge(UP)

        self.play(Write(title))
        self.wait(0.5)

        # Nodo central: Minsky
        center = Circle(radius=0.7, color=YELLOW)
        center_text = Text("Minsky", font_size=28).move_to(center.get_center())

        self.play(ShowCreation(center), FadeIn(center_text))
        self.wait(0.5)

        # Nodos alrededor (maestros y colegas)
        # Puedes ajustar nombres según tus PDFs
        names = [
            "Norbert\nWiener",
            "J. C. R.\nLicklider",
            "George\nMiller",
            "John\nMcCarthy",
            "Seymour\nPapert",
            "Newell\n& Simon",
        ]

        radius = 3.0
        outer_nodes = VGroup()
        outer_labels = VGroup()
        edges = VGroup()

        for k, name in enumerate(names):
            angle = 2 * np.pi * k / len(names)
            pos = center.get_center() + radius * np.array([np.cos(angle), np.sin(angle), 0])

            node = Circle(radius=0.5, color=WHITE).move_to(pos)
            label = Text(name, font_size=22).move_to(pos)

            edge = Line(center.get_edge_center(direction=pos - center.get_center()),
                        node.get_edge_center(direction=center.get_center() - pos))

            outer_nodes.add(node)
            outer_labels.add(label)
            edges.add(edge)

        # Aparecen conexiones una por una
        for e, n, lbl in zip(edges, outer_nodes, outer_labels):
            self.play(ShowCreation(e), ShowCreation(n), FadeIn(lbl), run_time=0.6)

        self.wait(1.5)

        # Agrupar por "maestros" y "colegas" con colores
        # (ejemplo simple: los 3 primeros = maestros, 3 últimos = colegas)
        maestros = outer_labels[:3]
        colegas = outer_labels[3:]

        self.play(*[ApplyMethod(m.set_color, GREEN) for m in maestros])
        maestros_title = Text("Maestros / influencia temprana", font_size=24)\
            .to_edge(LEFT).shift(DOWN * 2.5)
        self.play(FadeIn(maestros_title, shift=RIGHT))
        self.wait(0.5)

        self.play(*[ApplyMethod(c.set_color, BLUE) for c in colegas])
        colegas_title = Text("Colegas en IA y MIT", font_size=24)\
            .to_edge(RIGHT).shift(DOWN * 2.5)
        self.play(FadeIn(colegas_title, shift=LEFT))
        self.wait(2.5)



# 4) INTUICIÓN DE CNN (CONVOLUCIÓN)
class CNNKernel(Scene):
    def construct(self):
        title = Text("Idea básica de una CNN", font_size=40).to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)

        # Rejilla de "imagen"
        grid_size = 5
        cell_size = 0.6

        squares = VGroup()
        for i in range(grid_size):
            for j in range(grid_size):
                sq = Square(side_length=cell_size)
                sq.shift(
                    RIGHT * (j - grid_size / 2) * cell_size * 1.1 +
                    DOWN * (i - grid_size / 2) * cell_size * 1.1
                )
                squares.add(sq)

        squares.shift(LEFT * 2.5 + DOWN * 0.3)

        self.play(ShowCreation(squares), run_time=1.5)
        self.wait(0.5)

        # Kernel 3x3 (primer bloque 3x3 de la rejilla)
        first_block = VGroup(*[s for s in squares[:9]])
        kernel = SurroundingRectangle(
            first_block,
            buff=0.05,
            color=YELLOW
        )

        kernel_label = Text("Filtro 3×3 (kernel)", font_size=24)\
            .next_to(kernel, UP, buff=0.3)

        self.play(ShowCreation(kernel), FadeIn(kernel_label))
        self.wait(0.5)

        # Animar el movimiento del kernel (tipo escaneo)
        targets = []
        for offset in [0, 3, 6]:
            block = VGroup(*[
                squares[i + offset] for i in [0, 1, 2, 5, 6, 7, 10, 11, 12]
            ])
            targets.append(block)

        for block in targets[1:]:
            self.play(ApplyMethod(kernel.surround, block, buff=0.05), run_time=1.0)

        self.wait(0.5)

        text_local = Text(
            "Detección local de patrones\n(bordes, texturas, etc.)",
            font_size=24
        ).to_edge(RIGHT).shift(UP * 0.5)

        text_global = Text(
            "Varias capas → representación global",
            font_size=24
        ).next_to(text_local, DOWN, buff=0.5)

        self.play(FadeIn(text_local, shift=LEFT),
                  FadeIn(text_global, shift=LEFT))
        self.wait(3)
