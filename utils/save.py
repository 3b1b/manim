import dill
import inspect
import pickle

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
    parent_of_caller = get_calling_frame().f_back.f_locals["self"]
    parent_methods = filter(
        lambda x: x[1].im_func.func_code.co_filename == get_calling_filename(),
        inspect.getmembers(parent_of_caller, inspect.ismethod),
    )

    parent_methods.sort(key=lambda x: x[1].im_func.func_code.co_firstlineno)
    cur_position = next((i for i, pair in enumerate(parent_methods)
        if pair[0] == get_calling_function_name()))

    if cur_position > 0:
        prev_function = parent_methods[cur_position - 1][0]
    else:
        prev_function = None

    return prev_function

def save_state(self, filename=None):
    pass
    # if filename is None:
    #     filename = get_calling_function_name() + ".mnm"
    # state = self.__dict__.copy()
    # # must be removed before save to prevent segfault
    # if "writing_process" in self.__dict__:
    #     del state["writing_process"]
    # if "canvas" in state["camera"].__dict__:
    #     del state["camera"].__dict__["canvas"]
    # pickle.dump(state, open(filename, "wb"))

def load_previous_state(filename=None):
    return {}
    # if filename is None:
    #     filename = get_previous_function_name() + ".mnm"
    # loaded_state = pickle.load(open(filename, "rb"))
    # return loaded_state
