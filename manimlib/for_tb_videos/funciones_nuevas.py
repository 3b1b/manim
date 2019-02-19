from big_ol_pile_of_manim_imports import *

def direcciones_v1(text):
	direccion=[]
	for i in range(len(text)):
		if i%2!=0 and i!=0 and i!=len(text)-1:
			direccion.append(UP*0.5)
		elif i%2==0 and i!=0 and i!=len(text)-1:
			direccion.append(DOWN*0.5)
		elif i==0:
			direccion.append(LEFT)
		elif i==len(text)-1:
			direccion.append(RIGHT)
	return direccion
def direcciones_v2(text):
	direccion=[]
	for i in range(len(text)):
		direccion.append(UP*(len(text)-i)/len(text)*1.8)
	return direccion
def direcciones_v3(text):
	direccion=[]
	for i in range(len(text)):
		direccion.append(UP*(i)/len(text))
	return direccion

def coord(x,y):
	return np.array([x,y,0])

def Flecha(not1,not2,proporcion=0.96,**kwargs):
	flecha=Line(not1,not2,**kwargs)
	tip = Polygon(coord(0,0),coord(-0.13,0.3),coord(0,0.2),coord(0.13,0.3))
	tip.set_height(0.3)
	tip.set_stroke(width=0)
	tip.set_fill(opacity=1)
	v=(flecha.get_end()-flecha.get_start())/get_norm(flecha.get_end()-flecha.get_start())
	flecha.put_start_and_end_on(flecha.get_start(),flecha.get_start()+v*get_norm(flecha.get_end()-flecha.get_start())*proporcion)


	tip.move_to(flecha.get_end())
	tip.rotate(flecha.get_angle()+PI/2)
	flecha.add(tip)
	return flecha

def TypeWriter(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25,num_random=89,end=False):
    def devuelve_random(numero):
        for num in range(numero):
                for i in range(random.randint(1,5)):
                    if i==0:
                        i=i+1
                    if i==5:
                       i=i-1
                    t_random=random.randint(i,5)
        return t_random
    for num in range(num_random):
        for i in range(random.randint(1,2)):
            c_random=random.randint(i+1,3)
    for i in range(len(texto)):
        if i in spaces:
            self.add_sound("typewriter/espacio")
            self.wait(time_spaces)
        if i in enters:
            self.add_sound("typewriter/enter")
            self.wait(time_spaces)

        self.add_sound("typewriter/tecla%s"%devuelve_random(num_random))
        self.play(LaggedStart(FadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random(num_random)*time_random)
        if i==len(texto)-1 and end==True:
            self.add_sound("typewriter/fin")
            self.wait(0.1*c_random*time_random)

def KeyBoard(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25,num_random=89):
    def devuelve_random(numero):
        for num in range(numero):
                for i in range(random.randint(1,4)):
                    if i==0:
                        i=i+1
                    if i==3:
                    	i=i-1
                    t_random=random.randint(i,3)
        return t_random
    for num in range(num_random):
        for i in range(random.randint(1,2)):
            c_random=random.randint(i+1,3)
    for i in range(len(texto)):
        if i in spaces:
            self.add_sound("computer_keyboard/espacio")
            self.wait(time_spaces)
        if i in enters:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)
        self.add_sound("computer_keyboard/tecla%s"%devuelve_random(num_random))
        self.play(LaggedStart(FadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random(num_random)*time_random)
        if i==len(texto)-1:
            self.add_sound("computer_keyboard/enter")
            self.wait(time_spaces)


def KeyBoard_(self,texto,p=0.1,lag=0.08,time_random=0.05,random_begin=3,spaces=[],enters=[],time_spaces=0.25,num_random=89):
    def devuelve_random(numero):
        for num in range(numero):
                for i in range(random.randint(1,4)):
                    if i==0:
                        i=i+1
                    if i==3:
                    	i=i-1
                    t_random=random.randint(i,3)
        return t_random
    for num in range(num_random):
        for i in range(random.randint(1,2)):
            c_random=random.randint(i+1,3)
    for i in range(len(texto)):

        self.add_sound("computer_keyboard/tecla%s"%devuelve_random(num_random))
        texto[i].set_fill(None,1)
        self.play(LaggedStart(FadeIn, 
                    texto[i], run_time = p*len(texto[i]),
                    lag_ratio=lag/len(texto[i])))
        self.wait(0.1*devuelve_random(num_random)*time_random)
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
    self.play(LaggedStart(MoveToTarget,grupo_lineas,run_time=tiempo_texto),linea_guia.move_to,coordf,**kwargs)
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
    coord1=texto.get_right()+RIGHT*buff_linea
    coord2=linea.get_center()
    coordf=np.array([coord1[0],coord1[1],0])
    self.play(FadeIn(linea_guia))
    self.play(LaggedStart(Restore,texto_i,run_time=tiempo_pre_texto),LaggedStart(MoveToTarget,grupo_lineas,run_time=tiempo_pos_texto),
        linea_guia.move_to,coordf,**kwargs)
    self.play(FadeOut(linea_guia))
    return grupo_lineas
