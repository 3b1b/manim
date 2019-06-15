from manimlib.imports import *

#set_custom_quality(800,10)

class RedesEspanhol(Scene):
    def construct(self):
        self.redes_esp()

    def redes_esp(self):
        twitter = Twitter()
        reddits = Reddits()
        instagram = Instagram()
        patreon=Patreon()

        patreon[1].set_fill(BLACK)
        back_negro=patreon[1].copy().move_to(patreon[1])
        patreon.add(back_negro)

        redes_s=VGroup(*[obj.set_height(2)for obj in [patreon,reddits,twitter,instagram]])\
                .arrange_submobjects(RIGHT,buff=0.8)
        redes_s.move_to(ORIGIN)
        redes_f_pre=redes_s.copy()
        """ redes_f.arrange_submobjects(
            DOWN, aligned_edge=LEFT, buff=0.4
            ) """
        redes_f1=redes_f_pre[:2]
        redes_f2=redes_f_pre[2:]
        for redes_ in [redes_f1,redes_f2]:
            redes_.arrange(DOWN,buff=1.5)
        redes_f_pre2=VGroup(redes_f1,redes_f2).arrange(RIGHT,buff=7)
        redes_f=VGroup(*redes_f_pre).shift(UP*1.6)

        texto=VGroup(
            TextMobject("\\tt Theorem of Beethoven").set_color("#F96855"),
            TextMobject("\\tt r/ElteoremaDeBeethoven").match_color(reddits),
            TextMobject("\\tt @ElteoremadeB").match_color(twitter),
            TextMobject("\\tt ElteoremaDeBeethoven").set_color("#B52C94")
            )
        redes_f.to_edge(LEFT).scale(0.7).shift(LEFT*0.7)
        for i in range(len(texto)):
            texto[i].scale(0.8).next_to(redes_f[i],DOWN,buff=0.2)


        self.play(DrawBorderThenFill(redes_s),run_time=3)
        self.play(ReplacementTransform(redes_s,redes_f))
        self.wait(0.1)
        self.add_foreground_mobject(redes_f)
        circles=VGroup(*[Dot(redes_f[i].get_center(),color=WHITE,radius=twitter.get_width()*0.5).scale(0.9)for i in range(len(redes_f)-1)])
        texto.shift(RIGHT*2)
        punto=Dot(redes_f.get_center()).shift(RIGHT*2)
        vector=punto.get_center()[0]-redes_f.get_center()[0]
        circles.set_fill(None,0)
        self.add(circles)
        def update(grupo):
            for i in range(len(grupo)):
                grupo[i].move_to(redes_f[i+1].get_center())
                dif=(punto.get_center()[0]-grupo.get_center()[0])
                grupo.set_fill(WHITE,smooth(1-dif/vector))
                if i==0:
                    redes_f[i][-1].set_fill(WHITE,smooth(1-dif/vector))
            return grupo
        

        #self.play(FadeIn(circles))
        self.Oldplay(redes_f.shift,RIGHT*2,
            OldUpdateFromFunc(circles,update),
            *[Escribe(texto[i])for i in range(len(texto))])
        circles.set_fill(WHITE,1)
        self.add(circles)
        redes_fc=redes_f.copy()
        redes_fc.set_fill(opacity=0)
        redes_fc.set_stroke(WHITE,3)
        redes_fc[-1].set_stroke(BLACK,1.5)

        grupo_circulos=VGroup(*[Circle(color=WHITE).match_width(redes_fc[0])for x in range(4)])
        c=0
        for circulo in grupo_circulos:
            circulo.move_to(redes_fc[c].get_center())
            c+=1

        agradecimientos=Text("\\sc Agradecimientos\\\\ especiales a:",color=YELLOW)
        patreons=VGroup(
            Text("Guadalupe Martínez")
        )

        agradecimientos.move_to(LEFT*3)
        patreons.next_to(agradecimientos,DOWN)
        grupo_patreon=VGroup(agradecimientos,patreons).arrange(DOWN).to_edge(DOWN)
        #patreons.align_on_border(DOWN,buff=0)
        
        for x in range(2):
            self.play(
                ShowCreationThenDestruction(
                    grupo_circulos, 
                    time_width = 0.5,
                    run_time = 2,
                    rate_func=linear
                ),
                *[FadeIn(agradecimientos)for w in range(1) if x==0],
                *[Write(patreons)for w in range(1) if x==0]
            )

        self.wait(2)
        cuadro_negro=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(BLACK,0).set_stroke(None,0)
        self.add_foreground_mobject(cuadro_negro)
        self.play(cuadro_negro.set_fill,None,1)
        self.wait(5)

        #-----------------------------------
class RedesIngles(Scene):
    def construct(self):
        self.redes_ing()

    def redes_ing(self):
        twitter = Twitter()
        reddits = Reddits()
        instagram = Instagram()
        patreon=Patreon()

        patreon[1].set_fill(BLACK)
        back_negro=patreon[1].copy().move_to(patreon[1])
        patreon.add(back_negro)

        redes_s=VGroup(*[obj.set_height(2)for obj in [patreon,reddits,twitter,instagram]])\
                .arrange_submobjects(RIGHT,buff=0.8)
        redes_s.move_to(ORIGIN)
        redes_f_pre=redes_s.copy()
        """ redes_f.arrange_submobjects(
            DOWN, aligned_edge=LEFT, buff=0.4
            ) """
        redes_f1=redes_f_pre[:2]
        redes_f2=redes_f_pre[2:]
        for redes_ in [redes_f1,redes_f2]:
            redes_.arrange(DOWN,buff=1.5)
        redes_f_pre2=VGroup(redes_f1,redes_f2).arrange(RIGHT,buff=7)
        redes_f=VGroup(*redes_f_pre).shift(UP*1.6)

        texto=VGroup(
            TextMobject("\\tt Theorem of Beethoven").set_color("#F96855"),
            TextMobject("\\tt r/TheoremOfBeethoven").match_color(reddits),
            TextMobject("\\tt @ElteoremadeB").match_color(twitter),
            TextMobject("\\tt ElteoremaDeBeethoven").set_color("#B52C94")
            )
        redes_f.to_edge(LEFT).scale(0.7).shift(LEFT*0.7)
        for i in range(len(texto)):
            texto[i].scale(0.8).next_to(redes_f[i],DOWN,buff=0.2)


        self.play(DrawBorderThenFill(redes_s),run_time=3)
        self.play(ReplacementTransform(redes_s,redes_f))
        self.wait(0.1)
        self.add_foreground_mobject(redes_f)
        circles=VGroup(*[Dot(redes_f[i].get_center(),color=WHITE,radius=twitter.get_width()*0.5).scale(0.9)for i in range(len(redes_f)-1)])
        texto.shift(RIGHT*2)
        punto=Dot(redes_f.get_center()).shift(RIGHT*2)
        vector=punto.get_center()[0]-redes_f.get_center()[0]
        circles.set_fill(None,0)
        self.add(circles)
        def update(grupo):
            for i in range(len(grupo)):
                grupo[i].move_to(redes_f[i+1].get_center())
                dif=(punto.get_center()[0]-grupo.get_center()[0])
                grupo.set_fill(WHITE,smooth(1-dif/vector))
                if i==0:
                    redes_f[i][-1].set_fill(WHITE,smooth(1-dif/vector))
            return grupo
        

        #self.play(FadeIn(circles))
        self.Oldplay(redes_f.shift,RIGHT*2,
            OldUpdateFromFunc(circles,update),
            *[Escribe(texto[i])for i in range(len(texto))])
        circles.set_fill(WHITE,1)
        self.add(circles)
        redes_fc=redes_f.copy()
        redes_fc.set_fill(opacity=0)
        redes_fc.set_stroke(WHITE,3)
        redes_fc[-1].set_stroke(BLACK,1.5)

        grupo_circulos=VGroup(*[Circle(color=WHITE).match_width(redes_fc[0])for x in range(4)])
        c=0
        for circulo in grupo_circulos:
            circulo.move_to(redes_fc[c].get_center())
            c+=1

        agradecimientos=Text("\\sc Special thanks to:",color=YELLOW)
        patreons=VGroup(
            Text("Guadalupe Martínez")
        )

        agradecimientos.move_to(LEFT*3)
        patreons.next_to(agradecimientos,DOWN)
        grupo_patreon=VGroup(agradecimientos,patreons).arrange(DOWN).to_edge(DOWN)
        #patreons.align_on_border(DOWN,buff=0)
        
        for x in range(2):
            self.play(
                ShowCreationThenDestruction(
                    grupo_circulos, 
                    time_width = 0.5,
                    run_time = 2,
                    rate_func=linear
                ),
                *[FadeIn(agradecimientos)for w in range(1) if x==0],
                *[Write(patreons)for w in range(1) if x==0]
            )

        self.wait(2)
        cuadro_negro=Rectangle(width=FRAME_WIDTH,height=FRAME_HEIGHT).set_fill(BLACK,0).set_stroke(None,0)
        self.add_foreground_mobject(cuadro_negro)
        self.play(cuadro_negro.set_fill,None,1)
        self.wait(5)