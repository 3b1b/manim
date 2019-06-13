from manimlib.imports import *

set_custom_quality(800,10)

OUTPUT_DIRECTORY = "TESTS/ANIMATIONS_TESTS"

class AnimationTest(Scene):
	def construct(self):
		t=Text("Hola")
		self.Oldplay(Escribe(t))
		self.wait()

class TypeWriterScene(Scene):
    def construct(self):
        texto=Text("\\tt Ojalá funcione")[0]
        self.wait()
        KeyBoard(self,texto,lag=0.1)
        self.wait()