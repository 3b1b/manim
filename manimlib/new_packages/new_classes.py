# from manimlib.imports import *

# class CheckFormulaByTXT(Scene):
#     CONFIG={
#     "camera_config":{"background_color": BLACK},
#     "svg_type":"text",
#     "text": TexMobject(""),
#     "file":"",
#     "svg_scale":0.9,
#     "angle":0,
#     "flip_svg":False,
#     "fill_opacity": 1,
#     "remove": [],
#     "stroke_color": WHITE,
#     "fill_color": WHITE,
#     "stroke_width": 3,
#     "numbers_scale":0.5,
#     "show_numbers": True,
#     "animation": False,
#     "direction_numbers": UP,
#     "color_numbers": RED,
#     "space_between_numbers":0,
#     "show_elements":[],
#     "color_element":BLUE,
#     "set_size":"width",
#     "remove_stroke":[],
#     "show_stroke":[],
#     "warning_color":RED,
#     "stroke_":1
#     }
#     def construct(self):
#         self.imagen=self.text
#         self.imagen.set_width(FRAME_WIDTH)
#         if self.imagen.get_height()>FRAME_HEIGHT:
#             self.imagen.set_height(FRAME_HEIGHT)
#         self.imagen.scale(self.svg_scale)
#         if self.flip_svg==True:
#             self.imagen.flip()
#         if self.show_numbers==True:
#             self.print_formula(self.imagen.copy(),
#                 self.numbers_scale,
#                 self.direction_numbers,
#                 self.remove,
#                 self.space_between_numbers,
#                 self.color_numbers)

#         self.return_elements(self.imagen.copy(),self.show_elements)
#         for st in self.remove_stroke:
#             self.imagen[st].set_stroke(None,0)
#         for st in self.show_stroke:
#             self.imagen[st].set_stroke(None,self.stroke_)
#         if self.animation==True:
#             self.play(DrawBorderThenFill(self.imagen))
#         else:
#             c=0
#             for j in range(len(self.imagen)):
#                 permission_print=True
#                 for w in self.remove:
#                     if j==w:
#                         permission_print=False
#                 if permission_print:
#                     self.add(self.imagen[j])
#             c = c + 1
#         self.personalize_image()
#         self.wait()

#     def personalize_image(self):
#         pass

#     def print_formula(self,text,inverse_scale,direction,exception,buff,color):
#         text.set_color(self.warning_color)
#         self.add(text)
#         c = 0
#         for j in range(len(text)):
#             permission_print=True
#             for w in exception:
#                 if j==w:
#                     permission_print=False
#             if permission_print:
#                 self.add(text[j].set_color(self.stroke_color))
#         c = c + 1

#         c=0
#         for j in range(len(text)):
#             permission_print=True
#             element = TexMobject("%d" %c,color=color)
#             element.scale(inverse_scale)
#             element.next_to(text[j],direction,buff=buff)
#             for w in exception:
#                 if j==w:
#                     permission_print=False
#             if permission_print:
#                 self.add_foreground_mobjects(element)
#             c = c + 1 

#     def return_elements(self,formula,adds):
#         for i in adds:
#             self.add_foreground_mobjects(formula[i].set_color(self.color_element),
#                 TexMobject("%d"%i,color=self.color_element,background_stroke_width=0).scale(self.numbers_scale).next_to(formula[i],self.direction_numbers,buff=self.space_between_numbers))

