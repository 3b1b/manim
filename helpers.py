import numpy as np
import itertools as it
import operator as op
from PIL import Image
from colour import Color
import random
import inspect
import string
import re
import os
from scipy import linalg

from constants import *

CLOSED_THRESHOLD = 0.01
STRAIGHT_PATH_THRESHOLD = 0.01

def play_chord(*nums):
    commands = [
        "play",
        "-n",
        "-c1",
        "--no-show-progress",
        "synth",
    ] + [
        "sin %-"+str(num)
        for num in nums
    ] + [
        "fade h 0.5 1 0.5", 
        "> /dev/null"
    ]
    try:
        os.system(" ".join(commands))
    except:
        pass

def play_error_sound():
    play_chord(11, 8, 6, 1)


def play_finish_sound():
    play_chord(12, 9, 5, 2)

def get_smooth_handle_points(points):
    points = np.array(points)
    num_handles = len(points) - 1
    dim = points.shape[1]    
    if num_handles < 1:
        return np.zeros((0, dim)), np.zeros((0, dim))
    #Must solve 2*num_handles equations to get the handles.
    #l and u are the number of lower an upper diagonal rows
    #in the matrix to solve.
    l, u = 2, 1    
    #diag is a representation of the matrix in diagonal form
    #See https://www.particleincell.com/2012/bezier-splines/
    #for how to arive at these equations
    diag = np.zeros((l+u+1, 2*num_handles))
    diag[0,1::2] = -1
    diag[0,2::2] = 1
    diag[1,0::2] = 2
    diag[1,1::2] = 1
    diag[2,1:-2:2] = -2
    diag[3,0:-3:2] = 1
    #last
    diag[2,-2] = -1
    diag[1,-1] = 2
    #This is the b as in Ax = b, where we are solving for x,
    #and A is represented using diag.  However, think of entries
    #to x and b as being points in space, not numbers
    b = np.zeros((2*num_handles, dim))
    b[1::2] = 2*points[1:]
    b[0] = points[0]
    b[-1] = points[-1]
    solve_func = lambda b : linalg.solve_banded(
        (l, u), diag, b
    )
    if is_closed(points):
        #Get equations to relate first and last points
        matrix = diag_to_matrix((l, u), diag)
        #last row handles second derivative
        matrix[-1, [0, 1, -2, -1]] = [2, -1, 1, -2]
        #first row handles first derivative
        matrix[0,:] = np.zeros(matrix.shape[1])
        matrix[0,[0, -1]] = [1, 1]
        b[0] = 2*points[0]
        b[-1] = np.zeros(dim)
        solve_func = lambda b : linalg.solve(matrix, b)
    handle_pairs = np.zeros((2*num_handles, dim))
    for i in range(dim):
        handle_pairs[:,i] = solve_func(b[:,i])
    return handle_pairs[0::2], handle_pairs[1::2]

def diag_to_matrix(l_and_u, diag):
    """
    Converts array whose rows represent diagonal 
    entries of a matrix into the matrix itself.
    See scipy.linalg.solve_banded
    """
    l, u = l_and_u
    dim = diag.shape[1]
    matrix = np.zeros((dim, dim))
    for i in range(l+u+1):
        np.fill_diagonal(
            matrix[max(0,i-u):,max(0,u-i):],
            diag[i,max(0,u-i):]
        )
    return matrix

def is_closed(points):
    return np.linalg.norm(points[0] - points[-1]) < CLOSED_THRESHOLD

## Color

def color_to_rgb(color):
    return np.array(Color(color).get_rgb())

def color_to_rgba(color, alpha = 1):
    return np.append(color_to_rgb(color), [alpha])

def rgb_to_color(rgb):
    try:
        return Color(rgb = rgb)
    except:
        return Color(WHITE)

def rgba_to_color(rgba):
    return rgb_to_color(rgba[:3])

def invert_color(color):
    return rgb_to_color(1.0 - color_to_rgb(color))

def color_to_int_rgb(color):
    return (255*color_to_rgb(color)).astype('uint8')

def color_to_int_rgba(color, alpha = 255):
    return np.append(color_to_int_rgb(color), alpha)

def color_gradient(reference_colors, length_of_output):
    if length_of_output == 0:
        return reference_colors[0]
    rgbs = map(color_to_rgb, reference_colors)
    alphas = np.linspace(0, (len(rgbs) - 1), length_of_output)
    floors = alphas.astype('int')
    alphas_mod1 = alphas % 1
    #End edge case
    alphas_mod1[-1] = 1
    floors[-1] = len(rgbs) - 2
    return [
        rgb_to_color(interpolate(rgbs[i], rgbs[i+1], alpha))
        for i, alpha in zip(floors, alphas_mod1)
    ]

def interpolate_color(color1, color2, alpha):
    rgb = interpolate(color_to_rgb(color1), color_to_rgb(color2), alpha)
    return rgb_to_color(rgb)

def average_color(*colors):
    rgbs = np.array(map(color_to_rgb, colors))
    mean_rgb = np.apply_along_axis(np.mean, 0, rgbs)
    return rgb_to_color(mean_rgb)

###

def compass_directions(n = 4, start_vect = RIGHT):
    angle = 2*np.pi/n
    return np.array([
        rotate_vector(start_vect, k*angle)
        for k in range(n)
    ])

def partial_bezier_points(points, a, b):
    """
    Given an array of points which define 
    a bezier curve, and two numbres 0<=a<b<=1,
    return an array of the same size, which 
    describes the portion of the original bezier
    curve on the interval [a, b].

    This algorithm is pretty nifty, and pretty dense.
    """
    a_to_1 = np.array([
        bezier(points[i:])(a)
        for i in range(len(points))
    ])
    return np.array([
        bezier(a_to_1[:i+1])(b)
        for i in range(len(points))
    ])

def bezier(points):
    n = len(points) - 1
    return lambda t : sum([
        ((1-t)**(n-k))*(t**k)*choose(n, k)*point
        for k, point in enumerate(points)
    ])

def remove_list_redundancies(l):
    """
    Used instead of list(set(l)) to maintain order
    """
    result = []
    used = set()
    for x in l:
        if not x in used:
            result.append(x)
            used.add(x)
    return result

def list_update(l1, l2):
    """
    Used instead of list(set(l1).update(l2)) to maintain order,
    making sure duplicates are removed from l1, not l2.
    """
    return filter(lambda e : e not in l2, l1) + list(l2)

def list_difference_update(l1, l2):
    return filter(lambda e : e not in l2, l1)

def all_elements_are_instances(iterable, Class):
    return all(map(lambda e : isinstance(e, Class), iterable))

def adjacent_pairs(objects):
    return zip(objects, list(objects[1:])+[objects[0]])

def complex_to_R3(complex_num):
    return np.array((complex_num.real, complex_num.imag, 0))

def tuplify(obj):
    if isinstance(obj, str):
        return (obj,)
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
    Sets init args and CONFIG values as local variables

    The purpose of this function is to ensure that all 
    configuration of any object is inheritable, able to 
    be easily passed into instantiation, and is attached
    as an attribute of the object.
    """
    ### Assemble list of CONFIGs from all super classes
    classes_in_hierarchy = [obj.__class__]
    configs = []
    while len(classes_in_hierarchy) > 0:
        Class = classes_in_hierarchy.pop()
        classes_in_hierarchy += Class.__bases__
        if hasattr(Class, "CONFIG"):
            configs.append(Class.CONFIG)    

    #Order matters a lot here, first dicts have higher priority
    all_dicts = [kwargs, filtered_locals(local_args), obj.__dict__]
    all_dicts += configs
    obj.__dict__ = merge_config(all_dicts)

def merge_config(all_dicts):
    all_config = reduce(op.add, [d.items() for d in all_dicts])
    config = dict()
    for c in all_config:
        key, value = c
        if not key in config:
            config[key] = value
        else:
            #When two dictionaries have the same key, they are merged.
            if isinstance(value, dict) and isinstance(config[key], dict):
                config[key] = merge_config([config[key], value])
    return config

def digest_locals(obj, keys = None):
    caller_locals = filtered_locals(
        inspect.currentframe().f_back.f_locals
    )
    if keys is None:
        keys = caller_locals.keys()
    for key in keys:
        setattr(obj, key, caller_locals[key])

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

def random_bright_color():
    color = random_color()
    curr_rgb = color_to_rgb(color)
    new_rgb = interpolate(
        curr_rgb, np.ones(len(curr_rgb)), 0.5
    )
    return Color(rgb = new_rgb)

def random_color():
    return random.choice(PALETTE)


################################################

def straight_path(start_points, end_points, alpha):
    return interpolate(start_points, end_points, alpha)

def path_along_arc(arc_angle, axis = OUT):
    """
    If vect is vector from start to end, [vect[:,1], -vect[:,0]] is 
    perpendicualr to vect in the left direction.
    """
    if abs(arc_angle) < STRAIGHT_PATH_THRESHOLD:
        return straight_path
    if np.linalg.norm(axis) == 0:
        axis = OUT
    unit_axis = axis/np.linalg.norm(axis)
    def path(start_points, end_points, alpha):
        vects = end_points - start_points
        centers = start_points + 0.5*vects
        if arc_angle != np.pi:
            centers += np.cross(unit_axis, vects/2.0)/np.tan(arc_angle/2)
        rot_matrix = rotation_matrix(alpha*arc_angle, unit_axis)
        return centers + np.dot(start_points-centers, rot_matrix.T)
    return path

def clockwise_path():
    return path_along_arc(-np.pi)

def counterclockwise_path():
    return path_along_arc(np.pi)


################################################

def to_camel_case(name):
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

def get_full_image_path(image_file_name):
    possible_paths = [
        image_file_name,
        os.path.join(IMAGE_DIR, image_file_name),
        os.path.join(IMAGE_DIR, image_file_name + ".jpg"),
        os.path.join(IMAGE_DIR, image_file_name + ".png"),
        os.path.join(IMAGE_DIR, image_file_name + ".gif"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    raise IOError("File not Found")

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

def stretch_array_to_length(nparray, length):
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

### Rate Functions ###

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

def double_smooth(t):
    if t < 0.5:
        return 0.5*smooth(2*t)
    else:
        return 0.5*(1 + smooth(2*t - 1))

def there_and_back(t, inflection = 10.0):
    new_t = 2*t if t < 0.5 else 2*(1 - t)
    return smooth(new_t, inflection)

def there_and_back_with_pause(t):
    if t < 1./3:
        return smooth(3*t)
    elif t < 2./3:
        return 1
    else:
        return smooth(3 - 3*t)

def running_start(t, pull_factor = -0.5):
    return bezier([0, 0, pull_factor, pull_factor, 1, 1, 1])(t)

def not_quite_there(func = smooth, proportion = 0.7):
    def result(t):
        return proportion*func(t)
    return result

def wiggle(t, wiggles = 2):
    return there_and_back(t) * np.sin(wiggles*np.pi*t)

def squish_rate_func(func, a = 0.4, b = 0.6):
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
        #projection of vector to unit circle
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
    z = complex(*vector[:2])
    if z == 0:
        return 0
    return np.angle(complex(*vector[:2]))




