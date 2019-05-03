from manimlib.imports import *
from active_projects.eop.reusable_imports import *



class RandyIsSickOrNot(Scene):


    def construct(self):
        title = TextMobject("1 in 200")
        title.to_edge(UP)

        
        randy = SicklyPiCreature()
        randy.set_height(3)
        randy.move_to(2*LEFT)
        randy.change_mode("plain")
        randy.set_color(BLUE)
        randy.save_state()

        self.add(randy)

        p_sick = TexMobject("p(","\\text{sick}",") = 0.5\%").scale(1.7)
        p_sick.set_color_by_tex("sick", SICKLY_GREEN)
        p_sick.next_to(randy, UP, buff = LARGE_BUFF)
        self.add(p_sick)
        self.wait()
        
        self.play(
            ApplyMethod(randy.get_slightly_sick, rate_func = there_and_back)
        )
        self.play(Blink(randy))
        self.wait(2)

        self.play(
            ApplyMethod(randy.get_sick)
        )

        self.play(Blink(randy))
        self.wait()

        self.play(randy.get_better)

        self.play(
            ApplyMethod(randy.get_slightly_sick, rate_func = there_and_back)
        )
        self.play(Blink(randy))
        self.wait(0.5)

        self.play(
            ApplyMethod(randy.get_sick)
        )
        
        self.play(Blink(randy))
        self.play(randy.get_better)
        self.wait(3)



class OneIn200HasDisease(Scene):
    def construct(self):
        title = TextMobject("1 in 200")
        title.to_edge(UP)
        creature = PiCreature()

        all_creatures = VGroup(*[
            VGroup(*[
                creature.copy()
                for y in range(20)
            ]).arrange(DOWN, SMALL_BUFF)
            for x in range(10)
        ]).arrange(RIGHT, SMALL_BUFF)
        all_creatures.set_height(FRAME_HEIGHT * 0.8)
        all_creatures.next_to(title, DOWN)
        randy = all_creatures[0][0]
        all_creatures[0].remove(randy)
        randy.change_mode("sick")
        randy.set_color(SICKLY_GREEN)
        randy.save_state()
        randy.set_height(3)
        randy.center()
        randy.change_mode("plain")
        randy.set_color(BLUE)

        self.add(randy)

        #p_sick = TexMobject("p(","\\text{sick}",") = 0.5\%")
        #p_sick.set_color_by_tex("sick", SICKLY_GREEN)
        #p_sick.next_to(randy, RIGHT+UP)
        #self.add(p_sick)
        self.wait()
        
        self.play(
            randy.change_mode, "sick",
            randy.set_color, SICKLY_GREEN
        )
        self.play(Blink(randy))
        self.play(randy.restore)
        self.wait()
        self.play(
            Write(title),
            LaggedStartMap(FadeIn, all_creatures, run_time = 3)
        )
        self.wait()
