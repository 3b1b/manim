from scene import *
import Tkinter
from PIL import ImageTk, Image
import itertools as it
import time

class TkSceneRoot(Tkinter.Tk):
    def __init__(self, scene):
        if scene.frames == []:
            raise str(scene) + " has no frames!"
        self.scene = scene     
        Tkinter.Tk.__init__(self)

        self.height, self.width = scene.shape
        kwargs = {"height" : self.height, "width" : self.width}
        self.frame = Tkinter.Frame(self, **kwargs)
        self.frame.pack()
        self.canvas = Tkinter.Canvas(self.frame, **kwargs)
        self.canvas.configure(background='black')        
        self.canvas.place(x=-2,y=-2)

        last_time = time.time()
        for frame in it.cycle(self.scene.frames):
            try:
                self.show_new_image(frame)
            except:
                break
            sleep_time = self.scene.frame_duration
            sleep_time -= time.time() - last_time
            time.sleep(max(0, sleep_time))
            last_time = time.time()
        self.mainloop()

    def show_new_image(self, frame):
        image = Image.fromarray(frame).convert('RGB')
        image.resize(self.frame.size())
        photo = ImageTk.PhotoImage(image)
        self.canvas.delete(Tkinter.ALL)
        self.canvas.create_image(
            0, 0,
            image = photo, anchor = Tkinter.NW
        )
        # self.after(self.frame_duration_in_ms, self.show_new_image)
        self.update()
