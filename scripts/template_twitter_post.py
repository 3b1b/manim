from manim import *
import pkg_resources

version_num = pkg_resources.get_distribution("manim").version


class TwitterScene(Scene):
    def construct(self):
        self.camera.background_color = "#ece6e2"
        version = Tex(f"v{version_num}").to_corner(UR).set_color(BLACK)
        self.add(version)
        ## add twitter scene content here

        banner = ManimBanner(dark_theme=False).scale(0.3).to_corner(DR)
        self.play(FadeIn(banner))
        self.play(banner.expand())
        self.play(FadeOut(banner))
