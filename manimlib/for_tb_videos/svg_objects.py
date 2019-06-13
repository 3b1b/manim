from manimlib.imports import *

class Instagram(VGroup):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        back1=self.color_cell(
            SVGMobject("social_networks/instagram")[2],
            colors = ["#FED372","#B52C94","#4D67D8"]
            )
        back2=self.color_cell(
            SVGMobject("social_networks/instagram")[0],
            colors = ["#B52C94"]
            )
        back3=self.color_cell(
            SVGMobject("social_networks/instagram")[1],
            colors = ["#B83D8D","#8A5DA2","#8A5DA2"]
            )
        back4=self.color_cell(
            SVGMobject("social_networks/instagram")[3],
            colors = ["#D77A84","#B52C94","#BD368A"],
            vect=[0.2,1,0]
            )
        VGroup.__init__(self,**kwargs)
        self.add(back1,back2,back3,back4)

    def color_cell(self,cell,colors,vect=[0.45,1,0]):
        cell.set_color(color=colors,family=True)
        cell.set_stroke(color=colors)
        cell.set_sheen_direction(vect)
        return cell

class PatreonSVG(SVGMobject):
    CONFIG={
    "file_name":"social_networks/patreon.svg"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self, file_name=self.file_name, **kwargs)
        self[0].set_color("#F96855")
        self[2].set_color("#042F42")

        self.set_height(4)

class PatreonSVG2(SVGMobject):
    CONFIG={
    "file_name":"social_networks/patreon2.svg"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self, file_name=self.file_name, **kwargs)
        self[0].set_color("#F96855")
        self[2].set_color("#042F42")

        self.set_height(4)


class Mobile(SVGMobject):
    CONFIG={
    "file_name":"devices/mobile"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1,
        height = 8,
        stroke_color = WHITE,
        **kwargs)
        self[0].set_fill(WHITE)
        self[1].set_fill(BLACK)
        self[2].set_fill(None,0)
        self[2].set_stroke(WHITE,0.5)
        self[3].set_fill(BLACK)
        self[4].set_fill(BLACK)
        self[5].set_fill(BLACK)

class Tu(SVGMobject):
    CONFIG={
    "file_name":"fingers/tu"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 0,
        stroke_width = 0.2,
        height = 4,
        stroke_color = WHITE,
        **kwargs)
        self[0].set_fill("#F4D7AB",1).set_stroke(None,3)
        self[1:].set_stroke(None,0.1)
        self[4:].set_fill("#EDCE9F",1)
        self[11:15].set_fill(WHITE,1)
        self[7].set_fill(BLACK,1)
        self[10].set_fill(BLACK,1)
        self[12:14].set_fill("#EDCE9F",1)

class MeGusta(SVGMobject):
    CONFIG={
    "file_name":"mix/like"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 0,
        height = 3,
        stroke_color = WHITE,
        **kwargs)
        self[0].set_fill("#0277bd",1)
        self[1].set_fill("#01579b",1)
        self[2].set_fill(WHITE,1)
        self[3].set_fill("#01579b",1)

class NoMeGusta(MeGusta):
    def __init__(self, **kwargs):
        MeGusta.__init__(self)
        self.flip().rotate(np.pi)

class Dedo1(SVGMobject):
    CONFIG={
    "file_name":"fingers/dedo"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 0,
        height = 1,
        stroke_color = WHITE,
        **kwargs)

class Dedo2(SVGMobject):
    CONFIG={
    "file_name":"fingers/dedo2"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 0,
        height = 1.3,
        stroke_color = WHITE,
        **kwargs)

class Pin(SVGMobject):
    CONFIG={
    "file_name":"mix/pin"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 0,
        height = 3,
        stroke_color = WHITE,
        **kwargs)
        self.set_fill(RED_E,1)
        self.set_fill(GRAY,1)
        self.set_fill(RED,1)
        self.set_fill(RED_E,1)
        self.set_fill(RED_E,1)
        self.set_fill(RED,1)
        self.rotate(np.pi*0.1)

class MP3(SVGMobject):
    CONFIG={
    "file_name":"devices/mp3"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        **kwargs)
        self.scale(3)
        self[0].set_fill(RED,1)
        self[1].set_fill(BLUE,1)
        self[2].set_fill(WHITE,1)
        self[3].set_fill(WHITE,1)
        self[4:].set_fill(GRAY,1)

    
class Audifonos(SVGMobject):
    CONFIG={
    "file_name":"devices/headphones"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        **kwargs)
        self.set_fill("#d1d5d5",1).scale(0.5)

class Avion(SVGMobject):
    CONFIG={
    "file_name":"mix/avion1"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        fill_opacity = 1,
        stroke_width = 1.5,
        height = 1,
        stroke_color = TT_TEXTO,
        **kwargs)
        self.scale(2).set_fill(TT_TEXTO)

class Palomitas(SVGMobject):
    CONFIG={
    "file_name":"mix/palomitas"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 0,
        height = 1,
        stroke_color = TT_TEXTO,
        **kwargs)
        self.scale(2)
        self[0].set_fill("#efd35b")
        self[1].set_fill("#f9e595")
        self[2].set_fill("#f9e595").shift(RIGHT)
        self[3:7].set_fill("#e2ba13")
        self[7:11].set_fill("#f9e595")
        self[15:23].set_fill(RED)
        self[23].set_fill("#52a2e7")
        self[24].set_fill("#ff6243")
        self[25].set_fill("#3c66b1")
        self[26].set_fill("#c6c3cb")
        self[27].set_fill("#3c66b1",0.6)
        self[28].set_fill("#9b2b00")


class Luna(SVGMobject):
    CONFIG={
    "file_name":"mix/moon"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 0,
        height = 1,
        stroke_color = TT_TEXTO,
        **kwargs)
        self.scale(5)
        self[3:6].set_fill("#999999")
        self[6].set_fill("#ececec")
        self[2].set_fill("#cccccc")


class Planeta(SVGMobject):
    CONFIG={
    "file_name":"mix/planeta1"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 0,
        height = 1,
        stroke_color = TT_TEXTO,
        **kwargs)
        self.scale(5)
        svg[0].set_fill(BLUE)
        svg[1:].set_fill(GREEN)



class Pad(SVGMobject):
    CONFIG={
    "file_name":"mix/pad"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1.5,
        height = 1,
        color=TT_TEXTO,
        stroke_color = TT_TEXTO,
        **kwargs)
        self.scale(11)
        self[1].set_fill(BLACK)

class Pila(SVGMobject):
    CONFIG={
    "file_name":"mix/battery"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color = WHITE,
        **kwargs)


class Camara(SVGMobject):
    CONFIG={
    "file_name":"devices/camera"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color = WHITE,
        **kwargs)


class Reloj(SVGMobject):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name = "devices/clock",
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color = WHITE,
        **kwargs)

class Cursor(SVGMobject):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name = "mix/cursor",
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color = WHITE,
        **kwargs)

class Facebook(SVGMobject):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
            file_name = "social_networks/facebook",
            fill_opacity = 1,
            fill_color="#3C5A9A",
            stroke_width = 1,
            height = 4,
            stroke_color ="#3C5A9A",
        **kwargs)


class Reddits(SVGMobject):
    CONFIG={
    "file_name":"social_networks/reddit"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1,
        fill_color= "#FF3F18",
        height = 4,
        stroke_color = "#FF3F18",
        **kwargs)

class Ubicacion(SVGMobject):
    CONFIG={
    "file_name":"mix/placeholder"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color = WHITE,
        **kwargs)


class Twitter(SVGMobject):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name = "social_networks/twitter",
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color ="#12C0FF",
        fill_color="#12C0FF",
        **kwargs)


class YouTube(SVGMobject):
    CONFIG={
    "file_name":"social_networks/youtube"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1,
        fill_color="#FE0000",
        height = 4,
        stroke_color ="#FE0000",
        **kwargs)

class Basura(SVGMobject):
    CONFIG={
    "file_name":"mix/trash"
    }
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name=self.file_name, 
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color = WHITE,
        **kwargs)


class GitHub(SVGMobject):
    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        SVGMobject.__init__(self,
        file_name = "social_networks/github",
        fill_opacity = 1,
        stroke_width = 1,
        height = 4,
        stroke_color = WHITE,
        **kwargs)




