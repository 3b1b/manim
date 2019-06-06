from big_ol_pile_of_manim_imports import *
from proy_ext.formulas_txt.formulas import formulas
import csv





class Export(ExportCSV):
	CONFIG={
	"directory":"proy_ext/prueba_csv/csv/",
	"csv_name":"formula",
	}
#'''

class Export1(Export):
    CONFIG={
    "text":formulas[10],
    "csv_number":0,
    "remove":[9,11,13,19,17,28,29,33,34,35],
    }

class Export2(Export):
    CONFIG={
    "text":formulas[11],
    "csv_number":1,
    }


class ExportFin(Export):
	CONFIG={
	"csv_complete":True,
	"csv_range":1,
	}
#'''
#---------------------
#'''
class ExportPair(ExportCSVPairs):
	CONFIG={
	"directory":"proy_ext/prueba_csv/csv/",
	"csv_name":"pair",
	}

class Export1p(ExportPair):
    CONFIG={
    "text":formulas[0],
    "csv_number":0,
    }

class Export2p(ExportPair):
    CONFIG={
    "text":formulas[1],
    "csv_number":1,
    }

class Export3p(ExportPair):
    CONFIG={
    "text":formulas[2],
    "csv_number":2,
    "remove":[4,8,12,16]
    }

class Export4p(ExportPair):
    CONFIG={
    "text":formulas[3],
    "csv_number":3,
    }

class Export5p(ExportPair):
    CONFIG={
    "text":formulas[4],
    "csv_number":4,
    }

class ExportFinPair(ExportPair):
	CONFIG={
	"csv_complete":True,
	"csv_range":4,
	}
#'''