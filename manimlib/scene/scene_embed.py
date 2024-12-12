from __future__ import annotations

import inspect
import pyperclip
import traceback

from IPython.terminal import pt_inputhooks
from IPython.terminal.embed import InteractiveShellEmbed

from manimlib.animation.fading import VFadeInThenOut
from manimlib.config import manim_config
from manimlib.constants import RED
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.frame import FullScreenRectangle
from manimlib.module_loader import ModuleLoader


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manimlib.scene.scene import Scene


class InteractiveSceneEmbed:
    def __init__(self, scene: Scene):
        self.scene = scene
        self.checkpoint_manager = CheckpointManager()

        self.shell = self.get_ipython_shell_for_embedded_scene()
        self.enable_gui()
        self.ensure_frame_update_post_cell()
        self.ensure_flash_on_error()
        if manim_config.embed.autoreload:
            self.auto_reload()

    def launch(self):
        self.shell()

    def get_ipython_shell_for_embedded_scene(self) -> InteractiveShellEmbed:
        """
        Create embedded IPython terminal configured to have access to
        the local namespace of the caller
        """
        # Triple back should take us to the context in a user's scene definition
        # which is calling "self.embed"
        caller_frame = inspect.currentframe().f_back.f_back.f_back

        # Update the module's namespace to include local variables
        module = ModuleLoader.get_module(caller_frame.f_globals["__file__"])
        module.__dict__.update(caller_frame.f_locals)
        module.__dict__.update(self.get_shortcuts())
        exception_mode = manim_config.embed.exception_mode

        return InteractiveShellEmbed(
            user_module=module,
            display_banner=False,
            xmode=exception_mode
        )

    def get_shortcuts(self):
        """
        A few custom shortcuts useful to have in the interactive shell namespace
        """
        scene = self.scene
        return dict(
            play=scene.play,
            wait=scene.wait,
            add=scene.add,
            remove=scene.remove,
            clear=scene.clear,
            focus=scene.focus,
            save_state=scene.save_state,
            undo=scene.undo,
            redo=scene.redo,
            i2g=scene.i2g,
            i2m=scene.i2m,
            checkpoint_paste=self.checkpoint_paste,
            clear_checkpoints=self.checkpoint_manager.clear_checkpoints,
            reload=self.reload_scene  # Defined below
        )

    def enable_gui(self):
        """Enables gui interactions during the embed"""
        def inputhook(context):
            while not context.input_is_ready():
                if not self.scene.is_window_closing():
                    self.scene.update_frame(dt=0)
            if self.scene.is_window_closing():
                self.shell.ask_exit()

        pt_inputhooks.register("manim", inputhook)
        self.shell.enable_gui("manim")

    def ensure_frame_update_post_cell(self):
        """Ensure the scene updates its frame after each ipython cell"""
        def post_cell_func(*args, **kwargs):
            if not self.scene.is_window_closing():
                self.scene.update_frame(dt=0, force_draw=True)

        self.shell.events.register("post_run_cell", post_cell_func)

    def ensure_flash_on_error(self):
        """Flash border, and potentially play sound, on exceptions"""
        def custom_exc(shell, etype, evalue, tb, tb_offset=None):
            # Show the error don't just swallow it
            shell.showtraceback((etype, evalue, tb), tb_offset=tb_offset)
            rect = FullScreenRectangle().set_stroke(RED, 30).set_fill(opacity=0)
            rect.fix_in_frame()
            self.scene.play(VFadeInThenOut(rect, run_time=0.5))

        self.shell.set_custom_exc((Exception,), custom_exc)

    def reload_scene(self, embed_line: int | None = None) -> None:
        """
        Reloads the scene just like the `manimgl` command would do with the
        same arguments that were provided for the initial startup. This allows
        for quick iteration during scene development since we don't have to exit
        the IPython kernel and re-run the `manimgl` command again. The GUI stays
        open during the reload.

        If `embed_line` is provided, the scene will be reloaded at that line
        number. This corresponds to the `linemarker` param of the
        `extract_scene.insert_embed_line_to_module()` method.

        Before reload, the scene is cleared and the entire state is reset, such
        that we can start from a clean slate. This is taken care of by the
        run_scenes function in __main__.py, which will catch the error raised by the
        `exit_raise` magic command that we invoke here.

        Note that we cannot define a custom exception class for this error,
        since the IPython kernel will swallow any exception. While we can catch
        such an exception in our custom exception handler registered with the
        `set_custom_exc` method, we cannot break out of the IPython shell by
        this means.
        """
        # Update the global run configuration.
        run_config = manim_config.run
        run_config.is_reload = True
        if embed_line:
            run_config.embed_line = embed_line

        print("Reloading...")
        self.shell.run_line_magic("exit_raise", "")

    def auto_reload(self):
        """Enables IPython autoreload for automatic reloading of modules."""
        self.shell.magic("load_ext autoreload")
        self.shell.magic("autoreload all")

    def checkpoint_paste(
        self,
        skip: bool = False,
        record: bool = False,
        progress_bar: bool = True
    ):
        with self.scene.temp_config_change(skip, record, progress_bar):
            self.checkpoint_manager.checkpoint_paste(self.shell, self.scene)


class CheckpointManager:
    def __init__(self):
        self.checkpoint_states: dict[str, list[tuple[Mobject, Mobject]]] = dict()

    def checkpoint_paste(self, shell, scene):
        """
        Used during interactive development to run (or re-run)
        a block of scene code.

        If the copied selection starts with a comment, this will
        revert to the state of the scene the first time this function
        was called on a block of code starting with that comment.
        """
        code_string = pyperclip.paste()
        checkpoint_key = self.get_leading_comment(code_string)
        self.handle_checkpoint_key(scene, checkpoint_key)
        shell.run_cell(code_string)

    @staticmethod
    def get_leading_comment(code_string: str) -> str:
        leading_line = code_string.partition("\n")[0].lstrip()
        if leading_line.startswith("#"):
            return leading_line
        return ""

    def handle_checkpoint_key(self, scene, key: str):
        if not key:
            return
        elif key in self.checkpoint_states:
            # Revert to checkpoint
            scene.restore_state(self.checkpoint_states[key])

            # Clear out any saved states that show up later
            all_keys = list(self.checkpoint_states.keys())
            index = all_keys.index(key)
            for later_key in all_keys[index + 1:]:
                self.checkpoint_states.pop(later_key)
        else:
            self.checkpoint_states[key] = scene.get_state()

    def clear_checkpoints(self):
        self.checkpoint_states = dict()
