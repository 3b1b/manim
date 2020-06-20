from manim import *
from testing_utils import utils_test_scenes, get_scenes_to_test


#NOTE : All of those tests use cached data (in /test_cache)
# Cache functionality is tested within test_CLI.

class TextTest(Scene):
    def construct(self):
        t = Text('testing', font = "Arial")

        self.play(Animation(t))


class TextMobjectTest(Scene):
    def construct(self):
        constants.TEX_TEMPLATE = TexTemplate()

        t = TextMobject('Hello world !')

        self.play(Animation(t))


class TexMobjectTest(Scene):
    def construct(self):
        #IMPORTANT NOTE : This won't test the abitilty of manim to write/cache latex. 
        # i.e It will pass even if latex is not installed.
        # This is due to the fact that the latex used here has been cached (see test_cache directory)
        constants.TEX_TEMPLATE = TexTemplate()
    
        t = TexMobject(
            "\\sum_{n=1}^\\infty "
            "\\frac{1}{n^2} = \\frac{\\pi^2}{6}"
        )
        self.play(Animation(t))



def test_scenes(get_config_test):
    utils_test_scenes(get_scenes_to_test(__name__), get_config_test, "writing", caching_needed=True)
