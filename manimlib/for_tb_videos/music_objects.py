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
        'dy': 4,
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
        "bars":[],
        "partitions":20,
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
        self.bars_group = VGroup()
        self.key_signatures = VGroup()
        self.tempo = VGroup()
        if self.num_pentagrams == 0 and self.clefs != None:
            self.num_pentagrams = len(self.clefs)
        if self.num_pentagrams == 0 and self.clefs == None:
            self.num_pentagrams = 1
            self.clefs = "g"
        self.set_pentagrams()
        if self.clefs != None:
            self.set_clefs()
        if self.num_pentagrams == 2 and self.clefs == None:
            self.clefs = "gf"
            self.set_clefs()
        if self.show_reference:
            self.set_reference_system()
        for bar in self.bars:
            self.add_bar(bar)
        self.add(self.pentagrams,self.clefs_group,self.reference_numbers,self.additional_lines,self.bars_group,self.key_signatures,self.tempo)

    def set_pentagrams(self):
        for _ in range(self.num_pentagrams):
            pentagram = self.pentagram.copy()
            self.pentagrams.add(pentagram)
            self.reference_lines.add(pentagram[self.reference])
        self.pentagrams.arrange(**self.arrange_config)

    def add_bar(self,bar):
        reference_up = self.pentagrams[0][0]
        reference_down = self.pentagrams[-1][-1]

        proportion = 1 / self.partitions
        line = Line(
            reference_up.point_from_proportion(proportion * bar),
            reference_down.point_from_proportion(proportion * bar),
            **self.pentagram_config
            )
        self.bars_group.add(line)


    def set_clefs(self):
        count = 0
        try:
            for c in self.clefs:
                if c == "c":
                    clef = self.c_clef.copy()
                    clef.set_height(self.height)
                    clef.next_to(self.pentagrams[count].get_left(),RIGHT,buff=self.left_buff)
                    self.clefs_group.add(clef)
                elif c == "g":
                    clef = self.g_clef.copy()
                    clef.set_height(self.height / ALPHA_HEIGHT_G_CLEF)
                    clef.next_to(self.pentagrams[count].get_left(),RIGHT,buff=self.left_buff)
                    clef.shift(DOWN*(self.height/ALPHA_DOWN_G_CLEF))
                    self.clefs_group.add(clef)
                elif c == "f":
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
        for pentagram,clef in zip(self.pentagrams,self.clefs_group):
            pre_key_signature = SVGMobject(f"music_symbols/key_signature_{type}")[7:]
            main_width = self.pentagram.get_height()
            pre_key_signature.set_width(main_width/ALPHAS[f"ks_{type}"]["width"])
            pre_key_signature.next_to(clef,RIGHT,buff=buff)
            pre_key_signature.match_y(pentagram)
            pre_key_signature.shift(UP*main_width/ALPHAS[f"ks_{type}"]["dy"])
            if clef.get_height() < self.pentagrams[0].get_height():
                pre_key_signature.shift(DOWN*self.get_space_between_lines())
            key_signature = pre_key_signature[:n]
            self.key_signatures.add(key_signature)
        for i in range(len(self.key_signatures)):
            if i <= len(self.key_signatures) - 1 and i > 0:
                ks_pos = self.key_signatures[i]
                ks_pre = self.key_signatures[i-1]
                if ks_pos.get_x() > ks_pre.get_x():
                    ks_pre.match_x(ks_pos)



    def add_reference_of_proportion(self,number_width=0.2,buff=0.5,tick_height=0.4,index=0,direction=DOWN):
        partition = 1 / self.partitions
        reference_line = Line(
                self.pentagrams.get_corner(direction+LEFT),
                self.pentagrams.get_corner(direction+RIGHT),
            )
        reference_line.shift(direction*buff)
        reference_group = VGroup(reference_line)

        tick = Line(ORIGIN,UP*tick_height)
        for i in range(self.partitions+1):
            tick_position = reference_line.point_from_proportion(i * partition)
            new_tick = tick.move_to(tick_position).copy()
            number = FontText(f"{i}").set_height(number_width)
            number.next_to(new_tick,DOWN,buff=0.1)
            reference_group.add(new_tick,number)

        self.ticks = reference_group

    def add_tempo(self,num=4,den=None,proportion=0.2):
        if den == None:
            den = num
        num_mob = TexMobject("\\mathbf{%s}"%num)
        den_mob = TexMobject("\\mathbf{%s}"%den)
        tempo = VGroup(num_mob,den_mob)
        tempo.arrange(DOWN,buff=0)
        tempo.match_height(self.pentagrams[0])
        for pentagram in self.pentagrams:
            position = pentagram[2].point_from_proportion(proportion)
            tempo_copy = tempo.copy()
            tempo_copy.move_to(position)
            self.tempo.add(tempo_copy)


class Minim(VGroup):
    CONFIG = {
        "body_kwargs":{"stroke_width": 0, "stroke_opacity":1,"fill_opacity": 1},
        "stem_kwargs":{"stroke_width": 5.5, "stroke_opacity":1,"fill_opacity": 0},
        "add_stem":True,
        "stem_direction":DOWN,
        "type_note":"minim",
        "fix_size_factor":1,
        "alteration_buff":0,
    }
    def __init__(self,note=0,context=None,alteration=None,proportion=0.2,reference_line=0,**kwargs):
        super().__init__(**kwargs)
        self.set_type_note()
        self.add(self.body)
        self.set_custom_properties()
        self.reference_line = reference_line
        self.note_parts = {"body":self.body}
        self.principal = VGroup(self.body)
        if context != None:
            self.context = context
            self.note = note
            self.context.set_note_at(self,note,proportion,reference_line)
        if self.add_stem:
            self.sign = self.stem_direction[1]
            self.stem = self.set_symbol("stem")
            self.principal.add(self.stem)
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
        if symbol != "stem":
            symbol_object.shift(RIGHT*self.alteration_buff)
            self.note_parts["alteration"] = symbol_object
        self.note_parts[symbol] = symbol_object
        return self.note_parts[symbol]

    def set_note(self,note,proportion=None,reference_line=None,context=None):
        self.valid_context(context)
        if proportion != None:
            try:
                alteration_width = abs(self.body.get_left() - self.alteration.get_left())
            except:
                alteration_width = 0
            x_coord = self.context.get_proportion_line(proportion,reference_line)[0] - alteration_width/2
        else:
            x_coord = self.get_x()
        if reference_line == None:
            reference_line = self.reference_line
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


class ChordMobject(VGroup):
    def set_notes(self,notes,proportion=None,reference_lines=None,context=None):
        if context == None:
            context = self[0].context
        if reference_lines != None:
            for pre,pos,rl in zip(self,notes,reference_lines):
                pre.set_note(pos,proportion,rl,context)
        else:
            for pre,pos in zip(self,notes):
                pre.set_note(pos,proportion,pre.reference_line,context)


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

class WhiteKeySVG(SVGMobject):
    CONFIG={
        "file_name":"music_symbols/tecla_blanca"
    }

class BlackKeySVG(SVGMobject):
    CONFIG={
        "file_name":"music_symbols/tecla_negra"
    }

KEY_DICTIONARY = {"C":0,"Cs":1,"Db":1,"D":2,"Ds":3,"Eb":3,"E":4,"F":5,"Fs":6,"Gb":6,"G":7,"Gs":8,"Ab":8,"A":9,"As":10,"Bb":10,"B":11}

KEY_PROGRETION = ["C","Cs","Db","D","Ds","Eb","E","F","Fs","Gb","G","Gs","Ab","A","As","Bb","B"]
KEY_PROGRETION_IT = it.cycle(KEY_PROGRETION)

KEYBOARD_PROPORTION = 1.32

class Keyboard(VGroup):
    CONFIG={
        "prop": 1.32,
        "position": ORIGIN,
        "keyboard_kwargs": {
            "stroke_width": 1,
            "stroke_opacity":1,
            "stroke_color":BLACK
        },
        "origin_C": ORIGIN,
    }
    def __init__(self,octaves=4,key_type="keyboard",**kwargs):
        super().__init__(**kwargs)
        self.octaves = octaves
        self.key_type = key_type
        if key_type == "keyboard":
            keyboard = self.get_keyboard(octaves,**self.keyboard_kwargs)
            self.add(*keyboard)
            self.set_keyboard_keys()
            self.move_to(self.origin_C)
        self.number_keys = self.get_number_keys()
        self.black_keys = self.get_black_keys()
        self.initial_octaves = self.get_initial_octaves()

    def get_keyboard(self,octaves=4,**keyboard_kwargs):
        keyboard = VGroup()
        octave = self.get_octave(**keyboard_kwargs)
        for _ in range(octaves):
            if len(keyboard) == 0:
                keyboard.add(*octave.copy())
            else:
                pre_keyboard = octave.copy()
                pre_keyboard.next_to(keyboard,RIGHT,buff=0)
                keyboard.add(*pre_keyboard)

        keyboard.move_to(ORIGIN)
        return keyboard

    def get_black_keys(self):
        black_keys = VGroup()
        for key in self:
            if key.get_y() > self.get_y():
                black_keys.add(key)
        return black_keys

    def get_octave(self,**keyboard_kwargs):
        white_keys = VGroup(*[WhiteKeySVG(**keyboard_kwargs) for _ in range(7)]).arrange(RIGHT,buff=0)
        black_keys = VGroup()
        for i in [0,1,3,4,5]:
            black_key = BlackKeySVG().set_color(BLACK)
            black_key.scale(KEYBOARD_PROPORTION/white_keys[i].get_height())
            black_key.next_to(white_keys[i].get_top(),DOWN,buff=0)
            black_key.set_x(white_keys[i].get_right()[0])
            black_keys.add(black_key)
        octave = VGroup()
        sequence = ["D","D","N","D","D","D","N"]
        b = 0;w = 0
        for seq in sequence:
            if seq == "D":
                octave.add(white_keys[w])
                octave.add(black_keys[b])
                b += 1
            elif seq == "N":
                octave.add(white_keys[w])
            w += 1
        return octave

    def get_number_keys(self):
        numbers = VGroup()
        for i in range(len(self)):
            number = FontText(f"{i}")
            number.set_height(0.2)
            number.next_to(self[i],DOWN,buff=0.1)
            numbers.add(number)
        return numbers

    def set_piano_keys(self):
        octavas=7
        self.k = {}
        self.k["C"]  = [3+12*n for n in range(octavas)]
        self.k["Cs"] = [3+1+12*n for n in range(octavas)]
        self.k["Db"] = [3+1+12*n for n in range(octavas)]
        self.k["D"]  = [3+2+12*n for n in range(octavas)]
        self.k["Ds"] = [3+3+12*n for n in range(octavas)]
        self.k["Eb"] = [3+3+12*n for n in range(octavas)]
        self.k["E"]  = [3+4+12*n for n in range(octavas)]
        self.k["F"]  = [3+5+12*n for n in range(octavas)]
        self.k["Fs"] = [3+6+12*n for n in range(octavas)]
        self.k["Gb"] = [3+6+12*n for n in range(octavas)]
        self.k["G"]  = [3+7+12*n for n in range(octavas)]
        self.k["Gs"] = [3+8+12*n for n in range(octavas)]
        self.k["Ab"] = [3+8+12*n for n in range(octavas)]
        self.k["A"]  = [0,*[3+9+12*n for n in range(octavas)]]
        self.k["As"] = [1,*[3+10+12*n for n in range(octavas)]]
        self.k["Bb"] = [1,*[3+10+12*n for n in range(octavas)]]
        self.k["B"]  = [2,*[3+11+12*n for n in range(octavas)]]

    def set_keyboard_keys(self):
        octavas = self.octaves
        self.k = {}
        self.key = {}
        keys = KEY_PROGRETION
        count = 0
        for key,i in zip(keys,range(len(keys))):
            if key[-1] == "b":
                self.k[key] = self.k[f"{keys[i-1][0]}s"]
            else:
                self.k[key]  = [count+12*n for n in range(octavas)]
            if i < len(keys)-1 and len(keys[i])+len(keys[i+1])<4:
                count += 1

        for key in keys:
            self.key[key] = VGroup(*[self[self.k[key][k]] for k in range(octavas)])

    def get_initial_octaves(self):
        numbers = VGroup()
        for i in range(int(len(self)/12)):
            number = FontText(f"{i}")
            number.set_height(0.2)
            number.next_to(self[i*12],DOWN,buff=0.1)
            numbers.add(number)
        numbers.set_color(RED)
        return numbers

    def get_chord(self,reference=1,*keys,**remark_kwargs):
        reference_item = self.get_key_octave(keys[0],reference)
        reference_octave = self.get_octave_by_item(reference_item)
        chord = VGroup()
        total_keys = len(keys)
        for key,i in zip(keys,range(total_keys)):
            mob_key = self.key[key][reference_octave]
            chord.add(mob_key)
            if i < total_keys-1:
                if KEY_DICTIONARY[keys[i]] > KEY_DICTIONARY[keys[i+1]]:
                    reference_octave +=1
        return chord
            

    def get_key_octave(self,key,reference):
        return self.k[key][reference]
        #print(item_key)

    def get_octave_by_item(self,item):
        return int(item/12)