
from for_3b1b_videos.pi_creature import *
from active_projects.eop.reusables.eop_constants import *


class SicklyPiCreature(PiCreature):
    CONFIG = {
        "sick_color": SICKLY_GREEN
    }

    def get_slightly_sick(self):

        self.save_state()
        self.set_color(self.sick_color)

    def get_sick(self):

        self.get_slightly_sick()
        self.change_mode("sick")

    def get_better(self):
        self.restore()