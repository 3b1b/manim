from manimlib.imports import *

set_custom_quality(1400,20)

OUTPUT_DIRECTORY = "TESTS/SCENE_TESTS"

class Check1(CheckSVG):
	CONFIG={
	"file":"test/test.svg",
	}

class Check2(CheckText):
	CONFIG={
	"text":Text("Hola Mundo"),
	"color":[RED,GREEN],
	"sheen_direction":LEFT
	}

class Check3(CheckSVGPoints):
	CONFIG={
	"svg_type":"object",
	"scale":1.5,
	"show_element_points":[0],
	}
	def custom_object(self):
		return Line(LEFT,RIGHT)

class Check4(ExportCSV):
	CONFIG={
	"text":TextMobject("A","B","C")
	}

class Formula1CSV(ExportCSVPairs):
    CONFIG={
    "csv_name":"Formula", # <- This name is the same for all ExportCSVParis scenes
    "csv_number":0,       # <- This is a formula number 0
    "text":TexMobject("a","x","^","2","+","b","x","+","c","=","0"),
    "remove":[2]
    }

class Formula2CSV(ExportCSVPairs):
    CONFIG={
    "csv_name":"Formula", # <- This name is the same for all ExportCSVParis scenes
    "csv_number":1,       # <- This is a formula number 1
    "text":TexMobject("a","x","^","2","+","b","x","=","-","c"),
    "remove":[2]
    }

class Formula3CSV(ExportCSVPairs):
    CONFIG={
    "csv_name":"Formula", # <- This name is the same for all ExportCSVParis scenes
    "csv_number":2,       # <- This is a formula number 2
    "text":TexMobject("x","^","2","+","{","b","\\over","a","}","x","=","-","{","c","\\over","a","}"),
    "remove":[1,4,8,12,16]
    }

class FormulaFiles(ExportCSVPairs):
    CONFIG={
    "csv_name":"Formula", # <- This name is the same for all ExportCSVParis scenes
    "csv_range":2, # This is the range of the formulas, start with the formula 0 and ends with formula 2
    "csv_complete":True   # <- Use this line to create the entire document
    }