from PIL import Image
from animate import *
from mobject import *
from constants import *
from helpers import *
from tex_image_utils import load_pdf_images
from displayer import *
import itertools as it
import os
import numpy as np
from copy import deepcopy

from epii_animations import MULTIPLIER_COLOR, ADDER_COLOR, ONE_COLOR

CCCD_MOVIE_DIR = "cccd"

symbol_images = load_pdf_images("cccd_symbols.pdf", regen_if_exists = False)
phrase_images = load_pdf_images("cccd_phrases.pdf", regen_if_exists = False)

name_to_image = dict(
    zip([
        "two",
        "minus_1",
        "i",
        "x_squared",
        "four",
        "one",
        "multiplication_function",
        "deriv_def_base",
        "deriv_def_inner_e_to_x",
        "deriv_def_plus_h",
        "deriv_def_e_to_h",
        "deriv_def_one",
        "deriv_def_outer_e_to_x",
        "series_terms",
        "series_exponents",
        "series_exponents_minus_1",
        "d_series_coefficients",
        "one_plus",
        "d_series_simple",
        "deriv_x_squared",
        "deriv_e_to_x",
        "question_mark",
    ], symbol_images) + zip([
        "complex_derivative_title",
        "limit_explanation",
        "velocity_vector_explanation",
        "both_same_point",
        "maybe_like_this",
        "or_this",
        "why_vectors",
        "pause_and_ponder",
        "think_in_pictures",
        "remember_this",
    ], phrase_images)
)

def function_of_numbers():
    kwargs = {"dither_time" : 0}
    two, minus_1, i, x_squared, four, one = [
        ImageMobject(name_to_image[name])
        for name in ["two", "minus_1", "i", "x_squared",
                     "four", "one"]
    ]
    minus_1_copy = copy.deepcopy(minus_1)
    for mob1, mob2, height in [
        (two,     four,         2), 
        (minus_1, one,          0), 
        (i,       minus_1_copy, -2)
        ]:
        mob1.center().shift((-2, height, 0))
        mob2.center().shift((2, height, 0))
    x_squared.center()
    point = Point()
    inputs  = CompoundMobject(two, minus_1, i)
    outputs = CompoundMobject(four, one, minus_1_copy)
    return Transform(
        inputs, point, **kwargs
    ).then(
        Transform(point, outputs, **kwargs)
    ).with_background(x_squared)


def real_function_graph():
    graph = NumberLine()
    graph.add(NumberLine().rotate(np.pi / 2))
    int_size = graph.interval_size
    min_x = SPACE_WIDTH / int_size
    graph.add(FunctionGraph(
        lambda x : x**2,
        x_range = [-min_x, min_x]
    ))
    point = graph.points[-20,:]
    line = Line((2, 0, 0), (2, 1.1, 0)) #Terrible...
    line.highlight("yellow")
    return ShowCreation(graph).then(ShowCreation(line).with_background(graph))

def two_grids():
    grid1, grid2 = Grid(), Grid()
    return ShowCreation(grid1).then(
        Rotating(grid1, run_time = 7.0, radians = np.pi / 3).while_also(
            ShowCreation(grid2, dither_time = 2.0).while_also(
                Rotating, axis = [1, 1, 0]
            )
        )
    )

def z_squared():
    return ComplexHomotopy(square_homotopy)

def z_squared_marked():
    #Hard coded 2, i, -1
    return ComplexHomotopy(
        lambda (z, t) : z**(1 + t)
    ).while_also(
        ComplexHomotopy(
            lambda (z, t) : z + complex(2, 0)**(1 + t),
            Cross(
                color = random_color()
            )
        )
    ).while_also(
        ComplexHomotopy(
            lambda (z, t) : z + complex(-1, 0)**(1 + t),
            Cross(
                color = random_color()
            )
        )
    ).while_also(
        ComplexHomotopy(
            lambda (z, t) : z + complex(0, 1)**(1 + t),
            Cross(
                color = random_color()
            )
        )
    )

def multiplier_in_the_wild(point):
    func = ComplexFunction(lambda z : z*point)
    one = Cross().highlight(ONE_COLOR).shift((1, 0, 0))
    point = Cross().highlight(
        MULTIPLIER_COLOR
    ).shift((point.real, point.imag, 0))
    func_copy = copy.deepcopy(func)
    return func.then(
        func_copy.while_also(
            Transform(one, point, run_time = DEFAULT_ANIMATION_RUN_TIME)
        )
    ).then(
        Animation(
            Grid(), run_time = 2.0, dither_time = 0
        ).with_background(point)
    )

def random_looking_function():
    wongky_map = Transform(
        Grid(), CubeShell().scale(SPACE_HEIGHT), 
        alpha_func = lambda t : 0.5 * high_inflection_0_to_1(t),
        run_time = 3.0
    )
    return wongky_map.then(copy.deepcopy(wongky_map).reverse())

def zoom_in_on_map(function, is_homotopy, point, zoom_level):
    center_line = ParametricFunction(lambda t : (0, t * SPACE_HEIGHT, 0))
    half_width = SPACE_WIDTH / 2
    left_center = (-half_width + center_line.epsilon, 0, 0)
    right_center = (half_width - center_line.epsilon, 0, 0)
    left_divider = copy.deepcopy(center_line).shift(right_center)
    right_divider = copy.deepcopy(center_line).shift(left_center)

    point = complex(point)
    outer_circle = Circle().scale(SPACE_HEIGHT + SPACE_WIDTH + half_width)
    inner_circle = Circle().scale(zoom_level).shift(
        (point.real, point.imag, 0)
    )
    outer_to_inner = Transform(outer_circle, inner_circle).with_background(Grid())
    big_radius = min(half_width, SPACE_HEIGHT)
    big_circle = Circle().scale(big_radius)
    bts_ratio = big_radius / zoom_level
    half_grid = Grid().filter_out(lambda (x, y, z) : abs(x) > half_width or y > SPACE_HEIGHT)
    one = Cross().shift((1, 0, 0)).highlight(ONE_COLOR)
    if is_homotopy:
        global_function = ComplexHomotopy(function, copy.deepcopy(half_grid))
        def local_homotopoy((z, t)):
            return bts_ratio * (function((z/bts_ratio + point, t)) - function((point,t)))
        local_function  = ComplexHomotopy(local_homotopoy, copy.deepcopy(half_grid))
        one_following = ComplexHomotopy(
            lambda (z, t) : z + local_homotopoy((1, t)) - 1, 
            one
        )
        circle_following = ComplexHomotopy(
            lambda (z, t) : z + function((point, t)) - point,
            inner_circle
        )
    else:
        global_function = ComplexFunction(function, copy.deepcopy(half_grid))
        def local_lambda(z):
            return bts_ratio*(function(z/bts_ratio + point) - function(point))
        local_function  = ComplexFunction(local_lambda, copy.deepcopy(half_grid))
        one_following = ComplexFunction(lambda z : z + local_lambda(1) - 1, one)
        circle_following = ComplexFunction(
            lambda z : z + function(point) - point,
            inner_circle
        )
    zoom_region = Circle().scale(zoom_level)
    zoom_region.add(Grid().filter_out(lambda p : np.linalg.norm(p) > zoom_level))
    zoom_region.shift(left_center).shift((point.real, point.imag, 0))
    zoom_in = ComplexFunction(
        lambda z : bts_ratio * (z - point - complex(left_center[0], left_center[1])) + \
                   complex(right_center[0], right_center[1]),
        zoom_region
    ).set_run_time(DEFAULT_TRANSFORM_RUN_TIME)

    grow_local_grid = ShowCreation(
        Grid().filter_out(lambda p : np.linalg.norm(p) > big_radius),
        run_time = 1.0
    ).with_background(big_circle)
    def out_of_circle(points):
        return np.apply_along_axis(np.linalg.norm, 1, points) > big_radius
    local_function.filter_out(out_of_circle)
    for anim in global_function, outer_to_inner, circle_following:
        anim.shift(left_center).restrict_width(half_width).with_background(left_divider)
    for anim in local_function, grow_local_grid, one_following:
        anim.shift(right_center).with_background(right_divider, big_circle)
    for anim in outer_to_inner, zoom_in, grow_local_grid:
        anim.set_dither(0)
    #Kind of hacky...one day there will be a better way of doing this.
    show_left_grid = Animation(Mobject().add_points(*global_function.get_points_and_rgbs()))
    show_left_grid.with_background(copy.deepcopy(inner_circle).shift(left_center))
    return outer_to_inner.then(
        zoom_in.while_also(show_left_grid),
    ).then(
        grow_local_grid.while_also(show_left_grid).while_also(zoom_in)
    ).then(
        global_function.while_also(
            local_function
        ).while_also(
            circle_following
        ).while_also(
            one_following
        )
    )

def z_squared_derivative_example(point, zoom_level):
    point = complex(point)
    point_coords = np.array((point.real, point.imag, 0))
    circle = Circle().scale(zoom_level).shift(point_coords)
    z     = Cross(color = Circle.DEFAULT_COLOR).shift(point_coords)
    two_z = Cross(color = MULTIPLIER_COLOR).shift(2*point_coords)
    zero  = Cross()
    one   = Cross(color = ONE_COLOR).shift((1, 0, 0))
    plane = Grid()
    return Transform(circle, z).with_background(plane, zero).then(
        Transform(z, two_z).with_background(
            plane, zero
        ).while_also(
            Reveal(one).with_background(
                two_z, plane, zero
            )
        ).set_dither(0)
    ).then(
        ComplexFunction(lambda c : c * 2 * point, plane).with_background(
            two_z, zero
        ).while_also(
            ComplexFunction(lambda c : c - 1 + 2 * point, one)
        )
    )

def z_squared_derivative_2z(zoom_level):
    circles = Mobject()
    crosses = Mobject()
    mini_maps = []
    mini_grids = Mobject()
    example_range = range(-3, 4, 2)
    for x in example_range:
        for y in example_range:
            circle = Circle().scale(zoom_level).shift((x, y, 0))
            cross = Cross().shift((2*x, 2*y, 0))
            mini_grid = Grid(
                radius = zoom_level, 
                subinterval_size = 0.25
            ).filter_out(
                lambda point : np.linalg.norm(point) > zoom_level
            )
            mini_maps.append(
                ComplexFunction(
                    lambda z : (z + complex(x, y))**2 - complex(x, y)**2,
                    mini_grid
                ).filter_out(
                    lambda points : np.apply_along_axis(np.linalg.norm, 1, points) \
                                    > zoom_level
                ).with_background(
                    Circle().scale(zoom_level)
                ).shift((x, y, 0)).set_dither(0) 
            )#generate frames so that lambda doesn't change
            mini_grids.add(copy.deepcopy(mini_grid).shift((x, y, 0)))
            Mobject.align_data(circle, cross)
            circles.add(circle)
            crosses.add(cross)
    all_mini_maps = reduce(Animation.while_also, mini_maps)
    crosses.highlight(MULTIPLIER_COLOR)
    return FadeOut(Grid()).while_also(
        Animation(CompoundMobject(circles, mini_grids))
    ).then(
        all_mini_maps.with_background(circles)
    ).then(
        ComplexFunction(lambda z : 2*z).while_also(
            Transform(
                circles, crosses, 
                run_time = DEFAULT_ANIMATION_RUN_TIME
            )
        )
    )


def visualize_exp():
    kwargs1 = {"run_time" : 2.0, "dither_time" : 1.0}
    kwargs2 = {"run_time" : 2.0, "dither_time" : 0.0}
    cylinder = Grid().apply_function(
        lambda (x, y, z) : (x, np.sin(y), np.cos(y))
    ).rotate(np.pi/9, [0, 1, 0])
    exp_plane = Grid().apply_complex_function(np.exp)
    rotating_cyl = Rotating(cylinder, radians = np.pi/5, run_time = 5.0)
    return Transform(Grid(), cylinder, **kwargs1).then(
        Transform(cylinder, exp_plane, **kwargs2)
    )

def derivative_definition():
    base, inner_e_to_x, plus_h, e_to_h, one, outer_e_to_x = [
        ImageMobject(name_to_image["deriv_def_" + name])
        for name in [
            "base",
            "inner_e_to_x",
            "plus_h",
            "e_to_h",
            "one",
            "outer_e_to_x",
        ]
    ]
    shift = (-0.2, -0.2, 0)
    base.shift(shift)
    outer_e_to_x.shift(shift)
    limit_explanation = ImageMobject(name_to_image["limit_explanation"])
    limit_explanation.shift((1, -2, 0))
    return Transform(plus_h, e_to_h).with_background(
        base, inner_e_to_x
    ).then(
        Transform(inner_e_to_x, outer_e_to_x).while_also(
            Reveal(one, dither_time = 1.0, run_time = 1.0)
        ).with_background(base, e_to_h)
    ).then(
        Reveal(limit_explanation).with_background(
            base, outer_e_to_x, one, e_to_h
        )
    )


def take_derivative_of_series():
    series_terms, series_exponents, series_exponents_minus_1, \
    d_series_coefficients, one_plus, d_series_simple = [
        ImageMobject(name_to_image[name])
        for name in [
            "series_terms", 
            "series_exponents",
            "series_exponents_minus_1",
            "d_series_coefficients",
            "one_plus",
            "d_series_simple",
        ]
    ]
    coefficients = copy.deepcopy(series_exponents)
    fraction_bars = copy.deepcopy(series_exponents)
    coefficients.filter_out(lambda (x, y, z) : y < 0.5)
    series_exponents_minus_1.filter_out(lambda (x, y, z) : y < 0.5)
    fraction_bars.filter_out(lambda (x, y, z) : y > 0.5)
    exponenets_to_coefficients = Homotopy(
        lambda (x, y, z, t) : (x - 0.5*t, y - 0.5*t + np.sin(np.pi * t), z),
        coefficients
    ).with_background(fraction_bars)
    d_series_non_simple = CompoundMobject(
        series_terms, 
        copy.deepcopy(coefficients).shift((-0.5, -0.5, 0)), 
        series_exponents_minus_1, 
        series_exponents
    )
    d_series_simple.center().shift((1, 0, 0))

    #Yeah, this is totally good programming...
    fdxc = [-2, -0.4, 1.3] #first dividing x coordinates
    sdxc = [-1.7, -0.8, .3] #second dividing x coordinates
    broken_series_terms = [
        copy.deepcopy(d_series_non_simple).filter_out(
            lambda (x, y, z) : x > fdxc[0]),
        copy.deepcopy(d_series_non_simple).filter_out(
            lambda (x, y, z) : x > fdxc[1] or x < fdxc[0]),
        copy.deepcopy(d_series_non_simple).filter_out(
            lambda (x, y, z) : x > fdxc[2] or x < fdxc[1]),
        copy.deepcopy(d_series_non_simple).filter_out(
            lambda (x, y, z) : x < fdxc[2]),
    ]
    broken_dseries_terms = [
        copy.deepcopy(d_series_simple).filter_out(
            lambda (x, y, z) : x > sdxc[0]),
        copy.deepcopy(d_series_simple).filter_out(
            lambda (x, y, z) : x > sdxc[1] or x < sdxc[0]),
        copy.deepcopy(d_series_simple).filter_out(
            lambda (x, y, z) : x > sdxc[2] or x < sdxc[1]),
        copy.deepcopy(d_series_simple).filter_out(
            lambda (x, y, z) : x < sdxc[2]),
    ]
    simplify = None
    for term1, term2 in zip(broken_series_terms, broken_dseries_terms):
        anim = Transform(term1, term2)
        if simplify:
            simplify.while_also(anim)
        else:
            simplify = anim
    series_terms.add(series_exponents)
    return exponenets_to_coefficients.while_also(
        Reveal(series_exponents_minus_1).with_background(
            series_terms, series_exponents
        )
    ).while_also(
        Transform(one_plus, Point(one_plus.get_center()))
    ).set_dither(1.0, True).set_run_time(1.0, True).then(
        simplify
    )

def e_to_x_takes_adder_to_multiplier(point):
    point = complex(point)
    point_coords = (point.real, point.imag, 0)
    image = np.exp(point)
    image_coords = (image.real, image.imag, 0)
    adder_cross = Cross().shift(point_coords).highlight(ADDER_COLOR)
    multi_cross = Cross().shift(image_coords).highlight(MULTIPLIER_COLOR)
    zero = Cross()
    one = Cross().shift((1, 0, 0)).highlight(ONE_COLOR)

    adder = ComplexFunction(
        lambda z : z + point, 
        CompoundMobject(Grid(radius = SPACE_WIDTH + SPACE_HEIGHT), zero)
    ).with_background(adder_cross)
    e_to_x = ComplexFunction(np.exp).while_also(
        Transform(adder_cross, multi_cross, run_time = DEFAULT_ANIMATION_RUN_TIME)
    )
    multiplier = ComplexFunction(lambda z : image * z).while_also(
        Transform(one, multi_cross, run_time = DEFAULT_ANIMATION_RUN_TIME)
    ).with_background(zero, multi_cross)
    return adder.then(e_to_x).then(multiplier)

def e_to_x_derivative_zoom(point, zoom_level):
    point = complex(point)
    image_point = np.exp(point)
    both_same_point = ImageMobject(
        name_to_image["both_same_point"]
    ).shift((image_point.real, SPACE_HEIGHT - 1, 0))
    left_point  = (image_point.real - SPACE_WIDTH/2, image_point.imag, 0)
    right_point = (image_point.real + SPACE_WIDTH/2, image_point.imag, 0)
    left_arrow  = Arrow(left_point, (-1, -1, 0)).highlight("white")
    right_arrow = Arrow(right_point, (1, -1, 0)).highlight("white")

    e_deriv_anim = zoom_in_on_map(np.exp, False, point, zoom_level)
    #SUPER HACKY, YOU MUST MAKE A BETTER WAY TO DO THIS IN FUTURE
    last_anim = e_deriv_anim.generate_frames().following_animations[-1]
    background = Mobject()
    for anim in [last_anim] + last_anim.concurrent_animations:
        background.add_points(*anim.get_points_and_rgbs())
    # background.display()
    return e_deriv_anim.then(
        Reveal(CompoundMobject(
            left_arrow, right_arrow, both_same_point
        )).with_background(background)
    )

def other_possible_functions():
    phrases = [
        ImageMobject(name_to_image[name]).center().shift((0, -2, 0))
        for name in ["maybe_like_this", "or_this"]
    ]
    return ComplexFunction(np.sin).with_background(
        phrases[0]
    ).then(
        ComplexFunction(np.sinc).with_background(
            phrases[1]
        )
    )

def setup_velocity_vector_discussion(zoom_level):
    def homotopy((x, y, z, t)):
        t = 3*t - 1.5
        return (
            x + t,
            y + t**3 - t,
            z
        )
    big_radius = SPACE_HEIGHT
    def out_of_circle(points):
        return np.apply_along_axis(np.linalg.norm, 1, points) > big_radius
    landing_point = homotopy((0, 0, 0, 1))
    cross = Cross().highlight(Circle.DEFAULT_COLOR)
    small_circle = Circle().scale(2*zoom_level)
    big_circle = Circle().scale(big_radius)
    new_cross = copy.deepcopy(cross)
    for mob in new_cross, small_circle:
        mob.shift(landing_point)
    wandering = Homotopy(homotopy, cross)
    one = Cross().highlight(ONE_COLOR).shift((1, 0, 0))
    multiply = ComplexFunction(
        lambda z : z * complex(landing_point[0], landing_point[1])
    ).filter_out(out_of_circle)
    return wandering.then(
        Transform(small_circle, big_circle).with_background(
            new_cross
        )
    ).then(
        multiply.with_background(big_circle).while_also(
            Transform(one, new_cross, run_time = DEFAULT_ANIMATION_RUN_TIME)
        ).with_background(
            new_cross
        )
    )

    
def traced_path():
    path = ParametricFunction(
        lambda t : (
            np.sin(2 * np.pi * t),
            (t-1)**2 + 1,
            0
        )
    )
    new_path = copy.deepcopy(path).apply_complex_function(np.exp)
    return ShowCreation(path).then(
        Transform(path, new_path)
    )


def walking_north(start_point, vector_len):
    vv_explanation = ImageMobject(name_to_image["velocity_vector_explanation"])
    vv_explanation.scale(0.75).shift((0, -3, 0))

    walk_kwargs = {"alpha_func" : None, "run_time" : 5.0}
    start_point = complex(start_point)
    end_point = start_point + complex(0, 4)
    start_coords = (start_point.real, start_point.imag, 0)
    end_coords = (end_point.real, end_point.imag, 0)
    vector = Vector((0, vector_len, 0)).shift(start_coords)
    vector.add(vv_explanation)
    start_cross = Cross().shift(start_coords)
    end_cross = Cross().shift(end_coords)
    path = Line(start_coords, end_coords).highlight(start_cross.DEFAULT_COLOR)
    return Transform(
        start_cross, end_cross, **walk_kwargs
    ).with_background(Grid()).while_also(
        ShowCreation(path, **walk_kwargs)
    ).then(
        Animation(vector), True
    )

def map_north_vector(start_point, vector_len, zoom_level):
    question_mark = ImageMobject(name_to_image["question_mark"]).center()
    kwargs = {
        "run_time"    : DEFAULT_ANIMATION_RUN_TIME, 
        "dither_time" : DEFAULT_DITHER_TIME
    }
    start_point = complex(start_point)
    image_point = np.exp(start_point)
    start_coords = np.array((start_point.real, start_point.imag, 0))
    image_coords = np.array((image_point.real, image_point.imag, 0))

    vector = Vector((0, vector_len, 0)).add(Circle().scale(zoom_level))
    vimage = copy.deepcopy(vector)
    image_len = np.linalg.norm(image_coords)
    image_arg = np.log(image_point).imag
    stretched = copy.deepcopy(vimage).scale(image_len)

    vector.shift(start_coords)    
    for vect in vimage, stretched:
        vect.shift(image_coords)
    question_mark.shift(image_coords + (0.3, 0, 0))

    line_to_image = Line((0, 0, 0), image_coords)
    line_along_horiz = Line((0, 0, 0), (image_len, 0, 0)).highlight(Grid.DEFAULT_COLOR)

    return Transform(vector, vimage).then(
        Reveal(question_mark, dither_time = 0).with_background(vimage)
    ).then(
        Transform(vimage, stretched, **kwargs).while_also(
            ShowCreation(line_to_image, **kwargs)
        )
    ).with_background(Grid()).then(
        RotationAsTransform(
            copy.deepcopy(stretched).shift(-image_coords), 
            radians = image_arg, **kwargs
        ).shift(image_coords).while_also(
            RotationAsTransform(
                line_along_horiz, radians = image_arg, **kwargs
            ).with_background(Grid(), line_to_image)
        )
    )

def all_possible_vectors(vector_len):
    tvkwargs = {"run_time" : 2.0, "dither_time" : 0}
    turn_vectors = Animation(Grid(), **tvkwargs)
    prototype = Vector((0, vector_len, 0))
    start_vectors = Mobject()
    final_vectors = Mobject()
    radii = []
    example_range = range(-3, 4)
    for x, y in it.product(*[example_range]*2):
        length = np.linalg.norm((x, y))
        arg = np.log(complex(x, y)).imag
        new = copy.deepcopy(prototype)
        turn_vectors.while_also(
            ComplexFunction(
                lambda z : z * complex(x, y),
                new, **tvkwargs
            ).shift((x, y, 0))
        )
        if length > 0:
            radii.append(length)
        start_vectors.add(copy.deepcopy(new).shift((x, y, 0)))
        final_vectors.add(copy.deepcopy(new).scale(length).rotate(arg).shift((x, y, 0)))
    to_vectors = Transform(prototype, start_vectors, **tvkwargs).with_background(Grid())
    turn_vectors.set_name("TurnVectors")
    radii = sorted(set(radii))
    show_all_circles = Reveal(CompoundMobject(*[
        Circle().scale(radius) for radius in radii
    ]), dither_time = 2.0)
    show_all_circles.with_background(Grid(), final_vectors)
    show_all_circles.set_name("ShowAllCircles")
    return to_vectors.then(turn_vectors).then(show_all_circles)

class VelocityVectorsOfPath(Animation):
    def __init__(self, path, vector_len = 1, alpha_func = None, *args, **kwargs):
        self.path = path.points
        diffs = path.points[1:,:] - path.points[:-1, :]
        self.unit_distance = np.mean(np.apply_along_axis(np.linalg.norm, 1, diffs))
        Animation.__init__(
            self, Vector(point = (vector_len, 0, 0)), alpha_func = alpha_func
        )
        self.with_background(path)

    def update_mobject(self, alpha):
        index = int(alpha * self.path.shape[0])
        if index >= self.path.shape[0] - 1:
            return
        point1, point2 = self.path[index, :], self.path[index + 1, :]
        diff = (point2 - point1)
        distance = np.linalg.norm(diff)
        arg = np.log(complex(diff[0], diff[1])).imag
        self.mobject.points = self.starting_mobject.points * (distance / self.unit_distance)
        self.mobject.rotate(arg).shift(point1)


def map_trajectories(vector_len, path_func):
    half_width = SPACE_WIDTH / 2
    left_center = np.array((-half_width, 0, 0))
    right_center = np.array((half_width, 0, 0))
    dividing_line = Line((half_width, SPACE_HEIGHT, 0), (half_width, -SPACE_HEIGHT, 0))
    left_grid = Grid(radius = SPACE_HEIGHT)
    left_path = ParametricFunction(path_func).highlight("white")
    right_path = copy.deepcopy(left_path).apply_complex_function(np.exp)
    right_grid = copy.deepcopy(left_grid).apply_complex_function(np.exp)
    for grid in left_grid, right_grid:
        grid.filter_out(
            lambda (x, y, z) : abs(x) > half_width
        )
    left_start  = Cross().shift(left_path.points[0, :])
    right_start = Cross().shift(right_path.points[0, :])

    apply_function = ComplexFunction(
        np.exp, copy.deepcopy(left_grid)
    ).restrict_width(half_width + 0.1) #STUPID HACK
    move_right_grid = ComplexFunction(
        lambda z : z + SPACE_WIDTH, 
        copy.deepcopy(right_grid).shift(left_center),
        run_time = DEFAULT_TRANSFORM_RUN_TIME
    ).with_background(copy.deepcopy(left_grid).shift(left_center))
    draw_left_path  = ShowCreation(left_path)
    draw_right_path = ShowCreation(right_path)
    show_left_start  = Reveal(left_start)
    show_right_start = Reveal(right_start)
    left_vectors  = VelocityVectorsOfPath(left_path, vector_len)
    right_vectors = VelocityVectorsOfPath(right_path, vector_len)

    for anim in apply_function, draw_left_path, show_left_start, left_vectors:
        anim.shift(left_center).with_background(
            left_grid, dividing_line
        )
    for anim in draw_right_path, show_right_start, right_vectors:
        anim.shift(right_center).with_background(right_grid)
    for anim in draw_left_path, draw_right_path, show_left_start, show_right_start:
        anim.set_dither(0)
    for anim, bg in (show_left_start, left_path), (show_right_start, right_path):
        anim.set_alpha_func(there_and_back).with_background(bg)
    left_vectors.with_background(left_path)
    right_vectors.with_background(right_path)
    return apply_function.then(move_right_grid).then(
        draw_left_path.while_also(draw_right_path)
    ).then(
        show_left_start.while_also(show_right_start)
    ).then(
        left_vectors.while_also(right_vectors)
    )



if __name__ == '__main__':
    example_complex = complex(1, 1)
    example_complex2 = complex(2, -1)
    zoom_level = 0.5
    strong_zoom_level = 0.1
    vector_len = 0.5
    def square_homotopy((z, t)):
        return z**(1 + t)
    def example_walk(t):
        return ((t + 1)/2, ((t + 1)/2)**2, 0)
    def walk_imaginary_axis(t):
        return (0, np.pi * (t + 1), 0)
    functions = [
        # function_of_numbers,
        # real_function_graph,
        # two_grids,
        # z_squared,
        # z_squared_marked,
        # (multiplier_in_the_wild, [example_complex2]),
        # random_looking_function,
        # (zoom_in_on_map, [square_homotopy, True, example_complex, zoom_level]),
        # (zoom_in_on_map, [square_homotopy, True, example_complex, strong_zoom_level]),
        # (z_squared_derivative_example, [example_complex, zoom_level]),
        # (z_squared_derivative_2z, [zoom_level]),
        # visualize_exp,
        # take_derivative_of_series, 
        # derivative_definition, 
        # (e_to_x_takes_adder_to_multiplier, [example_complex]),
        # (e_to_x_derivative_zoom, [example_complex, strong_zoom_level]),
        # other_possible_functions,
        # (setup_velocity_vector_discussion, [strong_zoom_level]),
        # traced_path,
        # (walking_north, [example_complex, vector_len]),
        # (map_north_vector, [example_complex, vector_len, strong_zoom_level]),
        # (all_possible_vectors, [vector_len]),
        # (map_trajectories, [vector_len, example_walk]),
        # (map_trajectories, [vector_len, walk_imaginary_axis])
    ]

    full_path = os.path.join(MOVIE_DIR, CCCD_MOVIE_DIR)
    if not os.path.exists(full_path):
        os.mkdir(full_path)
    for func in functions:
        args = []
        if isinstance(func, tuple):
            func, args = func
        name = os.path.join(
            CCCD_MOVIE_DIR,
            to_cammel_case(func.__name__) + hash_args(args)
        )
        func(*args).write_to_movie(name)

    for anim in [ 
        # ComplexFunction(lambda z : 0.1*(z**3 - z**2 + 3)),
        # ComplexFunction(np.exp, Grid(radius = SPACE_HEIGHT)),
        ]:
        anim.write_to_movie(os.path.join(CCCD_MOVIE_DIR, str(anim)))

    for name in [
        # "complex_derivative_title",
        # "why_vectors",
        # "pause_and_ponder",
        # "think_in_pictures",
        # "remember_this",
        # "deriv_x_squared",
        # "deriv_e_to_x",
        # "multiplication_function",
        ]:
        ImageMobject(name_to_image[name]).center().save_image(
            os.path.join(CCCD_MOVIE_DIR, to_cammel_case(name))
        )








