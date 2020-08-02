from setuptools import setup, find_namespace_packages

setup(
    name="manimlib",
    version="0.2.0",
    description="Animation engine for explanatory math videos",
    license="MIT",
    packages=find_namespace_packages(),
    package_data={"manim": ["*.tex", "*.cfg"]},
    entry_points={
        "console_scripts": ["manim=manim.__main__:main", "manimcm=manim.__main__:main",]
    },
    install_requires=[
        "colour",
        "numpy",
        "Pillow",
        "progressbar",
        "scipy",
        "tqdm",
        "pycairo",
        "pydub",
        "pygments",
        "pyreadline; sys_platform == 'win32'",
        "rich",
    ],
)
