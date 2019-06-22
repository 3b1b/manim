#!/usr/bin/env python
from manimlib.imports import *
from active_projects.ode.part2.fourier_series import FourierOfName

name_color_pairs = [
    
]

circle_counts = [
    # 10,
    # 25,
    100,
]

if __name__ == "__main__":
    for name, color in name_color_pairs:
        for n_circles in circle_counts:
            try:
                first_name = name.split(" ")[0]
                scene = FourierOfName(
                    name_text=name,
                    name_color=color,
                    n_circles=n_circles,
                    file_writer_config={
                        "write_to_movie": True,
                        "output_directory": os.path.join(
                            "patron_fourier_names",
                            first_name,
                        ),
                        "file_name": "{}_Fouierified_{}_Separate_paths".format(
                            first_name,
                            n_circles
                        ),
                    },
                    camera_config={
                        "frame_rate": 24,
                    },
                )
            except:
                pass
