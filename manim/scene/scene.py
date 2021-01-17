"""Basic canvas for animations."""


__all__ = ["Scene"]


import inspect
import random
import warnings
import platform
import copy
import string
import types

from tqdm import tqdm
import numpy as np

from .. import config, logger
from ..animation.animation import Animation, Wait, prepare_animation
from ..animation.transform import MoveToTarget, _MethodAnimation
from ..camera.camera import Camera
from ..constants import *
from ..container import Container
from ..mobject.mobject import Mobject, _AnimationBuilder
from ..utils.iterables import list_update, list_difference_update
from ..utils.family import extract_mobject_family_members
from ..renderer.cairo_renderer import CairoRenderer
from ..utils.exceptions import EndSceneEarlyException


class Scene(Container):
    """A Scene is the canvas of your animation.

    The primary role of :class:`Scene` is to provide the user with tools to manage
    mobjects and animations.  Generally speaking, a manim script consists of a class
    that derives from :class:`Scene` whose :meth:`Scene.construct` method is overridden
    by the user's code.

    Mobjects are displayed on screen by calling :meth:`Scene.add` and removed from
    screen by calling :meth:`Scene.remove`.  All mobjects currently on screen are kept
    in :attr:`Scene.mobjects`.  Animations are played by calling :meth:`Scene.play`.

    A :class:`Scene` is rendered internally by calling :meth:`Scene.render`.  This in
    turn calls :meth:`Scene.setup`, :meth:`Scene.construct`, and
    :meth:`Scene.tear_down`, in that order.

    It is not recommended to override the ``__init__`` method in user Scenes.  For code
    that should be ran before a Scene is rendered, use :meth:`Scene.setup` instead.


    Examples
    --------
    Override the :meth:`Scene.construct` method with your code.

    .. code-block:: python

        class MyScene(Scene):
            def construct(self):
                self.play(Write(Text("Hello World!")))

    """

    def __init__(
        self,
        renderer=None,
        camera_class=Camera,
        always_update_mobjects=False,
        random_seed=0,
        **kwargs,
    ):
        self.camera_class = camera_class
        self.always_update_mobjects = always_update_mobjects
        self.random_seed = random_seed

        self.animations = None
        self.stop_condition = None
        self.moving_mobjects = None
        self.static_mobjects = None
        self.time_progression = None
        self.duration = None
        self.last_t = None

        if renderer is None:
            self.renderer = CairoRenderer(
                camera_class=self.camera_class,
                skip_animations=kwargs.get("skip_animations", False),
            )
        else:
            self.renderer = renderer
        self.renderer.init_scene(self)

        self.mobjects = []
        # TODO, remove need for foreground mobjects
        self.foreground_mobjects = []
        if self.random_seed is not None:
            random.seed(self.random_seed)
            np.random.seed(self.random_seed)

        Container.__init__(self, **kwargs)

    @property
    def camera(self):
        return self.renderer.camera

    def __deepcopy__(self, clone_from_id):
        cls = self.__class__
        result = cls.__new__(cls)
        clone_from_id[id(self)] = result
        for k, v in self.__dict__.items():
            if k in ["renderer", "time_progression"]:
                continue
            if k == "camera_class":
                setattr(result, k, v)
            setattr(result, k, copy.deepcopy(v, clone_from_id))

        # Update updaters
        for mobject in self.mobjects:
            cloned_updaters = []
            for updater in mobject.updaters:
                # Make the cloned updater use the cloned Mobjects as free variables
                # rather than the original ones. Analyzing function bytecode with the
                # dis module will help in understanding this.
                # https://docs.python.org/3/library/dis.html
                # TODO: Do the same for function calls recursively.
                free_variable_map = inspect.getclosurevars(updater).nonlocals
                cloned_co_freevars = []
                cloned_closure = []
                for i, free_variable_name in enumerate(updater.__code__.co_freevars):
                    free_variable_value = free_variable_map[free_variable_name]

                    # If the referenced variable has not been cloned, raise.
                    if id(free_variable_value) not in clone_from_id:
                        raise Exception(
                            f"{free_variable_name} is referenced from an updater "
                            "but is not an attribute of the Scene, which isn't "
                            "allowed."
                        )

                    # Add the cloned object's name to the free variable list.
                    cloned_co_freevars.append(free_variable_name)

                    # Add a cell containing the cloned object's reference to the
                    # closure list.
                    cloned_closure.append(
                        types.CellType(clone_from_id[id(free_variable_value)])
                    )

                cloned_updater = types.FunctionType(
                    updater.__code__.replace(co_freevars=tuple(cloned_co_freevars)),
                    updater.__globals__,
                    updater.__name__,
                    updater.__defaults__,
                    tuple(cloned_closure),
                )
                cloned_updaters.append(cloned_updater)
            clone_from_id[id(mobject)].updaters = cloned_updaters
        return result

    def render(self):
        """
        Render this Scene.
        """
        self.setup()
        try:
            self.construct()
        except EndSceneEarlyException:
            pass
        self.tear_down()
        # We have to reset these settings in case of multiple renders.
        self.renderer.scene_finished(self)
        logger.info(
            f"Rendered {str(self)}\nPlayed {self.renderer.num_plays} animations"
        )

    def setup(self):
        """
        This is meant to be implemented by any scenes which
        are commonly subclassed, and have some common setup
        involved before the construct method is called.
        """
        pass

    def tear_down(self):
        """
        This is meant to be implemented by any scenes which
        are commonly subclassed, and have some common method
        to be invoked before the scene ends.
        """
        pass

    def construct(self):
        """Add content to the Scene.

        From within :meth:`Scene.construct`, display mobjects on screen by calling
        :meth:`Scene.add` and remove them from screen by calling :meth:`Scene.remove`.
        All mobjects currently on screen are kept in :attr:`Scene.mobjects`.  Play
        animations by calling :meth:`Scene.play`.

        Notes
        -----
        Initialization code should go in :meth:`Scene.setup`.  Termination code should
        go in :meth:`Scene.tear_down`.

        Examples
        --------
        A typical manim script includes a class derived from :class:`Scene` with an
        overridden :meth:`Scene.contruct` method:

        .. code-block:: python

            class MyScene(Scene):
                def construct(self):
                    self.play(Write(Text("Hello World!")))

        See Also
        --------
        :meth:`Scene.setup`
        :meth:`Scene.render`
        :meth:`Scene.tear_down`

        """
        pass  # To be implemented in subclasses

    def __str__(self):
        return self.__class__.__name__

    def get_attrs(self, *keys):
        """
        Gets attributes of a scene given the attribute's identifier/name.

        Parameters
        ----------
        *keys : str
            Name(s) of the argument(s) to return the attribute of.

        Returns
        -------
        list
            List of attributes of the passed identifiers.
        """
        return [getattr(self, key) for key in keys]

    def update_mobjects(self, dt):
        """
        Begins updating all mobjects in the Scene.

        Parameters
        ----------
        dt: int or float
            Change in time between updates. Defaults (mostly) to 1/frames_per_second
        """
        for mobject in self.mobjects:
            mobject.update(dt)

    def should_update_mobjects(self):
        """
        Returns True if any mobject in Scene is being updated
        or if the scene has always_update_mobjects set to true.

        Returns
        -------
            bool
        """
        return self.always_update_mobjects or any(
            [mob.has_time_based_updater() for mob in self.get_mobject_family_members()]
        )

    def get_top_level_mobjects(self):
        """
        Returns all mobjects which are not submobjects.

        Returns
        -------
        list
            List of top level mobjects.
        """
        # Return only those which are not in the family
        # of another mobject from the scene
        families = [m.get_family() for m in self.mobjects]

        def is_top_level(mobject):
            num_families = sum([(mobject in family) for family in families])
            return num_families == 1

        return list(filter(is_top_level, self.mobjects))

    def get_mobject_family_members(self):
        """
        Returns list of family-members of all mobjects in scene.
        If a Circle() and a VGroup(Rectangle(),Triangle()) were added,
        it returns not only the Circle(), Rectangle() and Triangle(), but
        also the VGroup() object.

        Returns
        -------
        list
            List of mobject family members.
        """
        return extract_mobject_family_members(
            self.mobjects, use_z_index=self.renderer.camera.use_z_index
        )

    def add(self, *mobjects):
        """
        Mobjects will be displayed, from background to
        foreground in the order with which they are added.

        Parameters
        ---------
        *mobjects : Mobject
            Mobjects to add.

        Returns
        -------
        Scene
            The same scene after adding the Mobjects in.

        """
        mobjects = [*mobjects, *self.foreground_mobjects]
        self.restructure_mobjects(to_remove=mobjects)
        self.mobjects += mobjects
        if self.moving_mobjects:
            self.restructure_mobjects(
                to_remove=mobjects, mobject_list_name="moving_mobjects"
            )
            self.moving_mobjects += mobjects
        return self

    def add_mobjects_from_animations(self, animations):

        curr_mobjects = self.get_mobject_family_members()
        for animation in animations:
            # Anything animated that's not already in the
            # scene gets added to the scene
            mob = animation.mobject
            if mob is not None and mob not in curr_mobjects:
                self.add(mob)
                curr_mobjects += mob.get_family()

    def remove(self, *mobjects):
        """
        Removes mobjects in the passed list of mobjects
        from the scene and the foreground, by removing them
        from "mobjects" and "foreground_mobjects"

        Parameters
        ----------
        *mobjects : Mobject
            The mobjects to remove.
        """
        for list_name in "mobjects", "foreground_mobjects":
            self.restructure_mobjects(mobjects, list_name, False)
        return self

    def restructure_mobjects(
        self, to_remove, mobject_list_name="mobjects", extract_families=True
    ):
        """
        tl:wr
            If your scene has a Group(), and you removed a mobject from the Group,
            this dissolves the group and puts the rest of the mobjects directly
            in self.mobjects or self.foreground_mobjects.

        In cases where the scene contains a group, e.g. Group(m1, m2, m3), but one
        of its submobjects is removed, e.g. scene.remove(m1), the list of mobjects
        will be edited to contain other submobjects, but not m1, e.g. it will now
        insert m2 and m3 to where the group once was.

        Parameters
        ----------
        to_remove : Mobject
            The Mobject to remove.

        mobject_list_name : str, optional
            The list of mobjects ("mobjects", "foreground_mobjects" etc) to remove from.

        extract_families : bool, optional
            Whether the mobject's families should be recursively extracted.

        Returns
        -------
        Scene
            The Scene mobject with restructured Mobjects.
        """
        if extract_families:
            to_remove = extract_mobject_family_members(
                to_remove, use_z_index=self.renderer.camera.use_z_index
            )
        _list = getattr(self, mobject_list_name)
        new_list = self.get_restructured_mobject_list(_list, to_remove)
        setattr(self, mobject_list_name, new_list)
        return self

    def get_restructured_mobject_list(self, mobjects, to_remove):
        """
        Given a list of mobjects and a list of mobjects to be removed, this
        filters out the removable mobjects from the list of mobjects.

        Parameters
        ----------

        mobjects : list
            The Mobjects to check.

        to_remove : list
            The list of mobjects to remove.

        Returns
        -------
        list
            The list of mobjects with the mobjects to remove removed.
        """

        new_mobjects = []

        def add_safe_mobjects_from_list(list_to_examine, set_to_remove):
            for mob in list_to_examine:
                if mob in set_to_remove:
                    continue
                intersect = set_to_remove.intersection(mob.get_family())
                if intersect:
                    add_safe_mobjects_from_list(mob.submobjects, intersect)
                else:
                    new_mobjects.append(mob)

        add_safe_mobjects_from_list(mobjects, set(to_remove))
        return new_mobjects

    # TODO, remove this, and calls to this
    def add_foreground_mobjects(self, *mobjects):
        """
        Adds mobjects to the foreground, and internally to the list
        foreground_mobjects, and mobjects.

        Parameters
        ----------
        *mobjects : Mobject
            The Mobjects to add to the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobjects added.
        """
        self.foreground_mobjects = list_update(self.foreground_mobjects, mobjects)
        self.add(*mobjects)
        return self

    def add_foreground_mobject(self, mobject):
        """
        Adds a single mobject to the foreground, and internally to the list
        foreground_mobjects, and mobjects.

        Parameters
        ----------
        mobject : Mobject
            The Mobject to add to the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobject added.
        """
        return self.add_foreground_mobjects(mobject)

    def remove_foreground_mobjects(self, *to_remove):
        """
        Removes mobjects from the foreground, and internally from the list
        foreground_mobjects.

        Parameters
        ----------
        *to_remove : Mobject
            The mobject(s) to remove from the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobjects removed.
        """
        self.restructure_mobjects(to_remove, "foreground_mobjects")
        return self

    def remove_foreground_mobject(self, mobject):
        """
        Removes a single mobject from the foreground, and internally from the list
        foreground_mobjects.

        Parameters
        ----------
        mobject : Mobject
            The mobject to remove from the foreground.

        Returns
        ------
        Scene
            The Scene, with the foreground mobject removed.
        """
        return self.remove_foreground_mobjects(mobject)

    def bring_to_front(self, *mobjects):
        """
        Adds the passed mobjects to the scene again,
        pushing them to he front of the scene.

        Parameters
        ----------
        *mobjects : Mobject
            The mobject(s) to bring to the front of the scene.

        Returns
        ------
        Scene
            The Scene, with the mobjects brought to the front
            of the scene.
        """
        self.add(*mobjects)
        return self

    def bring_to_back(self, *mobjects):
        """
        Removes the mobject from the scene and
        adds them to the back of the scene.

        Parameters
        ----------
        *mobjects : Mobject
            The mobject(s) to push to the back of the scene.

        Returns
        ------
        Scene
            The Scene, with the mobjects pushed to the back
            of the scene.
        """
        self.remove(*mobjects)
        self.mobjects = list(mobjects) + self.mobjects
        return self

    def clear(self):
        """
        Removes all mobjects present in self.mobjects
        and self.foreground_mobjects from the scene.

        Returns
        ------
        Scene
            The Scene, with all of its mobjects in
            self.mobjects and self.foreground_mobjects
            removed.
        """
        self.mobjects = []
        self.foreground_mobjects = []
        return self

    def get_moving_mobjects(self, *animations):
        """
        Gets all moving mobjects in the passed animation(s).

        Parameters
        ----------
        *animations : Animation
            The animations to check for moving mobjects.

        Returns
        ------
        list
            The list of mobjects that could be moving in
            the Animation(s)
        """
        # Go through mobjects from start to end, and
        # as soon as there's one that needs updating of
        # some kind per frame, return the list from that
        # point forward.
        animation_mobjects = [anim.mobject for anim in animations]
        mobjects = self.get_mobject_family_members()
        for i, mob in enumerate(mobjects):
            update_possibilities = [
                mob in animation_mobjects,
                len(mob.get_family_updaters()) > 0,
                mob in self.foreground_mobjects,
            ]
            if any(update_possibilities):
                return mobjects[i:]
        return []

    def get_moving_and_static_mobjects(self, animations):
        all_mobjects = list_update(self.mobjects, self.foreground_mobjects)
        all_mobject_families = extract_mobject_family_members(
            all_mobjects,
            use_z_index=self.renderer.camera.use_z_index,
            only_those_with_points=True,
        )
        moving_mobjects = self.get_moving_mobjects(*animations)
        all_moving_mobject_families = extract_mobject_family_members(
            moving_mobjects,
            use_z_index=self.renderer.camera.use_z_index,
        )
        static_mobjects = list_difference_update(
            all_mobject_families, all_moving_mobject_families
        )
        return all_moving_mobject_families, static_mobjects

    def compile_animations(self, *args, **kwargs):
        """
        Creates _MethodAnimations from any _AnimationBuilders and updates animation
        kwargs with kwargs passed to play().
        Parameters
        ----------
        *animations : Tuple[:class:`Animation`]
            Animations to be played.
        **play_kwargs
            Configuration for the call to play().
        Returns
        -------
        Tuple[:class:`Animation`]
            Animations to be played.
        """
        animations = []
        for arg in args:
            try:
                animations.append(prepare_animation(arg))
            except TypeError:
                if inspect.ismethod(arg):
                    raise TypeError(
                        "Passing Mobject methods to Scene.play is no longer"
                        " supported. Use Mobject.animate instead."
                    )
                else:
                    raise TypeError(
                        f"Unexpected argument {arg} passed to Scene.play()."
                    )

        for animation in animations:
            for k, v in kwargs.items():
                setattr(animation, k, v)

        return animations

    def _get_animation_time_progression(self, animations, duration):
        """
        You will hardly use this when making your own animations.
        This method is for Manim's internal use.

        Uses :func:`~.get_time_progression` to obtain a
        CommandLine ProgressBar whose ``fill_time`` is
        dependent on the qualities of the passed Animation,

        Parameters
        ----------
        animations : List[:class:`~.Animation`, ...]
            The list of animations to get
            the time progression for.

        duration : int or float
            duration of wait time

        Returns
        -------
        time_progression
            The CommandLine Progress Bar.
        """
        if len(animations) == 1 and isinstance(animations[0], Wait):
            stop_condition = animations[0].stop_condition
            if stop_condition is not None:
                time_progression = self.get_time_progression(
                    duration,
                    f"Waiting for {stop_condition.__name__}",
                    n_iterations=-1,  # So it doesn't show % progress
                    override_skip_animations=True,
                )
            else:
                time_progression = self.get_time_progression(
                    duration, f"Waiting {self.renderer.num_plays}"
                )
        else:
            time_progression = self.get_time_progression(
                duration,
                "".join(
                    [
                        f"Animation {self.renderer.num_plays}: ",
                        str(animations[0]),
                        (", etc." if len(animations) > 1 else ""),
                    ]
                ),
            )
        return time_progression

    def get_time_progression(
        self, run_time, description, n_iterations=None, override_skip_animations=False
    ):
        """
        You will hardly use this when making your own animations.
        This method is for Manim's internal use.

        Returns a CommandLine ProgressBar whose ``fill_time``
        is dependent on the ``run_time`` of an animation,
        the iterations to perform in that animation
        and a bool saying whether or not to consider
        the skipped animations.

        Parameters
        ----------
        run_time : float
            The ``run_time`` of the animation.

        n_iterations : int, optional
            The number of iterations in the animation.

        override_skip_animations : bool, optional
            Whether or not to show skipped animations in the progress bar.

        Returns
        -------
        time_progression
            The CommandLine Progress Bar.
        """
        if self.renderer.skip_animations and not override_skip_animations:
            times = [run_time]
        else:
            step = 1 / self.renderer.camera.frame_rate
            times = np.arange(0, run_time, step)
        time_progression = tqdm(
            times,
            desc=description,
            total=n_iterations,
            leave=config["leave_progress_bars"],
            ascii=True if platform.system() == "Windows" else None,
            disable=not config["progress_bar"],
        )
        return time_progression

    def get_run_time(self, animations):
        """
        Gets the total run time for a list of animations.

        Parameters
        ----------
        animations : List[:class:`Animation`, ...]
            A list of the animations whose total
            ``run_time`` is to be calculated.

        Returns
        -------
        float
            The total ``run_time`` of all of the animations in the list.
        """

        if len(animations) == 1 and isinstance(animations[0], Wait):
            if animations[0].stop_condition is not None:
                return 0
            else:
                return animations[0].duration

        else:
            return np.max([animation.run_time for animation in animations])

    def play(self, *args, **kwargs):
        self.renderer.play(self, *args, **kwargs)

    def wait(self, duration=DEFAULT_WAIT_TIME, stop_condition=None):
        self.play(Wait(duration=duration, stop_condition=stop_condition))

    def wait_until(self, stop_condition, max_time=60):
        """
        Like a wrapper for wait().
        You pass a function that determines whether to continue waiting,
        and a max wait time if that is never fulfilled.

        Parameters
        ----------
        stop_condition : function
            The function whose boolean return value determines whether to continue waiting

        max_time : int or float, optional
            The maximum wait time in seconds, if the stop_condition is never fulfilled.
        """
        self.wait(max_time, stop_condition=stop_condition)

    def compile_animation_data(self, *animations, skip_rendering=False, **play_kwargs):
        if len(animations) == 0:
            warnings.warn("Called Scene.play with no animations")
            return None

        self.animations = self.compile_animations(*animations, **play_kwargs)
        self.add_mobjects_from_animations(self.animations)

        self.last_t = 0
        self.stop_condition = None
        self.moving_mobjects = None
        self.static_mobjects = None
        if len(self.animations) == 1 and isinstance(self.animations[0], Wait):
            self.update_mobjects(dt=0)  # Any problems with this?
            if self.should_update_mobjects():
                # TODO, be smart about setting a static image
                # the same way Scene.play does
                self.renderer.static_image = None
                self.stop_condition = self.animations[0].stop_condition
            else:
                self.duration = self.animations[0].duration
                if not skip_rendering:
                    self.add_static_frames(self.animations[0].duration)
                return None
        else:
            # Paint all non-moving objects onto the screen, so they don't
            # have to be rendered every frame
            (
                self.moving_mobjects,
                self.static_mobjects,
            ) = self.get_moving_and_static_mobjects(self.animations)
            self.renderer.save_static_frame_data(self, self.static_mobjects)

        self.duration = self.get_run_time(self.animations)
        self.time_progression = self._get_animation_time_progression(
            self.animations, self.duration
        )

        for animation in self.animations:
            animation.begin()

        return self

    def play_internal(self, skip_rendering=False):
        """
        This method is used to prep the animations for rendering,
        apply the arguments and parameters required to them,
        render them, and write them to the video file.

        Parameters
        ----------
        args
            Animation or mobject with mobject method and params
        kwargs
            named parameters affecting what was passed in ``args``,
            e.g. ``run_time``, ``lag_ratio`` and so on.
        """
        for t in self.time_progression:
            self.update_to_time(t)
            if not skip_rendering:
                self.renderer.render(self, self.moving_mobjects)
            if self.stop_condition is not None and self.stop_condition():
                self.time_progression.close()
                break

        for animation in self.animations:
            animation.finish()
            animation.clean_up_from_scene(self)
        self.renderer.static_image = None

    def update_to_time(self, t):
        dt = t - self.last_t
        self.last_t = t
        for animation in self.animations:
            animation.update_mobjects(dt)
            alpha = t / animation.run_time
            animation.interpolate(alpha)
        self.update_mobjects(dt)

    def add_static_frames(self, duration):
        self.renderer.update_frame(self)
        dt = 1 / self.renderer.camera.frame_rate
        self.renderer.add_frame(
            self.renderer.get_frame(),
            num_frames=int(duration / dt),
        )

    def add_sound(self, sound_file, time_offset=0, gain=None, **kwargs):
        """
        This method is used to add a sound to the animation.

        Parameters
        ----------
        sound_file : str
            The path to the sound file.

        time_offset : int,float, optional
            The offset in the sound file after which
            the sound can be played.

        gain :

        """
        if self.renderer.skip_animations:
            return
        time = self.renderer.time + time_offset
        self.renderer.file_writer.add_sound(sound_file, time, gain, **kwargs)
