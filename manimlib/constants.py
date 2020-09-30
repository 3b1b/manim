import numpy as np
import os

MEDIA_DIR = ""
VIDEO_DIR = ""
VIDEO_OUTPUT_DIR = ""
TEX_DIR = ""
TEXT_DIR = ""


def initialize_directories(config):
    global MEDIA_DIR
    global VIDEO_DIR
    global VIDEO_OUTPUT_DIR
    global TEX_DIR
    global TEXT_DIR

    video_path_specified = config["video_dir"] or config["video_output_dir"]

    if not (video_path_specified and config["tex_dir"]):
        if config["media_dir"]:
            MEDIA_DIR = config["media_dir"]
        else:
            MEDIA_DIR = os.path.join(
                os.path.expanduser('~'),
                "Dropbox (3Blue1Brown)/3Blue1Brown Team Folder"
            )
        if not os.path.isdir(MEDIA_DIR):
            MEDIA_DIR = os.path.join(os.getcwd(), "media")
        print(
            f"Media will be written to {MEDIA_DIR + os.sep}. You can change "
            "this behavior with the --media_dir flag."
        )
    else:
        if config["media_dir"]:
            print(
                "Ignoring --media_dir, since both --tex_dir and a video "
                "directory were both passed"
            )

    TEX_DIR = config["tex_dir"] or os.path.join(MEDIA_DIR, "Tex")
    TEXT_DIR = os.path.join(MEDIA_DIR, "texts")
    if not video_path_specified:
        VIDEO_DIR = os.path.join(MEDIA_DIR, "videos")
        VIDEO_OUTPUT_DIR = os.path.join(MEDIA_DIR, "videos")
    elif config["video_output_dir"]:
        VIDEO_OUTPUT_DIR = config["video_output_dir"]
    else:
        VIDEO_DIR = config["video_dir"]

    for folder in [VIDEO_DIR, VIDEO_OUTPUT_DIR, TEX_DIR, TEXT_DIR]:
        if folder != "" and not os.path.exists(folder):
            os.makedirs(folder)

NOT_SETTING_FONT_MSG='''
Warning:
You haven't set font.
If you are not using English, this may cause text rendering problem.
You set font like:
text = Text('your text', font='your font')
or:
class MyText(Text):
    CONFIG = {
        'font': 'My Font'
    }
'''
START_X = 30
START_Y = 20
NORMAL = 'NORMAL'
ITALIC = 'ITALIC'
OBLIQUE = 'OBLIQUE'
BOLD = 'BOLD'

TEX_USE_CTEX = False
TEX_TEXT_TO_REPLACE = "YourTextHere"
TEMPLATE_TEX_FILE = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    "tex_template.tex" if not TEX_USE_CTEX else "ctex_template.tex"
)
with open(TEMPLATE_TEX_FILE, "r") as infile:
    TEMPLATE_TEXT_FILE_BODY = infile.read()
    TEMPLATE_TEX_FILE_BODY = TEMPLATE_TEXT_FILE_BODY.replace(
        TEX_TEXT_TO_REPLACE,
        "\\begin{align*}\n" + TEX_TEXT_TO_REPLACE + "\n\\end{align*}",
    )

HELP_MESSAGE = """
   Usage:
   python extract_scene.py <module> [<scene name>]
   -p preview in low quality
   -s show and save picture of last frame
   -w write result to file [this is default if nothing else is stated]
   -o <file_name> write to a different file_name
   -l use low quality
   -m use medium quality
   -a run and save every scene in the script, or all args for the given scene
   -q don't print progress
   -f when writing to a movie file, export the frames in png sequence
   -t use transperency when exporting images
   -n specify the number of the animation to start from
   -r specify a resolution
   -c specify a background color
"""
SCENE_NOT_FOUND_MESSAGE = """
   {} is not in the script
"""
CHOOSE_NUMBER_MESSAGE = """
Choose number corresponding to desired scene/arguments.
(Use comma separated list for multiple entries)
Choice(s): """
INVALID_NUMBER_MESSAGE = "Fine then, if you don't want to give a valid number I'll just quit"

NO_SCENE_MESSAGE = """
   There are no scenes inside that module
"""

# There might be other configuration than pixel shape later...
PRODUCTION_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 1440,
    "pixel_width": 2560,
    "frame_rate": 60,
}

HIGH_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 1080,
    "pixel_width": 1920,
    "frame_rate": 60,
}

MEDIUM_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 720,
    "pixel_width": 1280,
    "frame_rate": 30,
}

LOW_QUALITY_CAMERA_CONFIG = {
    "pixel_height": 480,
    "pixel_width": 854,
    "frame_rate": 15,
}

DEFAULT_PIXEL_HEIGHT = PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_height"]
DEFAULT_PIXEL_WIDTH = PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_width"]
DEFAULT_FRAME_RATE = 60

DEFAULT_POINT_DENSITY_2D = 25
DEFAULT_POINT_DENSITY_1D = 250

DEFAULT_STROKE_WIDTH = 4

FRAME_HEIGHT = 8.0
FRAME_WIDTH = FRAME_HEIGHT * DEFAULT_PIXEL_WIDTH / DEFAULT_PIXEL_HEIGHT
FRAME_Y_RADIUS = FRAME_HEIGHT / 2
FRAME_X_RADIUS = FRAME_WIDTH / 2

SMALL_BUFF = 0.1
MED_SMALL_BUFF = 0.25
MED_LARGE_BUFF = 0.5
LARGE_BUFF = 1

DEFAULT_MOBJECT_TO_EDGE_BUFFER = MED_LARGE_BUFF
DEFAULT_MOBJECT_TO_MOBJECT_BUFFER = MED_SMALL_BUFF


# All in seconds
DEFAULT_POINTWISE_FUNCTION_RUN_TIME = 3.0
DEFAULT_WAIT_TIME = 1.0


ORIGIN = np.array((0., 0., 0.))
UP = np.array((0., 1., 0.))
DOWN = np.array((0., -1., 0.))
RIGHT = np.array((1., 0., 0.))
LEFT = np.array((-1., 0., 0.))
IN = np.array((0., 0., -1.))
OUT = np.array((0., 0., 1.))
X_AXIS = np.array((1., 0., 0.))
Y_AXIS = np.array((0., 1., 0.))
Z_AXIS = np.array((0., 0., 1.))

# Useful abbreviations for diagonals
UL = UP + LEFT
UR = UP + RIGHT
DL = DOWN + LEFT
DR = DOWN + RIGHT

TOP = FRAME_Y_RADIUS * UP
BOTTOM = FRAME_Y_RADIUS * DOWN
LEFT_SIDE = FRAME_X_RADIUS * LEFT
RIGHT_SIDE = FRAME_X_RADIUS * RIGHT

PI = np.pi
TAU = 2 * PI
DEGREES = TAU / 360

FFMPEG_BIN = "ffmpeg"

# Colors
COLOR_MAP = {
    "DARK_BLUE": "#236B8E",
    "DARK_BROWN": "#8B4513",
    "LIGHT_BROWN": "#CD853F",
    "BLUE_E": "#1C758A",
    "BLUE_D": "#29ABCA",
    "BLUE_C": "#58C4DD",
    "BLUE_B": "#9CDCEB",
    "BLUE_A": "#C7E9F1",
    "TEAL_E": "#49A88F",
    "TEAL_D": "#55C1A7",
    "TEAL_C": "#5CD0B3",
    "TEAL_B": "#76DDC0",
    "TEAL_A": "#ACEAD7",
    "GREEN_E": "#699C52",
    "GREEN_D": "#77B05D",
    "GREEN_C": "#83C167",
    "GREEN_B": "#A6CF8C",
    "GREEN_A": "#C9E2AE",
    "YELLOW_E": "#E8C11C",
    "YELLOW_D": "#F4D345",
    "YELLOW_C": "#FFFF00",
    "YELLOW_B": "#FFEA94",
    "YELLOW_A": "#FFF1B6",
    "GOLD_E": "#C78D46",
    "GOLD_D": "#E1A158",
    "GOLD_C": "#F0AC5F",
    "GOLD_B": "#F9B775",
    "GOLD_A": "#F7C797",
    "RED_E": "#CF5044",
    "RED_D": "#E65A4C",
    "RED_C": "#FC6255",
    "RED_B": "#FF8080",
    "RED_A": "#F7A1A3",
    "MAROON_E": "#94424F",
    "MAROON_D": "#A24D61",
    "MAROON_C": "#C55F73",
    "MAROON_B": "#EC92AB",
    "MAROON_A": "#ECABC1",
    "PURPLE_E": "#644172",
    "PURPLE_D": "#715582",
    "PURPLE_C": "#9A72AC",
    "PURPLE_B": "#B189C6",
    "PURPLE_A": "#CAA3E8",
    "WHITE": "#FFFFFF",
    "BLACK": "#000000",
    "LIGHT_GRAY": "#BBBBBB",
    "LIGHT_GREY": "#BBBBBB",
    "GRAY": "#888888",
    "GREY": "#888888",
    "DARK_GREY": "#444444",
    "DARK_GRAY": "#444444",
    "DARKER_GREY": "#222222",
    "DARKER_GRAY": "#222222",
    "GREY_BROWN": "#736357",
    "PINK": "#D147BD",
    "LIGHT_PINK": "#DC75CD",
    "GREEN_SCREEN": "#00FF00",
    "ORANGE": "#FF862F",
}
PALETTE = list(COLOR_MAP.values())
locals().update(COLOR_MAP)
for name in [s for s in list(COLOR_MAP.keys()) if s.endswith("_C")]:
    locals()[name.replace("_C", "")] = locals()[name]

# Streaming related configuration
LIVE_STREAM_NAME = "LiveStream"
TWITCH_STREAM_KEY = "YOUR_STREAM_KEY"
STREAMING_PROTOCOL = "tcp"
STREAMING_IP = "127.0.0.1"
STREAMING_PORT = "2000"
STREAMING_CLIENT = "ffplay"
STREAMING_URL = f"{STREAMING_PROTOCOL}://{STREAMING_IP}:{STREAMING_PORT}?listen"
STREAMING_CONSOLE_BANNER = """
Manim is now running in streaming mode. Stream animations by passing
them to manim.play(), e.g.
>>> c = Circle()
>>> manim.play(ShowCreation(c))
"""
code_languages_list = {"abap": "abap", "as": "as", "as3": "as3", "ada": "ada", "antlr": "antlr",
                       "antlr_as": "antlr-as",
                       "antlr_csharp": "antlr-csharp", "antlr_cpp": "antlr-cpp", "antlr_java": "antlr-java",
                       "antlr_objc": "antlr-objc", "antlr_perl": "antlr-perl", "antlr_python": "antlr-python",
                       "antlr_ruby": "antlr-ruby", "apacheconf": "apacheconf", "applescript": "applescript",
                       "aspectj": "aspectj",
                       "aspx_cs": "aspx-cs", "aspx_vb": "aspx-vb", "asy": "asy", "ahk": "ahk", "autoit": "autoit",
                       "awk": "awk",
                       "basemake": "basemake", "bash": "bash", "console": "console", "bat": "bat",
                       "bbcode": "bbcode",
                       "befunge": "befunge", "blitzmax": "blitzmax", "boo": "boo", "brainfuck": "brainfuck",
                       "bro": "bro",
                       "bugs": "bugs", "c": "c", "csharp": "csharp", "cpp": "cpp", "c_objdump": "c-objdump",
                       "ca65": "ca65",
                       "cbmbas": "cbmbas", "ceylon": "ceylon", "cfengine3": "cfengine3", "cfs": "cfs",
                       "cheetah": "cheetah",
                       "clojure": "clojure", "cmake": "cmake", "cobol": "cobol", "cobolfree": "cobolfree",
                       "coffee_script": "coffee-script", "cfm": "cfm", "common_lisp": "common-lisp", "coq": "coq",
                       "cpp_objdump": "cpp-objdump", "croc": "croc", "css": "css", "css_django": "css+django",
                       "css_genshitext": "css+genshitext", "css_lasso": "css+lasso", "css_mako": "css+mako",
                       "css_myghty": "css+myghty", "css_php": "css+php", "css_erb": "css+erb",
                       "css_smarty": "css+smarty",
                       "cuda": "cuda", "cython": "cython", "d": "d", "d_objdump": "d-objdump", "dpatch": "dpatch",
                       "dart": "dart",
                       "control": "control", "sourceslist": "sourceslist", "delphi": "delphi", "dg": "dg",
                       "diff": "diff",
                       "django": "django", "dtd": "dtd", "duel": "duel", "dylan": "dylan",
                       "dylan_console": "dylan-console",
                       "dylan_lid": "dylan-lid", "ec": "ec", "ecl": "ecl", "elixir": "elixir", "iex": "iex",
                       "ragel_em": "ragel-em",
                       "erb": "erb", "erlang": "erlang", "erl": "erl", "evoque": "evoque", "factor": "factor",
                       "fancy": "fancy",
                       "fan": "fan", "felix": "felix", "fortran": "fortran", "Clipper": "Clipper",
                       "fsharp": "fsharp", "gas": "gas",
                       "genshi": "genshi", "genshitext": "genshitext", "pot": "pot", "Cucumber": "Cucumber",
                       "glsl": "glsl",
                       "gnuplot": "gnuplot", "go": "go", "gooddata_cl": "gooddata-cl", "gosu": "gosu", "gst": "gst",
                       "groff": "groff",
                       "groovy": "groovy", "haml": "haml", "haskell": "haskell", "hx": "hx", "html": "html",
                       "html_cheetah": "html+cheetah", "html_django": "html+django", "html_evoque": "html+evoque",
                       "html_genshi": "html+genshi", "html_lasso": "html+lasso", "html_mako": "html+mako",
                       "html_myghty": "html+myghty", "html_php": "html+php", "html_smarty": "html+smarty",
                       "html_velocity": "html+velocity", "http": "http", "haxeml": "haxeml", "hybris": "hybris",
                       "idl": "idl",
                       "ini": "ini", "io": "io", "ioke": "ioke", "irc": "irc", "jade": "jade", "jags": "jags",
                       "java": "java",
                       "jsp": "jsp", "js": "js", "js_cheetah": "js+cheetah", "js_django": "js+django",
                       "js_genshitext": "js+genshitext", "js_lasso": "js+lasso", "js_mako": "js+mako",
                       "js_myghty": "js+myghty",
                       "js_php": "js+php", "js_erb": "js+erb", "js_smarty": "js+smarty", "json": "json",
                       "julia": "julia",
                       "jlcon": "jlcon", "kconfig": "kconfig", "koka": "koka", "kotlin": "kotlin", "lasso": "lasso",
                       "lighty": "lighty", "lhs": "lhs", "live_script": "live-script", "llvm": "llvm",
                       "logos": "logos",
                       "logtalk": "logtalk", "lua": "lua", "make": "make", "mako": "mako", "maql": "maql",
                       "mason": "mason",
                       "matlab": "matlab", "matlabsession": "matlabsession", "minid": "minid",
                       "modelica": "modelica",
                       "modula2": "modula2", "trac_wiki": "trac-wiki", "monkey": "monkey", "moocode": "moocode",
                       "moon": "moon",
                       "mscgen": "mscgen", "mupad": "mupad", "mxml": "mxml", "myghty": "myghty", "mysql": "mysql",
                       "nasm": "nasm",
                       "nemerle": "nemerle", "newlisp": "newlisp", "newspeak": "newspeak", "nginx": "nginx",
                       "nimrod": "nimrod",
                       "nsis": "nsis", "numpy": "numpy", "objdump": "objdump", "objective_c": "objective-c",
                       "objective_c_+": "objective-c++", "objective_j": "objective-j", "ocaml": "ocaml",
                       "octave": "octave",
                       "ooc": "ooc", "opa": "opa", "openedge": "openedge", "perl": "perl", "php": "php",
                       "plpgsql": "plpgsql",
                       "psql": "psql", "postgresql": "postgresql", "postscript": "postscript", "pov": "pov",
                       "powershell": "powershell", "prolog": "prolog", "properties": "properties",
                       "protobuf": "protobuf",
                       "puppet": "puppet", "pypylog": "pypylog", "python": "python", "python3": "python3",
                       "py3tb": "py3tb",
                       "pycon": "pycon", "pytb": "pytb", "qml": "qml", "racket": "racket", "ragel": "ragel",
                       "ragel_c": "ragel-c",
                       "ragel_cpp": "ragel-cpp", "ragel_d": "ragel-d", "ragel_java": "ragel-java",
                       "ragel_objc": "ragel-objc",
                       "ragel_ruby": "ragel-ruby", "raw": "raw", "rconsole": "rconsole", "rd": "rd",
                       "rebol": "rebol",
                       "redcode": "redcode", "registry": "registry", "rst": "rst", "rhtml": "rhtml",
                       "RobotFramework": "RobotFramework", "spec": "spec", "rb": "rb", "rbcon": "rbcon",
                       "rust": "rust",
                       "splus": "splus", "sass": "sass", "scala": "scala", "ssp": "ssp", "scaml": "scaml",
                       "scheme": "scheme",
                       "scilab": "scilab", "scss": "scss", "shell_session": "shell-session", "smali": "smali",
                       "smalltalk": "smalltalk", "smarty": "smarty", "snobol": "snobol", "sp": "sp", "sql": "sql",
                       "sqlite3": "sqlite3", "squidconf": "squidconf", "stan": "stan", "sml": "sml",
                       "systemverilog": "systemverilog",
                       "tcl": "tcl", "tcsh": "tcsh", "tea": "tea", "tex": "tex", "text": "text",
                       "treetop": "treetop", "ts": "ts",
                       "urbiscript": "urbiscript", "vala": "vala", "vb.net": "vb.net", "velocity": "velocity",
                       "verilog": "verilog",
                       "vgl": "vgl", "vhdl": "vhdl", "vim": "vim", "xml": "xml", "xml_cheetah": "xml+cheetah",
                       "xml_django": "xml+django", "xml_evoque": "xml+evoque", "xml_lasso": "xml+lasso",
                       "xml_mako": "xml+mako",
                       "xml_myghty": "xml+myghty", "xml_php": "xml+php", "xml_erb": "xml+erb",
                       "xml_smarty": "xml+smarty",
                       "xml_velocity": "xml+velocity", "xquery": "xquery", "xslt": "xslt", "xtend": "xtend",
                       "yaml": "yaml"}

code_styles_list = {0: "autumn", 1: "borland", 2: "bw", 3: "colorful", 4: "default", 5: "emacs",
                    6: "friendly", 7: "fruity", 8: "manni", 9: "monokai", 10: "murphy", 11: "native",
                    12: "pastie", 13: "perldoc", 14: "rrt", 15: "tango", 16: "trac", 17: "vim", 18: "vs"}
