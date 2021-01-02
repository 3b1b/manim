import inspect
import itertools as it
import sys

from manimlib.scene.scene import Scene
import manimlib.constants


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
    num_to_class = {}
    for count, scene_class in zip(it.count(1), scene_classes):
        name = scene_class.__name__
        print("%d: %s" % (count, name))
        num_to_class[count] = scene_class
    try:
        user_input = input(manimlib.constants.CHOOSE_NUMBER_MESSAGE)
        return [
            num_to_class[int(num_str)]
            for num_str in user_input.split(",")
        ]
    except KeyError:
        print(manimlib.constants.INVALID_NUMBER_MESSAGE)
        sys.exit(2)
        user_input = input(manimlib.constants.CHOOSE_NUMBER_MESSAGE)
        return [
            num_to_class[int(num_str)]
            for num_str in user_input.split(",")
        ]
    except EOFError:
        sys.exit(1)


def get_scenes_to_render(scene_classes, config):
    if len(scene_classes) == 0:
        print(manimlib.constants.NO_SCENE_MESSAGE)
        return []

    scene_kwargs = dict([
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

    if config["write_all"]:
        return [sc(**scene_kwargs) for sc in scene_classes]

    result = []
    for scene_name in config["scene_names"]:
        found = False
        for scene_class in scene_classes:
            if scene_class.__name__ == scene_name:
                scene = scene_class(**scene_kwargs)
                result.append(scene)
                found = True
                break
        if not found and (scene_name != ""):
            print(
                manimlib.constants.SCENE_NOT_FOUND_MESSAGE.format(
                    scene_name
                ),
                file=sys.stderr
            )
    if result:
        return result
    result = [scene_classes[0]] if len(scene_classes) == 1 else prompt_user_for_choice(scene_classes)
    return [scene_class(**scene_kwargs) for scene_class in result]


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
    all_scene_classes = get_scene_classes_from_module(module)
    scenes = get_scenes_to_render(all_scene_classes, config)
    return scenes


if __name__ == "__main__":
    main()
