import numpy as np


class CairoRenderer:
    def __init__(self, scene, camera, file_writer):
        self.scene = scene
        self.camera = camera
        self.file_writer = file_writer

    def get_frame(self):
        """
        Gets the current frame as NumPy array.

        Returns
        -------
        np.array
            NumPy array of pixel values of each pixel in screen.
            The shape of the array is height x width x 3
        """
        return np.array(self.camera.pixel_array)
