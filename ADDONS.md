# Installing an Add-on
1. Before any add-ons can be installed, the *addons* folder must be created in the root Manim directory (e.g., ``/manim/addons``).
2. Download the add-on from the source (it should be something like *test_addon.zip*).
3. Extract the contents of the zip to the *addons* folder.
4. Make sure that the contents of the add-on are located in the root folder of said add-on. (e.g., ``/manim/addons/test_addon/test_addon.py``).

# Creating an Add-on
## Using a sample
YoshiAsk's [GitHub repo](https://github.com/yoshiask/manim-addon-samples) will house a few add-on samples, all of which are under the MIT License.

## From scratch
In order to build an add-on, it is important to understand how add-ons work. When Manim is run, it searches every sub-folder in *addons*for Python modules. If the module contains a class named ``Main`` and a function called ``loaded``, then the ``loaded`` function is run. If it returns ``true``, then the add-on is deemed valid.

### File structure
An add-on's structure must follow a few rules in order to run properly. 

 - The main Python module must be in the add-on's root directory (e.g. ``manim/addons/test-addon/test-addon.py``). 
 - The main module must contain a class named ``Main``. This class will house the primary functionality of the add-on, including events (see *Events*).
 - ``Main`` must contain a function called ``loaded`` that returns ``true``. If either of these conditions is not fulfilled, then the add-on is not deemed valid and is not run.

It is suggested that all add-ons also implement the following:
- ``addon_info()``: See *Addon info*
- ``__str__()``: Return the name of the add-on

### Events
The current add-on API is event-based. Functions marked with a ``*`` must be included in every add-on's ``Main`` class.
|Event Name| Description |
|--|--|
| ``loaded()``* | Fired when the add-on is being loaded. |
| ``set_config(config)`` | Fired when Manim has parsed the command line arguments and generated the config. |
| ``on_rendered()`` | Fired when a scene is done rendering. |
| ``on_render_ready()`` | Fired just before a scene has started rendering. |

### Command-line arguments
Add-ons can also add command line arguments. This is done by adding ``parser_args()`` to ``Main``.  This function should return a list containing the flags to add. Manim's default flags follow the same format and can be found in ``manimlib.config.parse_cli()``.

    def parser_args():
		return [
			{
				'flag': "--hello_world",
				'action': "store_true",
				'help': "[{0}] Prints 'Hello World' when loaded".format("test-addon")
			},
			{
				'flag': "--foobar",
				'action': "store_true",
				'help': "[{0}] Prints 'foobar' when rendering is completed".format("test-addon")
			}
		]

### Add-on info
The ``manim addon-info`` command prints the information of all loaded add-ons. Add-ons can define info by adding ``addon_info()`` to ``Main``.

    def addon_info():
		return {
			'author': "Jane Doe",
			'name': "test_addon",
			'version' : "1.0.3.1",
			'desc': "Adds a couple of command line flags for testing"
		}

### Logging
Add-ons can always write to their own files, but they also have access to the public add-on log (``/manim/addons/addon_log.txt``). ``manimlib.addon_helper.log_text(text)`` will append the given text to the add-on log, while ``log_line(text)`` will append the text and a new line.
(If you are familiar with C#, it is much like ``Console.Write(text)`` and ``Console.WriteLine(text)``.

### Video directories
> This functionality is likely to change in future API versions.

Sometimes, it can be helpful for an add-on to know where the video renders are being saved. 
``manimlib.addon_helper.get_exported_video(config, n)`` returns the video path for the *n*th scene rendered.

``manimlib.addon_helper.get_video_dir()`` returns the absolute and normalized video folder (from ``manimlib.constants.VIDEO_DIR``).