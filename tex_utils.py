import os
import itertools as it
from PIL import Image
from constants import *

def tex_to_image(expression, 
                 size = "\HUGE",
                 template_tex_file = TEMPLATE_TEX_FILE):
    """
    Returns list of images for correpsonding with a list of expressions
    """
    return_list = False
    arg = expression
    if not isinstance(expression, str):
        #TODO, verify that expression is iterable of strings
        expression = "\n".join([
            "\onslide<%d>{"%count + exp + "}"
            for count, exp in zip(it.count(1), expression)
        ])
        return_list = True
    filestem = os.path.join(
        TEX_DIR, str(hash(expression + size))
    )
    if not os.path.exists(filestem + ".dvi"):
        if not os.path.exists(filestem + ".tex"):
            print " ".join([
                "Writing ",
                "".join(arg),
                "at size %s to "%(size),
                filestem,
            ])
            with open(template_tex_file, "r") as infile:
                body = infile.read()
                body = body.replace(SIZE_TO_REPLACE, size)
                body = body.replace(TEX_TEXT_TO_REPLACE, expression)
            with open(filestem + ".tex", "w") as outfile:
                outfile.write(body)
        commands = [
            "latex", 
            "-interaction=batchmode", 
            "-output-directory=" + TEX_DIR,
            filestem + ".tex"
        ]
        #TODO, Error check
        os.system(" ".join(commands))
    assert os.path.exists(filestem + ".dvi")
    result = dvi_to_png(filestem + ".dvi")
    return result if return_list else result[0]



def dvi_to_png(filename, regen_if_exists = False):
    """
    Converts a dvi, which potentially has multiple slides, into a 
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    possible_paths = [
        filename,
        os.path.join(TEX_DIR, filename),
        os.path.join(TEX_DIR, filename + ".dvi"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            directory, filename = os.path.split(path)
            name = filename.split(".")[0]
            images_dir = os.path.join(TEX_IMAGE_DIR, name)
            if not os.path.exists(images_dir):
                os.mkdir(images_dir)
            if os.listdir(images_dir) == [] or regen_if_exists:
                commands = [
                    "convert",
                    "-density",
                    str(PDF_DENSITY),
                    path,
                    "-size",
                    str(DEFAULT_WIDTH) + "x" + str(DEFAULT_HEIGHT),
                    os.path.join(images_dir, name + ".png")
                ]
                os.system(" ".join(commands))
            image_paths = [
                os.path.join(images_dir, name)
                for name in os.listdir(images_dir)
                if name.endswith(".png")
            ]
            image_paths.sort(cmp_enumerated_files)
            return [Image.open(path).convert('RGB') for path in image_paths]
    raise IOError("File not Found")

def cmp_enumerated_files(name1, name2):
    num1, num2 = [
        int(name.split(".")[0].split("-")[-1]) 
        for name in (name1, name2)
    ]
    return num1 - num2















