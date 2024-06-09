'''
Created by: Pranay Rishi Nalem
Date: June 8th, 2024 Time: 10:50 PM PST
Program Name: MathQuest Animations
Purpose: KTHack 2024
'''
from manim import *


class trigFunctionProofs(Scene):
    def construct(self):
        myShift=4
        pointA= [3-myShift,1.02-myShift,0]
        pointB= [9-myShift,1-myShift,0]
        pointC= [3-myShift,5-myShift,0]

        trigono = Line(pointA,pointB).append_points(Line(pointB,pointC).points).append_points(Line(pointC,pointA).points)
        cSide=Line(pointB,pointA) #side AB
        aSide=Line(pointB,pointC) #side BC
        bSide=Line(pointA,pointC) #side AC

        a_text = Text('A').next_to(pointA, DOWN)
        b_text = Text('B').next_to(pointB, DOWN)
        c_text = Text('C').next_to(pointC, UP)

        self.add(VGroup(a_text,b_text,c_text))
        self.wait(1)
        self.play(FadeIn(VGroup(aSide,bSide,cSide)))
        self.wait(1)

        a_1 = Angle(aSide, cSide, radius=0.7, other_angle=False)
        tex1 = MathTex(r"\beta").move_to(
        Angle(
        aSide, cSide, radius=0.7 + 3 * SMALL_BUFF, other_angle=False
        ).point_from_proportion(0.5)
        )
        self.play(FadeIn(a_1))
        self.play(FadeIn(tex1))
        self.wait()
        
        trig1_text=Tex(r"$cos(\beta)=\frac{adjacent \ AB}{hypotenuse \ CB}$").scale(0.9)
        trig2_text=Tex(r"$sec(\beta)=\frac{hypotenuse \ CB}{adjacent \ AB}$").scale(0.9)
        trig3_text=Tex(r"$tan(\beta)=\frac{opposite \ AC}{adjacent \ AB}$").scale(0.9)
        mobjects = VGroup(
        trig1_text,trig2_text,trig3_text
        )
        mobjects.scale(1.1)
        mobjects.arrange_submobjects(DOWN,buff=2).shift(4*LEFT)
        anims = AnimationGroup(
        *[GrowFromCenter(mob) for mob in mobjects]
        )
        self.play(anims)
        self.wait()

        trig1_text2=Tex(r"$cos(\theta)=\frac{adjacent}{hypotenuse}$").scale(0.9)
        trig2_text2=Tex(r"$sec(\theta)=\frac{hypotenuse}{adjacent}$").scale(0.9)
        trig3_text2=Tex(r"$tan(\theta)=\frac{opposite}{adjacent}$").scale(0.9)

        mobjects2 = VGroup(
        trig1_text2,trig2_text2,trig3_text2
        )
        mobjects2.scale(1.1)
        mobjects2.arrange_submobjects(DOWN,buff=0.1).shift(4*LEFT)
        self.play(ClockwiseTransform(mobjects, mobjects2))
        #self.wait()

        mobjects2.generate_target() # copy mobjects2 to target
        mobjects2.target.scale(1).shift(LEFT).shift(2.7*UP) # target.to_edge(LEFT+UP)
        self.remove(mobjects)
        self.play(MoveToTarget(mobjects2))
        self.wait()
        self.play(
        *[Uncreate(mob) for mob in VGroup(a_text,b_text,c_text,aSide,bSide,cSide,a_1,tex1)]
        )

        self.wait()

        HorShift=2.5
        VerShift=3
        q1= [1-HorShift,0-VerShift,0] #point Α
        q2= [8.92-HorShift,0-VerShift,0] #point Β
        q3= [1-HorShift,6.4-VerShift,0] #point c
        q4= [8.92-HorShift,6.4-VerShift,0] #point Δ
        q5= [5.66-HorShift,6.4-VerShift,0] #ποιντ Ε
        q6= [8.92-HorShift,4.07-VerShift,0] #ποιντ z

        a2_text = Text('A').next_to(q1,LEFT+UP)
        b2_text = Text('B').next_to(q2)
        c2_text = Text('C').next_to(q3, LEFT)
        d2_text = Text('D').next_to(q4)
        e2_text = Text('E').next_to(q5, DOWN)
        z2_text = Text('Z').next_to(q6)

        acSide=Line(q1,q3) #side AC
        aeSide=Line(q1,q5) #side AE
        abSide=Line(q1,q2) #side AB
        azSide=Line(q1,q6) #side AZ

        ceSide=Line(q3,q5) #side CE
        ezSide=Line(q5,q6) #side EZ
        edSide=Line(q5,q4) #side ED
        zdSide=Line(q6,q4) #side ZD
        zbSide=Line(q6,q2) #side ZB

        self.add(VGroup(a2_text,c2_text,acSide))

        #angle eAc
        a_3 = Angle(aeSide, acSide, radius=0.7, other_angle=False)
        texa3 = MathTex(r"\alpha").move_to(
        Angle(
        aeSide, acSide, radius=0.7 + 3 * SMALL_BUFF, other_angle=False
        ).point_from_proportion(0.5)
        )
        self.play(FadeIn(a_3))
        self.play(FadeIn(texa3))
        self.wait()

        tana_text = Tex(r"$tan(\alpha)$").next_to(ceSide, DOWN).shift(0.2*UP).scale(0.8)
        seca_text = Tex(r"$sec(\alpha)$").next_to(aeSide, LEFT).shift(2.8*RIGHT).rotate(58*PI/180).scale(0.8)
        tanb_text = Tex(r"$tan(\beta)$").next_to(edSide, DOWN).shift(0.2*UP).shift(.2*RIGHT).scale(0.8)
        one_text = Text('1').next_to(acSide, LEFT)
        secatanb_text = Tex(r"$sec(\alpha) \cdot \tan(\beta)$").next_to(ezSide).scale(0.7).shift(3.5*LEFT).shift(0.25*DOWN).rotate(-37*PI/180)
        tanatanb_text = Tex(r"$tan(\alpha) \cdot \tan(\beta)$").scale(0.5).rotate(-PI/2).next_to(zdSide)
        tanatanb2_text = Tex(r"$tan(\alpha) + \tan(\beta)$").scale(0.8).next_to(abSide, UP)
        tangtanatanb_text = Tex(r"$tan(\gamma)\cdot (tan(\alpha) + \tan(\beta))$").scale(0.5).rotate(-PI/2).next_to(zbSide)#.shift(2.5*LEFT)

        self.play(Create(one_text))
        self.wait()
        r_a= RightAngle(acSide,ceSide,length=0.3, quadrant=(-1,1), color=RED)
        self.play(Create(VGroup(aeSide,ceSide,e2_text,r_a)))
        self.wait()
