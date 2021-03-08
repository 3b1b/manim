from manimlib import *
import platform
 
sys_str = platform.system()
if sys_str == "Windows":
    Font = '阿里巴巴普惠体 B'
elif sys_str == "Darwin":
    Font = 'Microsoft YaHei Bold'
else:
    Exception("未匹配的操作系统")

def ObjAnd2Text(Obj, text1, text2, dframe=0.2, txt_height=0.28, OS_font=Font, obj_height=4):
    if isinstance(Obj,VMobject):
        pic = Rectangle(
            height = Obj.get_height() + 0.618,
            width = Obj.get_width() + 1.2,
            stroke_color = BLACK,
            fill_color = BLACK,
            fill_opacity = 0.618,
            ).move_to(Obj)
    else:
        pic = ImageMobject(Obj,height=obj_height)
    picText1 = Text(text1,
                    font=Font,
                    color="#308032"
        )\
        .set_height(txt_height-0.06)\
        .next_to(pic,DOWN,buff=SMALL_BUFF)
    picText2 = Text(text2,
                    font=Font, 
                    color=BLACK,
        )\
        .set_height(txt_height)\
        .next_to(picText1,DOWN,buff=SMALL_BUFF)
    picAndText = Group(pic,picText1,picText2).center()
    pic.rect = RoundedRectangle(
                    corner_radius=0.1,
                    color="#DDDDDD",
                    stroke_opacity = 0,
                    fill_color = "#DDDDDD",
                    fill_opacity = 1,
                    height=picAndText.get_height()+dframe,
                    width=picAndText.get_width()+dframe
        )
    VGroup(picText1,picText2).move_to((pic.get_bottom()+pic.rect.get_bottom())/2)
    return Group(pic.rect,pic,picText1,picText2)

def ObjAnd1Text(Obj, text2, dframe=0.2, txt_height=0.28, OS_font=Font, obj_height=4):
    if isinstance(Obj,VMobject):
        pic = Rectangle(
            height = Obj.get_height() + 0.618,
            width = Obj.get_width() + 1,
            stroke_color = BLACK,
            fill_color = BLACK,
            fill_opacity = 1,
            ).move_to(Obj)
    else:
        pic = ImageMobject(Obj,height=obj_height)
    picText2 = Text(text2, 
                    font=Font,
                    color=BLACK,
        )\
        .set_height(txt_height)\
        .next_to(pic, DOWN, buff=dframe-0.05)
    
    picAndText = Group(pic,picText2)
    pic.rect = RoundedRectangle(
                    corner_radius=0.1,
                    color="#DDDDDD",
                    stroke_opacity = 0,
                    fill_color = "#DDDDDD",
                    fill_opacity = 1,
                    height=picAndText.get_height()+dframe,
                    width=picAndText.get_width()+dframe
        ).move_to(picAndText)
    picText2.move_to((pic.get_bottom()+pic.rect.get_bottom())/2)
    return Group(pic.rect,pic,picText2)

def palyALL2(self,allParts):
    self.play(
        FadeIn(allParts[:2],scale=0.5),
        FadeIn(allParts[2],shift=TOP,scale=0.5),
        )
    self.play(Write(allParts[3]))
    self.wait(10)
    self.play(FadeOutAndShiftDown(allParts))

def palyALL1(self,allParts):
    self.play(
        FadeIn(allParts[:2],scale=0.5),
        )
    self.play(Write(allParts[2]))        
    self.wait(10)
    self.play(FadeOutAndShiftDown(allParts))

class FadeOutAndShift(FadeOut):
    CONFIG = {
        "direction": DOWN,
    }

    def __init__(self, mobject, direction=None, **kwargs):
        if direction is not None:
            self.direction = direction
        super().__init__(mobject, **kwargs)

    def create_target(self):
        target = super().create_target()
        target.shift(self.direction)
        return target

class FadeOutAndShiftDown(FadeOutAndShift):
    """
    Identical to FadeOutAndShift, just with a name that
    communicates the default
    """
    CONFIG = {
        "direction": DOWN,
    }