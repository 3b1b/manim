from manimlib.imports import *            

class PianoTest(Scene):
    CONFIG = {
    }
    def construct(self):
        keyboard = Keyboard()
        keyboard.to_edge(DOWN)
        self.add(keyboard)
        self.add_foreground_mobject(keyboard.black_keys)
        self.play(
            LaggedStartMap(FadeIn,keyboard,submobject_mode="lagged_start")
            )
        chord = keyboard.get_chord(0,"D","A","Cs","E")
        self.play(
            chord.set_color,RED
            )

        pentagram = Pentagram(clefs="gf",pentagram_config={"stroke_width":1},bars=[12,14])
        pentagram.add_key_signature("sharp",n=2)
        pentagram.add_tempo(proportion=3/20)
        pentagram.to_edge(UP,buff=1.5)
        chord = ChordMobject(
                    Minim(0,pentagram,"bemol",alteration_buff=0.2,proportion=5/20),
                    Minim(3,pentagram,"sharp",stem_direction=UP,reference_line=1,proportion=5/20)
                )

        note1_1 = Crotchet(2,pentagram,reference_line=0)
        note1_2 = Crotchet(0,pentagram,reference_line=0,alteration="bemol",proportion=0.4)
        note2_1 = Crotchet(2,pentagram,reference_line=1,alteration="natural")
        note2_2 = Crotchet(0,pentagram,reference_line=1,proportion=0.4)
        self.play(Write(pentagram))
        pentagram.add_ticks()
        self.add(pentagram.ticks,note1_1,note2_1)

        self.play(
            chord.set_notes,[-2,0],6/20,
            TransformFromCopy(note1_1,note1_2.principal),
            FadeIn(note1_2.alteration),
            TransformFromCopy(note2_1.principal,note2_2),
            )
        self.play(
            note1_2.set_note,4,
            note2_2.set_note,4,
            )
        vi = VerticalInterval(note1_2,note2_2,"2+")
        hv = HorizontalInterval(note1_1,note1_2,"5\\rm J")
        self.play(ShowInterval(vi),ShowInterval(hv))
        self.wait()


class MusicTest2(Scene):
    def construct(self):
        pentagram = Pentagram(height=1)
        pentagram.add_key_signature("sharp",2)
        chord = ChordMobject(
                    Minim(0,pentagram,"bemol"),
                    Minim(3,pentagram,"sharp",stem_direction=UP)
                )
        chord.set_proportion(0.3)
        self.add(pentagram,chord)
        self.play(chord[0].alteration.set_color,RED)
        self.wait()
        self.play(
            chord.set_notes,[-2,0],0.4,
            chord.set_color,RED
            )
        self.play(
            chord.set_notes,[-1,4],0.6,
            chord.set_color,ORANGE
            )
        self.play(
            chord.set_notes,[1,1],0.8,
            chord.set_color,TEAL
            )
        self.wait(2)

class MusicNumbers(Scene):
    def construct(self):
        self.bemol = MusicTeX(r"""
        \hsize=120mm
        \parindent 2pt
        \nostartrule
        \NOTes\qu{_e}\en
        """,stroke_width=0,stroke_opacity=0)

class Ligadura(Scene):
    def construct(self):
        dot1 = Dot()
        dot2 = Dot().shift(UL*2)
        reference_line = Line(dot1.get_center(),dot2.get_center())
        reference_line.rotate(PI/2)
        normal_vector = reference_line.get_unit_vector()
        ligadura_kwargs = {"stroke_width":0,"fill_opacity":1}
        buff1 = 0.3
        buff2 = buff1*1.2
        ligadura = VMobject(**ligadura_kwargs)
        top1 = reference_line.get_center()+normal_vector*buff1
        top2 = reference_line.get_center()+normal_vector*buff2

        ligadura.set_points_smoothly([
            dot1.get_center(),
            top1,
            dot2.get_center(),
            top2,
            dot1.get_center()
            ])
        self.add(ligadura)

class MusicTest1(Scene):
    def construct(self):
        pentagram = Pentagram(height=0.8,clefs="gfc")
        pentagram.add_key_signature("sharp",2)
        pentagram.add_ticks(buff=0.7)
        pentagram.add_tempo(3,4,proportion=3.5/30)

        chord = Chord(
                [-4,0,4],context=pentagram,
                alterations=[None,"bemol","sharp"],
                stems_directions=[DOWN,UP,UP],
                reference_lines=[0,1,1],
                alterations_buff=[0,0.2,0.3]
            )
        note = Minim(2,pentagram,"sharp",0.7,stem_direction=UP)

        self.add(pentagram,chord,note,pentagram.ticks)

        self.play(
            chord.set_notes,[-2,0,3],0.4,[0,0,0],
            chord.set_color,RED
            )
        pentagram.add_chord_name(chord,"I")


        self.wait()


class FinalTestX(Scene):
    def construct(self):
        keyboard = Keyboard()
        keyboard.to_edge(DOWN)
        self.add(keyboard)
        self.add_foreground_mobject(keyboard.black_keys)
        self.play(
            LaggedStartMap(FadeIn,keyboard,submobject_mode="lagged_start")
            )
        keyboard_chord = VGroup(
                keyboard.get_chord(1,"C0","G0","E0","Cs0"),
                keyboard.get_chord(0,"F0","A1","F0","D0"),
                keyboard.get_chord(0,"G0","G1","D0","B0"),
                keyboard.get_chord(0,"C0","G1","E0","C0"),
            )
        #chord1 = keyboard.get_chord(1,"C0","G0","E0","C0")
        #chord2 = keyboard.get_chord(0,"F0","A1","F0","C0")
        #chord3 = keyboard.get_chord(0,"G0","G0","D0","B0")
        #chord4 = keyboard.get_chord(0,"C0","G1","E0","C0") filter(lambda x: abs(x.get_y()-keyboard.get_y())>0.2,[*keyboard_chord[0]])
        self.add_foreground_mobjects(*[key for key in is_black_key(keyboard,keyboard_chord[0])])
        self.play(FadeIn(keyboard_chord[0]))

        self.play(
            ReplacementTransform(keyboard_chord[0],keyboard_chord[1]),
            )
        self.add_foreground_mobject(keyboard.black_keys)
        keyboard_chord[0].fade(1)
        self.wait()
        self.play(
            ReplacementTransform(keyboard_chord[1],keyboard_chord[2]),
            )

        #pentagram = Pentagram(clefs="gf",pentagram_config={"stroke_width":1},bars=[12,14])
        #pentagram.add_key_signature("sharp",n=2)
        #pentagram.add_tempo(proportion=3/20)
        #pentagram.to_edge(UP,buff=1.5)
        #chord = ChordMobject(
        #            Minim(0,pentagram,"bemol",alteration_buff=0.2,proportion=5/20),
        #            Minim(3,pentagram,"sharp",stem_direction=UP,reference_line=1,proportion=5/20)
        #        )

        #note1_1 = Crotchet(2,pentagram,reference_line=0)
        #note1_2 = Crotchet(0,pentagram,reference_line=0,alteration="bemol",proportion=0.4)
        #note2_1 = Crotchet(2,pentagram,reference_line=1,alteration="natural")
        #note2_2 = Crotchet(0,pentagram,reference_line=1,proportion=0.4)
        #self.play(Write(pentagram))
        #pentagram.add_ticks()
        #self.add(pentagram.ticks,note1_1,note2_1)

        #self.play(
        #    chord.set_notes,[-2,0],6/20,
        #    TransformFromCopy(note1_1,note1_2.principal),
        #    FadeIn(note1_2.alteration),
        #    TransformFromCopy(note2_1.principal,note2_2),
        #    )
        #self.play(
        #    note1_2.set_note,4,
        #    note2_2.set_note,4,
        #    )
        #vi = VerticalInterval(note1_2,note2_2,"2+")
        #hv = HorizontalInterval(note1_1,note1_2,"5\\rm J")
        #self.play(ShowInterval(vi),ShowInterval(hv))
        self.wait()

class FinalTest(Scene):
    def construct(self):
        # Set the keyboard and pentagram
        keyboard = Keyboard()
        pentagram = Pentagram(height=1,width=keyboard.get_width(),clefs="gf",arrange_config={"buff":1.5})
        pentagram.add_tempo(4,proportion=3.5/30)
        pentagram.to_edge(UP,buff=0.3)
        keyboard.to_edge(DOWN,buff=0.3)
        # Send the black keys to front
        self.add(keyboard)
        self.add_foreground_mobject(keyboard.black_keys)
        # Show keyboard
        self.play(
            LaggedStart(*[GrowFromPoint(key,key.get_bottom())for key in keyboard]),
            run_time=2
            )
        # Set chords of the keyboard
        keyboard_chords = VGroup(
                keyboard.get_chord(1,"C0","G0","E0","C0"),
                keyboard.get_chord(0,"F0","A1","F0","C0"),
                keyboard.get_chord(0,"G0","G1","D0","B0"),
                keyboard.get_chord(0,"C0","G1","E0","C0"),
            )
        # chords kwargs of pentagram
        pentagram_chords_kwargs = {
            "context":pentagram,
            "stems_directions":[DOWN,UP,DOWN,UP],
            "reference_lines":[1,1,0,0],
            "note_type":"crotchet"
        }
        # pentagram chords config
        # [[notes],proportion in the pentagram]
        chord_progretions = [
            [[-1,3,-4,1],7/30],
            [[-5,4,-3,1],13/30],
            [[-4,3,-5,0],19/30],
            [[-8,3,-4,1],25/30],
        ]
        # pentagram chords
        pentagram_chords = VGroup(
                *[Chord(
                notes,proportion,
                **pentagram_chords_kwargs
                )for notes,proportion in chord_progretions],
            )
        # pentagram chords colors
        chord_colors = it.cycle(keyboard.chord_colors)
        for chord in pentagram_chords:
            for key in chord:
                key.set_color(next(chord_colors))

        self.play(
            *[LaggedStartMap(GrowFromCenter,line) for line in pentagram.pentagrams],
            Write(pentagram.clefs_group),
            FadeInFromDown(pentagram.tempo),
        )
        self.play(
            FadeIn(keyboard_chords[0]),
            Write(pentagram_chords[0])
            )
        self.wait()
        self.play_chord_progretion(keyboard_chords,pentagram_chords,1)
        self.play_chord_progretion(keyboard_chords,pentagram_chords,2)
        # Add aditional 2 lines to the last chord
        pentagram.add_additional_line(-2,25/30,1)
        self.bring_to_back(pentagram.additional_lines)
        self.play_chord_progretion(keyboard_chords,pentagram_chords,3,FadeIn(pentagram.additional_lines))
        self.wait()

    def play_chord_progretion(self,keyboard_chords,pentagram_chords,index,*anims,**kwargs):
        self.play(
            ReplacementTransform(keyboard_chords[index-1],keyboard_chords[index]),
            TransformFromCopy(pentagram_chords[index-1],pentagram_chords[index]),
            *anims,
            run_time=2.5,
            **kwargs
            )
        self.wait()