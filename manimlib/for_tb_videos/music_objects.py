from manimlib.imports import *

# CONSTANTS

ERROR_NUMBER_CLEFS ="""

-----------------------------------
           #clefs > #pentagrams
-----------------------------------

"""

ALPHAS = {
    "stem":{
        "width":16.00022333751562,
        "heigth":0.36623730881369715,
        "unit_vector":np.array([ 3.15654676e-01,  9.48874136e-01, 0]),
        "vector_length":0.6966207908464077,
    },
    "bemol":{
        'width': 1.9047617482816004, 
        'vector_length': 1.1188564231965377, 
        'unit_vector': np.array([-9.58018319e-01,  2.86706992e-01, 0]), 
    },
    "sharp":{
        'width': 1.7777778087577196,
        'vector_length': 1.103450979190911,
        'unit_vector': np.array([-1.0000000e+00,  1.9213607e-16, 0]),
    },
    "natural":{
        'width': 2.5396825839395993,
        'vector_length': 1.1034510746729629,
        'unit_vector': np.array([-1.00000000e+00, -8.65304011e-08, 0]),
    },
    'ks_sharp': {
        'width': 0.5862067384103721,
        'dy': 6.932270571400658,
    },
    'ks_bemol': {
        'width': 0.5923343343242982,
        'dy': 9,
    }
}

ALPHA_HEIGHT_G_CLEF = 0.5743147103253643
ALPHA_HEIGHT_F_CLEF = 1.2929782931297076
ALPHA_DOWN_G_CLEF = -57.673398215985706
ALPHA_DOWN_F_CLEF = -8.176884884446107
ALPHA_HEIGHT_STEM  = 0.41596100500179733
ALPHA_WIDTH_HALF_DOT = 3.0644336712207947
ALPHA_LENGTH_VECTOR_HALF_DOT = 1.018861808179335
UNIT_VECTOR_HALF_DOT = np.array([9.30474096e-01,3.66357690e-01,0])
ALPHA_LENGTH_STEM = 0.41596100500179733
ALPHA_LENGTH_VECTOR_STEM = 0.7190178571802391
UNIT_VECTOR_STEM = np.array([-3.26004674e-01,-9.45368157e-01,0])
ALPHA_STROKE_STEM = 0.11963381920678877
ALPHA_ADDITIONAL_LINE = 0.686664
ALPHA_PENTAGRAM_ADDITIONAL_LINE = 0.5437653622504716
ALPHA_BEMOL_SCALE = 1.4461098901098903
UNIT_VECTOR_BEMOL = np.array([-9.11981280e-01,4.10231818e-01,0])
ALPHA_BEMOL_LENGTH_VECTOR = 0.8946186251034574

def sign(x):
    if x>=0: return 1
    else: return -1

def get_update_relative_note_part(self,main,relative):
    alpha_width = self.note_parts[main].get_width() / self.note_parts[relative].get_width()
    reference_line = Line(
        self.note_parts[main].get_center(),
        self.note_parts[relative].get_center(),
        )
    unit_vector = reference_line.get_unit_vector()
    vector_length = reference_line.get_length()
    alpha_vector_length = self.note_parts[main].get_width() / vector_length
    def update_relative(mob):
        width = mob.note_parts[main].get_width() / alpha_width
        mob.note_parts[relative].set_width(width)
        length = mob.note_parts[main].get_width() / alpha_vector_length
        vector = unit_vector * length
        if relative == "stem":
            sign = int(mob.sign)
        else:
            sign = 1
        mob.note_parts[relative].move_to(mob.note_parts[main].get_center()+vector*sign)
    return update_relative

class AdditionalLineNote(VMobject):
    def __init__(self,note,**kwargs):
        super().__init__(**kwargs)
        line_height = note.get_width() / ALPHA_ADDITIONAL_LINE
        self.set_points_as_corners([ORIGIN,RIGHT*line_height])
        self.move_to(note.body)
        self.set_stroke(None,note.get_width() / ALPHA_STROKE_STEM)

class Pentagram(VGroup):
    CONFIG = {
        "num_pentagrams": 0,
        "height":1,
        "width":FRAME_WIDTH - 2,
        "clefs":None,
        "arrange_config":{
            "direction":DOWN, "buff": 1    
        },
        "pentagram_config":{
            "stroke_width":4,
            "stroke_opacity":1,
            "fill_opacity":0
        },
        "clef_config":{
            "stroke_width":0,
            "stroke_opacity":0,
            "fill_opacity":1
        },
        "left_buff":0.14,
        "reference":2,
        "show_reference":False,
    }
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.pentagram = SVGMobject("music_symbols/c_clef",**self.pentagram_config)[:5]
        # Fix lines
        for i in range(1,len(self.pentagram)):
            self.pentagram[i].points[-1][0] = self.pentagram[0].points[-1][0]
        self.c_clef = SVGMobject("music_symbols/c_clef",**self.clef_config)[5]
        self.g_clef = SVGMobject("music_symbols/g_clef",**self.clef_config)[5]
        self.f_clef = SVGMobject("music_symbols/f_clef",**self.clef_config)[5]
        self.pentagram.set_width(self.width,stretch=True)
        self.pentagram.set_height(self.height,stretch=True)
        self.pentagrams = VGroup()
        self.clefs_group = VGroup()
        self.reference_lines = VGroup()
        self.reference_numbers = VGroup()
        self.additional_lines = VGroup()
        if self.num_pentagrams == 0 and self.clefs != None:
            self.num_pentagrams = len(self.clefs)
        if self.num_pentagrams == 0 and self.clefs == None:
            self.num_pentagrams = 1
            self.clefs = ["g_clef"]
        self.set_pentagrams()
        if self.clefs != None:
            self.set_clefs()
        if self.num_pentagrams == 2 and self.clefs == None:
            self.clefs = ["g_clef","f_clef"]
            self.set_clefs()
        if self.show_reference:
            self.set_reference_system()
        self.add(self.pentagrams,self.clefs_group,self.reference_numbers,self.additional_lines)

    def set_pentagrams(self):
        for _ in range(self.num_pentagrams):
            pentagram = self.pentagram.copy()
            self.pentagrams.add(pentagram)
            self.reference_lines.add(pentagram[self.reference])
        self.pentagrams.arrange(**self.arrange_config)


    def set_clefs(self):
        count = 0
        try:
            for c in self.clefs:
                if c == "c_clef":
                    clef = self.c_clef.copy()
                    clef.set_height(self.height)
                    clef.next_to(self.pentagrams[count].get_left(),RIGHT,buff=self.left_buff)
                    self.clefs_group.add(clef)
                elif c == "g_clef":
                    clef = self.g_clef.copy()
                    clef.set_height(self.height / ALPHA_HEIGHT_G_CLEF)
                    clef.next_to(self.pentagrams[count].get_left(),RIGHT,buff=self.left_buff)
                    clef.shift(DOWN*(self.height/ALPHA_DOWN_G_CLEF))
                    self.clefs_group.add(clef)
                elif c == "f_clef":
                    clef = self.f_clef.copy()
                    clef.set_height(self.height / ALPHA_HEIGHT_F_CLEF)
                    clef.next_to(self.pentagrams[count].get_left(),RIGHT,buff=self.left_buff)
                    clef.shift(DOWN*(self.height/ALPHA_DOWN_F_CLEF))
                    self.clefs_group.add(clef)
                count += 1
        except:
            print(ERROR_NUMBER_CLEFS)

    def get_space_between_lines(self):
        return abs(self.pentagram[1].get_y()-self.pentagram[2].get_y())

    def get_proportion_line(self,proportion,reference_line):
        return self.reference_lines[reference_line].point_from_proportion(proportion)

    def get_space_note(self,position):
        return self.get_space_between_lines()*position/2

    def set_note_at(self,mob,note = 0,proportion = 0.2,reference_line = 0):
        mob.set_height(self.get_space_between_lines()*mob.fix_size_factor)
        mob.move_to(self.get_proportion_line(proportion,reference_line))
        mob.shift(UP*self.get_space_note(note))

    def set_reference_system(self):
        for pentagram in self.pentagrams:
            for n in range(5):
                number = FontText(f"{-n+2}")
                number.set_height(self.get_space_between_lines()*0.8)
                number.next_to(pentagram[n],LEFT,buff=0.1)
                self.reference_numbers.add(number)

    def add_additional_line(self,nivel=2,proportion=0.2,pentagram=0,fade=0):
        note_space = self.get_space_between_lines()
        if nivel == 0:
            raise ValueError("nivel must be != 0")
        length_line = note_space / ALPHA_PENTAGRAM_ADDITIONAL_LINE
        additional_line = Line(ORIGIN,RIGHT*length_line)
        reference_dot = Dot()
        reference_dot.next_to(self.pentagrams[pentagram],UP*sign(nivel),buff=0)
        x_coord = self.get_proportion_line(proportion,pentagram)[0]
        group_lines = VGroup()
        for i in range(abs(nivel)):
            line = additional_line.copy()
            line.next_to(self.pentagrams[pentagram],UP*sign(nivel),buff = (note_space * (i + 1)))
            line.move_to([x_coord,line.get_y(),0])
            group_lines.add(line)
        group_lines.fade(fade)
        self.additional_lines.add(group_lines)

    def add_key_signature(self,type="sharp",n=7,reference_line=0,buff=0.1):
        pre_key_signature = SVGMobject(f"music_symbols/key_signature_{type}")[7:]
        main_width = self.pentagram.get_height()
        pre_key_signature.set_width(main_width/ALPHAS[f"ks_{type}"]["width"])
        pre_key_signature.next_to(self.clefs_group[reference_line],RIGHT,buff=buff)
        pre_key_signature.match_y(self.pentagram)
        pre_key_signature.shift(UP*main_width/ALPHAS[f"ks_{type}"]["dy"])
        key_signature = pre_key_signature[:n]
        self.add(key_signature)



class Minim(VGroup):
    CONFIG = {
        "body_kwargs":{"stroke_width": 0, "stroke_opacity":1,"fill_opacity": 1},
        "stem_kwargs":{"stroke_width": 5.5, "stroke_opacity":1,"fill_opacity": 0},
        "add_stem":True,
        "stem_direction":DOWN,
        "type_note":"minim",
        "fix_size_factor":1,
    }
    def __init__(self,note=0,context=None,alteration=None,proportion=0.2,reference_line=0,**kwargs):
        super().__init__(**kwargs)
        self.set_type_note()
        self.add(self.body)
        self.set_custom_properties()
        self.note_parts = {"body":self.body}
        if context != None:
            self.context = context
            self.note = note
            self.context.set_note_at(self,note,proportion,reference_line)
        if self.add_stem:
            self.sign = self.stem_direction[1]
            self.stem = self.set_symbol("stem")
            self.add(self.stem)
            self.add_updater(get_update_relative_note_part(self,"body","stem"))
        if alteration != None:
            self.add_alteration(alteration)
        else:
            self.alteration_name = None

    def alteration_updater(self,alteration):
        return get_update_relative_note_part(self,"body",alteration)

    def add_alteration(self,alteration):
        self.alteration_name = alteration
        self.alteration = self.set_symbol(alteration)
        self.add(self.alteration)
        self.add_updater(get_update_relative_note_part(self,"body",alteration))

    def set_type_note(self):
        if self.type_note != "semibreve":
            index = 1
        else:
            index = 0
        self.body = SVGMobject(f"music_symbols/{self.type_note}",**self.body_kwargs)[index]

    def valid_context(self,context):
        if context != None:
            self.context = context

    def set_symbol(self,symbol):
        if symbol in ["stem"]:
            symbol_object = SVGMobject(f"music_symbols/{self.type_note}",**self.body_kwargs)[0]
        elif symbol in ["sharp","bemol","natural"]:
            symbol_object = SVGMobject(f"music_symbols/{symbol}",**self.body_kwargs)[0]
        main_width = self.body.get_width()
        symbol_object.set_width(main_width / ALPHAS[symbol]["width"])
        vector_lenght_stem = main_width/ ALPHAS[symbol]["vector_length"]
        vector_stem = vector_lenght_stem * ALPHAS[symbol]["unit_vector"]
        symbol_object.move_to(self.body.get_center()+vector_stem)
        self.note_parts[symbol] = symbol_object
        if symbol != "stem":
            self.note_parts["alteration"] = symbol_object
        return self.note_parts[symbol]

    def set_note(self,note,proportion=None,reference_line=0,context=None):
        self.valid_context(context)
        if proportion != None:
            try:
                alteration_width = abs(self.body.get_left() - self.alteration.get_left())
            except:
                alteration_width = 0
            x_coord = self.context.get_proportion_line(proportion,reference_line)[0] - alteration_width/2
        else:
            x_coord = self.get_x()
        x_distance = x_coord - self.get_x()
        y_distance = self.body.get_y()-self.context.reference_lines[reference_line].get_y()
        note_distance = self.context.get_space_between_lines()/2
        note_self = np.round(y_distance/note_distance)
        if note != None:
            self.shift(UP*self.context.get_space_between_lines()*(note-note_self)/2+x_distance*RIGHT)

    def get_note(self,reference_line=0):
        y_distance = abs(self.body.get_y()-self.context.reference_lines[reference_line].get_y())
        note_distance = self.context.get_space_between_lines()/2
        note_self = np.round(y_distance/note_distance)
        return note_self

    def resume_updaters(self):
        if self.alteration_name != None:
            self.add_updater(get_update_relative_note_part(self,"body",self.alteration_name))
        if self.add_stem:
            self.add_updater(get_update_relative_note_part(self,"body","stem"))


    def set_custom_properties(self):
        pass


class Chord(VGroup):
    def set_notes(self,notes,proportion=None,reference_line=0,context=None):
        if context == None:
            context = self[0].context
        for pre,pos in zip(self,notes):
            pre.set_note(pos,proportion,reference_line,context)

    def set_proportion(self,proportion,reference_line=0,context=None):
        if context == None:
            context = self[0].context
        for note in self:
            note.set_note(None,proportion,reference_line,context)

class Crotchet(Minim):
    CONFIG = {
        "type_note":"crotchet"
    }

class Semibreve(Minim):
    CONFIG = {
        "type_note":"semibreve",
        "add_stem":False,
    }