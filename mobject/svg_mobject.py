from xml.dom import minidom
import warnings

from vectorized_mobject import VMobject
from topics.geometry import Rectangle, Circle
from helpers import *

class SVGMobject(VMobject):
    CONFIG = {
        "initial_scale_val" : 1,
        "should_center" : True,
    }
    def __init__(self, svg_file, **kwargs):
        digest_config(self, kwargs, locals())
        self.ensure_valid_file()
        VMobject.__init__(self, **kwargs)
        self.move_into_position()

    def ensure_valid_file(self):
        possible_paths = [
            self.svg_file,
            os.path.join(IMAGE_DIR, self.svg_file),
            os.path.join(IMAGE_DIR, self.svg_file + ".svg"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                self.svg_file = path
                return
        raise IOError("No file matching %s in image directory"%self.svg_file)

    def generate_points(self):
        doc = minidom.parse(self.svg_file)
        self.ref_to_element = {}
        for svg in doc.getElementsByTagName("svg"):
            self.add(*self.get_mobjects_from(svg))
        doc.unlink()

    def get_mobjects_from(self, element):
        result = []
        if not isinstance(element, minidom.Element):
            return result
        if element.tagName == 'defs':
            self.update_ref_to_element(element)
        elif element.tagName == 'style':
            pass #TODO, handle style
        elif element.tagName in ['g', 'svg']:
            result += it.chain(*[
                self.get_mobjects_from(child)
                for child in element.childNodes
            ])
        elif element.tagName == 'path':
            result.append(self.path_string_to_mobject(
                element.getAttribute('d')
            ))
        elif element.tagName == 'use':
            result += self.use_to_mobjects(element)
        elif element.tagName == 'rect':
            result.append(self.rect_to_mobject(element))
        elif element.tagName == 'circle':
            result.append(self.circle_to_mobject(element))
        else:
            warnings.warn("Unknown element type: " + element.tagName)
        result = filter(lambda m : m is not None, result)
        self.handle_transforms(element, VMobject(*result))
        return result

    def g_to_mobjects(self, g_element):
        mob = VMobject(*self.get_mobjects_from(g_element))
        self.handle_transforms(g_element, mob)
        return mob.submobjects

    def path_string_to_mobject(self, path_string):
        return VMobjectFromSVGPathstring(path_string)

    def use_to_mobjects(self, use_element):
        #Remove initial "#" character
        ref = use_element.getAttribute("xlink:href")[1:]
        if ref not in self.ref_to_element:
            warnings.warn("%s not recognized"%ref)
            return VMobject()
        return self.get_mobjects_from(
            self.ref_to_element[ref]
        )

    # <circle class="st1" cx="143.8" cy="268" r="22.6"/>

    def circle_to_mobject(self, circle_element):
        x, y, r = [
            float(circle_element.getAttribute(key))
            if circle_element.hasAttribute(key)
            else 0.0
            for key in "cx", "cy", "r"
        ]
        return Circle(radius = r).shift(x*RIGHT+y*DOWN)

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
        mob.shift(mob.get_center()-mob.get_corner(UP+LEFT))        
        return mob

    def handle_transforms(self, element, mobject):
        x, y = 0, 0
        try:
            x = float(element.getAttribute('x'))
            #Flip y
            y = -float(element.getAttribute('y'))
        except:
            pass
        mobject.shift(x*RIGHT+y*UP)
        #TODO, transforms

    def update_ref_to_element(self, defs):
        new_refs = dict([
            (element.getAttribute('id'), element)
            for element in defs.childNodes
            if isinstance(element, minidom.Element) and element.hasAttribute('id')
        ])
        self.ref_to_element.update(new_refs)

    def move_into_position(self):
        if self.should_center:
            self.center()
        self.scale_in_place(self.initial_scale_val)




class VMobjectFromSVGPathstring(VMobject):
    def __init__(self, path_string, **kwargs):
        digest_locals(self)
        VMobject.__init__(self, **kwargs)

    def get_path_commands(self):
        result = [
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
        result += map(lambda s : s.lower(), result)
        return result

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
        isLower = command.islower()
        command = command.upper()
        #new_points are the points that will be added to the curr_points
        #list. This variable may get modified in the conditionals below.
        points = self.growing_path.points
        new_points = self.string_to_points(coord_string)
        if isLower:
            new_points += points[-1]
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
            # self.mark_paths_closed = True
        self.growing_path.add_control_points(new_points)

    def string_to_points(self, coord_string):
        coord_string = coord_string.replace("-",",-")
        numbers = [
            float(s)
            for s in re.split("[ ,]", coord_string)
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

