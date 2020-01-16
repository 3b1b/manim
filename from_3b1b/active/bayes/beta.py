from manimlib.imports import *

OUTPUT_DIRECTORY = "bayes/beta"


class BarChart(Axes):
    CONFIG = {
        "x_min": 0,
        "x_max": 10,
        "y_min": 0,
        "y_max": 1,
        "axis_config": {
            "include_tip": False,
        },
        "y_axis_config": {
            "tick_frequency": 0.2,
        },
        "height": 5,
        "width": 10,
        "y_axis_numbers_to_show": range(20, 120, 20),
        "y_axis_label_height": 0.25,
        "include_h_lines": True,
        "h_line_style": {
            "stroke_width": 1,
            "stroke_color": LIGHT_GREY,
        }
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize()
        self.center()
        self.add_y_axis_labels()
        if self.include_h_lines:
            self.add_h_lines()
        self.add_bars()

    # Initializing methods
    def resize(self):
        self.x_axis.set_width(
            self.width,
            stretch=True,
            about_point=self.c2p(0, 0),
        )
        self.y_axis.set_height(
            self.height,
            stretch=True,
            about_point=self.c2p(0, 0),
        )

    def add_y_axis_labels(self):
        labels = VGroup()
        for value in self.y_axis_numbers_to_show:
            label = Integer(value, unit="\\%")
            label.set_height(self.y_axis_label_height)
            label.next_to(self.y_axis.n2p(0.01 * value), LEFT)
            labels.add(label)
        self.y_axis_labels = labels
        self.y_axis.add(labels)
        return self

    def add_h_lines(self):
        self.h_lines = VGroup()
        for tick in self.y_axis.tick_marks:
            line = Line(**self.h_line_style)
            line.match_width(self.x_axis)
            line.move_to(tick.get_center(), LEFT)
            self.h_lines.add(line)
        self.add(self.h_lines)

    def add_bars(self):
        pass

    # Bar manipulations
    


# Scenes
class BarChartTest(Scene):
    def construct(self):
        bar_chart = BarChart()
        bar_chart.to_edge(DOWN)
        self.add(bar_chart)
