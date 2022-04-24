import itertools as it
import numpy as np
import pyperclip

from manimlib.animation.fading import FadeIn
from manimlib.constants import ARROW_SYMBOLS, CTRL_SYMBOL, DELETE_SYMBOL, SHIFT_SYMBOL
from manimlib.constants import COMMAND_MODIFIER, SHIFT_MODIFIER
from manimlib.constants import DL, DOWN, DR, LEFT, ORIGIN, RIGHT, UL, UP, UR
from manimlib.constants import FRAME_WIDTH, SMALL_BUFF
from manimlib.constants import MANIM_COLORS, WHITE, GREY_C
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import Square
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.dot_cloud import DotCloud
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VHighlight
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.scene.scene import Scene
from manimlib.utils.family_ops import extract_mobject_family_members
from manimlib.utils.space_ops import get_norm
from manimlib.utils.tex_file_writing import LatexError


SELECT_KEY = 's'
GRAB_KEY = 'g'
X_GRAB_KEY = 'h'
Y_GRAB_KEY = 'v'
GRAB_KEYS = [GRAB_KEY, X_GRAB_KEY, Y_GRAB_KEY]
RESIZE_KEY = 't'
COLOR_KEY = 'c'
CURSOR_LOCATION_KEY = 'l'


# Note, a lot of the functionality here is still buggy and very much a work in progress.


class InteractiveScene(Scene):
    """
    To select mobjects on screen, hold ctrl and move the mouse to highlight a region,
    or just tap ctrl to select the mobject under the cursor.

    Pressing command + t will toggle between modes where you either select top level
    mobjects part of the scene, or low level pieces.

    Hold 'g' to grab the selection and move it around
    Hold 'h' to drag it constrained in the horizontal direction
    Hold 'v' to drag it constrained in the vertical direction
    Hold 't' to resize selection, adding 'shift' to resize with respect to a corner

    Command + 'c' copies the ids of selections to clipboard
    Command + 'v' will paste either:
        - The copied mobject
        - A Tex mobject based on copied LaTeX
        - A Text mobject based on copied Text
    Command + 'z' restores selection back to its original state
    Command + 's' saves the selected mobjects to file
    """
    corner_dot_config = dict(
        color=WHITE,
        radius=0.05,
        glow_factor=1.0,
    )
    selection_rectangle_stroke_color = WHITE
    selection_rectangle_stroke_width = 1.0
    colors = MANIM_COLORS
    selection_nudge_size = 0.05
    cursor_location_config = dict(
        font_size=14,
        fill_color=GREY_C,
        num_decimal_places=3,
    )

    def setup(self):
        self.selection = Group()
        self.selection_highlight = Group()
        self.selection_rectangle = self.get_selection_rectangle()
        self.color_palette = self.get_color_palette()
        self.cursor_location_label = self.get_cursor_location_label()
        self.unselectables = [
            self.selection,
            self.selection_highlight,
            self.selection_rectangle,
            self.cursor_location_label,
            self.camera.frame
        ]
        self.select_top_level_mobs = True
        self.regenerate_selection_search_set()

        self.is_selecting = False
        self.is_grabbing = False
        self.add(self.selection_highlight)

    def get_selection_rectangle(self):
        rect = Rectangle(
            stroke_color=self.selection_rectangle_stroke_color,
            stroke_width=self.selection_rectangle_stroke_width,
        )
        rect.fix_in_frame()
        rect.fixed_corner = ORIGIN
        rect.add_updater(self.update_selection_rectangle)
        return rect

    def update_selection_rectangle(self, rect):
        p1 = rect.fixed_corner
        p2 = self.mouse_point.get_center()
        rect.set_points_as_corners([
            p1, [p2[0], p1[1], 0],
            p2, [p1[0], p2[1], 0],
            p1,
        ])
        return rect

    def get_color_palette(self):
        palette = VGroup(*(
            Square(fill_color=color, fill_opacity=1, side_length=1)
            for color in self.colors
        ))
        palette.set_stroke(width=0)
        palette.arrange(RIGHT, buff=0.5)
        palette.set_width(FRAME_WIDTH - 0.5)
        palette.to_edge(DOWN, buff=SMALL_BUFF)
        palette.fix_in_frame()
        return palette

    def get_cursor_location_label(self):
        decimals = VGroup(*(
            DecimalNumber(**self.cursor_location_config)
            for n in range(3)
        ))

        def update_coords(decimals):
            for mob, coord in zip(decimals, self.mouse_point.get_location()):
                mob.set_value(coord)
            decimals.arrange(RIGHT, buff=decimals.get_height())
            decimals.to_corner(DR, buff=SMALL_BUFF)
            decimals.fix_in_frame()
            return decimals

        decimals.add_updater(update_coords)
        return decimals

    # Related to selection

    def toggle_selection_mode(self):
        self.select_top_level_mobs = not self.select_top_level_mobs
        self.refresh_selection_scope()
        self.regenerate_selection_search_set()

    def get_selection_search_set(self) -> list[Mobject]:
        return self.selection_search_set

    def regenerate_selection_search_set(self):
        selectable = list(filter(
            lambda m: m not in self.unselectables,
            self.mobjects
        ))
        if self.select_top_level_mobs:
            self.selection_search_set = selectable
        else:
            self.selection_search_set = [
                submob
                for mob in selectable
                for submob in mob.family_members_with_points()
            ]

    def refresh_selection_scope(self):
        curr = list(self.selection)
        if self.select_top_level_mobs:
            self.selection.set_submobjects([
                mob
                for mob in self.mobjects
                if any(sm in mob.get_family() for sm in curr)
            ])
            self.selection.refresh_bounding_box(recurse_down=True)
        else:
            self.selection.set_submobjects(
                extract_mobject_family_members(
                    curr, exclude_pointless=True,
                )
            )
        self.refresh_selection_highlight()

    def get_corner_dots(self, mobject: Mobject) -> Mobject:
        dots = DotCloud(**self.corner_dot_config)
        radius = self.corner_dot_config["radius"]
        if mobject.get_depth() < 1e-2:
            vects = [DL, UL, UR, DR]
        else:
            vects = list(it.product(*3 * [[-1, 1]]))
        dots.add_updater(lambda d: d.set_points([
            mobject.get_corner(v) + v * radius
            for v in vects
        ]))
        return dots

    def get_highlight(self, mobject: Mobject) -> Mobject:
        if isinstance(mobject, VMobject) and mobject.has_points() and not self.select_top_level_mobs:
            result = VHighlight(mobject)
            result.add_updater(lambda m: m.replace(mobject))
            return result
        else:
            return self.get_corner_dots(mobject)

    def refresh_selection_highlight(self):
        if len(self.selection) > 0:
            self.remove(self.selection_highlight)
            self.selection_highlight.set_submobjects([
                self.get_highlight(mob)
                for mob in self.selection
            ])
            index = min((
                i for i, mob in enumerate(self.mobjects)
                for sm in self.selection
                if sm in mob.get_family()
            ))
            self.mobjects.insert(index, self.selection_highlight)

    def add_to_selection(self, *mobjects):
        mobs = list(filter(
            lambda m: m not in self.unselectables and m not in self.selection,
            mobjects
        ))
        if len(mobs) == 0:
            return
        self.selection.add(*mobs)
        self.refresh_selection_highlight()
        for sm in mobs:
            for mob in self.mobjects:
                if sm in mob.get_family():
                    mob.set_animating_status(True)
        self.refresh_static_mobjects()

    def toggle_from_selection(self, *mobjects):
        for mob in mobjects:
            if mob in self.selection:
                self.selection.remove(mob)
                mob.set_animating_status(False)
            else:
                self.add_to_selection(mob)
        self.refresh_selection_highlight()

    def clear_selection(self):
        for mob in self.selection:
            mob.set_animating_status(False)
        self.selection.set_submobjects([])
        self.selection_highlight.set_submobjects([])
        self.refresh_static_mobjects()

    def add(self, *new_mobjects: Mobject):
        super().add(*new_mobjects)
        self.regenerate_selection_search_set()

    def remove(self, *mobjects: Mobject):
        super().remove(*mobjects)
        self.regenerate_selection_search_set()

    def disable_interaction(self, *mobjects: Mobject):
        for mob in mobjects:
            self.unselectables.append(mob)
        self.regenerate_selection_search_set()

    def enable_interaction(self, *mobjects: Mobject):
        for mob in mobjects:
            if mob in self.unselectables:
                self.unselectables.remove(mob)

    # Functions for keyboard actions

    def copy_selection(self):
        ids = map(id, self.selection)
        pyperclip.copy(",".join(map(str, ids)))

    def paste_selection(self):
        clipboard_str = pyperclip.paste()
        # Try pasting a mobject
        try:
            ids = map(int, clipboard_str.split(","))
            mobs = map(self.id_to_mobject, ids)
            mob_copies = [m.copy() for m in mobs if m is not None]
            self.clear_selection()
            self.play(*(
                FadeIn(mc, run_time=0.5, scale=1.5)
                for mc in mob_copies
            ))
            self.add_to_selection(*mob_copies)
            return
        except ValueError:
            pass
        # Otherwise, treat as tex or text
        if set("\\^=+").intersection(clipboard_str):  # Proxy to text for LaTeX
            try:
                new_mob = Tex(clipboard_str)
            except LatexError:
                return
        else:
            new_mob = Text(clipboard_str)
        self.clear_selection()
        self.add(new_mob)
        self.add_to_selection(new_mob)

    def delete_selection(self):
        self.remove(*self.selection)
        self.clear_selection()

    def restore_state(self, mobject_states: list[tuple[Mobject, Mobject]]):
        super().restore_state(mobject_states)
        self.refresh_selection_highlight()

    def enable_selection(self):
        self.is_selecting = True
        self.add(self.selection_rectangle)
        self.selection_rectangle.fixed_corner = self.mouse_point.get_center().copy()

    def gather_new_selection(self):
        self.is_selecting = False
        if self.selection_rectangle in self.mobjects:
            self.remove(self.selection_rectangle)
            additions = []
            for mob in reversed(self.get_selection_search_set()):
                if self.selection_rectangle.is_touching(mob):
                    additions.append(mob)
            self.add_to_selection(*additions)

    def prepare_grab(self):
        mp = self.mouse_point.get_center()
        self.mouse_to_selection = mp - self.selection.get_center()
        self.is_grabbing = True

    def prepare_resizing(self, about_corner=False):
        center = self.selection.get_center()
        mp = self.mouse_point.get_center()
        if about_corner:
            self.scale_about_point = self.selection.get_corner(center - mp)
        else:
            self.scale_about_point = center
        self.scale_ref_vect = mp - self.scale_about_point
        self.scale_ref_width = self.selection.get_width()
        self.scale_ref_height = self.selection.get_height()

    def toggle_color_palette(self):
        if len(self.selection) == 0:
            return
        if self.color_palette not in self.mobjects:
            self.save_state()
            self.add(self.color_palette)
        else:
            self.remove(self.color_palette)

    def group_selection(self):
        group = self.get_group(*self.selection)
        self.add(group)
        self.clear_selection()
        self.add_to_selection(group)

    def ungroup_selection(self):
        pieces = []
        for mob in list(self.selection):
            self.remove(mob)
            pieces.extend(list(mob))
        self.clear_selection()
        self.add(*pieces)
        self.add_to_selection(*pieces)

    def nudge_selection(self, vect: np.ndarray, large: bool = False):
        nudge = self.selection_nudge_size
        if large:
            nudge *= 10
        self.selection.shift(nudge * vect)

    def save_selection_to_file(self):
        if len(self.selection) == 1:
            self.save_mobject_to_file(self.selection[0])
        else:
            self.save_mobject_to_file(self.selection)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)
        char = chr(symbol)
        if char == SELECT_KEY and modifiers == 0:
            self.enable_selection()
        elif char in GRAB_KEYS and modifiers == 0:
            self.prepare_grab()
        elif char == RESIZE_KEY and modifiers in [0, SHIFT_MODIFIER]:
            self.prepare_resizing(about_corner=(modifiers == SHIFT_MODIFIER))
        elif symbol == SHIFT_SYMBOL:
            if self.window.is_key_pressed(ord("t")):
                self.prepare_resizing(about_corner=True)
        elif char == COLOR_KEY and modifiers == 0:
            self.toggle_color_palette()
        elif char == CURSOR_LOCATION_KEY and modifiers == 0:
            self.add(self.cursor_location_label)
        elif char == "c" and modifiers == COMMAND_MODIFIER:
            self.copy_selection()
        elif char == "v" and modifiers == COMMAND_MODIFIER:
            self.paste_selection()
        elif char == "x" and modifiers == COMMAND_MODIFIER:
            self.copy_selection()
            self.delete_selection()
        elif symbol == DELETE_SYMBOL:
            self.delete_selection()
        elif char == "a" and modifiers == COMMAND_MODIFIER:
            self.clear_selection()
            self.add_to_selection(*self.mobjects)
        elif char == "g" and modifiers == COMMAND_MODIFIER:
            self.group_selection()
        elif char == "g" and modifiers == COMMAND_MODIFIER | SHIFT_MODIFIER:
            self.ungroup_selection()
        elif char == "t" and modifiers == COMMAND_MODIFIER:
            self.toggle_selection_mode()
        elif char == "s" and modifiers == COMMAND_MODIFIER:
            self.save_selection_to_file()
        elif symbol in ARROW_SYMBOLS:
            self.nudge_selection(
                vect=[LEFT, UP, RIGHT, DOWN][ARROW_SYMBOLS.index(symbol)],
                large=(modifiers & SHIFT_MODIFIER),
            )

        # Conditions for saving state
        if char in [GRAB_KEY, X_GRAB_KEY, Y_GRAB_KEY, RESIZE_KEY]:
            self.save_state()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        super().on_key_release(symbol, modifiers)
        if chr(symbol) == SELECT_KEY:
            self.gather_new_selection()
        if chr(symbol) in GRAB_KEYS:
            self.is_grabbing = False
        elif chr(symbol) == CURSOR_LOCATION_KEY:
            self.remove(self.cursor_location_label)
        elif symbol == SHIFT_SYMBOL and self.window.is_key_pressed(ord(RESIZE_KEY)):
            self.prepare_resizing(about_corner=False)

    # Mouse actions
    def handle_grabbing(self, point: np.ndarray):
        diff = point - self.mouse_to_selection
        if self.window.is_key_pressed(ord(GRAB_KEY)):
            self.selection.move_to(diff)
        elif self.window.is_key_pressed(ord(X_GRAB_KEY)):
            self.selection.set_x(diff[0])
        elif self.window.is_key_pressed(ord(Y_GRAB_KEY)):
            self.selection.set_y(diff[1])

    def handle_resizing(self, point: np.ndarray):
        vect = point - self.scale_about_point
        if self.window.is_key_pressed(CTRL_SYMBOL):
            for i in (0, 1):
                scalar = vect[i] / self.scale_ref_vect[i]
                self.selection.rescale_to_fit(
                    scalar * [self.scale_ref_width, self.scale_ref_height][i],
                    dim=i,
                    about_point=self.scale_about_point,
                    stretch=True,
                )
        else:
            scalar = get_norm(vect) / get_norm(self.scale_ref_vect)
            self.selection.set_width(
                scalar * self.scale_ref_width,
                about_point=self.scale_about_point
            )

    def handle_sweeping_selection(self, point: np.ndarray):
        mob = self.point_to_mobject(
            point, search_set=self.get_selection_search_set(),
            buff=SMALL_BUFF
        )
        if mob is not None:
            self.add_to_selection(mob)

    def choose_color(self, point: np.ndarray):
        # Search through all mobject on the screen, not just the palette
        to_search = [
            sm
            for mobject in self.mobjects
            for sm in mobject.family_members_with_points()
            if mobject not in self.unselectables
        ]
        mob = self.point_to_mobject(point, to_search)
        if mob is not None:
            self.selection.set_color(mob.get_color())
        self.remove(self.color_palette)

    def toggle_clicked_mobject_from_selection(self, point: np.ndarray):
        mob = self.point_to_mobject(
            point,
            search_set=self.get_selection_search_set(),
            buff=SMALL_BUFF
        )
        if mob is not None:
            self.toggle_from_selection(mob)

    def on_mouse_motion(self, point: np.ndarray, d_point: np.ndarray) -> None:
        super().on_mouse_motion(point, d_point)
        if self.is_grabbing:
            self.handle_grabbing(point)
        elif self.window.is_key_pressed(ord(RESIZE_KEY)):
            self.handle_resizing(point)
        elif self.window.is_key_pressed(ord(SELECT_KEY)) and self.window.is_key_pressed(SHIFT_SYMBOL):
            self.handle_sweeping_selection(point)

    def on_mouse_release(self, point: np.ndarray, button: int, mods: int) -> None:
        super().on_mouse_release(point, button, mods)
        if self.color_palette in self.mobjects:
            self.choose_color(point)
        elif self.window.is_key_pressed(SHIFT_SYMBOL):
            self.toggle_clicked_mobject_from_selection(point)
        else:
            self.clear_selection()
