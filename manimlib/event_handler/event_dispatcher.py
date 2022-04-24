from __future__ import annotations

import numpy as np

from manimlib.event_handler.event_listner import EventListner
from manimlib.event_handler.event_type import EventType


class EventDispatcher(object):
    def __init__(self):
        self.event_listners: dict[
            EventType, list[EventListner]
        ] = {
            event_type: []
            for event_type in EventType
        }
        self.mouse_point = np.array((0., 0., 0.))
        self.mouse_drag_point = np.array((0., 0., 0.))
        self.pressed_keys: set[int] = set()
        self.draggable_object_listners: list[EventListner] = []

    def add_listner(self, event_listner: EventListner):
        assert(isinstance(event_listner, EventListner))
        self.event_listners[event_listner.event_type].append(event_listner)
        return self

    def remove_listner(self, event_listner: EventListner):
        assert(isinstance(event_listner, EventListner))
        try:
            while event_listner in self.event_listners[event_listner.event_type]:
                self.event_listners[event_listner.event_type].remove(event_listner)
        except:
            # raise ValueError("Handler is not handling this event, so cannot remove it.")
            pass
        return self

    def dispatch(self, event_type: EventType, **event_data):
        if event_type == EventType.MouseMotionEvent:
            self.mouse_point = event_data["point"]
        elif event_type == EventType.MouseDragEvent:
            self.mouse_drag_point = event_data["point"]
        elif event_type == EventType.KeyPressEvent:
            self.pressed_keys.add(event_data["symbol"])  # Modifiers?
        elif event_type == EventType.KeyReleaseEvent:
            self.pressed_keys.difference_update({event_data["symbol"]})  # Modifiers?
        elif event_type == EventType.MousePressEvent:
            self.draggable_object_listners = [
                listner
                for listner in self.event_listners[EventType.MouseDragEvent]
                if listner.mobject.is_point_touching(self.mouse_point)
            ]
        elif event_type == EventType.MouseReleaseEvent:
            self.draggable_object_listners = []

        propagate_event = None

        if event_type == EventType.MouseDragEvent:
            for listner in self.draggable_object_listners:
                assert(isinstance(listner, EventListner))
                propagate_event = listner.callback(listner.mobject, event_data)
                if propagate_event is not None and propagate_event is False:
                    return propagate_event

        elif event_type.value.startswith('mouse'):
            for listner in self.event_listners[event_type]:
                if listner.mobject.is_point_touching(self.mouse_point):
                    propagate_event = listner.callback(
                        listner.mobject, event_data)
                    if propagate_event is not None and propagate_event is False:
                        return propagate_event

        elif event_type.value.startswith('key'):
            for listner in self.event_listners[event_type]:
                propagate_event = listner.callback(listner.mobject, event_data)
                if propagate_event is not None and propagate_event is False:
                    return propagate_event

        return propagate_event

    def get_listners_count(self) -> int:
        return sum([len(value) for key, value in self.event_listners.items()])

    def get_mouse_point(self) -> np.ndarray:
        return self.mouse_point

    def get_mouse_drag_point(self) -> np.ndarray:
        return self.mouse_drag_point

    def is_key_pressed(self, symbol: int) -> bool:
        return (symbol in self.pressed_keys)

    __iadd__ = add_listner
    __isub__ = remove_listner
    __call__ = dispatch
    __len__ = get_listners_count
