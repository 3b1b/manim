import os
from PIL import Image
from constants import PDF_DIR, IMAGE_DIR, WIDTH, HEIGHT, PDF_DENSITY

def load_pdf_images(filename, regen_if_exists = False):
    """
    Converts a pdf, which potentially has multiple slides, into a 
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the pdf
    """
    #TODO, Handle case where there is one page in the pdf!
    possible_paths = [
        filename,
        os.path.join(PDF_DIR, filename),
        os.path.join(PDF_DIR, filename + ".pdf"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            directory, filename = os.path.split(path)
            name = filename.split(".")[0]
            images_dir = os.path.join(IMAGE_DIR, name)
            already_exists = os.path.exists(images_dir)
            if not already_exists:
                os.mkdir(images_dir)
            if not already_exists or regen_if_exists:
                commands = [
                    "convert",
                    "-density",
                    str(PDF_DENSITY),
                    path,
                    "-size",
                    str(WIDTH) + "x" + str(HEIGHT),
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

SYMBOL_IMAGES = load_pdf_images("symbols.pdf", regen_if_exists = False)

NAME_TO_IMAGE_FILE = dict(
    zip([
        "-3",
        "-2",
        "-1",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "cdots",
        "3Blue1Brown",
    ], SYMBOL_IMAGES)
)