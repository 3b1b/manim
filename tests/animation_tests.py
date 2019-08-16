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

class TimeTest(Scene):
	def print_time(self):
		print("Time:",round(self.time))

	def construct(self):
		dot=Dot()
		# 0 seconds
		self.print_time()
		self.play(Write(dot,run_time=2))
		# 2 second
		self.print_time()
		self.wait()
		# 3 seconds
		self.print_time()
		self.play(dot.shift,UP,run_time=1)
		# 4 seconds
		self.print_time()
		self.play(FadeToColor(dot,RED,run_time=3))
		# 7 seconds
		self.print_time()
		self.wait()
		# 8 seconds
		self.print_time()