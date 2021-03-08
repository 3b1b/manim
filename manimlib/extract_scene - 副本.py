import inspect
import sys
import logging

from manimlib.scene.scene import Scene
from manimlib.config import get_custom_config


class BlankScene(Scene):
    def construct(self):
        exec(get_custom_config()["universal_import_line"])
        self.embed()


def is_child_scene(obj, module):
    if not inspect.isclass(obj):
        return False
    if not issubclass(obj, Scene):
        return False
    if obj == Scene:
        return False
    if not obj.__module__.startswith(module.__name__):
        return False
    return True


def prompt_user_for_choice(scene_classes):
    name_to_class = {}
    max_digits = len(str(len(scene_classes)))
    for idx, scene_class in enumerate(scene_classes, start=1):
        name = scene_class.__name__
        print(f"{str(idx).zfill(max_digits)}: {name}")
        name_to_class[name] = scene_class
    try:
        user_input = input(
            "\nThat module has multiple scenes, "
            "which ones would you like to render?"
            "\nScene Name or Number: "
        )
        # return [
        #     name_to_class[split_str] if not split_str.isnumeric() else scene_classes[int(split_str)-1]
        #     for split_str in user_input.replace(" ", "").split(",")
        # ]
        class_num = [num_str for num_str in user_input.split(",")]
        for cn in class_num:
            if str.__contains__(str(cn), '-'):
                num1=cn[:cn.rfind('-', 1)]
                num2=cn[cn.rfind('-', 1)+1:]
                class_num.remove(cn)
                for tmp in range(int(num1),int(num2)+1):
                    class_num.append(tmp)
        return [scene_classes[int(num_str)-1] for num_str in class_num]
    except KeyError:
        logging.log(logging.ERROR, "Invalid scene")
        sys.exit(2)
    except EOFError:
        sys.exit(1)


def get_scene_config(config):
    return dict([
        (key, config[key])
        for key in [
            "window_config",
            "camera_config",
            "file_writer_config",
            "skip_animations",
            "start_at_animation_number",
            "end_at_animation_number",
            "leave_progress_bars",
            "preview",
        ]
    ])


def get_scenes_to_render(scene_classes, scene_config, config):
    if config["write_all"]:
        return [sc(**scene_config) for sc in scene_classes]

    result = []
    for scene_name in config["scene_names"]:
        found = False
        for scene_class in scene_classes:
            if scene_class.__name__ == scene_name:
                scene = scene_class(**scene_config)
                result.append(scene)
                found = True
                break
        if not found and (scene_name != ""):
            logging.log(
                logging.ERROR,
                f"No scene named {scene_name} found",
            )
    if result:
        return result
    if len(scene_classes) == 1:
        result = [scene_classes[0]]
    else:
        result = prompt_user_for_choice(scene_classes)
    return [scene_class(**scene_config) for scene_class in result]


def get_scene_classes_from_module(module):
    if hasattr(module, "SCENES_IN_ORDER"):
        return module.SCENES_IN_ORDER
    else:
        return [
            member[1]
            for member in inspect.getmembers(
                module,
                lambda x: is_child_scene(x, module)
            )
        ]


def main(config):
    module = config["module"]
    scene_config = get_scene_config(config)
    if module is None:
        # If no module was passed in, just play the blank scene
        return [BlankScene(**scene_config)]

    all_scene_classes = get_scene_classes_from_module(module)
    scenes = get_scenes_to_render(all_scene_classes, scene_config, config)
    return scenes
