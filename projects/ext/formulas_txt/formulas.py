from big_ol_pile_of_manim_imports import *
from io import *

class CheckFormulaByTXT(Scene):
    CONFIG={
    "camera_config":{"background_color": BLACK},
    "svg_type":"text",
    "text": TexMobject(""),
    "file":"",
    "svg_scale":0.9,
    "angle":0,
    "flip_svg":False,
    "fill_opacity": 1,
    "remove": [],
    "stroke_color": WHITE,
    "fill_color": WHITE,
    "stroke_width": 3,
    "numbers_scale":0.5,
    "show_numbers": True,
    "animation": False,
    "direction_numbers": UP,
    "color_numbers": RED,
    "space_between_numbers":0,
    "show_elements":[],
    "color_element":BLUE,
    "set_size":"width",
    "remove_stroke":[],
    "show_stroke":[],
    "warning_color":RED,
    "stroke_":1
    }
    def construct(self):
        self.imagen=self.text
        if self.set_size=="width":
            self.imagen.set_width(FRAME_WIDTH)
        else:
            self.imagen.set_height(FRAME_HEIGHT)
        self.imagen.scale(self.svg_scale)
        if self.flip_svg==True:
            self.imagen.flip()
        if self.show_numbers==True:
            self.print_formula(self.imagen.copy(),
                self.numbers_scale,
                self.direction_numbers,
                self.remove,
                self.space_between_numbers,
                self.color_numbers)

        self.return_elements(self.imagen.copy(),self.show_elements)
        for st in self.remove_stroke:
            self.imagen[st].set_stroke(None,0)
        for st in self.show_stroke:
            self.imagen[st].set_stroke(None,self.stroke_)
        if self.animation==True:
            self.play(DrawBorderThenFill(self.imagen))
        else:
            c=0
            for j in range(len(self.imagen)):
                permission_print=True
                for w in self.remove:
                    if j==w:
                        permission_print=False
                if permission_print:
                    self.add(self.imagen[j])
            c = c + 1
        self.personalize_image()
        self.wait()

    def personalize_image(self):
        pass

    def print_formula(self,text,inverse_scale,direction,exception,buff,color):
        text.set_color(self.warning_color)
        self.add(text)
        c = 0
        for j in range(len(text)):
            permission_print=True
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add(text[j].set_color(self.stroke_color))
        c = c + 1

        c=0
        for j in range(len(text)):
            permission_print=True
            element = TexMobject("%d" %c,color=color)
            element.scale(inverse_scale)
            element.next_to(text[j],direction,buff=buff)
            for w in exception:
                if j==w:
                    permission_print=False
            if permission_print:
                self.add_foreground_mobjects(element)
            c = c + 1 

    def return_elements(self,formula,adds):
        for i in adds:
            self.add_foreground_mobjects(formula[i].set_color(self.color_element),
                TexMobject("%d"%i,color=self.color_element,background_stroke_width=0).scale(self.numbers_scale).next_to(formula[i],self.direction_numbers,buff=self.space_between_numbers))


formulas=[]

a_color=RED_B
b_color=BLUE_B
c_color=GREEN_B
x_color=YELLOW_B

for i in range(1,17):
	formula_open=open("proy_ext/formulas_txt/formula%de.txt"%i,"r")
	formula=formula_open.readlines()
	formulas.append(TexMobject(*formula).scale(1.7))


for i in range(10):
	formulas[i].set_color_by_tex("a", a_color)
	formulas[i].set_color_by_tex("b", b_color)
	formulas[i].set_color_by_tex("c", c_color)
	formulas[i].set_color_by_tex("x", x_color)

colores_formulas=[
				(10,
					(
						(a_color,[10,25,31]),
						(b_color,[6,21]),
						(c_color,[26]),
						(x_color,[3]))
					),
				(11,
					(
						(a_color,[6,18,24]),
						(b_color,[3,14]),
						(c_color,[19]),
						(x_color,[0]))
					),
				(12,
					(
						(a_color,[7,18,24]),
						(b_color,[4,14]),
						(c_color,[19]),
						(x_color,[0]))
					),
				(13,
					(
						(a_color,[7,18,23]),
						(b_color,[4,14]),
						(c_color,[20]),
						(x_color,[0]))
					),
				(14,
					(
						(a_color,[13,18]),
						(b_color,[4,9]),
						(c_color,[15]),
						(x_color,[0]))
					),
]
for f,cambios in colores_formulas:
	for colores,simbolos in cambios:
		for simbolo in simbolos:
			formulas[f][simbolo].set_color(colores)

class ConfiguracionFormula11(CheckFormulaByTXT):
	CONFIG={
	"remove": [2,7,11,13,22,23],
	"text": formulas[11]
	}

class ConfiguracionFormula12(CheckFormulaByTXT):
	CONFIG={
	"remove": [],
	"text": formulas[12]
	}

class ConfiguracionFormula3(CheckFormulaByTXT):
	CONFIG={
	"remove": [],
	"text": formulas[3]
	}

class ConfiguracionFormula4(CheckFormulaByTXT):
	CONFIG={
	"remove": [],
	"text": formulas[4]
	}
