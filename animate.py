from PIL import Image
from colour import Color
import numpy as np
import warnings
import time
import os
import copy
import progressbar
import inspect
from images2gif import writeGif


from helpers import *
from mobject import *
import displayer as disp

class Animation(object):
    def __init__(self, 
                 mobject,
                 alpha_func = high_inflection_0_to_1,
                 run_time = DEFAULT_ANIMATION_RUN_TIME, 
                 pause_time = DEFAULT_ANIMATION_PAUSE_TIME,
                 dither_time = DEFAULT_DITHER_TIME,
                 name = None):
        if isinstance(mobject, type) and issubclass(mobject, Mobject):
            self.mobject = mobject()
            self.starting_mobject = mobject()
        elif isinstance(mobject, Mobject):
            self.mobject = mobject
            self.starting_mobject = copy.deepcopy(mobject)
        else:
            raise Exception("Invalid mobject parameter, must be \
                             subclass or instance of Mobject")
        self.reference_mobjects = [self.starting_mobject]
        self.alpha_func = alpha_func or (lambda x : x)
        self.run_time = run_time
        self.pause_time = pause_time
        self.dither_time = dither_time
        self.nframes, self.ndither_frames = self.get_frame_count()
        self.nframes_past = 0
        self.frames = []
        self.concurrent_animations = []
        self.following_animations = []
        self.reference_animations = []
        self.background_mobjects = []
        self.filter_functions = []
        self.restricted_height = SPACE_HEIGHT
        self.restricted_width  = SPACE_WIDTH
        self.spacial_center = np.zeros(3)
        self.name = self.__class__.__name__ + str(self.mobject)
        self.inputted_name = name

    def __str__(self):
        return self.inputted_name or self.name

    def get_points_and_rgbs(self):
        """
        It is the responsibility of this class to only emit points within
        the space.  Returns np array of points and corresponding np array 
        of rgbs
        """
        points = np.zeros(0)
        rgbs = np.zeros(0)
        for mobject in self.background_mobjects + [self.mobject]:
            points = np.append(points, mobject.points)
            rgbs   = np.append(rgbs, mobject.rgbs)
            #Kind of hacky
            if mobject.SHOULD_BUFF_POINTS: #TODO, think about this.
                up_nudge = np.array(
                    (2.0 * SPACE_HEIGHT / HEIGHT, 0, 0)
                )
                side_nudge = np.array(
                    (0, 2.0 * SPACE_WIDTH / WIDTH, 0)
                )
                for nudge in up_nudge, side_nudge, up_nudge + side_nudge:
                    points = np.append(points, mobject.points + nudge)
                    rgbs = np.append(rgbs, mobject.rgbs)
        points = points.reshape((points.size/3, 3))
        rgbs = rgbs.reshape((rgbs.size/3, 3))
        #Filters out what is out of bounds.
        admissibles = (abs(points[:,0]) < self.restricted_width) * \
                      (abs(points[:,1]) < self.restricted_height)
        for filter_function in self.filter_functions:
            admissibles *= ~filter_function(points)
        if any(self.spacial_center):
            points += self.spacial_center
            #Filter out points pushed off the edge
            admissibles *= (abs(points[:,0]) < SPACE_WIDTH) * \
                           (abs(points[:,1]) < SPACE_HEIGHT)
        if rgbs.shape[0] < points.shape[0]:
            #TODO, this shouldn't be necessary, find what's happening.
            points = points[:rgbs.shape[0], :]
            admissibles = admissibles[:rgbs.shape[0]]
        return points[admissibles, :], rgbs[admissibles, :]

    def update(self):
        if self.nframes_past > self.nframes:
            return False
        self.nframes_past += 1
        for anim in self.concurrent_animations + self.reference_animations:
            anim.update()
        self.update_mobject(self.alpha_func(self.get_fraction_complete()))
        return True

    def while_also(self, action, display = True, *args, **kwargs):
        if isinstance(action, type) and issubclass(action, Animation):
            self.reference_animations += [
                action(mobject, *args, **kwargs)
                for mobject in self.reference_mobjects + [self.mobject]
            ]
            self.name += action.__name__
            return self
        if action.mobject == self.mobject: 
            #This is just for a weird edge case
            action.mobject = self.starting_mobject    
        new_home = self.concurrent_animations if display else \
                   self.reference_animations
        new_home.append(action)
        self.name += str(action)
        return self

    def with_background(self, *mobjects):
        for anim in [self] + self.following_animations:
            anim.background_mobjects.append(CompoundMobject(*mobjects))
        return self

    def then(self, action, carry_over_background = False, *args, **kwargs):
        if isinstance(action, type) and issubclass(action, Animation):
            action = action(mobject = self.mobject, *args, **kwargs)
        if carry_over_background:
            action.background_mobjects += self.background_mobjects
        self.following_animations.append(action)
        if self.frames:
            self.frames += action.get_frames()
        self.name += "Then" + str(action)
        return self

    def get_image(self):
        all_points, all_rgbs = self.get_points_and_rgbs()
        for anim in self.concurrent_animations:
            new_points, new_rgbs = anim.get_points_and_rgbs()
            all_points = np.append(all_points, new_points)
            all_rgbs   = np.append(all_rgbs, new_rgbs)
        all_points = all_points.reshape((all_points.size/3, 3))
        all_rgbs = all_rgbs.reshape((all_rgbs.size/3, 3))
        return disp.get_image(all_points, all_rgbs)

    def generate_frames(self):
        print "Generating " + str(self) + "..."
        progress_bar = progressbar.ProgressBar(maxval=self.nframes)
        progress_bar.start()

        self.frames = []
        while self.update():
            self.frames.append(self.get_image())
            progress_bar.update(self.nframes_past - 1)
        self.clean_up()
        for anim in self.following_animations:
            self.frames += anim.get_frames()
        progress_bar.finish()
        return self

    def get_fraction_complete(self):
        result = float(self.nframes_past - self.ndither_frames) / (
                       self.nframes - 2 * self.ndither_frames)
        if result <= 0:
            return 0
        elif result >= 1:
            return 1
        return result

    def get_frames(self):
        if not self.frames:
            self.generate_frames()
        return self.frames

    def get_frame_count(self):
        nframes = int((self.run_time + 2*self.dither_time)/ self.pause_time)
        ndither_frames = int(self.dither_time / self.pause_time)
        return nframes, ndither_frames

    def filter_out(self, *filter_functions):
        self.filter_functions += filter_functions
        return self

    def restrict_height(self, height):
        self.restricted_height = min(height, SPACE_HEIGHT)
        return self

    def restrict_width(self, width):
        self.restricted_width = min(width, SPACE_WIDTH)   
        return self

    def shift(self, vector):
        self.spacial_center += vector
        for anim in self.following_animations:
            anim.shift(vector)
        return self

    def set_dither(self, time, apply_to_concurrent = False):
        self.dither_time = time
        if apply_to_concurrent:
            for anim in self.concurrent_animations + self.reference_animations:
                anim.set_dither(time)
        return self.reload()

    def set_run_time(self, time, apply_to_concurrent = False):
        self.run_time = time
        if apply_to_concurrent:
            for anim in self.concurrent_animations + self.reference_animations:
                anim.set_run_time(time)
        return self.reload()

    def set_alpha_func(self, alpha_func):
        if alpha_func is None:
            alpha_func = lambda x : x
        self.alpha_func = alpha_func
        return self

    def set_name(self, name):
        self.inputted_name = name
        return self

    def reload(self):
        self.nframes, self.ndither_frames = self.get_frame_count()
        if self.frames:
            self.nframes_past = 0
            self.generate_frames()
        return self

    def drag_pixels(self):
        self.frames = drag_pixels(self.get_frames())
        return self

    def reverse(self):
        self.get_frames().reverse()
        self.name = 'Reversed' + str(self)
        return self

    def write_to_gif(self, name = None):
        disp.write_to_gif(self, name or str(self))

    def write_to_movie(self, name = None):
        disp.write_to_movie(self, name or str(self))

    def update_mobject(self, alpha):
        #Typically ipmlemented by subclass
        pass

    def clean_up(self):
        pass

    def dither(self):
        pass
        

###### Concrete Animations ########

class Rotating(Animation):
    def __init__(self,
                 mobject,
                 axis = None,
                 axes = [[0, 0, 1], [0, 1, 0]], 
                 radians = 2 * np.pi,
                 run_time = 20.0,
                 dither_time = 0.0,
                 alpha_func = None,
                 *args, **kwargs):
        Animation.__init__(
            self, mobject,
            run_time = run_time, dither_time = dither_time,
            alpha_func = alpha_func,
            *args, **kwargs
        )
        self.axes = [axis] if axis else axes
        self.radians = radians

    def update_mobject(self, alpha):
        self.mobject.points = self.starting_mobject.points
        for axis in self.axes:
            self.mobject.rotate(
                self.radians * alpha,
                axis
            )
class RotationAsTransform(Rotating):
    def __init__(self, mobject, radians, 
                 run_time = DEFAULT_ANIMATION_RUN_TIME,
                 dither_time = DEFAULT_DITHER_TIME, 
                 *args, **kwargs):
        Rotating.__init__(
            self,
            mobject,
            axis = (0, 0, 1), 
            run_time = run_time,
            dither_time = dither_time,
            radians = radians,
            alpha_func = high_inflection_0_to_1,
        )

class FadeOut(Animation):
    def update_mobject(self, alpha):
        self.mobject.rgbs = self.starting_mobject.rgbs * (1 - alpha)

class Reveal(Animation):
    def update_mobject(self, alpha):
        self.mobject.rgbs = self.starting_mobject.rgbs * alpha
        if self.mobject.points.shape != self.starting_mobject.points.shape:
            self.mobject.points = self.starting_mobject.points
            #TODO, Why do you need to do this? Shouldn't points always align?

class Transform(Animation):
    def __init__(self, mobject1, mobject2, run_time = DEFAULT_TRANSFORM_RUN_TIME,
                 *args, **kwargs):
        count1, count2 = mobject1.get_num_points(), mobject2.get_num_points()
        Mobject.align_data(mobject1, mobject2)
        Animation.__init__(self, mobject1, run_time = run_time, *args, **kwargs)
        self.ending_mobject = mobject2
        self.mobject.SHOULD_BUFF_POINTS = \
            mobject1.SHOULD_BUFF_POINTS and mobject2.SHOULD_BUFF_POINTS
        self.reference_mobjects.append(mobject2)
        self.name += "To" + str(mobject2)

        if count2 < count1:
            #Ensure redundant pixels fade to black
            indices = self.non_redundant_m2_indices = \
                np.arange(0, count1-1, float(count1) / count2).astype('int')
            temp = np.zeros(mobject2.points.shape)
            temp[indices] = mobject2.rgbs[indices]
            mobject2.rgbs = temp

    def update_mobject(self, alpha):
        Mobject.interpolate(
            self.starting_mobject, 
            self.ending_mobject,
            self.mobject,
            alpha
        )

    def clean_up(self):
        if hasattr(self, "non_redundant_m2_indices"):
            #Reduce mobject (which has become identical to mobject2), as
            #well as mobject2 itself
            for mobject in [self.mobject, self.ending_mobject]:
                for attr in ['points', 'rgbs']:
                    setattr(
                        mobject, attr, 
                        getattr(
                            self.ending_mobject, 
                            attr
                        )[self.non_redundant_m2_indices]
                    )

class ApplyMethod(Transform):
    def __init__(self, method, mobject, *args, **kwargs):
        """
        method is a method of Mobject
        """
        method_args = ()
        if isinstance(method, tuple):
            method, method_args = method[0], method[1:]
        if not inspect.ismethod(method):
            raise "Not a valid Mobject method"
        Transform.__init__(
            self,
            mobject, 
            method(copy.deepcopy(mobject), *method_args),
            *args, **kwargs
        )        

class ApplyFunction(Transform):
    def __init__(self, function, mobject, run_time = DEFAULT_ANIMATION_RUN_TIME,
                 *args, **kwargs):
        map_image = copy.deepcopy(mobject)
        map_image.points = np.array(map(function, map_image.points))
        Transform.__init__(self, mobject, map_image, run_time = run_time, 
                           *args, **kwargs)
        self.name = "".join([
            "Apply",
            "".join([s.capitalize() for s in function.__name__.split("_")]),
            "To" + str(mobject)
        ])

class ComplexFunction(ApplyFunction):
    def __init__(self, function, *args, **kwargs):
        def point_map(point):
            x, y, z = point
            c = np.complex(x, y)
            c = function(c)
            return c.real, c.imag, z
        if len(args) > 0:
            args = list(args)
            mobject = args.pop(0)
        elif "mobject" in kwargs:
            mobject = kwargs.pop("mobject")
        else:
            mobject = Grid()
        ApplyFunction.__init__(self, point_map, mobject, *args, **kwargs)
        self.name = "ComplexFunction" + to_cammel_case(function.__name__)
        #Todo, abstract away function naming'

class Homotopy(Animation):
    def __init__(self, homotopy, *args, **kwargs):
        """
        Homotopy a function from (x, y, z, t) to (x', y', z')
        """
        self.homotopy = homotopy
        Animation.__init__(self, *args, **kwargs)

    def update_mobject(self, alpha):
        self.mobject.points = np.array([
            self.homotopy((x, y, z, alpha))
            for x, y, z in self.starting_mobject.points
        ])

class ComplexHomotopy(Homotopy):
    def __init__(self, complex_homotopy, *args, **kwargs):
        """
        Complex Hootopy a function (z, t) to z'
        """
        def homotopy((x, y, z, t)):
            c = complex_homotopy((complex(x, y), t))
            return (c.real, c.imag, z)
        if len(args) > 0:
            args = list(args)
            mobject = args.pop(0)
        elif "mobject" in kwargs:
            mobject = kwargs["mobject"]
        else:
            mobject = Grid()
        Homotopy.__init__(self, homotopy, mobject, *args, **kwargs)
        self.name = "ComplexHomotopy" + \
            to_cammel_case(complex_homotopy.__name__)


class ShowCreation(Animation):
    def update_mobject(self, alpha):
        new_num_points = int(alpha * self.starting_mobject.points.shape[0])
        for attr in ["points", "rgbs"]:
            setattr(
                self.mobject, 
                attr, 
                getattr(self.starting_mobject, attr)[:new_num_points, :]
            )

class Flash(Animation):
    def __init__(self, mobject, color = "white", slow_factor = 0.01,
                 run_time = 0.1, dither_time = 0, alpha_func = None,
                 *args, **kwargs):
        Animation.__init__(self, mobject, run_time = run_time, 
                           dither_time = dither_time,
                           alpha_func = alpha_func,
                           *args, **kwargs)
        self.intermediate = Mobject(color = color)
        self.intermediate.add_points([
            point + (x, y, 0)
            for point in self.mobject.points
            for x in [-1, 1]
            for y in [-1, 1]
        ])
        self.reference_mobjects.append(self.intermediate)
        self.slow_factor = slow_factor

    def update_mobject(self, alpha):
        #Makes alpha go from 0 to slow_factor to 0 instead of 0 to 1
        alpha = self.slow_factor * (1.0 - 4 * (alpha - 0.5)**2)
        Mobject.interpolate(
            self.starting_mobject, 
            self.intermediate, 
            self.mobject, 
            alpha
        )







