from big_ol_pile_of_manim_imports import *

class UsingBracesConcise(Scene):
#A more concise block of code with all columns aligned
	def construct(self):
		eq1_text=["4","x","+","3","y","=","0"]
		eq2_text=["5","x","-","2","y","=","3"]
		eq1_mob=TexMobject(*eq1_text)
		eq2_mob=TexMobject(*eq2_text)
		eq1_mob.set_color_by_tex_to_color_map({
		"x":RED_B,
		"y":GREEN_C
		})
		eq2_mob.set_color_by_tex_to_color_map({
		"x":RED_B,
		"y":GREEN_C
		})
		for i,item in enumerate(eq2_mob):
			item.align_to(eq1_mob[i],LEFT)
		eq1=VGroup(*eq1_mob)
		eq2=VGroup(*eq2_mob)
		eq2.shift(DOWN)
		eq_group=VGroup(eq1,eq2)
		braces=Brace(eq_group,LEFT)
		eq_text = braces.get_text("Some Shitty text lol")
		 
		self.play(Write(eq1),Write(eq2))
		self.play(GrowFromCenter(braces),Write(eq_text))