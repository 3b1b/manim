from manimlib.imports import *
'''
Codigo por Miroslav Olsak
https://github.com/mkoconnor/manim
https://www.youtube.com/user/procdalsinazev/feed
'''

class ChatBubble(VMobject):
	CONFIG = {
	"answer_color":GREEN_B,
	"response_color":BLUE_B,
	"background_chat_opacity":0.95,
	"background_chat_color":ORANGE,
	"match_background_color":True,
	"text_color":WHITE,
	"answer_message_t":False,
	"response_message_t":False,
    }
	def __init__(self, text, answer_bubble = False, border = 0.3,**kwargs):
		VMobject.__init__(self, **kwargs)
		self.answer_bubble = answer_bubble

		self.bubble = SVGMobject(file_name = "mix/Speach.svg",
         initial_scale_factor = 0.02,
         unpack_groups= True
         )[0]
		#self.bubble.set_fill(BLACK, opacity = background_chat_opacity)

		if answer_bubble: self.bubble.set_stroke(self.answer_color)
		else: self.bubble.set_stroke(self.response_color)

		if self.match_background_color:
			if answer_bubble: self.bubble.set_fill(self.answer_color,opacity = self.background_chat_opacity)
			else: self.bubble.set_fill(self.response_color,opacity = self.background_chat_opacity)
		else:
			self.bubble.set_fill(self.background_chat_color, opacity = self.background_chat_opacity)

		self.text = TextMobject(text, alignment="\\raggedright\\hsize = 0.7\\hsize",color=self.text_color)
		#print(self.text.get_tex_string())
		self.tip_h = self.bubble.points[16,1] - self.bubble.points[20,1]
		self.text.move_to(self.bubble.get_corner(LEFT+DOWN)+np.array([border,self.tip_h+border,0]), aligned_edge = LEFT+DOWN)
		size_shift = self.text.get_corner(UP+RIGHT) - self.bubble.get_corner(UP+RIGHT) + border
		shift_w = size_shift[0];print("[%f]"%(self.tip_h))
		shift_h = size_shift[1];print(*size_shift)
		for p in self.bubble.points[26:]: p[0] += shift_w
		#for p in self.bubble.points[-10:16]: p[1] += shift_h
		#for p in self.bubble.points[-36:13]: p[1] += shift_h
		self.add(self.bubble, self.text)

		if answer_bubble:
		    self.center()
		    self.bubble.scale([-1,1,1])
		    self.to_corner(RIGHT+DOWN)
		else:
		    self.to_corner(LEFT+DOWN)

def stretch_rate_func(f):
    f0 = f(0)
    f1 = f(1)
    def result(t):
        return (f(t)-f0)/(f1-f0)
    return result

class Conversation:
	def __init__(self, scene, start_answer = True,
		answer_color=GREEN_B,response_color=BLUE_B,
		background_chat_opacity=0.95,
		match_background_color=True,
		background_chat_color=BLACK,
		answer_message=False,
		response_message=False,
		text_color=BLACK,**kwargs):
		self.a_c=answer_color
		self.r_c=response_color
		self.b_c_o=background_chat_opacity
		self.m_b_c=match_background_color
		self.t_c=text_color
		self.b_c=background_chat_color
		self.scene = scene
		self.dialog = VGroup()
		self.next_answer = start_answer
		self.ad=answer_message,
		self.rd=response_message,

	def add_bubble(self, text, answer_bubble = True,**kwargs):
		#ChatBubble.__init__(self, text,**kwargs)
		bubble = ChatBubble(text, self.next_answer,
			answer_color=self.a_c,
			response_color=self.r_c,
			background_chat_opacity=self.b_c_o,
			match_background_color=self.m_b_c,
			text_color=self.t_c,
			background_chat_color=self.b_c,
			answer_message_t=self.ad,
			response_message_t=self.rd,
			**kwargs)
		self.next_answer = not self.next_answer

		height = bubble.get_height()
		shift = height - bubble.tip_h + 0.2
		dialog_target = self.dialog.copy()
		dialog_target.shift([0, shift, 0])
		bubble[0].set_stroke(None,0)
		#bubble.set_fill(opacity=0.7)
		#bubble.set_fill(bubble[0].get_color())
		bubble_target = bubble.copy()
		bubble.scale([1, 0, 1], about_point = np.array([0, -4.0, 0]))

		def dialog_rate_func(t):
		    bubble_rate = rush_from(t)
		    bubble_rel_pos = (bubble_rate - 1) * height / shift + 1
		    return np.exp(bubble_rel_pos-1)

		self.scene.play(Transform(self.dialog, dialog_target, rate_func = bezier([0, 0, 0.5, 1]),run_time=0.3),
		                Transform(bubble, bubble_target, rate_func = bezier([0, 0, 0.5, 1]),run_time=0.3),
		                )
		'''
		else:
			self.scene.play(Transform(self.dialog, dialog_target, rate_func = stretch_rate_func(dialog_rate_func)),
		                Transform(bubble, bubble_target, rate_func = rush_from))
		'''
		self.dialog.add(bubble)
        #self.scene.add(bubble)
