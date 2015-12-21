import numpy as np
import itertools as it
import operator as op
from PIL import Image
from colour import Color
import random
import inspect
import string
import re


from constants import *


def bezier(points):
    n = len(points) - 1
    return lambda t : sum([
        ((1-t)**(n-k))*(t**k)*choose(n, k)*point
        for point, k in zip(points, it.count())
    ])

def remove_list_redundancies(l):
    """
    Used instead of lsit(set(l)) to maintain order
    """
    return sorted(list(set(l)), lambda a, b : l.index(a) - l.index(b))

def list_update(l1, l2):
    """
    Used instead of list(set(l1).update(l2)) to maintain order,
    making sure duplicates are removed from l1, not l2.
    """
    return filter(lambda e : e not in l2, l1) + list(l2)

def all_elements_are_instances(iterable, Class):
    return all(map(lambda e : isinstance(e, Class), iterable))

def adjascent_pairs(objects):
    return zip(objects, list(objects[1:])+[objects[0]])

def complex_to_R3(complex_num):
    return np.array((complex_num.real, complex_num.imag, 0))

def tuplify(obj):
    try:
        return tuple(obj)
    except:
        return (obj,)

def instantiate(obj):
    """
    Useful so that classes or instance of those classes can be 
    included in configuration, which can prevent defaults from
    getting created during compilation/importing
    """
    return obj() if isinstance(obj, type) else obj

def get_all_descendent_classes(Class):
    awaiting_review = [Class]
    result = []
    while awaiting_review:
        Child = awaiting_review.pop()
        awaiting_review += Child.__subclasses__()
        result.append(Child)
    return result

def filtered_locals(local_args):
    result = local_args.copy()
    ignored_local_args = ["self", "kwargs"]
    for arg in ignored_local_args:
        result.pop(arg, local_args)
    return result


def digest_config(obj, kwargs, local_args = {}):
    """
    Sets init args and DEFAULT_CONFIG values as local variables
    """
    ### Assemble list of DEFAULT_CONFIGs from all super classes
    classes_in_heirarchy = [obj.__class__]
    default_configs = []
    while len(classes_in_heirarchy) > 0:
        Class = classes_in_heirarchy.pop()
        classes_in_heirarchy += Class.__bases__
        if hasattr(Class, "DEFAULT_CONFIG"):
            default_configs.append(Class.DEFAULT_CONFIG)    

    #Order matters a lot here, first dicts have higher priority
    all_dicts = [kwargs, filtered_locals(local_args), obj.__dict__]
    all_dicts += default_configs
    item_lists = reversed([d.items() for d in all_dicts])
    obj.__dict__ = dict(reduce(op.add, item_lists))

def digest_locals(obj):
    caller_locals = inspect.currentframe().f_back.f_locals
    obj.__dict__.update(filtered_locals(caller_locals))


def interpolate(start, end, alpha):
    return (1-alpha)*start + alpha*end

def center_of_mass(points):
    points = [np.array(point).astype("float") for point in points]
    return sum(points) / len(points)

def choose(n, r):
    if n < r: return 0
    if r == 0: return 1
    denom = reduce(op.mul, xrange(1, r+1), 1)
    numer = reduce(op.mul, xrange(n, n-r, -1), 1)
    return numer//denom

def is_on_line(p0, p1, p2, threshold = 0.01):
    """
    Returns true of p0 is on the line between p1 and p2
    """
    p0, p1, p2 = map(lambda tup : np.array(tup[:2]), [p0, p1, p2])
    p1 -= p0
    p2 -= p0
    return abs((p1[0] / p1[1]) - (p2[0] / p2[1])) < threshold


def intersection(line1, line2):
    """
    A "line" should come in the form [(x0, y0), (x1, y1)] for two
    points it runs through
    """
    p0, p1, p2, p3 = map(
        lambda tup : np.array(tup[:2]),
        [line1[0], line1[1], line2[0], line2[1]]
    )
    p1, p2, p3 = map(lambda x : x - p0, [p1, p2, p3])
    transform = np.zeros((2, 2))
    transform[:,0], transform[:,1] = p1, p2
    if np.linalg.det(transform) == 0: return
    inv = np.linalg.inv(transform)
    new_p3 = np.dot(inv, p3.reshape((2, 1)))
    #Where does line connecting (0, 1) to new_p3 hit x axis
    x_intercept = new_p3[0] / (1 - new_p3[1]) 
    result = np.dot(transform, [[x_intercept], [0]])
    result = result.reshape((2,)) + p0
    return result

def random_color():
    return random.choice(PALETTE)


################################################

def straight_path(start_points, end_points, alpha):
    return interpolate(start_points, end_points, alpha)

def path_along_arc(arc_angle):
    """
    If vect is vector from start to end, [vect[:,1], -vect[:,0]] is 
    perpendicualr to vect in the left direction.
    """
    if arc_angle == 0:
        return straight_path
    def path(start_points, end_points, alpha):
        vects = end_points - start_points
        centers = start_points + 0.5*vects
        if arc_angle != np.pi:
            for i, b in [(0, -1), (1, 1)]:
                centers[:,i] += 0.5*b*vects[:,1-i]/np.tan(arc_angle/2)
        return centers + np.dot(
            start_points-centers, 
            np.transpose(rotation_about_z(alpha*arc_angle))
        )
    return path

def clockwise_path():
    return path_along_arc(-np.pi)

def counterclockwise_path():
    return path_along_arc(np.pi)


################################################

def to_cammel_case(name):
    return "".join([
        filter(
            lambda c : c not in string.punctuation + string.whitespace, part
        ).capitalize()
        for part in name.split("_")
    ])

def initials(name, sep_values = [" ", "_"]):
    return "".join([
        (s[0] if s else "") 
        for s in re.split("|".join(sep_values), name)
    ])

def cammel_case_initials(name):
    return filter(lambda c : c.isupper(), name)

################################################

def drag_pixels(frames):
    curr = frames[0]
    new_frames = []
    for frame in frames:
        curr += (curr == 0) * np.array(frame)
        new_frames.append(np.array(curr))
    return new_frames

def invert_image(image):
    arr = np.array(image)
    arr = (255 * np.ones(arr.shape)).astype(arr.dtype) - arr
    return Image.fromarray(arr)

def streth_array_to_length(nparray, length):
    curr_len = len(nparray)
    if curr_len > length:
        raise Warning("Trying to stretch array to a length shorter than its own")
    indices = np.arange(length)/ float(length)
    indices *= curr_len
    return nparray[indices.astype('int')]

def make_even(iterable_1, iterable_2):
    list_1, list_2 = list(iterable_1), list(iterable_2)
    length = max(len(list_1), len(list_2))
    return (
        [list_1[(n * len(list_1)) / length] for n in xrange(length)],
        [list_2[(n * len(list_2)) / length] for n in xrange(length)]
    )

def make_even_by_cycling(iterable_1, iterable_2):
    length = max(len(iterable_1), len(iterable_2))
    cycle1 = it.cycle(iterable_1)
    cycle2 = it.cycle(iterable_2)
    return (
        [cycle1.next() for x in range(length)],
        [cycle2.next() for x in range(length)]
    )

### Alpha Functions ###

def sigmoid(x):
    return 1.0/(1 + np.exp(-x))

def smooth(t, inflection = 10.0):
    error = sigmoid(-inflection / 2)
    return (sigmoid(inflection*(t - 0.5)) - error) / (1 - 2*error)

def rush_into(t):
    return 2*smooth(t/2.0)

def rush_from(t):
    return 2*smooth(t/2.0+0.5) - 1

def slow_into(t):
    return np.sqrt(1-(1-t)*(1-t))

def there_and_back(t, inflection = 10.0):
    new_t = 2*t if t < 0.5 else 2*(1 - t)
    return smooth(new_t, inflection)


def not_quite_there(func = smooth, proportion = 0.7):
    def result(t):
        return proportion*func(t)
    return result

def wiggle(t, wiggles = 2):
    return there_and_back(t) * np.sin(wiggles*np.pi*t)

def squish_alpha_func(func, a = 0.4, b = 0.6):
    def result(t):
        if t < a:
            return func(0)
        elif t > b:
            return func(1)
        else:
            return func((t-a)/(b-a))
    return result

### Functional Functions ###

def composition(func_list):
    """
    func_list should contain elements of the form (f, args)
    """
    return reduce(
        lambda (f1, args1), (f2, args2) : (lambda x : f1(f2(x, *args2), *args1)), 
        func_list,
        lambda x : x
    )

def remove_nones(sequence):
    return filter(lambda x : x, sequence)

#Matrix operations
def thick_diagonal(dim, thickness = 2):
    row_indices = np.arange(dim).repeat(dim).reshape((dim, dim))
    col_indices = np.transpose(row_indices)
    return (np.abs(row_indices - col_indices)<thickness).astype('uint8')

def rotation_matrix(angle, axis):
    """
    Rotation in R^3 about a specified axess of rotation.
    """
    about_z = rotation_about_z(angle)
    z_to_axis = z_to_vector(axis)
    axis_to_z = np.linalg.inv(z_to_axis)
    return reduce(np.dot, [z_to_axis, about_z, axis_to_z])

def rotation_about_z(angle):
    return [
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle),  np.cos(angle), 0],
        [0, 0, 1]
    ]

def z_to_vector(vector):
    """
    Returns some matrix in SO(3) which takes the z-axis to the 
    (normalized) vector provided as an argument
    """
    norm = np.linalg.norm(vector)
    if norm == 0:
        return np.identity(3)
    v = np.array(vector) / norm
    phi = np.arccos(v[2])
    if any(v[:2]):
        #projection of vector to {x^2 + y^2 = 1}
        axis_proj = v[:2] / np.linalg.norm(v[:2])
        theta = np.arccos(axis_proj[0])
        if axis_proj[1] < 0:
            theta = -theta
    else:
        theta = 0
    phi_down = np.array([
        [np.cos(phi), 0, np.sin(phi)],
        [0, 1, 0],
        [-np.sin(phi), 0, np.cos(phi)]
    ])
    return np.dot(rotation_about_z(theta), phi_down)

def rotate_vector(vector, angle, axis = OUT):
    return np.dot(rotation_matrix(angle, axis), vector)

def angle_between(v1, v2):
    return np.arccos(np.dot(
        v1 / np.linalg.norm(v1), 
        v2 / np.linalg.norm(v2)
    ))

def angle_of_vector(vector):
    """
    Returns polar coordinate theta when vector is project on xy plane
    """
    return np.log(complex(*vector[:2])).imag




