from .camera import Camera
import copy


class JsCamera(Camera):
    def __init__(self, **kwargs):
        super().__init__(self, **kwargs)
        self.serialized_frame = []
        self.pixel_array = None

    def display_multiple_non_background_colored_vmobjects(self, vmobjects, _):
        for vmobject in vmobjects:
            # TODO: Store a proto instead of JSON.
            needs_redraw = False
            point_hash = hash(tuple(vmobject.points.flatten()))
            if vmobject.point_hash != point_hash:
                vmobject.point_hash = point_hash
                needs_redraw = True
            self.serialized_frame.append(
                {
                    "points": vmobject.points.tolist(),
                    "style": vmobject.get_style(simple=True),
                    "id": id(vmobject),
                    "needs_redraw": needs_redraw,
                }
            )

    def reset(self):
        self.serialized_frame = []

    def set_frame_to_background(self, background):
        self.serialized_frame = copy.deepcopy(background)
