from manimlib.imports import *

set_custom_quality(1400,20)

OUTPUT_DIRECTORY = "TESTS/SVG_TESTS"

class CheckSpeach(CheckSVGPoints):
	CONFIG={
    "file":"mix/Speach.svg",
	"scale":1.5,
    "shadow_point_number":1,
	"show_element_points":[0],
    "get_cero":True,
	}

class CheckSpeach2(CheckSVGPoints):
    CONFIG={
    "svg_type":"custom",
    "scale":1.5,
    "shadow_point_number":1,
    "show_element_points":[0],
    }
    def custom_object(self):
        chat=SVGMobject("mix/speach2")[0]
        chat.move_to(ORIGIN)
        #custom
        chat.points[5:11] += UP*0.1
        chat.points[7:11] += UP*0.1
        chat.rotate(PI/2)
        return chat

class Conversacion(Scene):
    def construct(self):
        conversation = Conversation(self)
        conversation.add_bubble("Hola!")
        self.wait(2)
        conversation.add_bubble("Hola, qué tal?\\\\ como tas")
        self.wait(2)
        conversation.add_bubble("Esta es mi primera animación de\\\\ conversación.\\\\ para ver que tal")
        self.wait(3) # 41
        conversation.add_bubble("Está muy bien!")
        self.wait(2) # 48
        conversation.add_bubble("x")
        self.wait(2)
        #self.play(FadeOut(conversation.dialog[:]))
        self.wait()

class TestSVG(CheckSVG):
    CONFIG={
        "show_numbers":True
    }
    def custom_object(self):
        image=VGroup(*[Dot() for i in range(7)]).arrange(RIGHT)
        return image