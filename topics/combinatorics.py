from helpers import *

from scene import Scene


DEFAULT_COUNT_NUM_OFFSET = (SPACE_WIDTH - 1, SPACE_HEIGHT - 1, 0)
DEFAULT_COUNT_RUN_TIME   = 5.0

class CountingScene(Scene):
    def count(self, items, item_type = "mobject", *args, **kwargs):
        if item_type == "mobject":
            self.count_mobjects(items, *args, **kwargs)
        elif item_type == "region":
            self.count_regions(items, *args, **kwargs)
        else:
            raise Exception("Unknown item_type, should be mobject or region")
        return self

    def count_mobjects(
        self, mobjects, mode = "highlight",
        color = "red", 
        display_numbers = True,
        num_offset = DEFAULT_COUNT_NUM_OFFSET,
        run_time   = DEFAULT_COUNT_RUN_TIME):
        """
        Note, leaves final number mobject as "number" attribute

        mode can be "highlight", "show_creation" or "show", otherwise
        a warning is given and nothing is animating during the count
        """
        if len(mobjects) > 50: #TODO
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
                mob.highlight(color)
                self.dither(frame_time)
                mob.highlight(original_color)
            if mode == "show_creation":
                self.play(ShowCreation(mob, run_time = frame_time))
            if mode == "show":
                self.add(mob)
                self.dither(frame_time)
            if display_numbers:
                self.remove(num_mob)
        if display_numbers:
            self.add(num_mob)
            self.number = num_mob
        return self

    def count_regions(self, regions, 
                      mode = "one_at_a_time",
                      num_offset = DEFAULT_COUNT_NUM_OFFSET,
                      run_time   = DEFAULT_COUNT_RUN_TIME,
                      **unused_kwargsn):
        if mode not in ["one_at_a_time", "show_all"]:
            raise Warning("Unknown mode")
        frame_time = run_time / (len(regions))
        for region, count in zip(regions, it.count(1)):
            num_mob = TexMobject(str(count))
            num_mob.center().shift(num_offset)
            self.add(num_mob)
            self.highlight_region(region)
            self.dither(frame_time)
            if mode == "one_at_a_time":
                self.reset_background()
            self.remove(num_mob)
        self.add(num_mob)
        self.number = num_mob
        return self


BIG_N_PASCAL_ROWS = 11
N_PASCAL_ROWS = 7

class PascalsTriangleScene(Scene):
    args_list = [
        (N_PASCAL_ROWS,),
        (BIG_N_PASCAL_ROWS,),
    ]
    @staticmethod
    def args_to_string(*args):
        return str(args[0])

    def __init__(self, nrows, *args, **kwargs):
        Scene.__init__(self, *args, **kwargs)
        self.nrows            = nrows
        self.diagram_height   = 2*SPACE_HEIGHT - 1
        self.diagram_width    = 1.5*SPACE_WIDTH
        self.cell_height      = self.diagram_height / nrows
        self.cell_width       = self.diagram_width / nrows
        self.portion_to_fill  = 0.7
        self.bottom_left      = np.array(
            (-self.cell_width * nrows / 2.0, -self.cell_height * nrows / 2.0, 0)
        )
        num_to_num_mob   = {} 
        self.coords_to_mobs   = {}
        self.coords = [(n, k) for n in range(nrows) for k in range(n+1)]    
        for n, k in self.coords:
            num = choose(n, k)              
            center = self.coords_to_center(n, k)
            if num not in num_to_num_mob:
                num_to_num_mob[num] = TexMobject(str(num))
            num_mob = num_to_num_mob[num].copy()
            scale_factor = min(
                1,
                self.portion_to_fill * self.cell_height / num_mob.get_height(),
                self.portion_to_fill * self.cell_width / num_mob.get_width(),
            )
            num_mob.center().scale(scale_factor).shift(center)
            if n not in self.coords_to_mobs:
                self.coords_to_mobs[n] = {}
            self.coords_to_mobs[n][k] = num_mob
        self.add(*[self.coords_to_mobs[n][k] for n, k in self.coords])

    def coords_to_center(self, n, k):
        return self.bottom_left + (
                self.cell_width * (k+self.nrows/2.0 - n/2.0), 
                self.cell_height * (self.nrows - n), 
                0
            )

    def generate_n_choose_k_mobs(self):
        self.coords_to_n_choose_k = {}
        for n, k in self.coords:
            nck_mob = TexMobject(r"{%d \choose %d}"%(n, k)) 
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

    def generate_sea_of_zeros(self):
        zero = TexMobject("0")
        self.sea_of_zeros = []
        for n in range(self.nrows):
            for a in range((self.nrows - n)/2 + 1):
                for k in (n + a + 1, -a -1):
                    self.coords.append((n, k))
                    mob = zero.copy()
                    mob.shift(self.coords_to_center(n, k))
                    self.coords_to_mobs[n][k] = mob
                    self.add(mob)











