from scene import *
import Tkinter
from PIL import ImageTk, Image

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

        self.frame_index = 0
        self.num_frames = len(self.scene.frames)
        self.frame_duration_in_ms = int(1000*scene.frame_duration)
        # self.after(0,self.show_new_image)
        while(1):
            self.frame_index = 0
            self.show_new_image()
        self.mainloop()



    def show_new_image(self):
        self.frame_index += 1
        if self.frame_index >= self.num_frames:
            return
        frame = self.scene.frames[self.frame_index]

        image = Image.fromarray(frame).convert('RGB')
        image.resize(self.frame.size())
        photo = ImageTk.PhotoImage(image)
        self.canvas.delete(Tkinter.ALL)
        self.canvas.create_image(
            0, 0,
            image = photo, anchor = Tkinter.NW
        )
        self.after(self.frame_duration_in_ms, self.show_new_image)
        self.update()
