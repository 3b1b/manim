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