import numpy as np
import os

from PIL import Image

from manimlib.utils.file_ops import seek_full_path_from_defaults


def get_full_raster_image_path(image_file_name):
    return seek_full_path_from_defaults(
        image_file_name,
        default_dir=os.path.join("assets", "raster_images"),
        extensions=[".jpg", ".png", ".gif"]
    )


def drag_pixels(frames):
    curr = frames[0]
    new_frames = []
    for frame in frames:
        curr += (curr == 0) * np.array(frame)
        new_frames.append(np.array(curr))
    return new_frames


def invert_image(image):
    arr = np.array(image)
    arr = (255 * np.ones(arr.shape)).astype(arr.dtype) - arr
    return Image.fromarray(arr)


def resize_and_crop(img, size, crop_type='top'):
    """
    :param img: source PIL image object
    :param size: (width, height) target size tuple
    :param crop_type: can be 'top', 'middle' or 'bottom', depending on this value, 
                        the image will cropped getting the 'top/left', 'middle' or 
                        'bottom/right' of the image to fit the size.

    :return: target PIL image object
    """
    if crop_type not in ['top', 'middle', 'bottom']:
        raise ValueError('ERROR: invalid value for crop_type')

    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])

    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], round(size[0] * img.size[1] / img.size[0])), Image.ANTIALIAS)

        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, round((img.size[1] - size[1]) / 2), img.size[0], round((img.size[1] + size[1]) / 2))
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
            
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((round(size[1] * img.size[0] / img.size[1]), size[1]), Image.ANTIALIAS)

        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = (round((img.size[0] - size[0]) / 2), 0,
                   round((img.size[0] + size[0]) / 2), img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])

        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]), Image.ANTIALIAS)
        # If the scale is the same, we do not need to crop
        
    return img
