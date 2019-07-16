from tqdm import tqdm as show_progress
import cv2

from manimlib.scene.scene import Scene


# TODO, is this depricated?
class SceneFromVideo(Scene):
    def construct(self, file_name,
                  freeze_last_frame=True,
                  time_range=None):
        cap = cv2.VideoCapture(file_name)
        self.shape = (
            int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)),
            int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        )
        fps = cap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.camera.frame_rate = fps
        frame_count = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        if time_range is None:
            start_frame = 0
            end_frame = frame_count
        else:
            start_frame, end_frame = [fps * t for t in time_range]

        frame_count = end_frame - start_frame
        print("Reading in " + file_name + "...")
        for count in show_progress(list(range(start_frame, end_frame + 1))):
            returned, frame = cap.read()
            if not returned:
                break
            # b, g, r = cv2.split(frame)
            # self.frames.append(cv2.merge([r, g, b]))
            self.frames.append(frame)
        cap.release()

        if freeze_last_frame and len(self.frames) > 0:
            self.original_background = self.background = self.frames[-1]

    def apply_gaussian_blur(self, ksize=(5, 5), sigmaX=5):
        self.frames = [
            cv2.GaussianBlur(frame, ksize, sigmaX)
            for frame in self.frames
        ]

    def apply_edge_detection(self, threshold1=50, threshold2=100):
        edged_frames = [
            cv2.Canny(frame, threshold1, threshold2)
            for frame in self.frames
        ]
        for index in range(len(self.frames)):
            for i in range(3):
                self.frames[index][:, :, i] = edged_frames[index]
