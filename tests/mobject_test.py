from manimlib.imports import *

set_custom_quality(800,20)

OUTPUT_DIRECTORY = "TESTS/MOBJECTS_TESTS"

class MobjectTest(Scene):
    def construct(self):
        width=2
        height=4
        #patron=Patron(width,height)
        oldpatron=OldPatron(width,height)
        square=Rectangle(width=width,height=height)
        self.add(square,oldpatron)

class MobjectTest2(Scene):
    def construct(self):
        width=ValueTracker(2)
        height=ValueTracker(4)
        end_width=3
        end_height=6
        #patron=Patron(width,height)
        pattern=RectanglePattern(width.get_value(),height.get_value())
        def update_pattern(mob):
            mob.become(RectanglePattern(width.get_value(),height.get_value()))
        
        self.add(pattern)
        self.wait()
        self.play(
            width.set_value,end_width,
            height.set_value,end_height,
            UpdateFromFunc(pattern,update_pattern)
            )
        self.wait()

class MobjectTest3(Scene):
    def construct(self):
        width=ValueTracker(2)
        height=ValueTracker(4)
        end_width=6
        end_height=3
        #patron=Patron(width,height)
        pattern=RectanglePattern(width.get_value(),height.get_value())
        def update_pattern(mob):
            mob.replace(RectanglePattern(width.get_value(),height.get_value()))
        
        self.add(pattern)
        self.wait()
        self.play(
            width.set_value,end_width,
            height.set_value,end_height,
            UpdateFromFunc(pattern,update_pattern)
            )
        self.wait()

class PatternExample(Scene):
    def construct(self):
        pattern_1=RectanglePattern(4,2)
        self.play(
            LaggedStart(*[ShowCreation(pat) for pat in pattern_1])
            )
        self.wait()