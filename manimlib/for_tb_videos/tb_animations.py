from manimlib.imports import *

class abrir_caja(Rotating):
    CONFIG={
        "run_time":0.75,
        "rate_func":smooth
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        sobre_izq=self.mobject.points[0]
        sobre_der=self.mobject.points[-1]
        self.mobject[1].rotate(
            alpha * PI*2.3/2,
            about_point=sobre_izq,
            about_edge=sobre_izq,
        )
        self.mobject[2].rotate(
            -alpha * PI*2.3/2,
            about_point=sobre_der,
            about_edge=sobre_der,
        )

class cerrar_caja(Rotating):
    CONFIG={
        "run_time":0.75,
        "rate_func":smooth
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        sobre_izq=self.mobject.points[0]
        sobre_der=self.mobject.points[-1]
        self.mobject[1].rotate(
            -alpha * PI*2.3/2,
            about_point=sobre_izq,
            about_edge=sobre_izq,
        )
        self.mobject[2].rotate(
            alpha * PI*2.3/2,
            about_point=sobre_der,
            about_edge=sobre_der,
        )

class girar_cuerda(Rotating):
    CONFIG={
        "run_time":3,
        "rate_func":there_and_back,
        "axis":DOWN
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        origen=self.mobject.get_end()
        self.mobject.rotate(
            alpha * 30*DEGREES,
            about_point=origen,
            about_edge=origen,
            axis=self.axis
        )

class girar_sistema(Rotating):
    CONFIG={
        "run_time":3,
        "rate_func":there_and_back,
        "axis":UP,
        "origen":ORIGIN
    }    
    def update_mobject(self, alpha):
        Animation.update_mobject(self, alpha)
        self.mobject.rotate(
            alpha * 45*DEGREES,
            about_point=self.origen,
            about_edge=self.origen,
            axis=self.axis
        )

#From Old version

def TypeWriter_(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25,end=False):
    def devuelve_random():
        return random.randint(1,5)
    for i in range(len(texto)):
        if i in spaces:
            self.add_sound("typewriter/espacio")
            self.wait(time_spaces)
        if i in enters:
            self.add_sound("typewriter/enter")
            self.wait(time_spaces)

        self.add_sound("typewriter/tecla%s"%devuelve_random())
        self.Oldplay(OldLaggedStart(OldFadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i==len(texto)-1 and end==True:
            self.add_sound("typewriter/fin")
            self.wait(0.1*devuelve_random()*time_random)

def TypeWriter(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25,end=False):
    def devuelve_random():
        return random.randint(1,5)
    for i in range(len(texto)):

        self.add_sound("typewriter/tecla%s"%devuelve_random())
        texto[i].set_fill(None,1)
        self.Oldplay(OldLaggedStart(OldFadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i<len(texto)-1:
            pre_ty=texto[i].get_center()[1]
            pre_tx=texto[i].get_center()[0]
            pos_ty=texto[i+1].get_center()[1]
            pos_tx=texto[i+1].get_center()[0]
            pre_width=texto[i].get_width()/2
            pos_width=texto[i+1].get_width()/2
            pre_height=texto[i].get_height()/2
            pos_height=texto[i+1].get_height()/2
            dist_min_x=(pre_width+pos_width)*1.6
            dist_min_y=(pre_height+pos_height)*1.2
            if i==0 or dist_max_x<dist_min_x:
                dist_max_x=dist_min_x
            if i==0 or dist_max_y<dist_min_y:
                dist_max_y=dist_min_y
            if abs(pre_ty-pos_ty)>dist_max_y:
                self.add_sound("typewriter/enter")
                self.wait(time_spaces)
            elif abs(pre_tx-pos_tx)>dist_max_x and abs(pre_ty-pos_ty)<dist_max_y:
                self.add_sound("typewriter/espacio")
                self.wait(time_spaces)
        if i==len(texto)-1:
            self.add_sound("typewriter/enter")
            self.wait(time_spaces)

def KeyBoard_(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25):
    def devuelve_random():
        return random.randint(1,3)
    for i in range(len(texto)):
        if i in spaces:
            self.add_sound("computer_keyboard/espacio")
            self.wait(time_spaces)
        if i in enters:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)
        self.add_sound("computer_keyboard/tecla%s"%devuelve_random())
        self.Oldplay(OldLaggedStart(OldFadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i==len(texto)-1:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)


def KeyBoard(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25):
    def devuelve_random():
        return random.randint(1,3)
    for i in range(len(texto)):

        self.add_sound("computer_keyboard/tecla%s"%devuelve_random())
        texto[i].set_fill(None,1)
        self.Oldplay(OldLaggedStart(OldFadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random()*time_random)
        if i<len(texto)-1:
            pre_ty=texto[i].get_center()[1]
            pre_tx=texto[i].get_center()[0]
            pos_ty=texto[i+1].get_center()[1]
            pos_tx=texto[i+1].get_center()[0]
            pre_width=texto[i].get_width()/2
            pos_width=texto[i+1].get_width()/2
            pre_height=texto[i].get_height()/2
            pos_height=texto[i+1].get_height()/2
            dist_min_x=(pre_width+pos_width)*1.6
            dist_min_y=(pre_height+pos_height)*1.2
            if i==0 or dist_max_x<dist_min_x:
                dist_max_x=dist_min_x
            if i==0 or dist_max_y<dist_min_y:
                dist_max_y=dist_min_y
            if abs(pre_ty-pos_ty)>dist_max_y:
                self.add_sound("computer_keyboard/enter")
                self.wait(time_spaces)
            elif abs(pre_tx-pos_tx)>dist_max_x and abs(pre_ty-pos_ty)<dist_max_y:
                self.add_sound("computer_keyboard/espacio")
                self.wait(time_spaces)
        if i==len(texto)-1:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)

def escribe_texto(self,texto,tiempo_texto=1.1,escala_linea=1.5,buff_linea=0.2,**kwargs):
    linea_guia=Line(texto.get_corner(UL),texto.get_corner(DL)).shift(LEFT*buff_linea).scale(escala_linea)
    grupo_lineas=VGroup()
    for letter in texto:
        linea = Line(letter.get_top(),letter.get_bottom())
        linea.replace(letter, dim_to_match=1)
        linea.fade(1)
        linea.save_state()
        grupo_lineas.add(linea)
        linea.target = letter

    coord1=texto.get_right()+RIGHT*buff_linea
    coord2=linea.get_center()
    coordf=np.array([coord1[0],coord1[1],0])
    self.play(FadeIn(linea_guia))
    self.Oldplay(OldLaggedStart(MoveToTarget,grupo_lineas,run_time=tiempo_texto),linea_guia.move_to,coordf,**kwargs)
    self.play(FadeOut(linea_guia))
    return grupo_lineas

def reescribe_texto(self,texto_i,texto,tiempo_pre_texto=1.1,tiempo_pos_texto=1.1,escala_linea=1.5,buff_linea=0.2,alineacion=UL,**kwargs):
    texto.move_to(texto_i,aligned_edge=alineacion)
    linea_guia=Line(texto.get_corner(UL),texto.get_corner(DL)).shift(LEFT*buff_linea).scale(escala_linea)
    grupo_lineas=VGroup()
    for letter in texto:
        linea = Line(letter.get_top(),letter.get_bottom())
        linea.replace(letter, dim_to_match=1)
        linea.fade(1)
        linea.save_state()
        grupo_lineas.add(linea)
        linea.target = letter
    if texto.get_width()<texto_i.get_width():
        texto_ref=texto_i
    else:
        texto_ref=texto
    coord1=texto_ref.get_right()+RIGHT*buff_linea
    coord2=linea.get_center()
    coordf=np.array([coord1[0],coord1[1],0])
    self.play(FadeIn(linea_guia))
    self.Oldplay(OldLaggedStart(OldRestore,texto_i,run_time=tiempo_pre_texto),LaggedStart(MoveToTarget,grupo_lineas,run_time=tiempo_pos_texto),
        linea_guia.move_to,coordf,**kwargs)
    self.play(FadeOut(linea_guia))
    return grupo_lineas

def seleccion_texto(self,texto,color=YELLOW,proporcion_h=1.2,proporcion_w=1.2,opacidad=0.7,direccion=LEFT):
    texto.rect=Rectangle(width=0.001,height=texto.get_height()*proporcion_h).set_fill(color).fade(opacidad).set_stroke(None,0)
    texto.pos_rect=Rectangle(width=texto.get_width()*proporcion_w,height=texto.get_height()*proporcion_h).set_fill(color).fade(opacidad).set_stroke(None,0)
    texto.pos_rect.move_to(texto)
    texto.rect.next_to(texto.pos_rect,direccion,buff=0)

def mostrar_seleccion_texto(self,texto):
    return Transform(texto.rect,texto.pos_rect)

def seleccion_grande_texto(self,texto,escala=1.1,color=YELLOW,opacidad=0.7):
    rectg=Rectangle(width=FRAME_X_RADIUS*2,height=texto.get_height()*escala).set_fill(color).fade(opacidad).set_stroke(None,0)
    rectg.move_to(ORIGIN)
    coord_x=rectg.get_center()[0]
    coord_y=texto.get_center()[1]
    rectg.move_to(np.array([coord_x,coord_y,0]))
    return rectg

def mueve_seleccion(self,rectg,objeto,**kwargs):
    rectg.generate_target()
    coord_x=rectg.get_center()[0]
    coord_y=objeto.get_center()[1]
    rectg.target.move_to(np.array([coord_x,coord_y,0]))
    self.play(MoveToTarget(rectg),**kwargs)