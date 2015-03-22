from PIL import Image
import itertools as it

from constants import *
from helpers import invert_image
from tex_image_utils import load_pdf_images


if __name__ == "__main__":
    folder = os.path.join(MOVIE_DIR, "dexp")
    if not os.path.exists(folder):
        os.makedirs(folder)
    images = load_pdf_images("discover_exp.pdf", regen_if_exists = False)
    for image, count in zip(images, it.count()):
        filepath = os.path.join(folder, "dexp-%d.png"%count)
        invert_image(image).save(filepath)
