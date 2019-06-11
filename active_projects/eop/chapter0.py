from manimlib.imports import *

class Introduction(TeacherStudentsScene):

    CONFIG = {
        "default_pi_creature_kwargs": {
        "color": MAROON_E,
        "flip_at_start": True,
        },
    }

    def construct(self):
        self.show_series()
        self.show_examples()

    def show_series(self):
        series = VideoSeries(num_videos = 11)
        series.to_edge(UP)
        this_video = series[0]
        this_video.set_color(YELLOW)
        this_video.save_state()
        this_video.set_fill(opacity = 0)
        this_video.center()
        this_video.set_height(FRAME_HEIGHT)
        self.this_video = this_video


        words = TextMobject(
            "Welcome to \\\\",
            "Essence of Probability"
        )
        words.set_color_by_tex("Essence of Probability", YELLOW)

        self.teacher.change_mode("happy")
        self.play(
            FadeIn(
                series,
                lag_ratio = 0.5,
                run_time = 2
            ),
            Blink(self.get_teacher())
        )
        self.teacher_says(words, target_mode = "hooray")
        self.change_student_modes(
            *["hooray"]*3,
            look_at_arg = series[1].get_left(),
            added_anims = [
                ApplyMethod(this_video.restore, run_time = 3),
            ]
        )
        self.play(*[
            ApplyMethod(
                video.shift, 0.5*video.get_height()*DOWN,
                run_time = 3,
                rate_func = squish_rate_func(
                    there_and_back, alpha, alpha+0.3
                )
            )
            for video, alpha in zip(series, np.linspace(0, 0.7, len(series)))
        ]+[
            Animation(self.teacher.bubble),
            Animation(self.teacher.bubble.content),
        ])

        self.play(
            FadeOut(self.teacher.bubble),
            FadeOut(self.teacher.bubble.content),
            self.get_teacher().change_mode, "raise_right_hand",
            *[
                ApplyMethod(pi.change_mode, "pondering")
                for pi in self.get_students()
            ]
        )
        self.wait()

        self.series = series


    def show_examples(self):

        self.wait(10)
        # put examples here in video editor
