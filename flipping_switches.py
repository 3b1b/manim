import random
from manimlib.imports import *
from manimlib.mobject.three_dimensions import Cube, Prism
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.svg import *
from math import sqrt


class Bulb(VGroup):
    CONFIG = {
    "stroke_width":1,
    "fill_color" : YELLOW,
    "color" : YELLOW,
    "fill_opacity": 1,
    }

    def generate_points(self):
        blb = Dot()
        self.add(blb)
        

class SwitchBoard(VMobject):
    CONFIG ={
    "fill_color":RED_D, 
    "fill_opacity":0.5,
    }
    def generate_points(self):
        rect = RoundedRectangle(height=0.7, width=0.4, fill_color=BLACK, fill_opacity=0.5,corner_radius=0.2)
        self.add(rect)

class Board(VMobject):
    CONFIG ={
    "fill_color":RED_D, 
    "fill_opacity":0.5,
    }
    def generate_points(self):
        rect = RoundedRectangle(height=0.7, width=1, fill_color=RED_D, fill_opacity=0.5,corner_radius=0.2)
        self.add(rect)

class Board1(VMobject):
    CONFIG ={
    "fill_color":RED_D, 
    "fill_opacity":0.5,
    }
    def generate_points(self):
        rect = RoundedRectangle(height=0.7, width=1.2, fill_color=RED_D, fill_opacity=0.5,corner_radius=0.2)
        self.add(rect)

class Switch(VGroup):
    CONFIG ={
        "fill_color":YELLOW_D, 
        "fill_opacity":0.5,
    }
    def generate_points(self):
        swb = SwitchBoard()
        swb.set_style(fill_color = RED_D)
        blb = Dot(fill_color = YELLOW_D)
        self.add(VGroup(swb, blb))
        
#this is the test class for test purpose        
class Test(ThreeDScene):
    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )

    def create_on_switch(self, point):
        swb = SwitchBoard(fill_color = BLACK)
        blb = Dot(fill_color = '#00ff00' ,radius = 0.18)
        blb.shift(DOWN*0.2)
        text = TexMobject("ON", font="Arial")
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(DOWN*0.5)
        text.scale(0.5)
        text1 = TexMobject("OFF")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(UP*0.5)
        text1.scale(0.5)
        '''
        rect = Rectangle(width=0.5,height=0.3)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(DOWN*(0.5))'''
        grp = VGroup(swb, blb)
        #grp.add(rect)
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)

    def toggle_switch(self, switch1, switch2,point):
        self.remove(switch1)
        self.add(switch2)
        self.play(self.get_hit_flash(point)) 

    def toggle_switch1(self,switch,point,flag):
        if(flag==True):
            s1 = self.create_off_switch(point)
            self.remove(switch)
            self.add(s1)
            self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            return s1
        else:
            s2 = self.create_on_switch(point)
            self.remove(switch)
            self.add(s2)
            self.play(self.get_hit_flash(point+np.array([0,-0.3,0])))
            return s2


    def create_off_switch(self,point):
        swb = SwitchBoard(fill_color = BLACK)
        blb = Dot(fill_color = '#FF0000',radius=0.18)
        blb.shift(UP*0.2)
        grp = VGroup(swb, blb)
        text = TexMobject("OFF",font='Arial')
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(UP*0.5)
        text.scale(0.5)
        text1 = TexMobject("ON")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(DOWN*0.5)
        text1.scale(0.5)
        '''
        rect = Rectangle(width=0.6,height=0.3,fill_color=BLACK)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(UP*(0.5))
        grp.add(rect)
        '''
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)
    
    def change_base_i(self,Switches,i):
        for k in range(0,len(Switches),i):
            temp=Switches[k][0]
            Switches[k][0] = Switches[k][1]
            Switches[k][1] = temp

    def construct(self):
               
        point = np.array([-7.5,2.8,0])
        flag = True
        point_f = list()
        for j in range(0,5):
            for i in range(0,2):
                point[0] +=0.7
                temp = np.array(point)
                point_f.append([temp,flag])
            point[1]-=1.48
            point[0]=-7.5    
        print(len(point_f))
        switch_list = list()
        for i in point_f:
            flag=True
            switch1 = self.create_on_switch(i[0])
            switch_list.append([switch1,i[0],i[1]])  #   i[0] == point and i[1] == flag
            self.play(ShowCreation(switch1,run_time=0.25))



            #print(i[2])
        print(switch_list[0][2])   
        print(switch_list[1][2])
        print(switch_list[2][2])
        for k in range(0,6):
            for idx, i in enumerate(switch_list):
                if((idx+1)%(k+1)==0):
                    i[0] = self.toggle_switch1(i[0],i[1],i[2])
                    i[2]^=True
                 

#test class ends here 
class NO_ON(ThreeDScene):
    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )    

    def create_on_switch1(self, point,value):
        swb = SwitchBoard(fill_color = BLACK) # ---  color changes to YELLOW_D to BLACk
        blb = Dot(fill_color = GREEN,radius = 0.18)
        blb.shift(DOWN*0.2)
        text = TexMobject(str(value),color=BLACK)
        '''
        rect = Rectangle(width=0.5,height=0.3)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(DOWN*(0.5))'''
        text.shift(DOWN*0.5)
        text.scale(0.5)
        grp = VGroup(swb, blb)
        grp.add(text)
        grp.shift(point)
        return(grp)

    def toggle_switch(self, switch1, switch2,point):
        self.remove(switch1)
        self.add(switch2)
        self.play(self.get_hit_flash(point)) 

    def toggle_switch1(self,switch,point,flag,value,rt=1):
        if(flag==True):
            s1 = self.create_off_switch(point,value)
            self.remove(switch)
            self.add(s1)
            self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            return s1
        else:
            s2 = self.create_on_switch1(point,value)
            self.remove(switch)
            self.add(s2)
            self.play(self.get_hit_flash(point+np.array([0,-0.3,0])))
            return s2


    def create_off_switch(self,point,value):
        swb = SwitchBoard(fill_color = BLACK)   # color changes to YELLOW_D to BLACK
        blb = Dot(fill_color = RED,radius=0.18)
        blb.shift(UP*0.2)
        text = TexMobject(str(value),color=BLACK)
        '''
        rect = Rectangle(width=0.6,height=0.3,fill_color=BLACK)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(UP*(0.5))
        grp.add(rect)
        '''
        text.shift(DOWN*0.5)
        text.scale(0.5)
        grp = VGroup(swb, blb)
        grp.add(text)
        grp.shift(point)
        return(grp)

    def construct(self):
               
        point = np.array([-7.5,2.8,0])
        flag = False
        point_f = list()
        for j in range(0,5):
            for i in range(0,20):
                point[0] +=0.7
                temp = np.array(point)
                point_f.append([temp,flag])
            point[1]-=1.48
            point[0]=-7.5    
        print(len(point_f))
        switch_list = list()
        no = 1
        for i in point_f:
            flag=True
            switch1 = self.create_off_switch(i[0],no)
            switch_list.append([switch1,i[0],i[1]])              #i[0] == point and i[1] == flag
            if(no<=10):
                rt = 0.25
            else:   
                rt = 0.02
            self.play(ShowCreation(switch1,run_time=rt))
            no+=1               
        print(point_f[99])
        # switch1 = self.create_on_switch1(point_f[99][0],no)
        # self.play(ShowCreation(switch1,run_time=0.02))
        self.wait(1)   
        ''' 
        for bhuk in range(6):
            focus = Rectangle(height=0.8,width=0.45,color=BLACK)
            focus.shift(point_f[bhuk][0])
            self.play(GrowArrow(focus))
            switch_list[bhuk][0] = self.toggle_switch1(switch_list[bhuk][0],switch_list[bhuk][1],switch_list[bhuk][2],bhuk+1)
            print(switch_list[bhuk][2])
            switch_list[bhuk][2] ^= True
            switch_list[bhuk][0] = self.toggle_switch1(switch_list[bhuk][0],switch_list[bhuk][1],switch_list[bhuk][2],bhuk+1)
            self.remove(focus)
            self.wait(1)   
               
        # switch_list at index 0-> switch_object  1 -> point  2 -> flag
          
        for bhuk in range(6): 
            switch_list[bhuk][2] ^= True
        '''
        count = 1   
        rate = 0.25 
        for k in range(0,4):
            val=1
            for idx, i in enumerate(switch_list):
                if((idx+1)%(k+1)==0):
                    if count>10:
                        rate = 0.02
                    if val <=5:
                        val+=1
                        focus = Rectangle(height=0.8,width=0.45,color=BLACK)
                        focus.shift(i[1])
                        self.play(GrowArrow(focus))
                        i[0] = self.toggle_switch1(i[0],i[1],i[2],idx+1,rate)
                        i[2]^=True 
                        self.remove(focus)
                    else:       
                        i[0] = self.toggle_switch1(i[0],i[1],i[2],idx+1,rate)
                        i[2]^=True     
                count+=1    

class TestScene(ThreeDScene):

    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )

    def create_on_switch(self, point):
        swb = SwitchBoard(fill_color = BLACK)
        blb = Dot(fill_color = RED_C)
        grp = VGroup(swb, blb)
        grp.shift(point)
        return(grp)

    def toggle_switch(self, switch1, switch2,point):
        self.remove(switch1)
        self.add(switch2)
        self.play(self.get_hit_flash(point))

    def create_off_switch(self,point):
        swb = SwitchBoard(fill_color = BLACK)
        blb = Dot(fill_color = GREEN_C)
        grp = VGroup(swb, blb)
        grp.shift(point)
        return(grp)
    
    def change_base_i(self,Switches,i):
        for k in range(0,len(Switches),i):
            temp=Switches[k][0]
            Switches[k][0] = Switches[k][1]
            Switches[k][1] = temp

    def construct(self):
        #self.annulus = 0.2
        #an = self.get_light([0, 0, 0])
        title = TextMobject("Flipping the Switches")
        title.scale(1.0)
        title.to_edge(UP)
        # self.add(title)
        '''
        switch1 = Switch_point([-4,3,0],True)
        switch2 = Switch_point([-4,2,0],False)
        # switch2 = OffSwitch()
        '''
        
        point = np.array([-7.6,2.8,0])
        flag = True
        point_f = list()
        for i in range(0,2):
            for j in range(0,6):
                point[0] +=2.1
                temp = np.array(point)
                point_f.append([temp,flag])
            point[1]-=2.1
            point[0] = -7.6
        print(len(point_f))    
        #list_of_switches with their corresspondinfg states 
        list_of_switches=list()
        for i in range(0,5):
            switch1 = self.create_on_switch(point_f[i][0])
            switch2 = self.create_off_switch(point_f[i][0])
            temp = np.array([switch1,switch2])
            list_of_switches.append(temp)
        print(len(list_of_switches))    

        for i in point_f:
            switch1 = self.create_on_switch(i[0])
            self.play(ShowCreation(switch1),ShowCreation(title))
        #changing phase of a bulb
        for i in range(len(point_f)):
            switch2 = self.create_off_switch(point_f[i][0])
            point_f[i][1]^=True
            self.toggle_switch(switch1, switch2, point_f[i][0])
        # self.play(ShowCreation(bulb))
        self.wait(1)
        # for i in range(0,len(point_f),2):
        #     point_f[i][1]^=True
        #     switch1 = self.create_on_switch(point_f[i][0])
        #     self.toggle_switch(switch2,switch1,point_f[i][0])
        # self.wait(1)

# this is the last play explaining about the number of times switch gets on and off       
class explanation(TestScene):

    def construct(self):
        title = TextMobject("Switch number 20")
        title.scale(1.0)
        title.to_edge(UP)
        self.add(title)
        point = [0,0,0]
        for i in range(1):
            switch1 = self.create_on_switch(point)
            switch2 = self.create_off_switch(point)
            point_f[i][1]^=True
            self.toggle_switch(switch1, switch2,point)
        # self.play(ShowCreation(bulb))
        self.wait(1)
        for i in range(len(point_f)):
            point_f[i][1]^=True
            switch1 = self.create_on_switch(point_f[i][0])
            self.toggle_switch(switch2,switch1,point_f[i][0])
        self.wait(1)


class Introduction(Test):
    CONFIG={
        "font":"Arial"
    }
    def construct(self):
        hi = TextMobject("Hey Folks!", font="Arial",color=BLACK)
        welcome =TextMobject( r'{\fontfamily{qag}\selectfont welcome back to another Cuemath Gems video}',color=BLACK)
        welcome.set_color(RED)
        welcome.shift(DOWN)
        welcome.align_to(hi)
        # welcome.set_font("Arial")
        #welcome.next_to(hi)
        problem_name = TextMobject("The name of this problem is",color=BLACK)
        name = TextMobject("Flipping Switches" ,color=BLACK)
        name.shift(DOWN)
        name.align_to(problem_name,LEFT)
        here_it = TextMobject("And here’s what it says….", font="Sans",color=BLACK)
        self.play(Write(hi))
        self.play(Write(welcome))
        self.add(welcome)
        hi.add(welcome)
        self.remove(hi)
        self.play(Transform(welcome,problem_name))
        self.play(Write(name))
        self.remove(problem_name)
        self.remove(welcome)
        # self.play(ApplyMethod(name.get_corner(UP+LEFT)))
        name.shift(UP*2+LEFT*4)
        # self.play(ApplyMethod(problem_name.match_color,name),Transform(name,name.scale(1)))
        self.play(Transform(name,here_it))


        #switchboard display
        x=2.5
        point = np.array([-2.5,-1,0])
        flag = True
        point_f = list()
        for i in range(0,5):
            point[0] +=0.7
            temp = np.array(point)
            point_f.append([temp,flag]) 
        print(len(point_f))
        switch_list = list()
        for i in point_f:
            flag=True
            switch1 = self.create_on_switch(i[0])
            switch_list.append([switch1,i[0],i[1]])  #   i[0] == point and i[1] == flag
            self.play(ShowCreation(switch1,run_time=0.3))


        imagine = TextMobject("")

class TableOfContents(Scene):
    def construct(self):
        items = VGroup(
            TextMobject("How the ellipse will arise"),
            TextMobject("Kepler's 2nd law"),
            TextMobject("The shape of velocities"),
        )
        items.arrange(
            DOWN, buff=LARGE_BUFF, aligned_edge=LEFT
        )
        items.to_edge(LEFT, buff=1.5)
        for item in items:
            item.add(Dot().next_to(item, LEFT))
            item.generate_target()
            item.target.set_fill(GREY, opacity=0.5)

        title = Title("The plan")
        scale_factor = 1.2

        self.add(title)
        self.play(LaggedStartMap(
            FadeIn, items,
            run_time=1,
            lag_ratio=0.7,
        ))
        self.wait()
        
        for item in items:
            other_items = VGroup(*[m for m in items if m is not item])
            new_item = item.copy()
            new_item.scale(scale_factor, about_edge=LEFT)
            new_item.set_fill(WHITE, 1)
            self.play(
                Transform(item, new_item),
                *list(map(MoveToTarget, other_items))
            )
            self.wait()


class second_hint_20(Scene):

    def create_on_switch1(self, point):
        swb = SwitchBoard(height=2, width=1.2, fill_color=BLACK, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#00FF00',radius = 0.5)
        blb.shift(DOWN*0.3)
        text = TexMobject("ON", font="Arial")
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(DOWN*5)
        text.scale(2)
        text1 = TexMobject("OFF")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(UP*5)
        text1.scale(2)
        '''
        rect = Rectangle(width=0.5,height=0.3)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(DOWN*(0.5))'''
        grp = VGroup(swb, blb)
        #grp.add(rect)
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)

    def create_off_switch(self,point):
        swb = SwitchBoard(fill_color = BLACK,height=2, width=1.2, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#FF0000',radius=0.5)
        blb.shift(UP*0.3)
        grp = VGroup(swb, blb)
        text = TexMobject("OFF",font='Arial')
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(UP*5)
        text.scale(2)
        text1 = TexMobject("ON")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(DOWN*5)
        text1.scale(2)
        '''
        rect = Rectangle(width=0.6,height=0.3,fill_color=BLACK)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(UP*(0.5))
        grp.add(rect)
        '''
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)  

    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )

    def toggle_switch1(self,switch,point,flag,value):
        if(flag==True):
            s1 = self.create_off_switch(point)
            self.remove(switch)
            self.add(s1)
            self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            return s1
        else:
            s2 = self.create_on_switch1(point)
            self.remove(switch)
            self.add(s2)
            self.play(self.get_hit_flash(point+np.array([0,-0.3,0])))
            return s2
 
      

    def construct(self):
        point = np.array([5,0,0])   
        switch_list = list()
        flag =  False
        text1 = TextMobject("Switch no. 20",color=BLACK)
        text1.shift(RIGHT*5+DOWN*1.6)
        self.add(text1)
        # self.add(counter)
        x = ' '
        # question = TextMobject("Is "+4*x+" is a factor of 20 ? ")
        # question.shift(LEFT*2+UP*2)
        # rect = SurroundingRectangle(question)
        # question.add(rect)
        # self.add(question)
        switch1 = self.create_off_switch(point)
        self.add(switch1)
        switch_list.append([switch1,point,flag])
        factor = TextMobject("Factors : ",color=BLACK)
        factor.shift(LEFT*4+DOWN*3)
        old_obj = TextMobject()
        old_obj.shift(LEFT*2+UP*2)
        self.add(old_obj)
        self.add(factor)
        point = np.array([-2,-3,0])
        z_fact =3
        for i in range(1,21):
            new_obj = TextMobject("Is 20 divisible by ",color=BLACK) 
            # self.add(new_obj)
            q_m = TextMobject("?",color=BLACK)
            if(20%i==0):
                value = TextMobject(str(i),fill_color=RED_D)
                value.set_color=RED_D
            else:
                value = TextMobject(str(i),fill_color=BLACK)   
                value.set_color=BLACK
            value.next_to(new_obj,RIGHT)
            q_m.next_to(value, RIGHT)
            new_obj.add(value)
            new_obj.add(q_m)
            new_obj.shift(LEFT*2+UP*2)
            self.play(Transform(old_obj,new_obj))
            # question_mark.shift(LEFT+UP*2)
            # self.add(question_mark)
            # self.remove(new_obj)
            factors = TextMobject()
            if 20%i == 0:
                yes = TextMobject("YES",color='#00FF00')
                # rect = Board1(opacity=0.2,fill_color=BLACK,corner_radius=0.2)
                # rect.add(yes)    
                yes.next_to(new_obj,DOWN*5)
                self.play(GrowFromCenter(yes),run_time=0.7)
                switch_list[0][0] = self.toggle_switch1(switch_list[0][0],switch_list[0][1],switch_list[0][2],i)
                switch_list[0][2]^=True
                self.get_hit_flash(switch_list[0][1])
                self.wait(1)
                self.remove(yes)
                value.set_color=RED_D
                # value = TextMobject(str(i)+",")
                z_fact-=0.66
                # value.shift(LEFT*z_fact+DOWN*3)
                # self.play(value.move_to(points))
                self.play(value.move_to, LEFT*z_fact+DOWN*3,fill_color=RED_D)
                # self.play(FadeOutAndShift(value))
                self.wait(1)
            else: 
                no = TextMobject("NO",color='#ff0000')
                # rect = Board(width=1,height=0.5,opacity=0.2,fill_color=BLACK,corner_radius=0.2)
                # rect.add(no)    
                no.next_to(new_obj,DOWN*5)
                self.play(GrowFromCenter(no),run_time=1)
                self.get_hit_flash(switch_list[0][1])
                self.remove(no)
        self.wait(1)        
             
class second_hint_25(Scene):

    def create_on_switch1(self, point):
        swb = SwitchBoard(height=2, width=1.2, fill_color=BLACK, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#00FF00',radius = 0.5)
        blb.shift(DOWN*0.3)
        text = TexMobject("ON", font="Arial")
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(DOWN*5)
        text.scale(2)
        text1 = TexMobject("OFF")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(UP*5)
        text1.scale(2)
        '''
        rect = Rectangle(width=0.5,height=0.3)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(DOWN*(0.5))'''
        grp = VGroup(swb, blb)
        #grp.add(rect)
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)

    def create_off_switch(self,point):
        swb = SwitchBoard(fill_color = BLACK,height=2, width=1.2, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#FF0000',radius=0.5)
        blb.shift(UP*0.3)
        grp = VGroup(swb, blb)
        text = TexMobject("OFF",font='Arial')
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(UP*5)
        text.scale(2)
        text1 = TexMobject("ON")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(DOWN*5)
        text1.scale(2)
        '''
        rect = Rectangle(width=0.6,height=0.3,fill_color=BLACK)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(UP*(0.5))
        grp.add(rect)
        '''
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)  

    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )

    def toggle_switch1(self,switch,point,flag,value):
        if(flag==True):
            s1 = self.create_off_switch(point)
            self.remove(switch)
            self.add(s1)
            self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            return s1
        else:
            s2 = self.create_on_switch1(point)
            self.remove(switch)
            self.add(s2)
            self.play(self.get_hit_flash(point+np.array([0,-0.3,0])))
            return s2
 
      

    def construct(self):
        point = np.array([5,0,0])   
        switch_list = list()
        flag =  False
        text1 = TextMobject("Switch no. 25",color=BLACK)
        text1.shift(RIGHT*5+DOWN*1.6)
        self.add(text1)
        # self.add(counter)
        x = ' '
        # question = TextMobject("Is "+4*x+" is a factor of 20 ? ")
        # question.shift(LEFT*2+UP*2)
        # rect = SurroundingRectangle(question)
        # question.add(rect)
        # self.add(question)
        switch1 = self.create_off_switch(point)
        self.add(switch1)
        switch_list.append([switch1,point,flag])
        factor = TextMobject("Factors : ",color=BLACK)
        factor.shift(LEFT*4+DOWN*3)
        old_obj = TextMobject()
        old_obj.shift(LEFT*2+UP*2)
        self.add(old_obj)
        self.add(factor)
        point = np.array([-2,-3,0])
        z_fact =3
        for i in range(1,26):
            new_obj = TextMobject("Is 25 divisible by ",color=BLACK) 
            # self.add(new_obj)
            q_m = TextMobject("?",color=BLACK)
            if(25%i==0):
                value = TextMobject(str(i),fill_color=RED_D)
                value.set_color=RED_D
            else:
                value = TextMobject(str(i),fill_color=BLACK)   
                value.set_color=BLACK
            value.next_to(new_obj,RIGHT)
            q_m.next_to(value, RIGHT)
            new_obj.add(value)
            new_obj.add(q_m)
            new_obj.shift(LEFT*2+UP*2)
            self.play(Transform(old_obj,new_obj))
            # question_mark.shift(LEFT+UP*2)
            # self.add(question_mark)
            # self.remove(new_obj)
            factors = TextMobject()
            if 25%i == 0:
                yes = TextMobject("YES",color='#00FF00')
                # rect = Board1(opacity=0.2,fill_color=BLACK,corner_radius=0.2)
                # rect.add(yes)    
                yes.next_to(new_obj,DOWN*5)
                self.play(GrowFromCenter(yes),run_time=0.7)
                switch_list[0][0] = self.toggle_switch1(switch_list[0][0],switch_list[0][1],switch_list[0][2],i)
                switch_list[0][2]^=True
                self.get_hit_flash(switch_list[0][1])
                self.wait(1)
                self.remove(yes)
                value.set_color=RED_D
                # value = TextMobject(str(i)+",")
                z_fact-=0.66
                # value.shift(LEFT*z_fact+DOWN*3)
                # self.play(value.move_to(points))
                self.play(value.move_to, LEFT*z_fact+DOWN*3,fill_color=RED_D)
                # self.play(FadeOutAndShift(value))
                self.wait(1)
            else: 
                no = TextMobject("NO",color='#ff0000')
                # rect = Board(width=1,height=0.5,opacity=0.2,fill_color=BLACK,corner_radius=0.2)
                # rect.add(no)    
                no.next_to(new_obj,DOWN*5)
                self.play(GrowFromCenter(no),run_time=1)
                self.get_hit_flash(switch_list[0][1])
                self.remove(no)

        self.wait(1)    

class second_hint_30(Scene):

    def create_on_switch1(self, point):
        swb = SwitchBoard(height=2, width=1.2, fill_color=BLACK, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#FF0000',radius = 0.5)
        blb.shift(DOWN*0.3)
        text = TexMobject("ON", font="Arial")
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(DOWN*5)
        text.scale(2)
        text1 = TexMobject("OFF")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(UP*5)
        text1.scale(2)
        grp = VGroup(swb, blb)
        #grp.add(rect)
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)

    def create_off_switch(self,point):
        swb = SwitchBoard(fill_color=BLACK,height=3,width=2.2, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#FF0000',radius=0.5)
        blb.shift(UP*0.3)
        grp = VGroup(swb, blb)
        text = TexMobject("OFF",font='Arial')
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(UP*5)
        text.scale(2)
        text1 = TexMobject("ON")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(DOWN*5)
        text1.scale(2)
        
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)  

    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )

    def toggle_switch1(self,switch,point,flag,value, extra_anim=None):
        if(flag==True):
            s1 = self.create_off_switch(point)
            self.remove(switch)
            self.add(s1)
            if(extra_anim is None):
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            else:
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])), extra_anim)
            return s1
        else:
            s2 = self.create_on_switch1(point)
            self.remove(switch)
            self.add(s2)
            if(extra_anim is None):
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            else:
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])), extra_anim)
            return s2
 
      

    def construct(self):
        point = np.array([5,0,0])   
        switch_list = list()
        flag =  False
        text1 = TextMobject("Switch no. 30",color=BLACK)
        text1.shift(RIGHT*5+DOWN*1.4)
        # self.add(text1)
        # self.add(counter)
        
        
        switch1 = self.create_off_switch(point)
        self.add(switch1)
        switch_list.append([switch1,point,flag])
        factor = TextMobject("Factors : ",color=BLACK)
        self.play(Write(text1))
        factor.shift(DOWN*3+LEFT*2)
        old_obj = TextMobject()
        old_obj.shift(LEFT*2.5+UP*2)
        self.add(old_obj)
        # self.add(factor)
        
        
        #changes from here no loops till 36 , however if you want to make changes just make a for loop from here 

        new_obj = TextMobject("Divisibility of number 30 :",color=BLACK)
        similar = TextMobject("And in this way ... ",color=BLACK) 
        # self.add(new_obj)

        value = TextMobject(str([1,2,3,5,6,10,15,30]),color=RED_D)
        value.set_color=RED_D   
        value.shift(LEFT*2.7+DOWN*2)
        new_obj.add(factor)

        new_obj.shift(LEFT*2.28+UP*2)
        # self.play((similar))
        self.play(FadeInFromDown(similar))
        self.remove(similar)
        self.play(Transform(old_obj,new_obj))
        self.play(Write(value))
        # self.toggle_switch1(switch_list[0][0],switch_list[0][1],switch_list[0][2],i, extra_anim = Write(value))
        self.wait(3)
        

class second_hint_36(Scene):

    def create_on_switch1(self, point):
        swb = SwitchBoard(height=2, width=1.2,fill_color=BLACK, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#00ff00',radius = 0.5)
        blb.shift(DOWN*0.3)
        text = TexMobject("ON", font="Arial")
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(DOWN*5)
        text.scale(2)
        text1 = TexMobject("OFF")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(UP*5)
        text1.scale(2)
        grp = VGroup(swb, blb)
        #grp.add(rect)
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)

    def create_off_switch(self,point):
        swb = SwitchBoard(fill_color=BLACK,height=3,width=2.2, fill_opacity=0.5,corner_radius=0.3)
        blb = Dot(fill_color = '#ff0000',radius=0.5)
        blb.shift(UP*0.3)
        grp = VGroup(swb, blb)
        text = TexMobject("OFF",font='Arial')
        text.add_background_rectangle(opacity=0)
        text.set_color(BLACK)
        text.shift(UP*5)
        text.scale(2)
        text1 = TexMobject("ON")
        text1.add_background_rectangle(opacity=0)
        text1.set_color(BLACK)
        text1.shift(DOWN*5)
        text1.scale(2)
        
        grp_text = VGroup(text,text1)
        grp.add(grp_text)
        grp.shift(point)
        return(grp)  

    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )

    def toggle_switch1(self,switch,point,flag,value, extra_anim=None):
        if(flag==True):
            s1 = self.create_off_switch(point)
            self.remove(switch)
            self.add(s1)
            if(extra_anim is None):
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            else:
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])), extra_anim)
            return s1
        else:
            s2 = self.create_on_switch1(point)
            self.remove(switch)
            self.add(s2)
            if(extra_anim is None):
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            else:
                self.play(self.get_hit_flash(point+np.array([0,0.3,0])), extra_anim)
            return s2
      

    def construct(self):
        point = np.array([5,0,0])   
        switch_list = list()
        flag =  False
        text1 = TextMobject("Switch no. 36",color=BLACK)
        text1.shift(RIGHT*5+DOWN*1.4)
        # self.add(text1)
        # self.add(counter)
        
        
        switch1 = self.create_on_switch1(point)
        self.add(switch1)
        switch_list.append([switch1,point,flag])
        factor = TextMobject("Factors : ",color=BLACK)
        self.play(Write(text1))
        factor.shift(DOWN*3+LEFT*2)
        old_obj = TextMobject()
        old_obj.shift(LEFT*2.5+UP*2)
        self.add(old_obj)
        # self.add(factor)
        
        
        #changes from here no loops till 36 , however if you want to make changes just make a for loop from here 

        new_obj = TextMobject("Divisibility of number 36 :",color=BLACK)
        similar = TextMobject("Similarly",color=BLACK) 
        # self.add(new_obj)

        value = TextMobject(str([1,2,3,4,6,9,12,18,36]),color=RED_D)
        value.set_color=RED_D   
        value.shift(LEFT*2.34+DOWN*2)
        new_obj.add(factor)

        new_obj.shift(LEFT*2.28+UP*2)
        # self.play((similar))
        self.play(FadeInFromDown(similar))
        self.remove(similar)
        self.play(Transform(old_obj,new_obj))
        self.play(Write(value))
        self.wait(3)
        
        # question_mark.shift(LEFT+UP*2)
        # self.remove(new_obj)


class Wrong(VMobject):
    CONFIG ={
    "fill_color":RED_D, 
    "fill_opacity":0.5,
    }
    def generate_points(self):
        line1 = Line(LEFT+DOWN,UP+RIGHT,fill_color=RED_D)
        line2 = Line(LEFT+UP,DOWN+RIGHT,fill_color=RED_D)
        line1.add(line2)
        self.add(line1) 

class LineDemo(Scene):
    config = {
        "x_min":-5,
        "x_max":5,
        "y_min":-5,
        "y_max":5,
    }   

    def construct(self):
        lineV = Line(LEFT*8,RIGHT*8,color='#D3D3D3',fill_color='#D3D3D3')
        lineH = Line(UP*5,DOWN*5,fill_color='#D3D3D3',color='#D3D3D3')
        line = VGroup(lineV,lineH)
        all_factors = [[1,2,4,5,10,20],[1,5,25],[1,2,3,5,6,10,15,30],[1,2,3,4,6,9,12,18,36]]
        true_false = [ 'OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF',
                        'OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON', 
                        'OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF',
                        'OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON \\rightarrow OFF \\rightarrow ON']

        self.add(line)
        self.play(ShowCreation(line))
        self.wait()
        
        factor_20 = TextMobject("Factors of 20 :",fill_color=BLACK,color=BLACK)
        factor_201 = TextMobject(" "+str(all_factors[0]),color=BLACK)
        true_false20 = TexMobject(str(true_false[0]), color=RED_D)
        factor_201.next_to(factor_20,DOWN)
        true_false20.next_to(factor_201,DOWN)  #true false has shifted down to factor part
        true_false20.scale(0.5)
        
        print("true_false[1]", true_false[0])
        factor_20.add(factor_201)
        self.play(factor_20.move_to, LEFT*4+UP*2)
        true_false20.shift(LEFT*4+UP*2)
        self.play(Write(true_false20))
        
        
        factor_25 = TextMobject("Factors of 25 :",fill_color=BLACK,color=BLACK)
        factor_251 = TextMobject(" "+str(all_factors[1]),color=BLACK)
        true_false25 = TexMobject(str(true_false[1]), color=RED_D)
        factor_251.next_to(factor_25,DOWN)
        true_false25.next_to(factor_251,DOWN)  #true false has been shifted down to factor part
        true_false25.scale(0.5)
        factor_25.add(factor_251)
        true_false25.shift(RIGHT*4+UP*2)
        
        self.play(factor_25.move_to, RIGHT*4+UP*2)
        self.play(Write(true_false25))        

        factor_30 = TextMobject("Factors of 30 :",fill_color=BLACK,color=BLACK)
        factor_301 = TextMobject(" "+str(all_factors[2]),color=BLACK)
        true_false30 = TexMobject(str(true_false[2]),color=RED_D)
        factor_301.next_to(factor_30,DOWN)
        true_false30.next_to(factor_301,DOWN)
        
        factor_30.add(factor_301)
        self.play(factor_30.move_to, LEFT*4+DOWN*2)
        true_false30.scale(0.4)
        true_false30.shift(LEFT*3.8+DOWN*2)
        self.play(Write(true_false30))

        factor_36 = TextMobject("Factors of 36 :",fill_color=BLACK,color=BLACK)
        factor_361 = TextMobject(" "+str(all_factors[3]),color=BLACK)
        true_false36 = TexMobject(str(true_false[3]),color=RED_D)
        factor_361.next_to(factor_36,DOWN)
        true_false36.next_to(factor_361,DOWN)
    
        factor_36.add(factor_361)
        true_false36.scale(0.4)
        self.play(factor_36.move_to, RIGHT*4+DOWN*2)
        true_false36.shift(RIGHT*3.6+DOWN*2)
        self.play(Write(true_false36))
        
        even1 = TextMobject("EVEN ",color='#FF0000')
        even2 = TextMobject("EVEN ",color='#FF0000')
        odd1 = TextMobject("ODD ",color='#00FF00')
        odd2 = TextMobject("ODD ",color='#00FF00')
        
        even1.shift(LEFT*4+UP*3.3)
        
        even2.shift(LEFT*4+DOWN*0.7)
        self.play(FadeIn(even1))
        self.play(FadeIn(even2))

        
        odd1.shift(RIGHT*3.6+UP*3.3)
        
        odd2.shift(RIGHT*3.6+DOWN*0.7)
        self.play(FadeIn(odd1)) 
        self.play(FadeIn(odd2))
        self.wait(2)   
        

class NO_100(ThreeDScene):
    def get_hit_flash(self, point):
        flash = Flash(
            point,
            line_length=0.2,
            flash_radius=0.4,
            run_time=1,
            remover=True,
        )
        flash_mob = flash.mobject
        for submob in flash_mob:
            submob.reverse_points()
        return Uncreate(
            flash.mobject,
            run_time=0.25,
            lag_ratio=0,
        )    

    def create_on_switch1(self, point,value):
        swb = SwitchBoard(fill_color = BLACK) # ---  color changes to YELLOW_D to BLACk
        blb = Dot(fill_color = GREEN,radius = 0.18)
        blb.shift(DOWN*0.2)
        text = TexMobject(str(value),color=BLACK)
        '''
        rect = Rectangle(width=0.5,height=0.3)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(DOWN*(0.5))'''
        text.shift(DOWN*0.5)
        text.scale(0.5)
        grp = VGroup(swb, blb)
        grp.add(text)
        grp.shift(point)
        return(grp)

    def toggle_switch(self, switch1, switch2,point):
        self.remove(switch1)
        self.add(switch2)
        self.play(self.get_hit_flash(point)) 

    def toggle_switch1(self,switch,point,flag,value,rt=1):
        if(flag==True):
            s1 = self.create_off_switch(point,value)
            self.remove(switch)
            self.add(s1)
            self.play(self.get_hit_flash(point+np.array([0,0.3,0])))
            return s1
        else:
            s2 = self.create_on_switch1(point,value)
            self.remove(switch)
            self.add(s2)
            self.play(self.get_hit_flash(point+np.array([0,-0.3,0])))
            return s2


    def create_off_switch(self,point,value):
        swb = SwitchBoard(fill_color = BLACK)   # color changes to YELLOW_D to BLACK
        blb = Dot(fill_color = RED,radius=0.18)
        blb.shift(UP*0.2)
        text = TexMobject(str(value),color=BLACK)
        '''
        rect = Rectangle(width=0.6,height=0.3,fill_color=BLACK)
        rect.set_style(
            fill_opacity=1,
            fill_color=BLACK,
            stroke_width=0,
        )
        rect.shift(UP*(0.5))
        grp.add(rect)
        '''
        text.shift(DOWN*0.5)
        text.scale(0.5)
        grp = VGroup(swb, blb)
        grp.add(text)
        grp.shift(point)
        return(grp)

    def construct(self):
               
        point = np.array([-7.5,2.8,0])
        flag = False
        point_f = list()
        for j in range(0,5):
            for i in range(0,20):
                point[0] +=0.7
                temp = np.array(point)
                point_f.append([temp,flag])
            point[1]-=1.48
            point[0]=-7.5    
        print(len(point_f))
        switch_list = list()
        no = 1
        for i in point_f:
            flag=True
            switch1 = self.create_off_switch(i[0],no)
            switch_list.append([switch1,i[0],i[1]])              #i[0] == point and i[1] == flag
            if(no<=10):
                rt = 0.25
            else:   
                rt = 0.02
            self.play(ShowCreation(switch1,run_time=rt))
            no+=1               
        print(point_f[99])
        # switch1 = self.create_on_switch1(point_f[99][0],no)
        # self.play(ShowCreation(switch1,run_time=0.02))
        self.wait(1)   
        ''' 
        for bhuk in range(6):
            focus = Rectangle(height=0.8,width=0.45,color=BLACK)
            focus.shift(point_f[bhuk][0])
            self.play(GrowArrow(focus))
            switch_list[bhuk][0] = self.toggle_switch1(switch_list[bhuk][0],switch_list[bhuk][1],switch_list[bhuk][2],bhuk+1)
            print(switch_list[bhuk][2])
            switch_list[bhuk][2] ^= True
            switch_list[bhuk][0] = self.toggle_switch1(switch_list[bhuk][0],switch_list[bhuk][1],switch_list[bhuk][2],bhuk+1)
            self.remove(focus)
            self.wait(1)   
               
        # switch_list at index 0-> switch_object  1 -> point  2 -> flag
          
        for bhuk in range(6): 
            switch_list[bhuk][2] ^= True
        '''
        count = 1   
        rate = 0.001 
        for k in range(0,101):
            for idx, i in enumerate(switch_list):
                if((idx+1)%(k+1)==0):
                    i[0] = self.toggle_switch1(i[0],i[1],i[2],idx+1,rate)
                    i[2]^=True     
        self.wait(2)                
        


