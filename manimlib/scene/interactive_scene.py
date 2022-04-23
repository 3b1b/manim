import numpy as np
import itertools as it
import pyperclip

from manimlib.animation.fading import FadeIn
from manimlib.constants import MANIM_COLORS, WHITE, GREY_C
from manimlib.constants import ORIGIN, UP, DOWN, LEFT, RIGHT, DL, UL, UR, DR
from manimlib.constants import FRAME_WIDTH, SMALL_BUFF
from manimlib.constants import SHIFT_SYMBOL, CTRL_SYMBOL, DELETE_SYMBOL, ARROW_SYMBOLS
from manimlib.constants import SHIFT_MODIFIER, COMMAND_MODIFIER
from manimlib.mobject.geometry import Rectangle
from manimlib.mobject.geometry import Square
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.svg.tex_mobject import Tex
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VHighlight
from manimlib.mobject.types.dot_cloud import DotCloud
from manimlib.scene.scene import Scene
from manimlib.utils.tex_file_writing import LatexError
from manimlib.utils.family_ops import extract_mobject_family_members
from manimlib.utils.space_ops import get_norm


SELECT_KEY = 's'
GRAB_KEY = 'g'
HORIZONTAL_GRAB_KEY = 'h'
VERTICAL_GRAB_KEY = 'v'
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

        self.is_selecting = False
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

    def get_selection_search_set(self):
        mobs = [m for m in self.mobjects if m not in self.unselectables]
        if self.select_top_level_mobs:
            return mobs
        else:
            return [
                submob
                for mob in mobs
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

    def get_corner_dots(self, mobject):
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

    def get_highlight(self, mobject):
        if isinstance(mobject, VMobject) and mobject.has_points() and not self.select_top_level_mobs:
            result = VHighlight(mobject)
            result.add_updater(lambda m: m.replace(mobject))
            return result
        else:
            return self.get_corner_dots(mobject)

    def refresh_selection_highlight(self):
        self.selection_highlight.set_submobjects([
            self.get_highlight(mob)
            for mob in self.selection
        ])

    def add_to_selection(self, *mobjects):
        mobs = list(filter(
            lambda m: m not in self.unselectables and m not in self.selection,
            mobjects
        ))
        if mobs:
            self.selection.add(*mobs)
            self.selection_highlight.add(*map(self.get_highlight, mobs))

    def toggle_from_selection(self, *mobjects):
        for mob in mobjects:
            if mob in self.selection:
                self.selection.remove(mob)
            else:
                self.add_to_selection(mob)
        self.refresh_selection_highlight()

    def clear_selection(self):
        self.selection.set_submobjects([])
        self.selection_highlight.set_submobjects([])

    def add(self, *new_mobjects: Mobject):
        for mob in new_mobjects:
            mob.make_movable()
        super().add(*new_mobjects)

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
            self.add_to_selection(*mob_copies)
            self.play(*(
                FadeIn(mc, run_time=0.5, scale=1.5)
                for mc in mob_copies
            ))
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

    # Event handlers

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        super().on_key_press(symbol, modifiers)
        char = chr(symbol)
        # Enable selection
        if char == SELECT_KEY and modifiers == 0:
            self.is_selecting = True
            self.add(self.selection_rectangle)
            self.selection_rectangle.fixed_corner = self.mouse_point.get_center().copy()
        # Prepare for move
        elif char in [GRAB_KEY, HORIZONTAL_GRAB_KEY, VERTICAL_GRAB_KEY] and modifiers == 0:
            mp = self.mouse_point.get_center()
            self.mouse_to_selection = mp - self.selection.get_center()
        # Prepare for resizing
        elif char == RESIZE_KEY and modifiers in [0, SHIFT_MODIFIER]:
            self.prepare_resizing(about_corner=(modifiers == SHIFT_MODIFIER))
        elif symbol == SHIFT_SYMBOL:
            if self.window.is_key_pressed(ord("t")):
                self.prepare_resizing(about_corner=True)
        # Show color palette
        elif char == COLOR_KEY and modifiers == 0:
            if len(self.selection) == 0:
                return
            if self.color_palette not in self.mobjects:
                self.save_state()
                self.add(self.color_palette)
            else:
                self.remove(self.color_palette)
        # Show coordiantes of cursor location
        elif char == CURSOR_LOCATION_KEY and modifiers == 0:
            self.add(self.cursor_location_label)
        # Command + c -> Copy mobject ids to clipboard
        elif char == "c" and modifiers == COMMAND_MODIFIER:
            self.copy_selection()
        # Command + v -> Paste
        elif char == "v" and modifiers == COMMAND_MODIFIER:
            self.paste_selection()
        # Command + x -> Cut
        elif char == "x" and modifiers == COMMAND_MODIFIER:
            self.copy_selection()
            self.delete_selection()
        # Delete
        elif symbol == DELETE_SYMBOL:
            self.delete_selection()
        # Command + a -> Select all
        elif char == "a" and modifiers == COMMAND_MODIFIER:
            self.clear_selection()
            self.add_to_selection(*self.mobjects)
        # Command + g -> Group selection
        elif char == "g" and modifiers == COMMAND_MODIFIER:
            group = self.get_group(*self.selection)
            self.add(group)
            self.clear_selection()
            self.add_to_selection(group)
        # Command + shift + g -> Ungroup the selection
        elif char == "g" and modifiers == COMMAND_MODIFIER | SHIFT_MODIFIER:
            pieces = []
            for mob in list(self.selection):
                self.remove(mob)
                pieces.extend(list(mob))
            self.clear_selection()
            self.add(*pieces)
            self.add_to_selection(*pieces)
        # Command + t -> Toggle selection mode
        elif char == "t" and modifiers == COMMAND_MODIFIER:
            self.toggle_selection_mode()
        # Command + z -> Undo
        elif char == "z" and modifiers == COMMAND_MODIFIER:
            self.undo()
        # Command + shift + z -> Redo
        elif char == "z" and modifiers == COMMAND_MODIFIER | SHIFT_MODIFIER:
            self.redo()
        # Command + s -> Save selections to file
        elif char == "s" and modifiers == COMMAND_MODIFIER:
            to_save = self.selection
            if len(to_save) == 1:
                to_save = to_save[0]
            self.save_mobject_to_file(to_save)
        # Keyboard movements
        elif symbol in ARROW_SYMBOLS:
            nudge = self.selection_nudge_size
            if (modifiers & SHIFT_MODIFIER):
                nudge *= 10
            vect = [LEFT, UP, RIGHT, DOWN][ARROW_SYMBOLS.index(symbol)]
            self.selection.shift(nudge * vect)

        # Conditions for saving state
        if char in [GRAB_KEY, HORIZONTAL_GRAB_KEY, VERTICAL_GRAB_KEY, RESIZE_KEY]:
            self.save_state()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        super().on_key_release(symbol, modifiers)
        if chr(symbol) == SELECT_KEY:
            self.is_selecting = False
            self.remove(self.selection_rectangle)
            for mob in reversed(self.get_selection_search_set()):
                if mob.is_movable() and self.selection_rectangle.is_touching(mob):
                    self.add_to_selection(mob)
        elif chr(symbol) == CURSOR_LOCATION_KEY:
            self.remove(self.cursor_location_label)
        elif symbol == SHIFT_SYMBOL:
            if self.window.is_key_pressed(ord(RESIZE_KEY)):
                self.prepare_resizing(about_corner=False)

    def on_mouse_motion(self, point: np.ndarray, d_point: np.ndarray) -> None:
        super().on_mouse_motion(point, d_point)
        # Move selection
        if self.window.is_key_pressed(ord(GRAB_KEY)):
            self.selection.move_to(point - self.mouse_to_selection)
        # Move selection restricted to horizontal
        elif self.window.is_key_pressed(ord(HORIZONTAL_GRAB_KEY)):
            self.selection.set_x((point - self.mouse_to_selection)[0])
        # Move selection restricted to vertical
        elif self.window.is_key_pressed(ord(VERTICAL_GRAB_KEY)):
            self.selection.set_y((point - self.mouse_to_selection)[1])
        # Scale selection
        elif self.window.is_key_pressed(ord(RESIZE_KEY)):
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
        # Add to selection
        elif self.window.is_key_pressed(ord(SELECT_KEY)) and self.window.is_key_pressed(SHIFT_SYMBOL):
            mob = self.point_to_mobject(
                point, search_set=self.get_selection_search_set(),
                buff=SMALL_BUFF
            )
            if mob is not None:
                self.add_to_selection(mob)

    def on_mouse_release(self, point: np.ndarray, button: int, mods: int) -> None:
        super().on_mouse_release(point, button, mods)
        if self.color_palette in self.mobjects:
            # Search through all mobject on the screne, not just the palette
            to_search = list(it.chain(*(
                mobject.family_members_with_points()
                for mobject in self.mobjects
                if mobject not in self.unselectables
            )))
            mob = self.point_to_mobject(point, to_search)
            if mob is not None:
                self.selection.set_color(mob.get_color())
            self.remove(self.color_palette)
        elif self.window.is_key_pressed(SHIFT_SYMBOL):
            mob = self.point_to_mobject(
                point,
                search_set=self.get_selection_search_set(),
                buff=SMALL_BUFF
            )
            if mob is not None:
                self.toggle_from_selection(mob)
        else:
            self.clear_selection()
