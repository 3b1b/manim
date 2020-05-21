from setuptools import setup, find_namespace_packages
setup(
    name="manim",
    version="0.2.0",
    description="Animation engine for explanatory math videos",
    license="MIT",
    packages=find_namespace_packages(),
    package_data={ "manim": ["*.tex"] },
    entry_points={
        "console_scripts": [
            "manim=manim:main",
            "manimcm=manim:main",
        ]
    },
    install_requires=[
        "colour",
        "argparse",
        "colour",
        "numpy",
        "Pillow",
        "progressbar",
        "scipy",
        "tqdm",
        "opencv-python",
        "pycairo",
        "pydub",
        "pygments",
        "pyreadline; sys_platform == 'win32'",
    ],
)
