from manimlib.constants import *
from manimlib.mobject.numbers import Integer
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.types.vectorized_mobject import VMobject, VGroup
from manimlib.scene.scene import Scene
from manimlib.utils.simple_functions import choose


DEFAULT_COUNT_NUM_OFFSET = (FRAME_X_RADIUS - 1, FRAME_Y_RADIUS - 1, 0)
DEFAULT_COUNT_RUN_TIME = 5.0


class CountingScene(Scene):
    def count(self, items, item_type="mobject", *args, **kwargs):
        if item_type == "mobject":
            self.count_mobjects(items, *args, **kwargs)
        elif item_type == "region":
            self.count_regions(items, *args, **kwargs)
        else:
            raise Exception("Unknown item_type, should be mobject or region")
        return self

    def count_mobjects(
        self, mobjects, mode="highlight",
        color="red",
        display_numbers=True,
        num_offset=DEFAULT_COUNT_NUM_OFFSET,
        run_time=DEFAULT_COUNT_RUN_TIME,
    ):
        """
        Note, leaves final number mobject as "number" attribute

        mode can be "highlight", "show_creation" or "show", otherwise
        a warning is given and nothing is animating during the count
        """
        if len(mobjects) > 50:  # TODO
            raise Exception("I don't know if you should be counting \
                             too many mobjects...")
        if len(mobjects) == 0:
            raise Exception("Counting mobject list of length 0")
        if mode not in ["highlight", "show_creation", "show"]:
            raise Warning("Unknown mode")
        frame_time = run_time / len(mobjects)
        if mode == "highlight":
            self.add(*mobjects)
        for mob, num in zip(mobjects, it.count(1)):
            if display_numbers:
                num_mob = TexMobject(str(num))
                num_mob.center().shift(num_offset)
                self.add(num_mob)
            if mode == "highlight":
                original_color = mob.color
                mob.set_color(color)
                self.wait(frame_time)
                mob.set_color(original_color)
            if mode == "show_creation":
                self.play(ShowCreation(mob, run_time=frame_time))
            if mode == "show":
                self.add(mob)
                self.wait(frame_time)
            if display_numbers:
                self.remove(num_mob)
        if display_numbers:
            self.add(num_mob)
            self.number = num_mob
        return self

    def count_regions(self, regions,
                      mode="one_at_a_time",
                      num_offset=DEFAULT_COUNT_NUM_OFFSET,
                      run_time=DEFAULT_COUNT_RUN_TIME,
                      **unused_kwargsn):
        if mode not in ["one_at_a_time", "show_all"]:
            raise Warning("Unknown mode")
        frame_time = run_time / (len(regions))
        for region, count in zip(regions, it.count(1)):
            num_mob = TexMobject(str(count))
            num_mob.center().shift(num_offset)
            self.add(num_mob)
            self.set_color_region(region)
            self.wait(frame_time)
            if mode == "one_at_a_time":
                self.reset_background()
            self.remove(num_mob)
        self.add(num_mob)
        self.number = num_mob
        return self


def combinationMobject(n, k):
    return Integer(choose(n, k))


class GeneralizedPascalsTriangle(VMobject):
    CONFIG = {
        "nrows": 7,
        "height": FRAME_HEIGHT - 1,
        "width": 1.5 * FRAME_X_RADIUS,
        "portion_to_fill": 0.7,
        "submob_class": combinationMobject,
    }

    def generate_points(self):
        self.cell_height = float(self.height) / self.nrows
        self.cell_width = float(self.width) / self.nrows
        self.bottom_left = (self.cell_width * self.nrows / 2.0) * LEFT + \
                           (self.cell_height * self.nrows / 2.0) * DOWN
        self.coords_to_mobs = {}
        self.coords = [
            (n, k)
            for n in range(self.nrows)
            for k in range(n + 1)
        ]
        for n, k in self.coords:
            center = self.coords_to_center(n, k)
            num_mob = self.submob_class(n, k)  # TexMobject(str(num))
            scale_factor = min(
                1,
                self.portion_to_fill * self.cell_height / num_mob.get_height(),
                self.portion_to_fill * self.cell_width / num_mob.get_width(),
            )
            num_mob.center().scale(scale_factor).shift(center)
            if n not in self.coords_to_mobs:
                self.coords_to_mobs[n] = {}
            self.coords_to_mobs[n][k] = num_mob
        self.add(*[
            self.coords_to_mobs[n][k]
            for n, k in self.coords
        ])
        return self

    def coords_to_center(self, n, k):
        x_offset = self.cell_width * (k + self.nrows / 2.0 - n / 2.0)
        y_offset = self.cell_height * (self.nrows - n)
        return self.bottom_left + x_offset * RIGHT + y_offset * UP

    def generate_n_choose_k_mobs(self):
        self.coords_to_n_choose_k = {}
        for n, k in self.coords:
            nck_mob = TexMobject(r"{%d \choose %d}" % (n, k))
            scale_factor = min(
                1,
                self.portion_to_fill * self.cell_height / nck_mob.get_height(),
                self.portion_to_fill * self.cell_width / nck_mob.get_width(),
            )
            center = self.coords_to_mobs[n][k].get_center()
            nck_mob.center().scale(scale_factor).shift(center)
            if n not in self.coords_to_n_choose_k:
                self.coords_to_n_choose_k[n] = {}
            self.coords_to_n_choose_k[n][k] = nck_mob
        return self

    def fill_with_n_choose_k(self):
        if not hasattr(self, "coords_to_n_choose_k"):
            self.generate_n_choose_k_mobs()
        self.submobjects = []
        self.add(*[
            self.coords_to_n_choose_k[n][k]
            for n, k in self.coords
        ])
        return self

    def generate_sea_of_zeros(self):
        zero = TexMobject("0")
        self.sea_of_zeros = []
        for n in range(self.nrows):
            for a in range((self.nrows - n) / 2 + 1):
                for k in (n + a + 1, -a - 1):
                    self.coords.append((n, k))
                    mob = zero.copy()
                    mob.shift(self.coords_to_center(n, k))
                    self.coords_to_mobs[n][k] = mob
                    self.add(mob)
        return self

    def get_lowest_row(self):
        n = self.nrows - 1
        lowest_row = VGroup(*[
            self.coords_to_mobs[n][k]
            for k in range(n + 1)
        ])
        return lowest_row


class PascalsTriangle(GeneralizedPascalsTriangle):
    CONFIG = {
        "submob_class": combinationMobject,
    }
