from manim import *

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


def test_scenes(get_config_test, Tester):
    CONFIG = get_config_test
    CONFIG["font"] = "Gabriola"
    module_name = os.path.splitext(os.path.basename(__file__))[
        0].replace('test_', '')
    for name, scene_tested in inspect.getmembers(sys.modules[__name__], lambda m: inspect.isclass(m) and m.__module__ == __name__):
        Tester(scene_tested, CONFIG, module_name, caching_needed=True).test()
