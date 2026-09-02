from __future__ import annotations

from collections import OrderedDict
from fractions import Fraction
import sys

import av
import numpy as np
from PIL import Image

from manimlib.mobject.types.image_mobject import ImageMobject
from manimlib.renderer.texture import LayeredPixels
from manimlib.renderer.uniform_block import COMMON_UNIFORMS
from manimlib.renderer.uniform_block import uniform_block_dtype
from manimlib.utils.images import get_full_video_path
from manimlib.utils.rate_functions import linear

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self, Tuple


# How many decoded frames one source keeps, where it has not read the whole video in
DEFAULT_CACHE_SIZE: int = 32
# Up to how many bytes of decoded frames a video is preloaded, held whole both in memory and
# on the gpu rather than read a frame at a time, which for the short clips this is aimed at
# is every one of them
PRELOAD_LIMIT: int = 64_000_000


class VideoSource(object):
    """
    The frames of one video file, decoded on demand and returned as straight rgba, alpha
    included where the video carries one.

    Shared by every mobject naming the file, so a grid of characters drawn from one clip
    decodes each frame once between them.
    """
    _sources: dict[str, VideoSource] = dict()

    @classmethod
    def get(cls, path: str, preload: bool | None = None) -> VideoSource:
        """
        The source for this file, shared with everything else naming it, and so read one way
        or the other for the whole of it: one asked for whole now is read in now, but one
        already read in whole stays that way.
        """
        source = cls._sources.get(path)
        if source is None:
            source = cls._sources[path] = cls(path, preload)
        elif preload and not source.preloaded:
            source.read_all()
        return source

    def __deepcopy__(self, memo: dict) -> VideoSource:
        """Shared rather than copied; the container behind it cannot be copied in any case."""
        return self

    def __init__(self, path: str, preload: bool | None = None):
        self.path = path
        self.is_live = path.startswith("/dev/video") or path.isdigit()
        kw = {}
        if path.isdigit():
            kw["format"] = "avfoundation"
        elif path.startswith("/dev/video"):
            kw["format"] = "v4l2"

        if self.is_live:
            kw["options"] = {
                "fflags": "nobuffer",
                "flags": "low_delay",
                "framedrop": "strict"
            }
        self.container = av.open(path, **kw)
        self.stream = self.container.streams.video[0]
        self.stream.thread_type = "AUTO"

        self.width = self.stream.codec_context.width
        self.height = self.stream.codec_context.height
        self.frame_rate = Fraction(self.stream.average_rate or self.stream.guessed_rate or 30)

        if self.is_live:
            self.num_frames = sys.maxsize
            self.duration = float("inf")
            preload = False
        else:
            self.num_frames = self.get_num_frames()
            self.duration = float(self.num_frames / self.frame_rate)

        self.num_frames = self.get_num_frames()
        self.duration = float(self.num_frames / self.frame_rate)

        # A window of decoded frames, where the whole clip is not held, see remember
        self.cache: OrderedDict[int, np.ndarray] = OrderedDict()
        # Where a sequential read has got to, so that the common case of asking for one frame
        # after another never seeks
        self.decoder = None
        self.next_index = 0

        # Every frame as one array, held only where the whole clip was read in
        self.all_frames: np.ndarray | None = None
        self.preloaded = False
        if preload is None:
            preload = self.fits_at_once()
        if preload:
            self.read_all()

    def get_num_frames(self) -> int:
        """
        How many frames the video holds: what the container says, else the duration times
        the frame rate, else a count from reading through.
        """
        if self.is_live:
            return sys.maxsize
        if self.stream.frames:
            return self.stream.frames
        if self.stream.duration and self.stream.time_base:
            seconds = float(self.stream.duration * self.stream.time_base)
            return max(1, round(seconds * float(self.frame_rate)))
        if self.container.duration:
            seconds = self.container.duration / av.time_base
            return max(1, round(seconds * float(self.frame_rate)))
        return sum(1 for _ in self.container.decode(self.stream))

    def fits_at_once(self) -> bool:
        """Whether the whole clip is small enough to hold at once, see PRELOAD_LIMIT."""
        return self.num_frames * self.width * self.height * 4 <= PRELOAD_LIMIT

    def get_all_frames(self) -> np.ndarray:
        """Every frame as one array of layers, decoded once and kept."""
        if self.all_frames is None:
            self.read_all()
        return self.all_frames

    def read_all(self) -> None:
        """
        Decode the whole clip, after which every frame is there to be read without any
        further decoding, see get_frame.
        """
        self.container.seek(0, stream=self.stream)
        frames = [self.to_rgba(frame) for frame in self.container.decode(self.stream)]
        # What was decoded is what there is, whatever the container claimed
        self.num_frames = max(1, len(frames))
        self.duration = float(self.num_frames / self.frame_rate)
        # Held as one array rather than a frame at a time: it is what an upload wants, and
        # keeping the window as well would be keeping the clip twice over
        self.all_frames = np.stack(frames or [self.blank_frame()])
        self.cache.clear()
        self.preloaded = True

    def blank_frame(self) -> np.ndarray:
        """A frame of nothing, the size of the video's own."""
        return np.zeros((self.height, self.width, 4), dtype=np.uint8)

    def to_rgba(self, frame) -> np.ndarray:
        """One decoded frame as straight rgba bytes."""
        return frame.to_ndarray(format="rgba")

    def seek(self, index: int) -> None:
        """Put the read at the last keyframe at or before this frame."""
        if self.is_live:
            if self.decoder is None:
                self.decoder = self.container.decode(self.stream)
            return
        time_base = self.stream.time_base or Fraction(1, int(self.frame_rate))
        offset = int(index / self.frame_rate / time_base)
        self.container.seek(offset, stream=self.stream, backward=True, any_frame=False)
        self.decoder = self.container.decode(self.stream)
        self.next_index = None

    def get_live_frame(self) -> np.ndarray:
        """Gets the next frame for a video streaming device."""
        if self.decoder is None:
            self.decoder = self.container.decode(self.stream)

        try:
            frame = next(self.decoder)
            self.current_live_frame = self.to_rgba(frame)
        except (StopIteration, av.AVError):
            if self.current_live_frame is None:
                return self.blank_frame()

        return self.current_live_frame

    def get_frame(self, index: int) -> np.ndarray:
        """
        The pixels of one frame, straight out of the whole clip where that was read in, and
        otherwise decoded up to, see read_up_to.

        Where the read runs off the end, the frame count having only been an estimate, what
        was decodable is taken to be the whole video and its last frame stands in.
        """
        if self.is_live:
            return self.get_live_frame()
        if self.preloaded:
            return self.get_all_frames()[int(np.clip(index, 0, self.num_frames - 1))]
        while True:
            index = int(np.clip(index, 0, self.num_frames - 1))
            pixels = self.cache.get(index)
            if pixels is not None:
                self.cache.move_to_end(index)
                return pixels
            pixels = self.read_up_to(index)
            if pixels is not None:
                return pixels
            if index == 0:
                # Nothing in the file decodes at all, so there is nothing to show of it
                return self.blank_frame()
            self.num_frames = index
            index -= 1

    def read_up_to(self, index: int) -> np.ndarray | None:
        """
        Decode forward to a frame from where the last read left off, seeking first where that
        is already past it, so a jump backwards costs a keyframe seek and a jump forwards the
        frames between. None where the read runs off the end before reaching it.
        """
        if self.decoder is None or self.next_index is None or index < self.next_index:
            self.seek(index)
        for frame in self.decoder:
            at = self.index_of(frame)
            self.next_index = at + 1
            if at >= index:
                pixels = self.to_rgba(frame)
                self.remember(at, pixels)
                # Under what was asked for too, where the video holds no frame there, so
                # that asking again reads from the cache rather than seeking afresh
                if at != index:
                    self.remember(index, pixels)
                return pixels
        self.decoder = None
        return None

    def index_of(self, frame) -> int:
        """Which frame of the video a decoded one is, from its timestamp."""
        if frame.pts is None or self.stream.time_base is None:
            return self.next_index or 0
        seconds = float(frame.pts * self.stream.time_base)
        return round(seconds * float(self.frame_rate))

    def remember(self, index: int, pixels: np.ndarray) -> None:
        self.cache[index] = pixels
        self.cache.move_to_end(index)
        while len(self.cache) > DEFAULT_CACHE_SIZE:
            self.cache.popitem(last=False)


class VideoFrames(LayeredPixels):
    """
    The frames of a video on the gpu, and which of them is showing.

    A preloaded clip goes up once as a stack of every frame, shared by every mobject naming
    the file, and changing frame is then just a change of layer: no decode, no upload. One
    read a frame at a time keeps a single layer, rewritten as the frame changes.

    The frame number is held here beside the pixels so the two survive a copy or a become.
    """

    def __init__(
        self,
        video: VideoSource,
        loaded: int = -1,
        layers: np.ndarray | None = None,
    ):
        self.video = video
        # Which frame the single layer holds, where the clip is not preloaded. Only a record
        # of what was uploaded; which frame is showing is the mobject's uniform
        self.loaded = loaded
        if video.preloaded:
            super().__init__(video.get_all_frames(), key=video.path)
        elif layers is not None:
            super().__init__(layers)
        else:
            super().__init__(video.blank_frame()[np.newaxis])

    @property
    def preloaded(self) -> bool:
        """
        Whether every frame is up at once, and so shared with every other mobject naming the
        file. Settled when these were made, whatever the source reads in later.
        """
        return self.key is not None

    def copy(self) -> VideoFrames:
        # A preloaded stack is read alike by everything holding it, so a copy holds that one
        if self.preloaded:
            return self
        return VideoFrames(self.video, self.loaded, self.layers)

    def load(self, index: int) -> None:
        """Make the pixels of a frame available to be drawn."""
        if self.preloaded or index == self.loaded:
            return
        self.loaded = index
        self.set_layers(self.video.get_frame(index)[np.newaxis])

    def get_pixels(self, index: int) -> np.ndarray:
        """The straight rgba pixels of one frame."""
        return self.layers[index if self.preloaded else 0]


class VideoMobject(ImageMobject):
    """
    A video showing whichever frame set_time was last given, and otherwise an ImageMobject
    in every respect.

    A time past the end either holds on the last frame, or comes round to the beginning
    if loop is set to True
    """

    shader_file: str = "video.wgsl"
    uniform_dtype: np.dtype = uniform_block_dtype(*COMMON_UNIFORMS, ("frame", 1))

    def __init__(
        self,
        filename: str,
        height: float = 4.0,
        time: float = 0.0,
        loop: bool = False,
        preload: bool | None = None,
        **kwargs
    ):
        self.loop = loop
        # Read by init_texture, which the constructor below reaches
        self._preload = preload
        super().__init__(filename, height=height, **kwargs)
        self.set_time(time)

    def init_texture(self, filename: str) -> VideoFrames:
        """
        A clip preloaded is decoded whole and goes up as one stack shared by everything
        naming the file, moving between its frames costing no more than a uniform; one that
        is not is read a frame at a time, which every mobject drawn from it needs its own
        layer of. Small enough clips are preloaded by default, see PRELOAD_LIMIT.
        """
        path = str(get_full_video_path(filename))
        return VideoFrames(VideoSource.get(path, self._preload))

    @property
    def frames(self) -> VideoFrames:
        """
        The frames this is drawn from, read from where the mobject holds its images rather
        than kept alongside them, so that a copy reads its own rather than these.
        """
        return self.textures["Texture"]

    @property
    def source(self) -> VideoSource:
        """The video the frames come from, which is likewise the frames' to say."""
        return self.frames.video

    @property
    def video_path(self) -> str:
        return self.source.path

    @property
    def preloaded(self) -> bool:
        """
        Whether the whole clip is held at once, and so shared with every other mobject
        naming the file, rather than read a frame at a time.
        """
        return self.frames.preloaded

    @property
    def frame_index(self) -> int:
        """ Which frame of the video is showing, which the uniform alone decides. """
        index = round(float(self.uniforms["frame"]))
        if self.loop:
            return index % self.source.num_frames
        return int(np.clip(index, 0, self.source.num_frames - 1))

    def get_source_size(self) -> Tuple[int, int]:
        return (self.source.width, self.source.height)

    # Which frame is showing

    def set_time(self, time: float):
        """ Show the frame at a given time in seconds. """
        return self.set_frame(time * float(self.source.frame_rate))

    def increment_time(self, dt: float):
        """ Move on by a length of time. """
        return self.set_time(self.get_time() + dt)

    def play_from(self, time: float = 0.0):
        """ Play on from a given time. """
        self.set_time(time)
        return self.add_updater(lambda mob, dt: mob.increment_time(dt))

    def animate_set_time(self, time: float, run_time=None, rate_func=linear, **kwargs):
        """Play up to a given time, by default taking as long as the clip it covers."""
        if run_time is None:
            run_time = abs(time - self.get_time())
        return self.animate(run_time=run_time, rate_func=rate_func).set_time(time)

    def set_frame(self, index: float):
        """ Show a frame by its number rather than its time. """
        if not self.loop:
            index = np.clip(index, 0, self.source.num_frames - 1)
        self.uniforms["frame"] = index
        self.frames.load(self.frame_index)
        return self

    def get_time(self) -> float:
        """
        Where the video has got to, in seconds, which is not quite the time of the frame
        showing: a time between two frames is kept as it was given, see increment_time, and
        a clip which loops goes on counting past its own end rather than beginning again.
        """
        return float(self.uniforms["frame"] / self.source.frame_rate)

    def get_duration(self) -> float:
        return self.source.duration

    def get_num_frames(self) -> int:
        return self.source.num_frames

    def get_frame_rate(self) -> float:
        return float(self.source.frame_rate)

    # Reading it

    def get_pixels(self) -> np.ndarray:
        """The straight rgba pixels of the frame now showing."""
        return self.frames.get_pixels(self.frame_index)

    def interpolate(self, mobject1, mobject2, alpha, *args, **kwargs) -> Self:
        """
        Blend as any mobject does, then make sure the pixels match the frame the blended
        uniform now names, which for a preloaded clip is already so and otherwise is an upload.
        """
        super().interpolate(mobject1, mobject2, alpha, *args, **kwargs)
        self.frames.load(self.frame_index)
        return self

    @property
    def image(self) -> Image.Image:
        """ The frame now showing, as an image, which is what ImageMobject reads pixels from. """
        return Image.fromarray(self.get_pixels(), mode="RGBA")


class Sprite(VideoMobject):
    """
    A VideoMobject read nearest pixel rather than blended, keeping pixel art crisp however
    far it is scaled up.
    """
    texture_filter: str = "nearest"
