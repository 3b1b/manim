from for_3b1b_videos.pi_creature import *

class PiCreatureClass(VGroup):
    CONFIG = {
        "width" : 3,
        "height" : 2
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        for i in range(self.width):
            for j in range(self.height):
                pi = PiCreature().scale(0.3)
                pi.move_to(i*DOWN + j* RIGHT)
                self.add(pi)



def FlashThroughClass(Animation):
    CONFIG = {
        "highlight_color" : GREEN,
    }

    def __init__(self, mobject, mode = "linear", **kwargs):

        digest_config(self, kwargs)
        self.indices = range(self.height * self.width)
        
        if mode == "random":
            np.random.shuffle(self.indices)

        Animation.__init__(self, mobject, **kwargs)
        

    def update_mobject(self, alpha):
        index = int(np.floor(alpha * self.height * self.width))
        for pi in self.mobject:
            pi.set_color(BLUE_E)
        self.mobject[index].set_color(self.highlight_color)
