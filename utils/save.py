import dill
import inspect

def get_calling_frame():
    this_file = inspect.currentframe().f_code.co_filename
    frame = inspect.currentframe()
    while frame.f_code.co_filename == this_file:
        frame = frame.f_back
    return frame

def get_calling_filename():
    return get_calling_frame().f_code.co_filename

def get_calling_function_name():
    return get_calling_frame().f_code.co_name

def get_previous_function_name():
    calling_scene = get_calling_frame().f_back.f_locals["self"]
    print(calling_scene)
    calling_scene_parts = list(filter(
        lambda x: x[1].__func__.__code__.co_filename == get_calling_filename(),
        inspect.getmembers(calling_scene, inspect.ismethod),
    ))

    calling_scene_parts.sort(key=lambda x: x[1].__func__.__code__.co_firstlineno)
    cur_position = next((i for i, pair in enumerate(calling_scene_parts)
        if pair[0] == get_calling_function_name()))

    if cur_position > 0:
        prev_function = calling_scene_parts[cur_position - 1][0]
    else:
        prev_function = None

    return prev_function

def save_state(self, filename=None):
    if filename is None:
        filename = get_calling_function_name() + ".mnm"
    state = self.__dict__.copy()
    dill.dump(self, open(filename, "wb"))

def load_previous_state(filename=None):
    if filename is None:
        filename = get_previous_function_name() + ".mnm"
    loaded_state = dill.load(open(filename, "rb"))
    return loaded_state.__dict__
