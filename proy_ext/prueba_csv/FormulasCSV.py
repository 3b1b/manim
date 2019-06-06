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

class Export6p(ExportPair):
    CONFIG={
    "text":formulas[5],
    "csv_number":5,
    }


class Export7p(ExportPair):
    CONFIG={
    "text":formulas[6],
    "csv_number":6,
    }

class Export8p(ExportPair):
    CONFIG={
    "text":formulas[7],
    "csv_number":7,
    }


class Expor9p(ExportPair):
    CONFIG={
    "text":formulas[8],
    "csv_number":8,
    }


class Export10p(ExportPair):
    CONFIG={
    "text":formulas[9],
    "csv_number":9,
    }


class Export11p(ExportPair):
    CONFIG={
    "text":formulas[10],
    "csv_number":10,
    }

class Export12p(ExportPair):
    CONFIG={
    "text":formulas[11],
    "csv_number":11,
    }

class Export13p(ExportPair):
    CONFIG={
    "text":formulas[12],
    "csv_number":12,
    }

class Export14p(ExportPair):
    CONFIG={
    "text":formulas[13],
    "csv_number":13,
    }

class Export15p(ExportPair):
    CONFIG={
    "text":formulas[14],
    "csv_number":14,
    }

class Export16p(ExportPair):
    CONFIG={
    "text":formulas[15],
    "csv_number":15,
    }

class ExportFinPair(ExportPair):
	CONFIG={
	"csv_complete":True,
	"csv_range":15,
	}
#'''
