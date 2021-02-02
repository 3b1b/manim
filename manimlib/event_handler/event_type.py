from enum import Enum


class EventType(Enum):
    MouseMotionEvent = 'mouse_motion_event'
    MousePressEvent = 'mouse_press_event'
    MouseReleaseEvent = 'mouse_release_event'
    MouseDragEvent = 'mouse_drag_event'
    MouseScrollEvent = 'mouse_scroll_event'
    KeyPressEvent = 'key_press_event'
    KeyReleaseEvent = 'key_release_event'
