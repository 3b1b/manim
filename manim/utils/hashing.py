import json
import zlib
import inspect
import copy
import dis
import numpy as np
from types import ModuleType

from ..logger import logger


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        This method is used to serialize objects to JSON format.
        
        If obj is a function, then it will return a dict with two keys : 'code', for the code source, and 'nonlocals' for all nonlocalsvalues. (including nonlocals functions, that will be serialized as this is recursive.)
        if obj is a np.darray, it converts it into a list.
        if obj is an object with __dict__ attribute, it returns its __dict__.
        Else, will let the JSONEncoder do the stuff, and throw an error if the type is not suitable for JSONEncoder. 

        Parameters
        ----------
        obj : Any
            Arbitrary object to convert

        Returns
        -------
        Any
            Python object that JSON encoder will recognize

        """
        if inspect.isfunction(obj) and not isinstance(obj, ModuleType):
            cvars = inspect.getclosurevars(obj)
            cvardict = {**copy.copy(cvars.globals), **copy.copy(cvars.nonlocals)}
            for i in list(cvardict):
                # NOTE : All module types objects are removed, because otherwise it throws ValueError: Circular reference detected if not. TODO
                if isinstance(cvardict[i], ModuleType):
                    del cvardict[i]
            return {"code": inspect.getsource(obj), "nonlocals": cvardict}
        elif isinstance(obj, np.ndarray):
            return list(obj)
        elif hasattr(obj, "__dict__"):
            temp = getattr(obj, "__dict__")
            return self._encode_dict(temp)
        elif isinstance(obj, np.uint8):
            return int(obj)
        try:
            return json.JSONEncoder.default(self, obj)
        except TypeError:
            # This is used when the user enters an unknown type in CONFIG. Rather than throwing an error, we transform
            # it into a string "Unsupported type for hashing" so that it won't affect the hash.
            return "Unsupported type for hashing"

    def _encode_dict(self, obj):
        """Clean dicts to be serialized : As dict keys must be of the type (str, int, float, bool), we have to change them when they are not of the right type.
        To do that, if one is not of the good type we turn it into its hash using the same
        method as all the objects here.

        Parameters
        ----------
        obj : Any
            The obj to be cleaned.
        
        Returns
        -------
        Any
            The object cleaned following the processus above.
        """

        def key_to_hash(key):
            if not isinstance(key, (str, int, float, bool)) and key is not None:
                # print('called')
                return zlib.crc32(json.dumps(key, cls=CustomEncoder).encode())
            return key

        if isinstance(obj, dict):
            return {key_to_hash(k): self._encode_dict(v) for k, v in obj.items()}
        return obj

    def encode(self, obj):
        return super().encode(self._encode_dict(obj))


def get_json(obj):
    """Recursively serialize `object` to JSON using the :class:`CustomEncoder` class.

    Paramaters
    ----------
    dict_config : :class:`dict`
        The dict to flatten

    Returns
    -------
    :class:`str` 
        The flattened object
    """
    return json.dumps(obj, cls=CustomEncoder)


def get_camera_dict_for_hashing(camera_object):
    """Remove some keys from `camera_object.__dict__` that are very heavy and useless for the caching functionality.

    Parameters
    ----------
    camera_object : :class:`~.Camera`
        The camera object used in the scene

    Returns
    -------
    :class:`dict`
        `Camera.__dict__` but cleaned.
    """
    camera_object_dict = copy.copy(camera_object.__dict__)
    # We have to clean a little bit of camera_dict, as pixel_array and background are two very big numpy arrays.
    # They are not essential to caching process.
    # We also have to remove pixel_array_to_cairo_context as it contains used memory adress (set randomly). See l.516 get_cached_cairo_context in camera.py
    for to_clean in ["background", "pixel_array", "pixel_array_to_cairo_context"]:
        camera_object_dict.pop(to_clean, None)
    return camera_object_dict


def get_hash_from_play_call(camera_object, animations_list, current_mobjects_list):
    """Take the list of animations and a list of mobjects and output their hashes. This is meant to be used for `scene.play` function.

    Parameters
    -----------
    camera_object : :class:`~.Camera`
        The camera object used in the scene.

    animations_list : Iterable[:class:`~.Animation`]
        The list of animations.

    current_mobjects_list : Iterable[:class:`~.Mobject`]
        The list of mobjects.

    Returns
    -------
    :class:`str` 
        A string concatenation of the respective hashes of `camera_object`, `animations_list` and `current_mobjects_list`, separated by `_`.
    """
    camera_json = get_json(get_camera_dict_for_hashing(camera_object))
    animations_list_json = [
        get_json(x) for x in sorted(animations_list, key=lambda obj: str(obj))
    ]
    current_mobjects_list_json = [
        get_json(x) for x in sorted(current_mobjects_list, key=lambda obj: str(obj))
    ]
    hash_camera, hash_animations, hash_current_mobjects = [
        zlib.crc32(repr(json_val).encode())
        for json_val in [camera_json, animations_list_json, current_mobjects_list_json]
    ]
    return "{}_{}_{}".format(hash_camera, hash_animations, hash_current_mobjects)


def get_hash_from_wait_call(
    camera_object, wait_time, stop_condition_function, current_mobjects_list
):
    """Take a wait time, a boolean function as a stop condition and a list of mobjects, and then output their individual hashes. This is meant to be used for `scene.wait` function.

    Parameters
    -----------
    wait_time : :class:`float`
        The time to wait

    stop_condition_function : Callable[[...], bool]
        Boolean function used as a stop_condition in `wait`.

    Returns
    -------
    :class:`str`
        A concatenation of the respective hashes of `animations_list and `current_mobjects_list`, separated by `_`.
    """
    camera_json = get_json(get_camera_dict_for_hashing(camera_object))
    current_mobjects_list_json = [
        get_json(x) for x in sorted(current_mobjects_list, key=lambda obj: str(obj))
    ]
    hash_current_mobjects = zlib.crc32(repr(current_mobjects_list_json).encode())
    hash_camera = zlib.crc32(repr(camera_json).encode())
    if stop_condition_function is not None:
        hash_function = zlib.crc32(get_json(stop_condition_function).encode())
        return "{}_{}{}_{}".format(
            hash_camera,
            str(wait_time).replace(".", "-"),
            hash_function,
            hash_current_mobjects,
        )
    else:
        return "{}_{}_{}".format(
            hash_camera, str(wait_time).replace(".", "-"), hash_current_mobjects
        )
