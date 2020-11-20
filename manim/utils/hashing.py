"""Utilities for scene caching."""

import json
import zlib
import inspect
import copy
import numpy as np
from types import ModuleType, MappingProxyType, FunctionType, MethodType
from time import perf_counter

from .. import logger

ALREADY_PROCESSED_ID = {}


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
        if not (isinstance(obj, ModuleType)) and isinstance(
            obj, (MethodType, FunctionType)
        ):
            cvars = inspect.getclosurevars(obj)
            cvardict = {**copy.copy(cvars.globals), **copy.copy(cvars.nonlocals)}
            for i in list(cvardict):
                # NOTE : All module types objects are removed, because otherwise it throws ValueError: Circular reference detected if not. TODO
                if isinstance(cvardict[i], ModuleType):
                    del cvardict[i]
            try:
                code = inspect.getsource(obj)
            except OSError:
                # This happens when rendering videos included in the documentation
                # within doctests and should be replaced by a solution avoiding
                # hash collision (due to the same, empty, code strings) at some point.
                # See https://github.com/ManimCommunity/manim/pull/402.
                code = ""
            return self._check_iterable({"code": code, "nonlocals": cvardict})
        elif isinstance(obj, np.ndarray):
            if obj.size > 1000:
                obj = np.resize(obj, (100, 100))
                return f"TRUNCATED ARRAY: {repr(obj)}"
            # We return the repr and not a list to avoid the JsonEncoder to iterate over it.
            return repr(obj)
        elif hasattr(obj, "__dict__"):
            temp = getattr(obj, "__dict__")
            # MappingProxy is scene-caching nightmare. It contains all of the object methods and attributes. We skip it as the mechanism will at some point process the object, but instancied
            # Indeed, there is certainly no case where scene-caching will recieve only a non instancied object, as this is never used in the library or encouraged to be used user-side.
            if isinstance(temp, MappingProxyType):
                return "MappingProxy"
            return self._check_iterable(temp)
        elif isinstance(obj, np.uint8):
            return int(obj)

        return f"Unsupported type for serializing -> {str(type(obj))}"

    def _handle_already_processed(self, obj):
        """Handle if an object has been already processed by checking the id of the object.

        This prevents the mechanism to handle an object several times, and is used to prevent any circular reference.

        Parameters
        ----------
        obj : Any
            The obj to check.

        Returns
        -------
        Any
            "already_processed" string if it has been processed, otherwise obj.
        """
        global ALREADY_PROCESSED_ID
        if id(obj) in ALREADY_PROCESSED_ID:
            return "already_processed"
        if not isinstance(obj, (str, int, bool, float)):
            ALREADY_PROCESSED_ID[id(obj)] = obj
        return obj

    def _check_iterable(self, iterable):
        """Check for circular reference at each iterable that will go through the JSONEncoder, as well as key of the wrong format.

        If a key with a bad format is found (i.e not a int, string, or float), it gets replaced byt its hash using the same process implemented here.
        If a circular reference is found within the iterable, it will be replaced by the string "already processed".

        Parameters
        ----------
        iterable : Iterable[Any]
            The iterable to check.
        """

        def _key_to_hash(key):
            return zlib.crc32(json.dumps(key, cls=CustomEncoder).encode())

        def _iter_check_list(lst):
            # We have to make a copy, as we don't want to touch to the original list
            # A deepcopy isn't necessary as it is already recursive.
            lst_copy = copy.copy(lst)
            if isinstance(lst, tuple):
                # NOTE: Sometimes a tuple can pass through this function. As a tuple
                # is immutable, we convert it to a list to be able to modify it.
                # It's ok as it is a copy.
                lst_copy = list(lst_copy)
            for i, el in enumerate(lst):
                if not isinstance(lst, tuple):
                    lst_copy[i] = self._handle_already_processed(
                        el
                    )  # ISSUE here, because of copy.
                if isinstance(el, (list, tuple)):
                    lst_copy[i] = _iter_check_list(el)
                elif isinstance(el, dict):
                    lst_copy[i] = _iter_check_dict(el)
            return lst_copy

        def _iter_check_dict(dct):
            # We have to make a copy, as we don't want to touch to the original dict
            # A deepcopy isn't necessary as it is already recursive.
            dct_copy = copy.copy(dct)
            for k, v in dct.items():
                dct_copy[k] = self._handle_already_processed(v)
                # We check if the k is of the right format (supporter by Json)
                if not isinstance(k, (str, int, float, bool)) and k is not None:
                    k_new = _key_to_hash(k)
                    # We delete the value coupled with the old key, as the value is now coupled with the new key.
                    dct_copy[k_new] = dct_copy[k]
                    del dct_copy[k]
                else:
                    k_new = k
                if isinstance(v, dict):
                    dct_copy[k_new] = _iter_check_dict(v)
                elif isinstance(v, (list, tuple)):
                    dct_copy[k_new] = _iter_check_list(v)
            return dct_copy

        if isinstance(iterable, (list, tuple)):
            return _iter_check_list(iterable)
        elif isinstance(iterable, dict):
            return _iter_check_dict(iterable)

    def encode(self, obj):
        """Overriding of :meth:`JSONEncoder.encode`, to make our own process.

        Parameters
        ----------
        obj: Any
            The object to encode in JSON.

        Returns
        -------
        :class:`str`
           The object encoder with the standard json process.
        """
        # We need to mark as already processed the first object to go in the process,
        # As after, only objects that come from iterables will be marked as such.
        global ALREADY_PROCESSED_ID
        ALREADY_PROCESSED_ID[id(obj)] = obj
        if isinstance(obj, (dict, list, tuple)):
            return super().encode(self._check_iterable(obj))
        return super().encode(obj)


def get_json(obj):
    """Recursively serialize `object` to JSON using the :class:`CustomEncoder` class.

    Parameters
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


def get_hash_from_play_call(
    scene_object, camera_object, animations_list, current_mobjects_list
):
    """Take the list of animations and a list of mobjects and output their hashes. This is meant to be used for `scene.play` function.

    Parameters
    -----------
    scene_object : :class:`~.Scene`
        The scene object.

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
    logger.debug("Hashing ...")
    global ALREADY_PROCESSED_ID
    # We add the scene object within the ALREADY_PROCESSED_ID, as we don't want to process because pretty much all of its attributes will be soon or later processed (in one of the three hashes).
    ALREADY_PROCESSED_ID = {id(scene_object): scene_object}
    t_start = perf_counter()
    camera_json = get_json(get_camera_dict_for_hashing(camera_object))
    animations_list_json = [get_json(x) for x in sorted(animations_list, key=str)]
    current_mobjects_list_json = [
        get_json(x) for x in sorted(current_mobjects_list, key=str)
    ]
    hash_camera, hash_animations, hash_current_mobjects = [
        zlib.crc32(repr(json_val).encode())
        for json_val in [camera_json, animations_list_json, current_mobjects_list_json]
    ]
    t_end = perf_counter()
    logger.debug("Hashing done in %(time)s s.", {"time": str(t_end - t_start)[:8]})
    hash_complete = f"{hash_camera}_{hash_animations}_{hash_current_mobjects}"
    # This will reset ALREADY_PROCESSED_ID as all the hashing processus is finished.
    ALREADY_PROCESSED_ID = {}
    logger.debug("Hash generated :  %(h)s", {"h": hash_complete})
    return hash_complete


def get_hash_from_wait_call(
    scene_object,
    camera_object,
    wait_time,
    stop_condition_function,
    current_mobjects_list,
):
    """Take a wait time, a boolean function as a stop condition and a list of mobjects, and then output their individual hashes. This is meant to be used for `scene.wait` function.

    Parameters
    -----------
    scene_object : :class:`~.Scene`
        The scene object.
    camera_object : :class:`~.Camera`
        The camera object.
    wait_time : :class:`float`
        The time to wait
    stop_condition_function : Callable[[...], bool]
        Boolean function used as a stop_condition in `wait`.

    Returns
    -------
    :class:`str`
        A concatenation of the respective hashes of `animations_list and `current_mobjects_list`, separated by `_`.
    """
    logger.debug("Hashing ...")
    t_start = perf_counter()
    global ALREADY_PROCESSED_ID
    # We add the scene object within the ALREADY_PROCESSED_ID, as we don't want to process because pretty much all of its attributes will be soon or later processed (in one of the three hashes).
    ALREADY_PROCESSED_ID = {id(scene_object): scene_object}
    camera_json = get_json(get_camera_dict_for_hashing(camera_object))
    current_mobjects_list_json = [
        get_json(x) for x in sorted(current_mobjects_list, key=str)
    ]
    hash_current_mobjects = zlib.crc32(repr(current_mobjects_list_json).encode())
    hash_camera = zlib.crc32(repr(camera_json).encode())
    if stop_condition_function is not None:
        hash_function = zlib.crc32(get_json(stop_condition_function).encode())
        # This will reset ALREADY_PROCESSED_ID as all the hashing processus is finished.
        ALREADY_PROCESSED_ID = {}
        t_end = perf_counter()
        logger.debug("Hashing done in %(time)s s.", {"time": str(t_end - t_start)[:8]})
        hash_complete = f"{hash_camera}_{str(wait_time).replace('.', '-')}{hash_function}_{hash_current_mobjects}"
        logger.debug("Hash generated :  %(h)s", {"h": hash_complete})
        return hash_complete
    ALREADY_PROCESSED_ID = {}
    t_end = perf_counter()
    logger.debug("Hashing done in %(time)s s.", {"time": str(t_end - t_start)[:8]})
    hash_complete = (
        f"{hash_camera}_{str(wait_time).replace('.', '-')}_{hash_current_mobjects}"
    )

    logger.debug("Hash generated :  %(h)s", {"h": hash_complete})
    return hash_complete
