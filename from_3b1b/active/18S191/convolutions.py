from manimlib.imports import *


def box_blur(n):
    return np.ones((n, n)) / (n**2)


class ConvolutionIntroduction(ThreeDScene):
    def construct(self):
        frame = self.camera.frame

        # Setup the pixel grids
        image = Image.open(get_full_raster_image_path("Mario"))

        arr = np.array(image)
        arr = arr[80::40, 0::40]
        height, width = arr.shape[:2]

        pixel_array = VGroup(*[
            Square(fill_color=rgb_to_hex(arr[i, j] / 255), fill_opacity=1)
            for i in range(height)
            for j in range(width)
        ])
        pixel_array.arrange_in_grid(height, width, buff=0)
        pixel_array.set_height(6)
        pixel_array.set_stroke(WHITE, 1)
        pixel_array.to_edge(LEFT, buff=LARGE_BUFF)

        new_array = pixel_array.copy()
        new_array.next_to(pixel_array, RIGHT, buff=2)
        new_array.set_fill(BLACK, 0)

        self.add(pixel_array)
        self.add(new_array)

        # Setup kernel
        def get_kernel_array(kernel, pixel_array=pixel_array, tex=None):
            kernel_array = VGroup()
            for row in kernel:
                for x in row:
                    square = pixel_array[0].copy()
                    square.set_fill(BLACK, 0)
                    square.set_stroke(BLUE, 2)
                    if tex:
                        value = TexMobject(tex)
                    else:
                        value = DecimalNumber(x, num_decimal_places=3)
                    value.set_width(square.get_width() * 0.7)
                    value.set_stroke(BLACK, 1, background=True)
                    value.move_to(square)
                    square.add(value)
                    kernel_array.add(square)
            kernel_array.arrange_in_grid(*kernel.shape, buff=0)
            kernel_array.move_to(pixel_array[0])
            return kernel_array

        kernel = box_blur(3)
        kernel_array = get_kernel_array(kernel, tex="1 / 9")
        self.add(kernel_array)

        # Define step
        right_rect = new_array[0].copy()
        right_rect.set_stroke(BLUE, 2)
        self.add(right_rect)

        def step(pos=0):
            i = pos // width
            j = pos % width

            h, w = kernel.shape
            pixels = np.array([
                square.fill_rgbas[0]
                for square in pixel_array
            ]).reshape((height, width, 4))

            rgba = sum([
                kernel[k, l] * pixels[i - k, j - l]
                for k in range(-(w // 2), w // 2 + 1)
                for l in range(-(h // 2), h // 2 + 1)
                if (0 <= i - k < pixels.shape[0]) and (0 <= j - l < pixels.shape[1])
            ])

            kernel_array.move_to(pixel_array[pos])
            right_rect.move_to(new_array[pos])
            new_array[pos].fill_rgbas[0] = rgba

        def walk(start, stop, time=5, surface=None):
            for n in range(start, stop):
                step(n)
                if surface:
                    surface.move_to(kernel_array, IN)
                self.wait(time / (stop - start))

        # Setup zooming
        def zoom_to_kernel():
            self.play(
                frame.set_height, 1.5 * kernel_array.get_height(),
                frame.move_to, kernel_array,
                run_time=2
            )

        def zoom_to_new_pixel():
            self.play(
                frame.set_height, 1.5 * kernel_array.get_height(),
                frame.move_to, right_rect,
                run_time=2
            )

        def reset_frame():
            self.play(
                frame.to_default_state
            )

        # Example walking
        # walk(0, 151, 15)
        last_i = 0
        next_i = 151
        walk(last_i, next_i, 5)
        self.wait()
        zoom_to_kernel()
        self.wait()
        reset_frame()
        zoom_to_new_pixel()
        self.wait()
        reset_frame()

        # last_i = next_i
        # next_i = 200
        # walk(151, 200, 2)
        # self.wait(0.5)
        # zoom_to_kernel()
        # self.wait()
        # reset_frame()
        # zoom_to_new_pixel()
        # self.wait()
        # reset_frame()

        last_i = next_i
        next_i = len(pixel_array)
        walk(last_i, next_i, 10)
        # self.wait()
        # zoom_to_kernel()
        # self.wait()
        # reset_frame()
        self.wait()

        # Gauss kernel
        gauss_kernel = np.array([
            [0.00296902, 0.0133062, 0.0219382, 0.0133062, .00296902],
            [0.0133062, 0.0596343, 0.0983203, 0.0596343, 0.0133062],
            [0.0219382, 0.0983203, 0.162103, 0.0983203, 0.0219382],
            [0.0133062, 0.0596343, 0.0983203, 0.0596343, 0.0133062],
            [0.00296902, 0.0133062, 0.0219382, 0.0133062, 0.00296902],
        ])  # Oh good, hard coded, I hope you feel happy with yourself.
        gauss_array = get_kernel_array(gauss_kernel)
        kernel_array.set_submobjects(gauss_array)

        kernel = gauss_kernel
        new_array.set_fill(BLACK, 0)

        walk(0, 200, time=5)
        # walk(0, 200, time=10)
        self.wait()
        zoom_to_kernel()
        self.wait()

        # Gauss surface
        gaussian = ParametricSurface(
            lambda u, v: [u, v, np.exp(-(u**2) - v**2)],
            u_range=(-3, 3),
            v_range=(-3, 3),
            resolution=(101, 101),
        )
        gaussian.set_color(BLUE, 0.8)
        gaussian.match_width(kernel_array)
        gaussian.stretch(2, 2)

        def update_surface(surface, kernel_array=kernel_array):
            surface.move_to(kernel_array, IN)

        update_surface(gaussian)
        self.play(
            FadeIn(gaussian),
            frame.set_phi, 70 * DEGREES,
            frame.set_theta, 10 * DEGREES,
            run_time=3
        )
        self.wait()
        self.play(
            frame.set_height, 8,
            frame.set_theta, 0,
            frame.set_x, 0,
            run_time=3,
        )

        # More walking
        walk(200, len(pixel_array), time=10, surface=gaussian)
        self.wait()
        self.play(frame.to_default_state, run_time=2)
        self.wait()
