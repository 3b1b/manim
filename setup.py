from setuptools import setup, find_namespace_packages


setup(name='manim',
      version='0.1.0',
      description='Animation engine for explanatory math videos',
      author='Grant Sanderson',
      author_email='grant@3blue1brown.com',
      url='https://github.com/3b1b/manim',
      license='MIT',
      packages=find_namespace_packages(),
      install_requires=[
         'colour',
         'numpy',
         'Pillow',
         'progressbar',
         'scipy',
         'tqdm',
         'opencv-python',
         'pycairo',
         'pydub',
      ],
      scripts=['manim.py', 'stage_scenes.py', 'big_ol_pile_of_manim_imports.py'],
      package_data={'manimlib': ['*.tex', 'files/**']},
)
