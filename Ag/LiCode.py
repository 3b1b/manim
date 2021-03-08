from manimlib import *

class SquareLocTxt():
    def __init__(self, h, square, loc_txt_colors, buff = 0):
        grid_color = "#333333"
        grid = Square(
                    side_length=2,
                    fill_color=grid_color,
                    fill_opacity=1,
                    stroke_color="#111111",
                    stroke_width=2,
                    )\
            .get_grid(square, square, height=h, buff=buff)
        
        for i in range(square*square):
            text = DecimalNumber(0,
                    font_size=25,
                    num_decimal_places=0
                    )
            grid[i].txt = text
            grid[i].txt.move_to(grid[i])

        for loc_txt_color in loc_txt_colors:
            loc = loc_txt_color[0]
            num = loc_txt_color[1]
            color = loc_txt_color[2]
            grid[loc].set_style(
                    fill_color=color,
                    fill_opacity=1,
                    stroke_color="#111111",
                    stroke_width=2,
                    )
            grid[loc].txt=DecimalNumber(num,
                    font_size=25,
                    num_decimal_places=0,
                    color=BLACK
                    )
            grid[loc].txt.move_to(grid[loc])

        self.sq_Vg=VGroup()
        for i in range(len(grid)):
            self.sq_Vg.add(VGroup(grid[i],grid[i].txt))
 
class ConvolutionPic(Scene):
    def construct(self):
        white_7loc = [8,12,16,18,24,30,32,36,40] 
        loctc7 = [[]]*len(white_7loc)
        for i,w7 in enumerate(white_7loc):
            loctc7[i]=[w7,1,WHITE]
        sq7_7 = SquareLocTxt(4,7,loctc7)
 
        white_3loc = [0,4,8] 
        loctc3 = [[]]*len(white_3loc)
        for i,w3 in enumerate(white_3loc):
            loctc3[i]=[w3,1,WHITE]
        sq3_3 = SquareLocTxt(4*3/7,3,loctc3)

        white_5loc = [i for i in range(5*5)] 
        loctc5 = [[]]*len(white_5loc)
        areas = [[]]*len(white_5loc)
        formulas = [[]]*len(white_5loc)
        for i,w5 in enumerate(white_5loc):
            div = i // 5  #商
            mod = i % 5   #余
            txt = sq7_7.sq_Vg[8+div*7+mod-8][1].number*sq3_3.sq_Vg[0][1].number\
                + sq7_7.sq_Vg[8+div*7+mod-7][1].number*sq3_3.sq_Vg[1][1].number\
                + sq7_7.sq_Vg[8+div*7+mod-6][1].number*sq3_3.sq_Vg[2][1].number\
                + sq7_7.sq_Vg[8+div*7+mod-1][1].number*sq3_3.sq_Vg[3][1].number\
                + sq7_7.sq_Vg[8+div*7+mod-0][1].number*sq3_3.sq_Vg[4][1].number\
                + sq7_7.sq_Vg[8+div*7+mod+1][1].number*sq3_3.sq_Vg[5][1].number\
                + sq7_7.sq_Vg[8+div*7+mod+6][1].number*sq3_3.sq_Vg[6][1].number\
                + sq7_7.sq_Vg[8+div*7+mod+7][1].number*sq3_3.sq_Vg[7][1].number\
                + sq7_7.sq_Vg[8+div*7+mod+8][1].number*sq3_3.sq_Vg[8][1].number
            loctc5[i] = [w5,txt,RED_A]
            areas[i] = VGroup(
                    sq7_7.sq_Vg[8+div*7+mod-8],
                    sq7_7.sq_Vg[8+div*7+mod-7],
                    sq7_7.sq_Vg[8+div*7+mod-6],
                    sq7_7.sq_Vg[8+div*7+mod-1],
                    sq7_7.sq_Vg[8+div*7+mod-0],
                    sq7_7.sq_Vg[8+div*7+mod+1],
                    sq7_7.sq_Vg[8+div*7+mod+6],
                    sq7_7.sq_Vg[8+div*7+mod+7],
                    sq7_7.sq_Vg[8+div*7+mod+8],
                )
            jia = Tex("+",font_size=36)
            cheng = Tex("*",font_size=40)
            deng = Tex("=",font_size=40)
            formula1 = VGroup(
                        sq7_7.sq_Vg[8+div*7+mod-8][1].copy(),cheng.copy(),sq3_3.sq_Vg[0][1].copy(),
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod-7][1].copy(),cheng.copy(),sq3_3.sq_Vg[1][1].copy(),
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod-6][1].copy(),cheng.copy(),sq3_3.sq_Vg[2][1].copy(),
                        ).arrange(RIGHT,buff=0.1)
            formula2 = VGroup(
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod-1][1].copy(),cheng.copy(),sq3_3.sq_Vg[3][1].copy(),
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod-0][1].copy(),cheng.copy(),sq3_3.sq_Vg[4][1].copy(),
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod+1][1].copy(),cheng.copy(),sq3_3.sq_Vg[5][1].copy(),
                        ).arrange(RIGHT,buff=0.1)
            formula3 = VGroup(
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod+6][1].copy(),cheng.copy(),sq3_3.sq_Vg[6][1].copy(),
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod+7][1].copy(),cheng.copy(),sq3_3.sq_Vg[7][1].copy(),
                        jia.copy(),sq7_7.sq_Vg[8+div*7+mod+8][1].copy(),cheng.copy(),sq3_3.sq_Vg[8][1].copy(),
                        ).arrange(RIGHT,buff=0.1)
            formula4 = VGroup(deng.copy(),DecimalNumber(txt,font_size=25,num_decimal_places=0))\
                        .arrange(RIGHT,buff=0.1)
            formulas[i]= VGroup(formula1,formula2,formula3,formula4)\
                        .arrange(DOWN,aligned_edge=RIGHT,buff=0.2)\
                        .set_color(RED).to_corner(UR)\
                        .rotate(-25* DEGREES,axis=UP)\
                        .rotate(4.3* DEGREES,axis=OUT)
        sq7_7.formula = formulas
        sq7_7.area = areas
        sq5_5 = SquareLocTxt(4*5/7,5,loctc5)

        sq7_7.sq_Vg.shift(OUT*(-8)).scale(1.2)
        sq3_3.sq_Vg.move_to(sq7_7.sq_Vg[21]).shift(OUT*11.5).scale(0.58)
        sq5_5.sq_Vg.move_to(sq7_7.sq_Vg[38]).shift(OUT*12).scale(0.75)

        lines7_3s = [[]]*len(white_5loc)
        lines3_5s = [[]]*len(white_5loc)
        ret7_7s = [[]]*len(white_5loc)
        ret5_5s = [[]]*len(white_5loc)
        ret3_3s = [[]]*len(white_5loc)

        for numCNA in range(5*5):
            lines7_3 = VGroup()
            lines3_5 = VGroup()
            for point in [UL,UR,DL,DR]:
                line1 = DashedLine(
                    start=sq7_7.area[numCNA].get_corner(point),
                    end=sq3_3.sq_Vg.get_corner(point),
                    color=GREEN,
                    stroke_width=2
                    )
                line2 = DashedLine(
                    start=sq3_3.sq_Vg.get_corner(point),
                    end=sq5_5.sq_Vg[numCNA].get_corner(point),
                    color=GREEN,
                    stroke_width=6
                    )
                lines7_3s[numCNA] = lines7_3.add(line1)
                lines3_5s[numCNA] = lines3_5.add(line2)
            
            ret7_7s[numCNA] = Square().match_height(sq7_7.area[numCNA])\
                        .set_style(
                            fill_color=GREEN,
                            fill_opacity=0.6,
                            stroke_color=GREEN_A,
                            stroke_width=2.5
                            )\
                        .move_to(sq7_7.area[numCNA])
            ret5_5s[numCNA] = Square().match_height(sq5_5.sq_Vg[numCNA])\
                        .set_style(
                            fill_color=GREEN,
                            fill_opacity=0.6,
                            stroke_color=GREEN_A,
                            stroke_width=2.5)\
                        .move_to(sq5_5.sq_Vg[numCNA])

            ret3_3s[numCNA] = Square().match_height(sq3_3.sq_Vg)\
                        .set_style(
                            fill_color=GREEN,
                            fill_opacity=0.2,
                            stroke_color=GREEN_A,
                            stroke_width=2)\
                        .move_to(sq3_3.sq_Vg)
        
        frame = self.camera.frame
        frame.set_euler_angles(
            theta=90 * DEGREES,
            phi=-30 * DEGREES,
            gamma=29.9
        ) 

        self.play(Write(sq7_7.sq_Vg))
        self.wait()
        self.play(ShowCreation(sq3_3.sq_Vg))
        self.wait()
        self.play(FadeIn(sq5_5.sq_Vg,scale=0.5))
        num = 0
        self.play(Write(ret7_7s[num]))
        self.play(ShowCreation(lines7_3s[num]))
        self.play(Write(ret3_3s[num]))
        self.play(ShowCreation(lines3_5s[num]))
        self.play(
                Write(ret5_5s[num]),
                ShowCreation(sq7_7.formula[num]),
                )
        self.wait()
        
        self.play(LaggedStartMap(
            FadeOut,VGroup(
                    ret7_7s[num],
                    lines7_3s[num],
                    ret3_3s[num],
                    lines3_5s[num],
                    ret5_5s[num],
                    sq7_7.formula[num],
                    )
                )
            )
        k = 4
        for i in range(1,k):
            self.add( 
                        VGroup(
                        ret7_7s[i],
                        lines7_3s[i],
                        ret3_3s[i],
                        lines3_5s[i],
                        ret5_5s[i],
                        sq7_7.formula[i],
                        )
                )
            self.wait(1)
            if i < k-1:
                self.remove( 
                            VGroup(
                            ret7_7s[i],
                            lines7_3s[i],
                            ret3_3s[i],
                            lines3_5s[i],
                            ret5_5s[i],
                            sq7_7.formula[i],
                        )
                    )



        





        
        
