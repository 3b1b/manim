from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.geometry import Line
from manimlib.constants import *
class Table(VGroup):
#TODO : Add proper length checking to avoid smaller than useful vertical lines when dealing with TeX
# Use CONFIG instead of directly passing parameters to function?

    def get_table(tabledict:dict,buff_length=0.3,line_color=WHITE,text_color=WHITE):
        
        def flatten(inlist):
            outlist=[]
            for element in inlist:
                for sub_element in element:
                    outlist.append(sub_element)
            return outlist
        
        table=VGroup() #The table is a VGroup with all the fields, records and separators.
        
        fields=list(tabledict.keys()) #Since the data is recieved as a dict, the keys will be the fields

        cell_length=TexMobject(max(fields + flatten(tabledict.values()), key=len)).get_width()+2*buff_length #The length of a record/field of max length is the base cell size
        cell_height=TexMobject(max(fields + flatten(tabledict.values()), key=len)).get_height()+2*buff_length
       
        #The first position is set like so.
        field_position=[ (cell_length-TexMobject(fields[0]).get_width())/2 + TexMobject(fields[0]).get_width()/2, 0,0 ] #The initial position of the first field. This is 
        #NOTE: Coordinates of TexMobjects in Manim are taken from centre, not top-right. Adjustments have been made.
        
        total_table_width=(cell_length-TexMobject(fields[0]).get_width())/2

        total_table_height=cell_height*(len(tabledict[max(tabledict.keys(),key=len)])+1)

        for n in range(len(fields)):
            
            field=TexMobject(fields[n])
            
            field_length=field.get_width() #This is the length that the actual field name will take up on-screen
            
            if n+1<len(fields): #This gets the nxt field if it exists and chooses an empty TexMobject if it doesn't
                next_field=TexMobject(fields[n+1])
            else:
                next_field=TexMobject("")
            
            next_field_length=next_field.get_width() #Gets the next fields length
            
            
            field.move_to(field_position)
            
            
            space_to_right_of_field=(cell_length-field_length)/2
            
            space_to_left_of_next_field=(cell_length-next_field_length)/2
            
            space_to_leave= space_to_right_of_field + space_to_left_of_next_field + next_field_length/2
            
            #next_field_length/2 is added to account for the fact that coordinates are taken from centre and not left edges.

            total_table_width+=field_length+space_to_leave/2
            table.add(field)
            field_position=field.get_right()+(space_to_leave,0,0)
        
        for keynum in range(len(tabledict.keys())):
            key=list(tabledict.keys())[keynum] #gets the actual key
            recordlist=tabledict[key] #selects the list with the records for 
            
            if recordlist!=[]:

                record_position=[table[keynum].get_center()[0], -((cell_height-TexMobject(fields[keynum]).get_height())/2 + TexMobject(fields[keynum]).get_height()/2 + cell_height ),0]
                
                #the record position is set to be the [center of the field it belongs to, buffer space above the record + centered height of the record, 0  ]

                for recordnum in range(len(recordlist)):    # for each record for
                    record=TexMobject(recordlist[recordnum]) # the selected field
                 
                    
                    if recordnum+1<len(recordlist): #This gets the nxt record if it exists and chooses an empty TexMobject if it doesn't
                        next_record=TexMobject(recordlist[recordnum+1])
                    else:
                        next_record=TexMobject("")
                

                    record.move_to(record_position)
                    record_position=record.get_center()+(0,-cell_height,0)
                    table.add(record)
            else:
                pass
                
        line_hor=Line(start=(0,-2*cell_height/3,0),end=(total_table_width,-2*cell_height/3,0),color=line_color)
        table.add(line_hor)
        
        for l in range (len(fields)-1):
            line=Line( start=(table[l].get_center()+ (cell_length/2,cell_height/2,0)), end =(table[l].get_center()+ (cell_length/2,-total_table_height,0)))
            table.add(line)

        return table
