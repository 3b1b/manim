import Tkinter
from PIL import ImageTk, Image
import itertools as it
import time


class TkSceneRoot(Tkinter.Tk):
    def __init__(self, scene):
        if scene.frames == []:
            raise Exception(str(scene) + " has no frames!")
        Tkinter.Tk.__init__(self)

        kwargs = {
            "height" : scene.camera.pixel_shape[0],        
            "width" : scene.camera.pixel_shape[1],
        }
        self.frame = Tkinter.Frame(self, **kwargs)
        self.frame.pack()
        self.canvas = Tkinter.Canvas(self.frame, **kwargs)
        self.canvas.configure(background='black')        
        self.canvas.place(x=0,y=0)

        last_time = time.time()
        for frame in it.cycle(scene.frames):
            try:
                self.show_new_image(frame)
            except:
                break
            sleep_time = scene.frame_duration
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
        self.update()
