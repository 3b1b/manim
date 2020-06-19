import numpy as np
import os 
import inspect

def set_test_scene(scene_object, CONFIG, module_name): 
    """Function used to set up the test data for a new feature. Please Refer to the wiki."""
    scene = scene_object(**CONFIG)
    data = scene.get_frame()
    path = os.path.join("manim", "tests","tests_data","{}".format(module_name))
    if not os.path.isdir(path):
        os.makedirs(path)
    np.save(os.path.join(path, str(scene)), data)
    print('Saved in ' + path + '\n')
