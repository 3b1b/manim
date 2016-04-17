from xml.dom import minidom
import warnings

from vectorized_mobject import VMobject
from topics.geometry import Rectangle, Circle
from helpers import *

SVG_SCALE_VALUE = 0.05

class SVGMobject(VMobject):
    CONFIG = {
        "stroke_width" : 0,
        "fill_opacity" : 1.0,
        "fill_color"   : WHITE, #TODO...
    }    
    def __init__(self, svg_file, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        doc = minidom.parse(self.svg_file)
        defs = doc.getElementsByTagName("defs")[0]
        g = doc.getElementsByTagName("g")[0]        
        ref_to_mob = self.get_ref_to_mobject_map(defs)
        for element in g.childNodes:
            if not isinstance(element, minidom.Element):
                continue
            mob = None
            if element.tagName == 'use':
                mob = self.use_to_mobject(element, ref_to_mob)
            elif element.tagName == 'rect':
                mob = self.rect_to_mobject(element)
            elif element.tagName == 'circle':
                mob = self.circle_to_mobject(element)
            else:
                warnings.warn("Unknown element type: " + element.tagName)
            if mob is not None:
                self.add(mob)
        doc.unlink()
        self.move_into_position()
        self.organize_submobjects()

    def use_to_mobject(self, use_element, ref_to_mob):
        #Remove initial "#" character
        ref = use_element.getAttribute("xlink:href")[1:]
        try:
            mob = ref_to_mob[ref]
        except:
            warnings.warn("%s not recognized"%ref)
            return
        if mob in self.submobjects:
            mob = VMobjectFromSVGPathstring(
                mob.get_original_path_string()
            )
        self.handle_transform(use_element, mob)
        self.handle_shift(use_element, mob)
        return mob

    def circle_to_mobject(self, circle_element):
        pass

    def rect_to_mobject(self, rect_element):
        if rect_element.hasAttribute("fill"):
            if Color(str(rect_element.getAttribute("fill"))) == Color(WHITE):
                return
        mob = Rectangle(
            width = float(rect_element.getAttribute("width")),
            height = float(rect_element.getAttribute("height")),
            stroke_width = 0,
            fill_color = WHITE,
            fill_opacity = 1.0
        )
        self.handle_shift(rect_element, mob)
        mob.shift(mob.get_center()-mob.get_corner(DOWN+LEFT))        
        return mob

    def handle_shift(self, element, mobject):
        x, y = 0, 0
        if element.hasAttribute('x'):
            x = float(element.getAttribute('x'))
        if element.hasAttribute('y'):
            #Flip y
            y = -float(element.getAttribute('y'))
        mobject.shift(x*RIGHT+y*UP)

    def handle_transform(self, element, mobject):
        pass

    def move_into_position(self):
        self.center()
        self.scale(SVG_SCALE_VALUE)
        self.init_colors()

    def organize_submobjects(self):
        self.submobjects.sort(
            lambda m1, m2 : int((m1.get_left()-m2.get_left())[0])
        )

    def get_ref_to_mobject_map(self, defs):
        ref_to_mob = {}
        for element in defs.childNodes:
            if not isinstance(element, minidom.Element):
                continue
            ref = element.getAttribute('id')
            if element.tagName == "path":
                path_string = element.getAttribute('d')
                mob = VMobjectFromSVGPathstring(path_string)
                ref_to_mob[ref] = mob
            if element.tagName == "use":
                ref_to_mob[ref] = self.use_to_mobject(element, ref_to_mob)
        return ref_to_mob


class VMobjectFromSVGPathstring(VMobject):
    def __init__(self, path_string, **kwargs):
        digest_locals(self)
        VMobject.__init__(self, **kwargs)

    def get_path_commands(self):
        return [
            "M", #moveto
            "L", #lineto
            "H", #horizontal lineto
            "V", #vertical lineto
            "C", #curveto
            "S", #smooth curveto
            "Q", #quadratic Bezier curve
            "T", #smooth quadratic Bezier curveto
            "A", #elliptical Arc
            "Z", #closepath
        ]

    def generate_points(self):
        pattern = "[%s]"%("".join(self.get_path_commands()))
        pairs = zip(
            re.findall(pattern, self.path_string),
            re.split(pattern, self.path_string)[1:]
        )
        #Which mobject should new points be added to
        self.growing_path = self
        for command, coord_string in pairs:
            self.handle_command(command, coord_string)
        #people treat y-coordinate differently
        self.rotate(np.pi, RIGHT)

    def handle_command(self, command, coord_string):
        #new_points are the points that will be added to the curr_points
        #list. This variable may get modified in the conditionals below.
        points = self.growing_path.points
        new_points = self.string_to_points(coord_string)
        if command == "M": #moveto
            if len(points) > 0:
                self.growing_path = self.add_subpath(new_points)
            else:
                self.growing_path.start_at(new_points[0])
            return
        elif command in ["L", "H", "V"]: #lineto
            if command == "H":
                new_points[0,1] = points[-1,1]
            elif command == "V":
                new_points[0,1] = new_points[0,0]
                new_points[0,0] = points[-1,0]
            new_points = new_points[[0, 0, 0]]
        elif command == "C": #curveto
            pass #Yay! No action required
        elif command in ["S", "T"]: #smooth curveto
            handle1 = points[-1]+(points[-1]-points[-2])
            new_points = np.append([handle1], new_points, axis = 0)
        if command in ["Q", "T"]: #quadratic Bezier curve
            #TODO, this is a suboptimal approximation
            new_points = np.append([new_points[0]], new_points, axis = 0)
        elif command == "A": #elliptical Arc
            raise Exception("Not implemented")
        elif command == "Z": #closepath
            if not is_closed(points):
                #Both handles and new anchor are the start
                new_points = points[[0, 0, 0]]
        self.growing_path.add_control_points(new_points)

    def string_to_points(self, coord_string):
        numbers = [
            float(s)
            for s in coord_string.split(" ")
            if s != ""
        ]
        if len(numbers)%2 == 1:
            numbers.append(0)
        num_points = len(numbers)/2
        result = np.zeros((num_points, self.dim))
        result[:,:2] = np.array(numbers).reshape((num_points, 2))
        return result

    def get_original_path_string(self):
        return self.path_string

