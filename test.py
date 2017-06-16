from mobject.tex_mobject import TexMobject
from mobject import Mobject
from mobject.image_mobject import ImageMobject
from mobject.vectorized_mobject import VMobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from topics.numerals import *
from scene import Scene
from camera import Camera
from mobject.svg_mobject import *
from mobject.tex_mobject import *
from mobject.vectorized_mobject import *

from topics.matrix import *
from topics.vector_space_scene import *

import helpers
#import myhelpers
import math
import decimal


def curvy_squish(point):
    x, y, z = point
    return (x+np.cos(y))*RIGHT + (y+np.sin(x))*UP

def get_orthonormal_eigenbasis(matrix):
    """ given a matrix, returns a list of eigenvectors
        that form an orthogonal basis of the space
        the matrix lives in
    """
    eigenvals, eigenvecs = np.linalg.eig(matrix) #get eigenvalues and eigenvalues of the matrix
    eigenvals = clean(eigenvals) #remove weird floats
    print(eigenvals)
    eigenvecs = clean1(eigenvecs) #^^
    #transpose the matrix of eigenvectors so each element is an eigenvector
    eigenvecs = [[j[i] for j in eigenvecs] for i in range(len(eigenvecs))]
    repeat_dict = repeats(eigenvals) #get dictionary of repeated eigenvalues/locations or False
    if not repeat_dict: #if no repeated eigenvalues, eigenvectors form an orthogonal basis
        return eigenvecs
    else:
        for key in repeat_dict: #for each repeated eigenvalue
            evecs = []
            for i in repeat_dict[key]: #get list of associated eigenvectors
                evecs += [eigenvecs[i]]
            if not repeat_vector(evecs): #need a different way to evaluate if contains parallel vectors
                for i in range(len(evecs)): #gram-schmidt process (orthogonalizes vectors)
                    for j in range(i-1):
                        scalar = (np.dot(evecs[j], evecs[i])/np.dot(evecs[j], evecs[j])) # (j dot i)/(j dot j)
                        evecs[i] -= np.multiply(scalar, evecs[j]) #subtract component in direction of evecs[j]
                    evecs[i] = np.multiply(1/np.linalg.norm(evecs[i]), evecs[i]).tolist() #normalize
                for i in range(len(repeat_dict[key])):
                    eigenvecs[repeat_dict[key][i]] = evecs[i] # replace in list of eigenvectors
            else: #there is a repeated vector in the list of associated eigenvectors
                return False #the eigenvalue is incomplete and thus the matrix is deficient
        return eigenvecs #all eigenvalues are complete, so we can return list of orthogonalized eigenvectors


def repeat_vector(L):
    """ returns True if L, a list of lists,
        contains two of the same list, and
        False otherwise
    """
    for i in range(len(L)):
        if L[i] in L[:i]: #if there exists earlier in the list another identical vector
            return True
        elif np.multiply(-1, L[i]).tolist() in L[:i]: #or an antiparallel vector
            return True
    return False

def repeats(L):
    """ returns the elements of L that
        are repeated twice (or more);
        returns False otherwise
    """
    out = {}
    for i in range(len(L)):
        #if somewhere else in the list there exists an identical element
        if (L[i] in L[:i]) or (L[i] in L[(i+1):]):
            if L[i] not in out: #that is not in our dictionary
                out[L[i]] = [i] #add its location
            else: #that is in our dictionary
                out[L[i]] += [i] #add its location
    if out == {}: #if we have no repeated values
        return False
    else: #otherwise return the dictionary of locations of repeats
        return out

def clean(L):
    """ removes floating point error smaller than 10^-6
    """
    out = []
    for i in range(len(L)):
        a = round(decimal.Decimal(L[i].real),6) #find the real part that is probably not a float error
        b = round(decimal.Decimal(L[i].imag),6) #same as above, but imaginary
        if b == 0: # if no imaginary part
            out += [a] #add real to output
        elif a == 0: #if no real part
            out += [b*1j] #add imaginary to output
        else: #add complex to output
            out += [a+b*1j]
    return out

def clean1(L):
    """ clean(L) for 2d lists
    """
    out = []
    for i in range(len(L)):
        out += [clean(L[i])] #clean elements (that are lists) individually
    return out


def get_det_text(matrix, determinant = None, background_rect = True):
    parens = TexMobject(["(", ")"])
    parens.scale(2)
    parens.stretch_to_fit_height(matrix.get_height())
    l_paren, r_paren = parens.split()
    l_paren.next_to(matrix, LEFT, buff = 0.1)
    r_paren.next_to(matrix, RIGHT, buff = 0.1)
    det = TextMobject("det").next_to(l_paren, LEFT, buff = 0.1)
    if background_rect:
        det.add_background_rectangle()
    det_text = VMobject(det, l_paren, r_paren)
    if determinant is not None:
        eq = TexMobject("=")
        eq.next_to(r_paren, RIGHT, buff = 0.1)
        result = TexMobject(str(determinant))
        result.next_to(eq, RIGHT, buff = 0.2)
        det_text.add(eq, result)
    return det_text

class Test(VectorScene):
    def construct(self):
        self.setup()
        self.test()
        self.dither()

    def test(self):
        a_vector = Vector(np.array([1,1]))
        myhelpers.put_vector_at(a_vector, np.array([2,2,0]))
        self.add_vector(a_vector)
        self.dither()
        self.dither()
        another_vector = Vector(np.array([-2,2]))
        another_vector = myhelpers.put_vector_at(another_vector, np.array([-3,-1,0]))
        print(another_vector.points)
        self.add_vector(another_vector)

class Det2(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.add_unit_square()
        a, b, c, d = 3, 2, 3.5, 2
        self.dither()
        self.apply_transposed_matrix([[a, 0], [0, 1]])
        i_brace = Brace(self.i_hat, DOWN)
        width = TexMobject("a").scale(1.5)
        i_brace.put_at_tip(width)
        width.highlight(X_COLOR)
        width.add_background_rectangle()
        self.play(GrowFromCenter(i_brace), Write(width))
        self.dither()

        self.apply_transposed_matrix([[1, 0], [0, d]])
        side_brace = Brace(self.square, RIGHT)
        height = TexMobject("d").scale(1.5)
        side_brace.put_at_tip(height)
        height.highlight(Y_COLOR)
        height.add_background_rectangle()
        self.play(GrowFromCenter(side_brace), Write(height))
        self.dither()

        self.apply_transposed_matrix(
            [[1, 0], [float(b)/d, 1]],
            added_anims = [
                ApplyMethod(m.shift, b*RIGHT)
                for m in side_brace, height
            ]
        )
        self.dither()
        self.play(*map(FadeOut, [i_brace, side_brace, width, height]))
        matrix1 = np.dot(
            [[a, b], [c, d]],
            np.linalg.inv([[a, b], [0, d]])
        )
        matrix2 = np.dot(
            [[a, b], [-c, d]],
            np.linalg.inv([[a, b], [c, d]])
        )
        self.apply_transposed_matrix(matrix1.transpose(), path_arc = 0)
        self.dither()
        self.apply_transposed_matrix(matrix2.transpose(), path_arc = 0)
        self.dither()

a_mat, b_mat, c_mat, d_mat = -3,-1,1,2
class Det3(LinearTransformationScene):
    global a_mat
    global b_mat
    global c_mat
    global d_mat
    #shows geometric derivation of formula for determinant

    def construct(self):
        self.setup()
        self.add_unit_square()
        self.apply_transposed_matrix([[a_mat, b_mat], [c_mat, d_mat]], path_arc = 0, run_time = 0)
        self.add_braces()
        self.add_polygons()
        self.show_formula()
        self.dither()

    def get_matrix(self):
        matrix = Matrix([["a", "b"], ["c", "d"]])
        matrix.highlight_columns(X_COLOR, Y_COLOR)
        ma, mb, mc, md = matrix.get_entries().split()
        ma.shift(0.1*DOWN)
        mc.shift(0.7*mc.get_height()*DOWN)
        matrix.shift(2*DOWN+4*LEFT)
        return matrix

    def add_polygons(self):
        a = self.i_hat.get_end()[0]*RIGHT
        b = self.j_hat.get_end()[0]*RIGHT
        c = self.i_hat.get_end()[1]*UP
        d = self.j_hat.get_end()[1]*UP

        shapes_colors_and_tex = [
            (Polygon(ORIGIN, a, a+c), MAROON, "ac/2"),
            (Polygon(ORIGIN, d+b, d, d), TEAL, "\\dfrac{bd}{2}"),
            (Polygon(a+c, a+b+c, a+b+c, a+b+c+d), TEAL, "\\dfrac{bd}{2}"),
            (Polygon(b+d, a+b+c+d, b+c+d), MAROON, "ac/2"),
            (Polygon(a, a+b, a+b+c, a+c), PINK, "bc"),
            (Polygon(d, d+b, d+b+c, d+c), PINK, "bc"),
        ]
        if a_mat < 0 and b_mat < 0 and c_mat>0 and d_mat>0:
            shapes_colors_and_tex = [
                (Polygon(ORIGIN, d+b, b, b),TEAL, "\\dfrac{bd}{2}"),
                (Polygon(a+c, a+c+d, a+c+d, a+b+c+d), TEAL, "\\dfrac{bd}{2}"),
                (Polygon(a+d,a+d+b,a+d+b+c,a+c+d), PINK, "bc"),
                (Polygon(ORIGIN,b,b+c,c), PINK, "bc"),
                (Polygon(a+d+b, a+b+c+d, b+d), MAROON, "ac/2"),
                (Polygon(ORIGIN, c, a+c), MAROON, "ac/2"),
            ]
            print(a,b,c,d)
        everyone = VMobject()
        for shape, color, tex in shapes_colors_and_tex:
            shape.set_stroke(width = 0)
            shape.set_fill(color = color, opacity = 0.7)
            tex_mob = TexMobject(tex)
            tex_mob.scale(0.7)
            tex_mob.move_to(shape.get_center_of_mass())
            everyone.add(shape, tex_mob)
        self.play(FadeIn(
            everyone,
            submobject_mode = "lagged_start",
            run_time = 1
        ))

    def add_braces(self):
        a = self.i_hat.get_end()[0]*RIGHT
        b = self.j_hat.get_end()[0]*RIGHT
        c = self.i_hat.get_end()[1]*UP
        d = self.j_hat.get_end()[1]*UP

        quads = [
            (ORIGIN, a, DOWN, "a"),
            (a, a+b, DOWN, "b"),
            (a+b, a+b+c, RIGHT, "c"),
            (a+b+c, a+b+c+d, RIGHT, "d"),
            (a+b+c+d, b+c+d, UP, "a"),
            (b+c+d, d+c, UP, "b"),
            (d+c, d, LEFT, "c"),
            (d, ORIGIN, LEFT, "d"),
        ]

        if a_mat < 0:
            quads[2],quads[3],quads[6],quads[7] = [
                (a+b, a+b+c, LEFT,"c"),
                (a+b+c,a+b+c+d, LEFT, "d"),
                (d+c, d, RIGHT, "c"),
                (d, ORIGIN, RIGHT, "d")
            ]


        everyone = VMobject()
        for p1, p2, direction, char in quads:
            line = Line(p1, p2)
            brace = Brace(line, direction, buff = 0)
            text = brace.get_text(char)
            text.add_background_rectangle()
            if char in ["a", "c"]:
                text.highlight(X_COLOR)
            else:
                text.highlight(Y_COLOR)
            everyone.add(brace, text)
        self.play(Write(everyone), run_time = 1)


    def show_formula(self):
        matrix = self.get_matrix()
        det_text = get_det_text(matrix)
        f_str = "=(a+b)(c+d)-ac-bd-2bc=ad-bc"
        formula = TexMobject(f_str)

        formula.next_to(det_text, RIGHT)
        everyone = VMobject(det_text, matrix, formula)
        everyone.scale_to_fit_width(2*SPACE_WIDTH - 1)
        everyone.next_to(DOWN, DOWN)
        background_rect = BackgroundRectangle(everyone)
        self.play(
            ShowCreation(background_rect),
            Write(everyone)
        )
        self.dither()



global_v_coords = [2,1]
global_transposed_matrix = np.array([[3,2], [-3,-2]])
global_result = np.dot(np.array(global_v_coords), np.array(global_transposed_matrix))
class Det1(LinearTransformationScene):
    #shows transformation by a matrix with determinant zero
    global global_v_coords
    global global_transposed_matrix
    CONFIG = {
        "transposed_matrix" : global_transposed_matrix,
        "v_coords" : global_v_coords,
        "v_coord_strings" : [str(global_v_coords[0]), str(global_v_coords[1])],
        "result_coords_string" : """
            =
            \\left[ \\begin{array}{c}
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][0])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][0])+""") \\\\
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][1])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][1])+""")
            \\end{array}\\right]
            =
            \\left[ \\begin{array}{c}
                """+str(global_result[0])+""" \\\\
                """+str(global_result[1])+"""
            \\end{array}\\right]
        """
    }
    def construct(self):
        self.setup()
        self.label_bases()
        self.introduce_vector()
        self.apply_transposed_matrix(self.transposed_matrix, path_arc = 0)
        #new_matrix = np.dot(np.linalg.inv(self.transposed_matrix), self.transposed_matrix.T)
        #self.apply_transposed_matrix(new_matrix)
        self.write_linear_map_rule()
        self.show_basis_vector_coords()

    def label_bases(self):
        triplets = [
            (self.i_hat, "\\hat{\\imath}", X_COLOR),
            (self.j_hat, "\\hat{\\jmath}", Y_COLOR),
        ]
        label_mobs = []
        for vect, label, color in triplets:
            label_mobs.append(self.add_transformable_label(
                vect, label, "\\text{Transformed } " + label,
                color = color,
                direction = "right",
            ))
        self.i_label, self.j_label = label_mobs

    def introduce_vector(self):
        v = self.add_vector(self.v_coords)
        coords = Matrix(self.v_coords)
        coords.scale(VECTOR_LABEL_SCALE_FACTOR)
        coords.next_to(v.get_end(), np.sign(self.v_coords[0])*RIGHT)
        self.play(Write(coords, run_time = 1))
        v_def = self.get_v_definition()
        pre_def = VMobject(
            VectorizedPoint(coords.get_center()),
            VMobject(*[
                mob.copy()
                for mob in coords.get_mob_matrix().flatten()
            ])
        )
        self.play(Transform(
            pre_def, v_def,
            run_time = 2,
            submobject_mode = "all_at_once"
        ))
        self.remove(pre_def)
        self.add_foreground_mobject(v_def)
        self.show_linear_combination(clean_up=False)
        self.remove(coords)

    def show_linear_combination(self, clean_up = True):
        vector = NiceVector(np.append(self.v_coords, [0]))
        vectorlist = vector.linear_decomposition()
        total_vec = np.array([0,0,0])
        i_hat = [int(val) for val in self.i_hat.get_end()]
        j_hat = [int(val) for val in self.j_hat.get_end()]
        for i in range(len(vectorlist)):
            vec = vectorlist[i]
            vec_stuff = np.array([int(val) for val in vec.get_end()])
            if abs(int(vectorlist[i].get_end()[0])):
                vec = NiceVector(vec.get_end()).highlight(X_COLOR)
            else:
                vec = NiceVector(vec.get_end()).highlight(Y_COLOR)
            vec.put_at(total_vec)
            self.add_nice_vector(vec)
            total_vec += np.array([vec_stuff[0]*i_hat[0] + vec_stuff[1]*j_hat[0], vec_stuff[0]*i_hat[1] + vec_stuff[1]*j_hat[1], 0])
            vectorlist[i] = vec
            self.add_transformable_mobject(vec)
        if clean_up:
            for vec in vectorlist:
                self.remove(vec)

    def get_v_definition(self):
        v_def = TexMobject([
            "\\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "\\hat{\\imath}",
            "+%s"%self.v_coord_strings[1],
            "\\hat{\\jmath}",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = v_def.split()
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        v_def.add_background_rectangle()
        v_def.to_corner(UP + LEFT)
        self.v_def = v_def
        return v_def

    def write_linear_map_rule(self):
        rule = TexMobject([
            "\\text{Transformed } \\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "(\\text{Transformed }\\hat{\\imath})",
            "+%s"%self.v_coord_strings[1],
            "(\\text{Transformed } \\hat{\\jmath})",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = rule.split()
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        rule.scale(0.85)
        rule.next_to(self.v_def, DOWN, buff = 0.2)
        rule.to_edge(LEFT)
        rule.add_background_rectangle()

        self.play(Write(rule, run_time = 2))
        self.dither()
        self.linear_map_rule = rule


    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        for coords in i_coords, j_coords:
            coords.add_background_rectangle()
            coords.scale(0.7)
        i_coords.next_to(self.i_hat.get_end(), RIGHT)
        j_coords.next_to(self.j_hat.get_end(), LEFT)

        calculation = TexMobject([
            " = %s"%self.v_coord_strings[0],
            matrix_to_tex_string(self.transposed_matrix[0]),
            "+%s"%self.v_coord_strings[1],
            matrix_to_tex_string(self.transposed_matrix[1]),
        ])
        equals_neg_1, i_hat, plus_2, j_hat = calculation.split()
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        calculation.scale(0.8)
        calculation.next_to(self.linear_map_rule, DOWN)
        calculation.to_edge(LEFT)
        calculation.add_background_rectangle()

        result = TexMobject(self.result_coords_string)
        result.scale(0.8)
        result.add_background_rectangle()
        result.next_to(calculation, DOWN)
        result.to_edge(LEFT)

        self.play(Write(i_coords, run_time = 1))
        self.dither()
        self.play(Write(j_coords, run_time = 1))
        self.dither()
        self.play(Write(calculation))
        self.dither()
        self.play(Write(result))
        self.dither()

global_v_coords = [-1,4]
global_transposed_matrix = np.array([[4,3], [-2,1]])
global_result = np.dot(np.array(global_v_coords), np.array(global_transposed_matrix))
class Test2(LinearTransformationScene):
    #shows linear transformation of a vector wrt its linear decomposition into basis vectors
    global global_v_coords
    global global_transposed_matrix
    CONFIG = {
        "transposed_matrix" : global_transposed_matrix,
        "v_coords" : global_v_coords,
        "v_coord_strings" : [str(global_v_coords[0]), str(global_v_coords[1])],
        "result_coords_string" : """
            =
            \\left[ \\begin{array}{c}
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][0])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][0])+""") \\\\
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][1])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][1])+""")
            \\end{array}\\right]
            =
            \\left[ \\begin{array}{c}
                """+str(global_result[0])+""" \\\\
                """+str(global_result[1])+"""
            \\end{array}\\right]
        """
    }
    def construct(self):
        self.setup()
        self.label_bases()
        self.introduce_vector()
        self.apply_transposed_matrix(self.transposed_matrix, path_arc=0)
        #new_matrix = np.dot(np.linalg.inv(self.transposed_matrix), self.transposed_matrix.T)
        #self.apply_transposed_matrix(new_matrix)
        self.write_linear_map_rule()
        self.show_basis_vector_coords()

    def label_bases(self):
        triplets = [
            (self.i_hat, "\\hat{\\imath}", X_COLOR),
            (self.j_hat, "\\hat{\\jmath}", Y_COLOR),
        ]
        label_mobs = []
        for vect, label, color in triplets:
            label_mobs.append(self.add_transformable_label(
                vect, label, "\\text{Transformed } " + label,
                color = color,
                direction = "right",
            ))
        self.i_label, self.j_label = label_mobs

    def introduce_vector(self):
        v = self.add_vector(self.v_coords)
        coords = Matrix(self.v_coords)
        coords.scale(VECTOR_LABEL_SCALE_FACTOR)
        coords.next_to(v.get_end(), np.sign(self.v_coords[0])*RIGHT)
        self.play(Write(coords, run_time = 1))
        v_def = self.get_v_definition()
        pre_def = VMobject(
            VectorizedPoint(coords.get_center()),
            VMobject(*[
                mob.copy()
                for mob in coords.get_mob_matrix().flatten()
            ])
        )
        self.play(Transform(
            pre_def, v_def,
            run_time = 2,
            submobject_mode = "all_at_once"
        ))
        self.remove(pre_def)
        self.add_foreground_mobject(v_def)
        self.show_linear_combination(clean_up=False)
        self.remove(coords)

    def show_linear_combination(self, clean_up = True):
        vector = NiceVector(np.append(self.v_coords, [0]))
        vectorlist = vector.linear_decomposition()
        total_vec = np.array([0,0,0])
        i_hat = [int(val) for val in self.i_hat.get_end()]
        j_hat = [int(val) for val in self.j_hat.get_end()]
        for i in range(len(vectorlist)):
            vec = vectorlist[i]
            vec_stuff = np.array([int(val) for val in vec.get_end()])
            if abs(int(vectorlist[i].get_end()[0])):
                vec = NiceVector(vec.get_end()).highlight(X_COLOR)
            else:
                vec = NiceVector(vec.get_end()).highlight(Y_COLOR)
            vec.put_at(total_vec)
            self.add_nice_vector(vec)
            total_vec += np.array([vec_stuff[0]*i_hat[0] + vec_stuff[1]*j_hat[0], vec_stuff[0]*i_hat[1] + vec_stuff[1]*j_hat[1], 0])
            vectorlist[i] = vec
            self.add_transformable_mobject(vec)
        if clean_up:
            for vec in vectorlist:
                self.remove(vec)

    def get_v_definition(self):
        v_def = TexMobject([
            "\\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "\\hat{\\imath}",
            "+%s"%self.v_coord_strings[1],
            "\\hat{\\jmath}",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = v_def.split()
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        v_def.add_background_rectangle()
        v_def.to_corner(UP + LEFT)
        self.v_def = v_def
        return v_def

    def write_linear_map_rule(self):
        rule = TexMobject([
            "\\text{Transformed } \\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "(\\text{Transformed }\\hat{\\imath})",
            "+%s"%self.v_coord_strings[1],
            "(\\text{Transformed } \\hat{\\jmath})",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = rule.split()
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        rule.scale(0.85)
        rule.next_to(self.v_def, DOWN, buff = 0.2)
        rule.to_edge(LEFT)
        rule.add_background_rectangle()

        self.play(Write(rule, run_time = 2))
        self.dither()
        self.linear_map_rule = rule


    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        for coords in i_coords, j_coords:
            coords.add_background_rectangle()
            coords.scale(0.7)
        i_coords.next_to(self.i_hat.get_end(), RIGHT)
        j_coords.next_to(self.j_hat.get_end(), LEFT)

        calculation = TexMobject([
            " = %s"%self.v_coord_strings[0],
            matrix_to_tex_string(self.transposed_matrix[0]),
            "+%s"%self.v_coord_strings[1],
            matrix_to_tex_string(self.transposed_matrix[1]),
        ])
        equals_neg_1, i_hat, plus_2, j_hat = calculation.split()
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        calculation.scale(0.8)
        calculation.next_to(self.linear_map_rule, DOWN)
        calculation.to_edge(LEFT)
        calculation.add_background_rectangle()

        result = TexMobject(self.result_coords_string)
        result.scale(0.8)
        result.add_background_rectangle()
        result.next_to(calculation, DOWN)
        result.to_edge(LEFT)

        self.play(Write(i_coords, run_time = 1))
        self.dither()
        self.play(Write(j_coords, run_time = 1))
        self.dither()
        self.play(Write(calculation))
        self.dither()
        self.play(Write(result))
        self.dither()

global_v_coords = [-1,4]
global_transposed_matrix = np.array([[4,3], [-2,1]]).T
global_result = np.dot(np.array(global_v_coords), np.array(global_transposed_matrix))
class Test3(LinearTransformationScene):
    global global_v_coords
    global global_transposed_matrix
    CONFIG = {
        "include_background_plane" : False,
        "transposed_matrix" : global_transposed_matrix,
        "v_coords" : global_v_coords,
        "v_coord_strings" : [str(global_v_coords[0]), str(global_v_coords[1])],
        "result_coords_string" : """
            =
            \\left[ \\begin{array}{c}
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][0])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][0])+""") \\\\
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][1])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][1])+""")
            \\end{array}\\right]
            =
            \\left[ \\begin{array}{c}
                """+str(global_result[0])+""" \\\\
                """+str(global_result[1])+"""
            \\end{array}\\right]
        """
    }
    def construct(self):
        self.setup()
        self.add_transformable_mobject_a(DumberPlane())
        self.label_bases()
        self.add_vector(self.v_coords)
        self.transposed_matrix = self.transposed_matrix.T
        self.apply_transposed_matrix(self.transposed_matrix, path_arc = 0)
        self.write_matrices()
        self.dither()
        self.dither()
        self.dither()
        self.dither()
        self.dither()
        self.dither()
        self.dither()

    def label_bases(self):
        triplets = [
            (self.i_hat, "\\hat{\\imath}", X_COLOR),
            (self.j_hat, "\\hat{\\jmath}", Y_COLOR),
        ]
        label_mobs = []
        for vect, label, color in triplets:
            label_mobs.append(self.add_transformable_label(
                vect, label, "\\text{Transformed } " + label,
                color = color,
                direction = "right",
            ))
        self.i_label, self.j_label = label_mobs

    def write_matrices(self):
        matrix = matrix_to_mobject(self.transposed_matrix)
        transposed_matrix = matrix_to_mobject(self.transposed_matrix.T)
        matrix.scale(0.85)
        transposed_matrix.scale(0.85)
        matrix.to_edge(LEFT)
        transposed_matrix.to_edge(RIGHT)
        matrix.add_background_rectangle()
        transposed_matrix.add_background_rectangle()

        self.play(Write(matrix, run_time = 2))
        self.play(Write(transposed_matrix, run_time=2))
        return self

    def show_linear_combination(self, clean_up = True):
        vector = NiceVector(np.append(self.v_coords, [0]))
        vectorlist = vector.linear_decomposition()
        total_vec = np.array([0,0,0])
        i_hat = [int(val) for val in self.i_hat.get_end()]
        j_hat = [int(val) for val in self.j_hat.get_end()]
        for i in range(len(vectorlist)):
            vec = vectorlist[i]
            vec_stuff = np.array([int(val) for val in vec.get_end()])
            if abs(int(vectorlist[i].get_end()[0])):
                vec = NiceVector(vec.get_end()).highlight(X_COLOR)
            else:
                vec = NiceVector(vec.get_end()).highlight(Y_COLOR)
            vec.put_at(total_vec)
            self.add_nice_vector(vec)
            total_vec += np.array([vec_stuff[0]*i_hat[0] + vec_stuff[1]*j_hat[0], vec_stuff[0]*i_hat[1] + vec_stuff[1]*j_hat[1], 0])
            vectorlist[i] = vec
            self.add_transformable_mobject(vec)
        if clean_up:
            for vec in vectorlist:
                self.remove(vec)

    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        for coords in i_coords, j_coords:
            coords.add_background_rectangle()
            coords.scale(0.7)
        i_coords.next_to(self.i_hat.get_end(), RIGHT)
        j_coords.next_to(self.j_hat.get_end(), RIGHT)

        calculation = TexMobject([
            " = %s"%self.v_coord_strings[0],
            matrix_to_tex_string(self.transposed_matrix[0]),
            "+%s"%self.v_coord_strings[1],
            matrix_to_tex_string(self.transposed_matrix[1]),
        ])
        equals_neg_1, i_hat, plus_2, j_hat = calculation.split()
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        calculation.scale(0.8)
        calculation.next_to(self.linear_map_rule, DOWN)
        calculation.to_edge(LEFT)
        calculation.add_background_rectangle()

        result = TexMobject(self.result_coords_string)
        result.scale(0.8)
        result.add_background_rectangle()
        result.next_to(calculation, DOWN)
        result.to_edge(LEFT)

        self.play(Write(i_coords, run_time = 1))
        self.dither()
        self.play(Write(j_coords, run_time = 1))
        self.dither()
        self.play(Write(calculation))
        self.dither()
        self.play(Write(result))
        self.dither()

global_transposed_matrix = np.array([[0,1], [-2,3]])
eigen_vals, eigen_vecs = np.linalg.eig(global_transposed_matrix.T)
eigen_vals = clean(eigen_vals)
eigen_vecs = clean1(eigen_vecs)
eigen_vecs = [[j[i] for j in eigen_vecs] for i in range(len(eigen_vecs))]
class EigenTest(LinearTransformationScene):
    global global_transposed_matrix
    CONFIG = {
        "transposed_matrix" : global_transposed_matrix,
    }
    def construct(self):
        self.setup()
        self.label_bases()
        self.draw_eigenvectors()
        self.apply_transposed_matrix(self.transposed_matrix, path_arc = 0)
        self.apply_transposed_matrix(self.transposed_matrix, path_arc = 0)
        #self.apply_transposed_matrix(self.transposed_matrix)
        #new_matrix = np.dot(np.linalg.inv(self.transposed_matrix), self.transposed_matrix.T)
        #self.apply_transposed_matrix(new_matrix)
        #self.show_basis_vector_coords()

    def label_bases(self):
        triplets = [
            (self.i_hat, "\\hat{\\imath}", X_COLOR),
            (self.j_hat, "\\hat{\\jmath}", Y_COLOR),
        ]
        label_mobs = []
        for vect, label, color in triplets:
            label_mobs.append(self.add_transformable_label(
                vect, label, "\\text{Transformed } " + label,
                color = color,
                direction = "right",
            ))
        self.i_label, self.j_label = label_mobs

    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        for coords in i_coords, j_coords:
            coords.add_background_rectangle()
            coords.scale(0.7)
        i_coords.next_to(self.i_hat.get_end(), RIGHT)
        j_coords.next_to(self.j_hat.get_end(), LEFT)

        i_hat, j_hat = self.i_hat, self.j_hat
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)

        self.play(Write(i_coords, run_time = 1))
        self.dither()
        self.play(Write(j_coords, run_time = 1))
        self.dither()

    def draw_eigenvectors(self):
        global eigen_vecs
        n = 150
        r = 3
        for theta in range(n):
            angle = theta*2*np.pi/n
            coords = r*np.array([math.cos(angle), math.sin(angle)])
            theta = float(theta)
            vec = Vector(coords, color = Color(hue=theta/n, saturation=1, luminance=.5))
            self.add_vector(vec, animate=False)
        for vec in eigen_vecs:
            vec = np.array([vec[0], vec[1], 0])
            self.add_vector(Vector(vec), color=WHITE, animate=False)
            self.add_transformable_mobject(DashedLine(10*vec, -10*vec))
        #self.add_vector(Vector([1,1], color=WHITE, animate= False))
        #self.add_vector(Vector([1,-1.5], color=WHITE, animate=False))

global_transposed_matrix = np.array([[4,-2], [2,0]])
class EigenTest1(LinearTransformationScene):
    global global_transposed_matrix
    CONFIG = {
        "transposed_matrix" : global_transposed_matrix,
    }
    def construct(self):
        self.setup()
        self.label_bases()
        self.draw_eigenvectors()
        self.apply_transposed_matrix(self.transposed_matrix, path_arc = 0)
        #new_matrix = np.dot(np.linalg.inv(self.transposed_matrix), self.transposed_matrix.T)
        #self.apply_transposed_matrix(new_matrix)
        self.show_basis_vector_coords()

    def label_bases(self):
        triplets = [
            (self.i_hat, "\\hat{\\imath}", X_COLOR),
            (self.j_hat, "\\hat{\\jmath}", Y_COLOR),
        ]
        label_mobs = []
        for vect, label, color in triplets:
            label_mobs.append(self.add_transformable_label(
                vect, label, "\\text{Transformed } " + label,
                color = color,
                direction = "right",
            ))
        self.i_label, self.j_label = label_mobs

    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        for coords in i_coords, j_coords:
            coords.add_background_rectangle()
            coords.scale(0.7)
        i_coords.next_to(self.i_hat.get_end(), RIGHT)
        j_coords.next_to(self.j_hat.get_end(), LEFT)

        i_hat, j_hat = self.i_hat, self.j_hat
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)

        self.play(Write(i_coords, run_time = 1))
        self.dither()
        self.play(Write(j_coords, run_time = 1))
        self.dither()

    def draw_eigenvectors(self):
        n = 100
        r = 2.5
        for theta in range(n):
            angle = theta*2*np.pi/n
            coords = r*np.array([math.cos(angle), math.sin(angle)])
            theta = float(theta)
            vec = Vector(coords, color = Color(hue=theta/n, saturation=1, luminance=.5))
            #self.add_vector(vec)
            self.add_transformable_mobject(vec)
        self.add_transformable_mobject(Vector([1,-1], color=WHITE))
        self.add_transformable_mobject(Vector([-1,1], color=WHITE))

class TransformJustOneVector(VectorScene):
    def construct(self):
        self.lock_in_faded_grid()
        v1_coords = [-3, 1]
        t_matrix = [[0, -1], [2, -1]]
        v1 = Vector(v1_coords)
        v2 = Vector(
            np.dot(np.array(t_matrix).transpose(), v1_coords),
            color = PINK
        )
        for v, word in (v1, "Input"), (v2, "Output"):
            v.label = TextMobject("%s vector"%word) #creates TextMobject "In/Output Vector"
            v.label.next_to(v.get_end(), UP) #places v.label on top of the end of v
            v.label.highlight(v.get_color()) #colors v.label appropriately
            self.play(ShowCreation(v)) #plays animation
            self.play(Write(v.label))
        self.dither()
        self.remove(v2)
        self.play(
            Transform(          #animation of transformation
                v1.copy(), v2,
                path_arc = -np.pi/2, run_time = 3
            ),
            ApplyMethod(v1.fade)
        )
        self.dither()

class TransformManyVectors(LinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [[2, 1], [1, 2]],
        "use_dots" : False,
    }
    def construct(self):
        self.lock_in_faded_grid()
        vectors = VMobject(*[
            Vector([x, y])
            for x in np.arange(-int(SPACE_WIDTH)+0.5, int(SPACE_WIDTH)+0.5)
            for y in np.arange(-int(SPACE_HEIGHT)+0.5, int(SPACE_HEIGHT)+0.5)
        ])
        vectors.submobject_gradient_highlight(PINK, YELLOW)
        t_matrix = self.transposed_matrix
        transformed_vectors = VMobject(*[
            Vector(
                np.dot(np.array(t_matrix).transpose(), v.get_end()[:2]),
                color = v.get_color()
            )
            for v in vectors.split()
        ])

        self.play(ShowCreation(vectors, submobject_mode = "lagged_start"))
        self.dither()
        if self.use_dots:
            self.play(Transform(
                vectors, self.vectors_to_dots(vectors),
                run_time = 3,
                submobject_mode = "lagged_start"
            ))
            transformed_vectors = self.vectors_to_dots(transformed_vectors)
            self.dither()
        self.play(Transform(
            vectors, transformed_vectors,
            run_time = 3,
            path_arc = -np.pi/2
        ))
        self.dither()
        if self.use_dots:
            self.play(Transform(
                vectors, self.dots_to_vectors(vectors),
                run_time = 2,
                submobject_mode = "lagged_start"
            ))
            self.dither()

    def vectors_to_dots(self, vectors):
        return VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])

    def dots_to_vectors(self, dots):
        return VMobject(*[
            Vector(dot.get_center(), color = dot.get_color())
            for dot in dots.split()
        ])

class TransformManyVectorsAsPoints(TransformManyVectors):
    CONFIG = {
        "use_dots" : True
    }

class TransformInfiniteGrid(LinearTransformationScene):
    CONFIG = {
        "include_background_plane" : False,
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
        },
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        self.play(ShowCreation(
            self.plane, run_time = 3, submobject_mode = "lagged_start"
        ))
        self.dither()
        self.apply_transposed_matrix([[2, 1], [1, 2]], path_arc = 0)
        self.dither()

class TransformInfiniteGridWithBackground(TransformInfiniteGrid):
    CONFIG = {
        "include_background_plane" : True,
        "foreground_plane_kwargs" : {
            "x_radius" : 2*SPACE_WIDTH,
            "y_radius" : 2*SPACE_HEIGHT,
            "secondary_line_ratio" : 0
        },

    }


class IntroduceLinearTransformations(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
    }
    def construct(self):
        self.setup()
        self.dither()
        self.apply_transposed_matrix([[2, 1], [1, 2]])
        self.dither()

        lines_rule = TextMobject("Lines remain lines")
        lines_rule.shift(2*UP).to_edge(LEFT)
        origin_rule = TextMobject("Origin remains fixed")
        origin_rule.shift(2*UP).to_edge(RIGHT)
        arrow = Arrow(origin_rule, ORIGIN)
        dot = Dot(ORIGIN, radius = 0.1, color = RED)

        for rule in lines_rule, origin_rule:
            rule.add_background_rectangle()

        self.play(
            Write(lines_rule, run_time = 2),
        )
        self.dither()
        self.play(
            Write(origin_rule, run_time = 2),
            ShowCreation(arrow),
            GrowFromCenter(dot)
        )
        self.dither()

class SimpleLinearTransformationScene(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "transposed_matrix" : [[2, 1], [1, 2]]
    }
    def construct(self):
        self.setup()
        self.dither()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.dither()

class SimpleNonlinearTransformationScene(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "words" : "Not linear: some lines get curved"
    }
    def construct(self):
        self.setup()
        self.dither()
        self.apply_nonlinear_transformation(self.func)
        words = TextMobject(self.words)
        words.to_corner(UP+RIGHT)
        words.highlight(RED)
        words.add_background_rectangle()
        self.play(Write(words))
        self.dither()

    def func(self, point):
        return curvy_squish(point)

class MovingOrigin(SimpleNonlinearTransformationScene):
    CONFIG = {
        "words" : "Not linear: Origin moves"
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        dot = Dot(ORIGIN, color = RED)
        self.add_transformable_mobject(dot)

    def func(self, point):
        matrix_transform = self.get_matrix_transformation([[2, 0], [1, 1]])
        return matrix_transform(point) + 2*UP+3*LEFT

class SneakyNonlinearTransformation(SimpleNonlinearTransformationScene):
    CONFIG = {
        "words" : "\\dots"
    }
    def func(self, point):
        x, y, z = point
        new_x = np.sign(x)*SPACE_WIDTH*smooth(abs(x) / SPACE_WIDTH)
        new_y = np.sign(y)*SPACE_HEIGHT*smooth(abs(y) / SPACE_HEIGHT)
        return [new_x, new_y, 0]

class SneakyNonlinearTransformationExplained(SneakyNonlinearTransformation):
    CONFIG = {
        "words" : "Not linear: diagonal lines get curved"
    }
    def setup(self):
        LinearTransformationScene.setup(self)
        diag = Line(
            SPACE_HEIGHT*LEFT+SPACE_HEIGHT*DOWN,
            SPACE_HEIGHT*RIGHT + SPACE_HEIGHT*UP
        )
        diag.insert_n_anchor_points(20)
        diag.change_anchor_mode("smooth")
        diag.highlight(YELLOW)
        self.play(ShowCreation(diag))
        self.add_transformable_mobject(diag)

class GridLinesRemainParallel(SimpleLinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [
            [3, 0],
            [1, 2]
        ]
    }
    def construct(self):
        SimpleLinearTransformationScene.construct(self)
        text = TextMobject([
            "Grid lines remain",
            "parallel",
            "and",
            "evenly spaced",
        ])
        glr, p, a, es = text.split()
        p.highlight(YELLOW)
        es.highlight(GREEN)
        text.add_background_rectangle()
        text.shift(-text.get_bottom())
        self.play(Write(text))
        self.dither()

class Rotation(SimpleLinearTransformationScene):
    CONFIG = {
        "angle" : np.pi/3,
    }
    def construct(self):
        self.transposed_matrix = [
            [np.cos(self.angle), np.sin(self.angle)],
            [-np.sin(self.angle), np.cos(self.angle)]
        ]
        SimpleLinearTransformationScene.construct(self)

class YetAnotherLinearTransformation(SimpleLinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [
            [-1, 1],
            [3, 2],
        ]
    }
    def construct(self):
        SimpleLinearTransformationScene.construct(self)
        words = TextMobject("""
            How would you describe
            one of these numerically?
            """
        )
        words.add_background_rectangle()
        words.to_edge(UP)
        words.highlight(GREEN)
        formula = TexMobject([
            matrix_to_tex_string(["x_\\text{in}", "y_\\text{in}"]),
            "\\rightarrow ???? \\rightarrow",
            matrix_to_tex_string(["x_\\text{out}", "y_{\\text{out}}"])
        ])
        formula.add_background_rectangle()

        self.play(Write(words))
        self.dither()
        self.play(
            ApplyMethod(self.plane.fade, 0.7),
            ApplyMethod(self.background_plane.fade, 0.7),
            Write(formula, run_time = 2),
            Animation(words)
        )
        self.dither()

class FollowIHatJHat(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        i_hat = self.add_vector([1, 0], color = X_COLOR)
        i_label = self.label_vector(
            i_hat, "\\hat{\\imath}",
            color = X_COLOR,
            label_scale_factor = 1
        )
        j_hat = self.add_vector([0, 1], color = Y_COLOR)
        j_label = self.label_vector(
            j_hat, "\\hat{\\jmath}",
            color = Y_COLOR,
            label_scale_factor = 1
        )

        self.dither()
        self.play(*map(FadeOut, [i_label, j_label]))
        self.apply_transposed_matrix([[-1, 1], [-2, -1]])
        self.dither()

global_v_coords = [-2,-4]
global_transposed_matrix = [[5,3], [-2,0]]
global_result = np.dot(np.array(global_v_coords), np.array(global_transposed_matrix))
class TrackBasisVectorsExample(LinearTransformationScene):
    global global_v_coords
    global global_transposed_matrix
    CONFIG = {
        "transposed_matrix" : global_transposed_matrix,
        "v_coords" : global_v_coords,
        "v_coord_strings" : [str(global_v_coords[0]), str(global_v_coords[1])],
        "result_coords_string" : """
            =
            \\left[ \\begin{array}{c}
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][0])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][0])+""") \\\\
                """+str(global_v_coords[0])+"""("""+str(global_transposed_matrix[0][1])+""") + """+str(global_v_coords[1])+"""("""+str(global_transposed_matrix[1][1])+""")
            \\end{array}\\right]
            =
            \\left[ \\begin{array}{c}
                """+str(global_result[0])+""" \\\\
                """+str(global_result[1])+"""
            \\end{array}\\right]
        """
    }
    def construct(self):
        self.setup()
        self.label_bases()
        self.introduce_vector()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.show_linear_combination(clean_up=False)
        self.write_linear_map_rule()
        self.show_basis_vector_coords()

    def label_bases(self):
        triplets = [
            (self.i_hat, "\\hat{\\imath}", X_COLOR),
            (self.j_hat, "\\hat{\\jmath}", Y_COLOR),
        ]
        label_mobs = []
        for vect, label, color in triplets:
            label_mobs.append(self.add_transformable_label(
                vect, label, "\\text{Transformed } " + label,
                color = color,
                direction = "right",
            ))
        self.i_label, self.j_label = label_mobs

    def introduce_vector(self):
        v = self.add_vector(self.v_coords)
        coords = Matrix(self.v_coords)
        coords.scale(VECTOR_LABEL_SCALE_FACTOR)
        coords.next_to(v.get_end(), np.sign(self.v_coords[0])*RIGHT)

        self.play(Write(coords, run_time = 1))
        v_def = self.get_v_definition()
        pre_def = VMobject(
            VectorizedPoint(coords.get_center()),
            VMobject(*[
                mob.copy()
                for mob in coords.get_mob_matrix().flatten()
            ])
        )
        self.play(Transform(
            pre_def, v_def,
            run_time = 2,
            submobject_mode = "all_at_once"
        ))
        self.remove(pre_def)
        self.add_foreground_mobject(v_def)
        self.show_linear_combination(clean_up=True)
        self.remove(coords)

    def show_linear_combination(self, clean_up = True):
        i_hat_copy, j_hat_copy = [m.copy() for m in self.i_hat, self.j_hat]
        global i_list
        global j_list
        i_vector = [int(self.i_hat.copy().get_end()[0]),int(self.i_hat.copy().get_end()[1])]
        j_vector = [int(self.j_hat.copy().get_end()[0]),int(self.j_hat.copy().get_end()[1])]


        i_list = []
        total_i_vec = np.array([0,0])
        if self.v_coords[0] < 0:
            i_vector = [-1*i_vector[0],-1*i_vector[1]]
            #total_i_vec = np.array([0,0])
            #print(total_i_vec)
            for i in range(abs(self.v_coords[0])): #assumes input vectors of the form (a,b) have integer a, b
                i_vec = Vector(i_vector)
                i_list += i_vec
                i_vec.highlight(X_COLOR)
                self.add_vector(i_vec)
                self.play(ApplyMethod(i_vec.shift, Vector(total_i_vec).get_end()))
                total_i_vec += np.array(i_vector)

        else:
            #total_i_vec = np.array([0,0]) #([-1,0])
            for i in range(abs(self.v_coords[0])-1):
                i_vec = self.i_hat.copy()
                i_list += i_vec
                i_vec.highlight(X_COLOR)
                self.add_vector(i_vec)
                self.play(ApplyMethod(i_vec.shift, Vector(total_i_vec).get_end()))
                total_i_vec += np.array(i_vector)


        j_list = []
        total_j_vec = total_i_vec
        #total_j_vec = np.array([-int(self.i_hat.get_end()[0])-int(self.j_hat.get_end()[0])+1,-int(self.i_hat.get_end()[1])-int(self.j_hat.get_end()[1])])
        if self.v_coords[1] < 0:
            #for element in j_vector: element *= -1
            j_vector = [-1*j_vector[0],-1*j_vector[1]]
            for j in range(abs(self.v_coords[1])):
                j_vec = Vector(j_vector)
                j_list += j_vec
                j_vec.highlight(Y_COLOR)
                self.add_vector(j_vec)
                #self.play(ApplyMethod(j_vec.shift, Vector(np.array([self.v_coords[0],0])).get_end()))
                #total_j_vec += np.array([int(self.j_hat.get_end()[0]),int(self.j_hat.get_end()[1])])
                self.play(ApplyMethod(j_vec.shift, Vector(total_j_vec).get_end()))
                total_j_vec += np.array(j_vector)

        else:
            total_j_vec = np.array([0,0]) #([0,1])
            for j in range(abs(self.v_coords[1])):
                #j_vec = self.j_hat.copy()
                j_vec = Vector(np.array([0,-1]))
                j_list += j_vec
                j_vec.highlight(Y_COLOR)
                self.add_vector(j_vec)
                #self.play(ApplyMethod(j_vec.shift, Vector(np.array([self.v_coords[0],0])).get_end()))
                #total_j_vec += np.array([int(self.j_hat.get_end()[0]),-1*int(self.j_hat.get_end()[1])])
                total_j_vec += np.array([0,-1])
                self.play(ApplyMethod(j_vec.shift, Vector(total_j_vec).get_end()))
        #for i_vec in i_list:
        #    i_vec.highlight(YELLOW)
        #for j_vec in j_list:
        #    j_vec.highlight(YELLOW)
        self.dither()
        if clean_up:
            total_list = i_list + j_list
            for vec in total_list:
                self.remove(vec)

    def get_v_definition(self):
        v_def = TexMobject([
            "\\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "\\hat{\\imath}",
            "+%s"%self.v_coord_strings[1],
            "\\hat{\\jmath}",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = v_def.split()
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        v_def.add_background_rectangle()
        v_def.to_corner(UP + LEFT)
        self.v_def = v_def
        return v_def

    def write_linear_map_rule(self):
        rule = TexMobject([
            "\\text{Transformed } \\vec{\\textbf{v}}",
            " = %s"%self.v_coord_strings[0],
            "(\\text{Transformed }\\hat{\\imath})",
            "+%s"%self.v_coord_strings[1],
            "(\\text{Transformed } \\hat{\\jmath})",
        ])
        v, equals_neg_1, i_hat, plus_2, j_hat = rule.split()
        v.highlight(YELLOW)
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        rule.scale(0.85)
        rule.next_to(self.v_def, DOWN, buff = 0.2)
        rule.to_edge(LEFT)
        rule.add_background_rectangle()

        self.play(Write(rule, run_time = 2))
        self.dither()
        self.linear_map_rule = rule


    def show_basis_vector_coords(self):
        i_coords = matrix_to_mobject(self.transposed_matrix[0])
        j_coords = matrix_to_mobject(self.transposed_matrix[1])
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        for coords in i_coords, j_coords:
            coords.add_background_rectangle()
            coords.scale(0.7)
        i_coords.next_to(self.i_hat.get_end(), RIGHT)
        j_coords.next_to(self.j_hat.get_end(), RIGHT)

        calculation = TexMobject([
            " = %s"%self.v_coord_strings[0],
            matrix_to_tex_string(self.transposed_matrix[0]),
            "+%s"%self.v_coord_strings[1],
            matrix_to_tex_string(self.transposed_matrix[1]),
        ])
        equals_neg_1, i_hat, plus_2, j_hat = calculation.split()
        i_hat.highlight(X_COLOR)
        j_hat.highlight(Y_COLOR)
        calculation.scale(0.8)
        calculation.next_to(self.linear_map_rule, DOWN)
        calculation.to_edge(LEFT)
        calculation.add_background_rectangle()

        result = TexMobject(self.result_coords_string)
        result.scale(0.8)
        result.add_background_rectangle()
        result.next_to(calculation, DOWN)
        result.to_edge(LEFT)

        self.play(Write(i_coords, run_time = 1))
        self.dither()
        self.play(Write(j_coords, run_time = 1))
        self.dither()
        self.play(Write(calculation))
        self.dither()
        self.play(Write(result))
        self.dither()

class WatchManyVectorsMove(TransformManyVectors):
    def construct(self):
        self.setup()
        vectors = VMobject(*[
            Vector([x, y])
            for x in np.arange(-int(SPACE_WIDTH)+0.5, int(SPACE_WIDTH)+0.5)
            for y in np.arange(-int(SPACE_HEIGHT)+0.5, int(SPACE_HEIGHT)+0.5)
        ])
        vectors.submobject_gradient_highlight(PINK, YELLOW)
        dots = self.vectors_to_dots(vectors)
        self.play(ShowCreation(dots, submobject_mode = "lagged_start"))
        self.play(Transform(
            dots, vectors,
            submobject_mode = "lagged_start",
            run_time = 2
        ))
        self.remove(dots)
        for v in vectors.split():
            self.add_vector(v, animate = False)
        self.apply_transposed_matrix([[1, -2], [3, 0]])
        self.dither()
        self.play(
            ApplyMethod(self.plane.fade),
            FadeOut(vectors),
            Animation(self.i_hat),
            Animation(self.j_hat),
        )
        self.dither()

class NowWithoutWatching(Scene):
    def construct(self):
        text = TextMobject("Now without watching...")
        text.to_edge(UP)
        randy = Randolph(mode = "pondering")
        self.add(randy)
        self.play(Write(text, run_time = 1))
        self.play(ApplyMethod(randy.blink))
        self.dither(2)

class DeduceResultWithGeneralCoordinates(Scene):
    def construct(self):
        i_hat_to = TexMobject("\\hat{\\imath} \\rightarrow")
        j_hat_to = TexMobject("\\hat{\\jmath} \\rightarrow")
        i_coords = Matrix([1, -2])
        j_coords = Matrix([3, 0])
        i_coords.next_to(i_hat_to, RIGHT, buff = 0.1)
        j_coords.next_to(j_hat_to, RIGHT, buff = 0.1)
        i_group = VMobject(i_hat_to, i_coords)
        j_group = VMobject(j_hat_to, j_coords)
        i_group.highlight(X_COLOR)
        j_group.highlight(Y_COLOR)
        i_group.next_to(ORIGIN, LEFT, buff = 1).to_edge(UP)
        j_group.next_to(ORIGIN, RIGHT, buff = 1).to_edge(UP)

        vect = Matrix(["x", "y"])
        x, y = vect.get_mob_matrix().flatten()
        VMobject(x, y).highlight(YELLOW)
        rto = TexMobject("\\rightarrow")
        equals = TexMobject("=")
        plus = TexMobject("+")
        row1 = TexMobject("1x + 3y")
        row2 = TexMobject("-2x + 0y")
        VMobject(
            row1.split()[0], row2.split()[0], row2.split()[1]
        ).highlight(X_COLOR)
        VMobject(
            row1.split()[1], row1.split()[4], row2.split()[2], row2.split()[5]
        ).highlight(YELLOW)
        VMobject(
            row1.split()[3], row2.split()[4]
        ).highlight(Y_COLOR)
        result = Matrix([row1, row2])
        result.show()
        vect_group = VMobject(
            vect, rto,
            x.copy(), i_coords.copy(), plus,
            y.copy(), j_coords.copy(), equals,
            result
        )
        vect_group.arrange_submobjects(RIGHT, buff = 0.1)

        self.add(i_group, j_group)
        for mob in vect_group.split():
            self.play(Write(mob))
        self.dither()

class MatrixVectorMultiplication(LinearTransformationScene):
    CONFIG = {
        "abstract" : False
    }
    def construct(self):
        self.setup()
        matrix = self.build_to_matrix()
        self.label_matrix(matrix)
        vector, formula = self.multiply_by_vector(matrix)
        self.reposition_matrix_and_vector(matrix, vector, formula)

    def build_to_matrix(self):
        self.dither()
        self.apply_transposed_matrix([[3, -2], [2, 1]])
        self.dither()
        i_coords = vector_coordinate_label(self.i_hat)
        j_coords = vector_coordinate_label(self.j_hat)
        if self.abstract:
            new_i_coords = Matrix(["a", "c"])
            new_j_coords = Matrix(["b", "d"])
            new_i_coords.move_to(i_coords)
            new_j_coords.move_to(j_coords)
            i_coords = new_i_coords
            j_coords = new_j_coords
        i_coords.highlight(X_COLOR)
        j_coords.highlight(Y_COLOR)
        i_brackets = i_coords.get_brackets()
        j_brackets = j_coords.get_brackets()
        for coords in i_coords, j_coords:
            rect = BackgroundRectangle(coords)
            coords.rect = rect

        abstract_matrix = np.append(
            i_coords.get_mob_matrix(),
            j_coords.get_mob_matrix(),
            axis = 1
        )
        concrete_matrix = Matrix(
            copy.deepcopy(abstract_matrix),
            add_background_rectangles = True
        )
        concrete_matrix.to_edge(UP)
        if self.abstract:
            m = concrete_matrix.get_mob_matrix()[1, 0]
            m.shift(m.get_height()*DOWN/2)
        matrix_brackets = concrete_matrix.get_brackets()

        self.play(ShowCreation(i_coords.rect), Write(i_coords))
        self.play(ShowCreation(j_coords.rect), Write(j_coords))
        self.dither()
        self.remove(i_coords.rect, j_coords.rect)
        self.play(
            Transform(
                VMobject(*abstract_matrix.flatten()),
                VMobject(*concrete_matrix.get_mob_matrix().flatten()),
            ),
            Transform(i_brackets, matrix_brackets),
            Transform(j_brackets, matrix_brackets),
            run_time = 2,
            submobject_mode = "all_at_once"
        )
        everything = VMobject(*self.get_mobjects())
        self.play(
            FadeOut(everything),
            Animation(concrete_matrix)
        )
        return concrete_matrix

    def label_matrix(self, matrix):
        title = TextMobject("``2x2 Matrix''")
        title.to_edge(UP+LEFT)
        col_circles = []
        for i, color in enumerate([X_COLOR, Y_COLOR]):
            col = VMobject(*matrix.get_mob_matrix()[:,i])
            col_circle = Circle(color = color)
            col_circle.stretch_to_fit_width(matrix.get_width()/3)
            col_circle.stretch_to_fit_height(matrix.get_height())
            col_circle.move_to(col)
            col_circles.append(col_circle)
        i_circle, j_circle = col_circles
        i_message = TextMobject("Where $\\hat{\\imath}$ lands")
        j_message = TextMobject("Where $\\hat{\\jmath}$ lands")
        i_message.highlight(X_COLOR)
        j_message.highlight(Y_COLOR)
        i_message.next_to(i_circle, DOWN, buff = 2, aligned_edge = RIGHT)
        j_message.next_to(j_circle, DOWN, buff = 2, aligned_edge = LEFT)
        i_arrow = Arrow(i_message, i_circle)
        j_arrow = Arrow(j_message, j_circle)

        self.play(Write(title))
        self.dither()
        self.play(ShowCreation(i_circle))
        self.play(
            Write(i_message, run_time = 1.5),
            ShowCreation(i_arrow),
        )
        self.dither()
        self.play(ShowCreation(j_circle))
        self.play(
            Write(j_message, run_time = 1.5),
            ShowCreation(j_arrow)
        )
        self.dither()
        self.play(*map(FadeOut, [
            i_message, i_circle, i_arrow, j_message, j_circle, j_arrow
        ]))


    def multiply_by_vector(self, matrix):
        vector = Matrix(["x", "y"]) if self.abstract else Matrix([5, 7])
        vector.scale_to_fit_height(matrix.get_height())
        vector.next_to(matrix, buff = 2)
        brace = Brace(vector, DOWN)
        words = TextMobject("Any  ol' vector")
        words.next_to(brace, DOWN)

        self.play(
            Write(vector),
            GrowFromCenter(brace),
            Write(words),
            run_time = 1
        )
        self.dither()

        v1, v2 = vector.get_mob_matrix().flatten()
        mob_matrix = matrix.copy().get_mob_matrix()
        col1 = Matrix(mob_matrix[:,0])
        col2 = Matrix(mob_matrix[:,1])
        formula = VMobject(
            v1.copy(), col1, TexMobject("+"), v2.copy(), col2
        )
        formula.arrange_submobjects(RIGHT, buff = 0.1)
        formula.center()
        formula_start = VMobject(
            v1.copy(),
            VMobject(*matrix.copy().get_mob_matrix()[:,0]),
            VectorizedPoint(),
            v2.copy(),
            VMobject(*matrix.copy().get_mob_matrix()[:,1]),
        )

        self.play(
            FadeOut(brace),
            FadeOut(words),
            Transform(
                formula_start, formula,
                run_time = 2,
                submobject_mode = "all_at_once"
            )
        )
        self.dither()
        self.show_result(formula)
        return vector, formula

    def show_result(self, formula):
        if self.abstract:
            row1 = ["a", "x", "+", "b", "y"]
            row2 = ["c", "x", "+", "d", "y"]
        else:
            row1 = ["3", "(5)", "+", "2", "(7)"]
            row2 = ["-2", "(5)", "+", "1", "(7)"]
        row1 = VMobject(*map(TexMobject, row1))
        row2 = VMobject(*map(TexMobject, row2))
        for row in row1, row2:
            row.arrange_submobjects(RIGHT, buff = 0.1)
        final_sum = Matrix([row1, row2])
        row1, row2 = final_sum.get_mob_matrix().flatten()
        row1.split()[0].highlight(X_COLOR)
        row2.split()[0].highlight(X_COLOR)
        row1.split()[3].highlight(Y_COLOR)
        row2.split()[3].highlight(Y_COLOR)
        equals = TexMobject("=")
        equals.next_to(formula, RIGHT)
        final_sum.next_to(equals, RIGHT)

        self.play(
            Write(equals, run_time = 1),
            Write(final_sum)
        )
        self.dither()


    def reposition_matrix_and_vector(self, matrix, vector, formula):
        start_state = VMobject(matrix, vector)
        end_state = start_state.copy()
        end_state.arrange_submobjects(RIGHT, buff = 0.1)
        equals = TexMobject("=")
        equals.next_to(formula, LEFT)
        end_state.next_to(equals, LEFT)
        brace = Brace(formula, DOWN)
        brace_words = TextMobject("Where all the intuition is")
        brace_words.next_to(brace, DOWN)
        brace_words.highlight(YELLOW)

        self.play(
            Transform(
                start_state, end_state,
                submobject_mode = "all_at_once"
            ),
            Write(equals, run_time = 1)
        )
        self.dither()
        self.play(
            FadeIn(brace),
            FadeIn(brace_words),
            submobject_mode = "lagged_start"
        )
        self.dither()

class MatrixVectorMultiplicationAbstract(MatrixVectorMultiplication):
    CONFIG = {
        "abstract" : True,
    }

class ColumnsToBasisVectors(LinearTransformationScene):
    CONFIG = {
        "t_matrix" : [[3, 1], [1, 2]]
    }
    def construct(self):
        self.setup()
        vector_coords = [-1, 2]

        vector = self.move_matrix_columns(self.t_matrix, vector_coords)
        self.scale_and_add(vector, vector_coords)
        self.dither(3)

    def move_matrix_columns(self, transposed_matrix, vector_coords = None):
        matrix = np.array(transposed_matrix).transpose()
        matrix_mob = Matrix(matrix)
        matrix_mob.to_corner(UP+LEFT)
        matrix_mob.add_background_to_entries()
        col1 = VMobject(*matrix_mob.get_mob_matrix()[:,0])
        col1.highlight(X_COLOR)
        col2 = VMobject(*matrix_mob.get_mob_matrix()[:,1])
        col2.highlight(Y_COLOR)
        matrix_brackets = matrix_mob.get_brackets()
        matrix_background = BackgroundRectangle(matrix_mob)
        self.add_foreground_mobject(matrix_background, matrix_mob)

        if vector_coords is not None:
            vector = Matrix(vector_coords)
            VMobject(*vector.get_mob_matrix().flatten()).highlight(YELLOW)
            vector.scale_to_fit_height(matrix_mob.get_height())
            vector.next_to(matrix_mob, RIGHT)
            vector_background = BackgroundRectangle(vector)
            self.add_foreground_mobject(vector_background, vector)

        new_i = Vector(matrix[:,0])
        new_j = Vector(matrix[:,1])
        i_label = vector_coordinate_label(new_i).highlight(X_COLOR)
        j_label = vector_coordinate_label(new_j).highlight(Y_COLOR)
        i_coords = VMobject(*i_label.get_mob_matrix().flatten())
        j_coords = VMobject(*j_label.get_mob_matrix().flatten())
        i_brackets = i_label.get_brackets()
        j_brackets = j_label.get_brackets()
        i_label_background = BackgroundRectangle(i_label)
        j_label_background = BackgroundRectangle(j_label)
        i_coords_start = VMobject(
            matrix_background.copy(),
            col1.copy(),
            matrix_brackets.copy()
        )
        i_coords_end = VMobject(
            i_label_background,
            i_coords,
            i_brackets,
        )
        j_coords_start = VMobject(
            matrix_background.copy(),
            col2.copy(),
            matrix_brackets.copy()
        )
        j_coords_end = VMobject(
            j_label_background,
            j_coords,
            j_brackets,
        )

        transform_matrix1 = np.array(matrix)
        transform_matrix1[:,1] = [0, 1]
        transform_matrix2 = np.dot(
            matrix,
            np.linalg.inv(transform_matrix1)
        )

        self.dither()
        self.apply_transposed_matrix(
            transform_matrix1.transpose(),
            added_anims = [Transform(i_coords_start, i_coords_end)],
            path_arc = np.pi/2,
        )
        self.add_foreground_mobject(i_coords_start)
        self.apply_transposed_matrix(
            transform_matrix2.transpose(),
            added_anims = [Transform(j_coords_start, j_coords_end) ],
            path_arc = np.pi/2,
        )
        self.add_foreground_mobject(j_coords_start)
        self.dither()

        self.matrix = VGroup(matrix_background, matrix_mob)
        self.i_coords = i_coords_start
        self.j_coords = j_coords_start

        return vector if vector_coords is not None else None


    def scale_and_add(self, vector, vector_coords):
        i_copy = self.i_hat.copy()
        j_copy = self.j_hat.copy()
        i_target = i_copy.copy().scale(vector_coords[0]).fade(0.3)
        j_target = j_copy.copy().scale(vector_coords[1]).fade(0.3)

        coord1, coord2 = vector.copy().get_mob_matrix().flatten()
        coord1.add_background_rectangle()
        coord2.add_background_rectangle()

        self.play(
            Transform(i_copy, i_target),
            ApplyMethod(coord1.next_to, i_target.get_center(), DOWN)
        )
        self.play(
            Transform(j_copy, j_target),
            ApplyMethod(coord2.next_to, j_target.get_center(), LEFT)
        )
        j_copy.add(coord2)
        self.play(ApplyMethod(j_copy.shift, i_copy.get_end()))
        self.add_vector(j_copy.get_end())
        self.dither()

class Describe90DegreeRotation(LinearTransformationScene):
    CONFIG = {
        "transposed_matrix" : [[0, 1], [-1, 0]],
        "title" : "$90^\\circ$ rotation counterclockwise",
    }
    def construct(self):
        self.setup()
        title = TextMobject(self.title)
        title.shift(DOWN)
        title.add_background_rectangle()
        matrix = Matrix(np.array(self.transposed_matrix).transpose())
        matrix.to_corner(UP+LEFT)
        matrix_background = BackgroundRectangle(matrix)
        col1 = VMobject(*matrix.get_mob_matrix()[:,0])
        col2 = VMobject(*matrix.get_mob_matrix()[:,1])
        col1.highlight(X_COLOR)
        col2.highlight(Y_COLOR)
        self.add_foreground_mobject(matrix_background, matrix.get_brackets())

        self.dither()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.dither()
        self.play(Write(title))
        self.add_foreground_mobject(title)

        for vect, color, col in [(self.i_hat, X_COLOR, col1), (self.j_hat, Y_COLOR, col2)]:
            label = vector_coordinate_label(vect)
            label.highlight(color)
            background = BackgroundRectangle(label)
            coords = VMobject(*label.get_mob_matrix().flatten())
            brackets = label.get_brackets()

            self.play(ShowCreation(background), Write(label))
            self.dither()
            self.play(
                ShowCreation(background, rate_func = lambda t : smooth(1-t)),
                ApplyMethod(coords.replace, col),
                FadeOut(brackets),
            )
            self.remove(label)
            self.add_foreground_mobject(coords)
            self.dither()
        self.show_vector(matrix)

    def show_vector(self, matrix):
        vector = Matrix(["x", "y"])
        VMobject(*vector.get_mob_matrix().flatten()).highlight(YELLOW)
        vector.scale_to_fit_height(matrix.get_height())
        vector.next_to(matrix, RIGHT)
        v_background = BackgroundRectangle(vector)

        matrix = np.array(self.transposed_matrix).transpose()
        inv = np.linalg.inv(matrix)
        self.apply_transposed_matrix(inv.transpose(), run_time = 0.5)
        self.add_vector([1, 2])
        self.dither()
        self.apply_transposed_matrix(self.transposed_matrix)
        self.play(ShowCreation(v_background), Write(vector))
        self.dither()

class DescribeShear(Describe90DegreeRotation):
    CONFIG = {
        "transposed_matrix" : [[1, 0], [1, 1]],
        "title" : "``Shear''",
    }

class OtherWayAround(Scene):
    def construct(self):
        self.play(Write("What about the other way around?"))
        self.dither(2)

class DeduceTransformationFromMatrix(ColumnsToBasisVectors):
    def construct(self):
        self.setup()
        self.move_matrix_columns([[1, 2], [3, 1]])

class LinearlyDependentColumns(ColumnsToBasisVectors):
    def construct(self):
        self.setup()
        title = TextMobject("Linearly dependent")
        subtitle = TextMobject("columns")
        title.add_background_rectangle()
        subtitle.add_background_rectangle()
        subtitle.next_to(title, DOWN)
        title.add(subtitle)
        title.shift(UP).to_edge(LEFT)
        title.highlight(YELLOW)
        self.add_foreground_mobject(title)
        self.move_matrix_columns([[2, 1], [-2, -1]])

class NextVideo(Scene):
    def construct(self):
        title = TextMobject("Next video: Matrix multiplication as composition")
        title.to_edge(UP)
        rect = Rectangle(width = 16, height = 9, color = BLUE)
        rect.scale_to_fit_height(6)
        rect.next_to(title, DOWN)

        self.add(title)
        self.play(ShowCreation(rect))
        self.dither()

class FinalSlide(Scene):
    def construct(self):
        text = TextMobject("""
            \\footnotesize
            Technically, the definition of ``linear'' is as follows:
            A transformation L is linear if it satisfies these
            two properties:

            \\begin{align*}
                L(\\vec{\\textbf{v}} + \\vec{\\textbf{w}})
                &= L(\\vec{\\textbf{v}}) + L(\\vec{\\textbf{w}})
                & & \\text{``Additivity''} \\\\
                L(c\\vec{\\textbf{v}}) &= c L(\\vec{\\textbf{v}})
                & & \\text{``Scaling''}
            \\end{align*}

            I'll talk about these properties later on, but I'm a big
            believer in first understanding things visually.
            Once you do, it becomes much more intuitive why these
            two properties make sense.  So for now, you can
            feel fine thinking of linear transformations as those
            which keep grid lines parallel and evenly spaced
            (and which fix the origin in place), since this visual
            definition is actually equivalent to the two properties
            above.
        """, enforce_new_line_structure = False)
        text.scale_to_fit_height(2*SPACE_HEIGHT - 2)
        text.to_edge(UP)
        self.add(text)
        self.dither()

### Old scenes

class RotateIHat(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        i_hat, j_hat = self.get_basis_vectors()
        i_label, j_label = self.get_basis_vector_labels()
        self.add_vector(i_hat)
        self.play(Write(i_label, run_time = 1))
        self.dither()
        self.play(FadeOut(i_label))
        self.apply_transposed_matrix([[0, 1], [-1, 0]])
        self.dither()
        self.play(Write(j_label, run_time = 1))
        self.dither()

class TransformationsAreFunctions(Scene):
    def construct(self):
        title = TextMobject([
            """Linear transformations are a
            special kind of""",
            "function"
        ])
        title_start, function = title.split()
        function.highlight(YELLOW)
        title.to_edge(UP)

        equation = TexMobject([
            "L",
            "(",
            "\\vec{\\textbf{v}}",
            ") = ",
            "\\vec{\\textbf{w}}",
        ])
        L, lp, _input, equals, _output = equation.split()
        L.highlight(YELLOW)
        _input.highlight(MAROON_C)
        _output.highlight(BLUE)
        equation.scale(2)
        equation.next_to(title, DOWN, buff = 1)

        starting_vector = TextMobject("Starting vector")
        starting_vector.shift(DOWN+3*LEFT)
        starting_vector.highlight(MAROON_C)
        ending_vector = TextMobject("The vector where it lands")
        ending_vector.shift(DOWN).to_edge(RIGHT)
        ending_vector.highlight(BLUE)

        func_arrow = Arrow(function.get_bottom(), L.get_top(), color = YELLOW)
        start_arrow = Arrow(starting_vector.get_top(), _input.get_bottom(), color = MAROON_C)
        ending_arrow = Arrow(ending_vector, _output, color = BLUE)


        self.add(title)
        self.play(
            Write(equation),
            ShowCreation(func_arrow)
        )
        for v, a in [(starting_vector, start_arrow), (ending_vector, ending_arrow)]:
            self.play(Write(v), ShowCreation(a), run_time = 1)
        self.dither()

class UsedToThinkinfOfFunctionsAsGraphs(VectorScene):
    def construct(self):
        self.show_graph()
        self.show_inputs_and_output()

    def show_graph(self):
        axes = self.add_axes()
        graph = FunctionGraph(lambda x : x**2, x_min = -2, x_max = 2)
        name = TexMobject("f(x) = x^2")
        name.next_to(graph, RIGHT).to_edge(UP)
        point = Dot(graph.point_from_proportion(0.8))
        point_label = TexMobject("(x, x^2)")
        point_label.next_to(point, DOWN+RIGHT, buff = 0.1)

        self.play(ShowCreation(graph))
        self.play(Write(name, run_time = 1))
        self.play(
            ShowCreation(point),
            Write(point_label),
            run_time = 1
        )
        self.dither()

        def collapse_func(p):
            return np.dot(p, [RIGHT, RIGHT, OUT]) + (SPACE_HEIGHT+1)*DOWN
        self.play(
            ApplyPointwiseFunction(
                collapse_func, axes,
                submobject_mode = "all_at_once",
            ),
            ApplyPointwiseFunction(collapse_func, graph),
            ApplyMethod(point.shift, 10*DOWN),
            ApplyMethod(point_label.shift, 10*DOWN),
            ApplyFunction(lambda m : m.center().to_edge(UP), name),
            run_time = 1
        )
        self.clear()
        self.add(name)
        self.dither()

    def show_inputs_and_output(self):
        numbers = range(-3, 4)
        inputs = VMobject(*map(TexMobject, map(str, numbers)))
        inputs.arrange_submobjects(DOWN, buff = 0.5, aligned_edge = RIGHT)
        arrows = VMobject(*[
            Arrow(LEFT, RIGHT).next_to(mob)
            for mob in inputs.split()
        ])
        outputs = VMobject(*[
            TexMobject(str(num**2)).next_to(arrow)
            for num, arrow in zip(numbers, arrows.split())
        ])
        everyone = VMobject(inputs, arrows, outputs)
        everyone.center().to_edge(UP, buff = 1.5)

        self.play(Write(inputs, run_time = 1))
        self.dither()
        self.play(
            Transform(inputs.copy(), outputs),
            ShowCreation(arrows)
        )
        self.dither()

class TryingToVisualizeFourDimensions(Scene):
    def construct(self):
        randy = Randolph().to_corner()
        bubble = randy.get_bubble()
        formula = TexMobject("""
            L\\left(\\left[
                \\begin{array}{c}
                    x \\\\
                    y
                \\end{array}
            \\right]\\right) =
            \\left[
                \\begin{array}{c}
                    2x + y \\\\
                    x + 2y
                \\end{array}
            \\right]
        """)
        formula.next_to(randy, RIGHT)
        formula.split()[3].highlight(X_COLOR)
        formula.split()[4].highlight(Y_COLOR)
        VMobject(*formula.split()[9:9+4]).highlight(MAROON_C)
        VMobject(*formula.split()[13:13+4]).highlight(BLUE)
        thought = TextMobject("""
            Do I imagine plotting
            $(x, y, 2x+y, x+2y)$???
        """)
        thought.split()[-17].highlight(X_COLOR)
        thought.split()[-15].highlight(Y_COLOR)
        VMobject(*thought.split()[-13:-13+4]).highlight(MAROON_C)
        VMobject(*thought.split()[-8:-8+4]).highlight(BLUE)

        bubble.position_mobject_inside(thought)
        thought.shift(0.2*UP)

        self.add(randy)

        self.play(
            ApplyMethod(randy.look, DOWN+RIGHT),
            Write(formula)
        )
        self.play(
            ApplyMethod(randy.change_mode, "pondering"),
            ShowCreation(bubble),
            Write(thought)
        )
        self.play(Blink(randy))
        self.dither()
        self.remove(thought)
        bubble.make_green_screen()
        self.dither()
        self.play(Blink(randy))
        self.play(ApplyMethod(randy.change_mode, "confused"))
        self.dither()
        self.play(Blink(randy))
        self.dither()

class ForgetAboutGraphs(Scene):
    def construct(self):
        self.play(Write("You must unlearn graphs"))
        self.dither()

class ThinkAboutFunctionAsMovingVector(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "leave_ghost_vectors" : True,
    }
    def construct(self):
        self.setup()
        vector = self.add_vector([2, 1])
        label = self.add_transformable_label(vector, "v")
        self.dither()
        self.apply_transposed_matrix([[1, 1], [-3, 1]])
        self.dither()

class PrepareForFormalDefinition(TeacherStudentsScene):
    def construct(self):
        self.setup()
        self.teacher_says("Get ready for a formal definition!")
        self.dither(3)
        bubble = self.student_thinks("")
        bubble.make_green_screen()
        self.dither(3)

class AdditivityProperty(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "give_title" : True,
        "transposed_matrix" : [[2, 0], [1, 1]],
        "nonlinear_transformation" : None,
        "vector_v" : [2, 1],
        "vector_w" : [1, -2],
        "proclaim_sum" : True,
    }
    def construct(self):
        self.setup()
        added_anims = []
        if self.give_title:
            title = TextMobject("""
                First fundamental property of
                linear transformations
            """)
            title.to_edge(UP)
            title.highlight(YELLOW)
            title.add_background_rectangle()
            self.play(Write(title))
            added_anims.append(Animation(title))
        self.dither()
        self.play(ApplyMethod(self.plane.fade), *added_anims)

        v, w = self.draw_all_vectors()
        self.apply_transformation(added_anims)
        self.show_final_sum(v, w)

    def draw_all_vectors(self):
        v = self.add_vector(self.vector_v, color = MAROON_C)
        v_label = self.add_transformable_label(v, "v")
        w = self.add_vector(self.vector_w, color = GREEN)
        w_label = self.add_transformable_label(w, "w")
        new_w = w.copy().fade(0.4)
        self.play(ApplyMethod(new_w.shift, v.get_end()))
        sum_vect = self.add_vector(new_w.get_end(), color = PINK)
        sum_label = self.add_transformable_label(
            sum_vect,
            "%s + %s"%(v_label.expression, w_label.expression),
            rotate = True
        )
        self.play(FadeOut(new_w))
        return v, w

    def apply_transformation(self, added_anims):
        if self.nonlinear_transformation:
            self.apply_nonlinear_transformation(self.nonlinear_transformation)
        else:
            self.apply_transposed_matrix(
                self.transposed_matrix,
                added_anims = added_anims
            )
        self.dither()

    def show_final_sum(self, v, w):
        new_w = w.copy()
        self.play(ApplyMethod(new_w.shift, v.get_end()))
        self.dither()
        if self.proclaim_sum:
            text = TextMobject("It's still their sum!")
            text.add_background_rectangle()
            text.move_to(new_w.get_end(), aligned_edge = -new_w.get_end())
            text.shift_onto_screen()
            self.play(Write(text))
            self.dither()

class NonlinearLacksAdditivity(AdditivityProperty):
    CONFIG = {
        "give_title" : False,
        "nonlinear_transformation" : curvy_squish,
        "vector_v" : [3, 2],
        "vector_w" : [2, -3],
        "proclaim_sum" : False,
    }

class SecondAdditivityExample(AdditivityProperty):
    CONFIG = {
        "give_title" : False,
        "transposed_matrix" : [[1, -1], [2, 1]],
        "vector_v" : [-2, 2],
        "vector_w" : [3, 0],
        "proclaim_sum" : False,
    }

class ShowGridCreation(Scene):
    def construct(self):
        plane = NumberPlane()
        coords = VMobject(*plane.get_coordinate_labels())
        self.play(ShowCreation(plane, run_time = 3))
        self.play(Write(coords, run_time = 3))
        self.dither()

class MoveAroundAllVectors(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
        "focus_on_one_vector" : False,
        "include_background_plane" : False,
    }
    def construct(self):
        self.setup()
        vectors = VMobject(*[
            Vector([x, y])
            for x in np.arange(-int(SPACE_WIDTH)+0.5, int(SPACE_WIDTH)+0.5)
            for y in np.arange(-int(SPACE_HEIGHT)+0.5, int(SPACE_HEIGHT)+0.5)
        ])
        vectors.submobject_gradient_highlight(PINK, YELLOW)
        dots = self.get_dots(vectors)

        self.dither()
        self.play(ShowCreation(dots))
        self.dither()
        self.play(Transform(dots, vectors))
        self.dither()
        self.remove(dots)
        if self.focus_on_one_vector:
            vector = vectors.split()[43]#yeah, great coding Grant
            self.remove(vectors)
            self.add_vector(vector)
            self.play(*[
                FadeOut(v)
                for v in vectors.split()
                if v is not vector
            ])
            self.dither()
            self.add(vector.copy().highlight(DARK_GREY))
        else:
            for vector in vectors.split():
                self.add_vector(vector, animate = False)
        self.apply_transposed_matrix([[3, 0], [1, 2]])
        self.dither()
        dots = self.get_dots(vectors)
        self.play(Transform(vectors, dots))
        self.dither()

    def get_dots(self, vectors):
        return VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])

class ReasonForThinkingAboutArrows(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False
    }
    def construct(self):
        self.setup()
        self.plane.fade()
        v_color = MAROON_C
        w_color = BLUE

        v = self.add_vector([3, 1], color = v_color)
        w = self.add_vector([1, -2], color = w_color)
        vectors = VMobject(v, w)

        self.to_and_from_dots(vectors)
        self.scale_and_add(vectors)
        self.apply_transposed_matrix([[1, 1], [-1, 0]])
        self.scale_and_add(vectors)

    def to_and_from_dots(self, vectors):
        vectors_copy = vectors.copy()
        dots = VMobject(*[
            Dot(v.get_end(), color = v.get_color())
            for v in vectors.split()
        ])

        self.dither()
        self.play(Transform(vectors, dots))
        self.dither()
        self.play(Transform(vectors, vectors_copy))
        self.dither()

    def scale_and_add(self, vectors):
        vectors_copy = vectors.copy()
        v, w, = vectors.split()
        scaled_v = Vector(0.5*v.get_end(), color = v.get_color())
        scaled_w = Vector(1.5*w.get_end(), color = w.get_color())
        shifted_w = scaled_w.copy().shift(scaled_v.get_end())
        sum_vect = Vector(shifted_w.get_end(), color = PINK)

        self.play(
            ApplyMethod(v.scale, 0.5),
            ApplyMethod(w.scale, 1.5),
        )
        self.play(ApplyMethod(w.shift, v.get_end()))
        self.add_vector(sum_vect)
        self.dither()
        self.play(Transform(
            vectors, vectors_copy,
            submobject_mode = "all_at_once"
        ))
        self.dither()

class LinearTransformationWithOneVector(LinearTransformationScene):
    CONFIG = {
        "show_basis_vectors" : False,
    }
    def construct(self):
        self.setup()
        v = self.add_vector([3, 1])
        self.vector_to_coords(v)
        self.apply_transposed_matrix([[-1, 1], [-2, -1]])
        self.vector_to_coords(v)



class OpeningQuote(Scene):
    def construct(self):
        words = TextMobject([
            "It is my experience that proofs involving",
            "matrices",
            "can be shortened by 50\\% if one",
            "throws the matrices out."
        ])
        words.scale_to_fit_width(2*SPACE_WIDTH - 2)
        words.to_edge(UP)
        words.split()[1].highlight(GREEN)
        words.split()[3].highlight(BLUE)
        author = TextMobject("-Emil Artin")
        author.highlight(YELLOW)
        author.next_to(words, DOWN, buff = 0.5)

        self.play(FadeIn(words))
        self.dither(2)
        self.play(Write(author, run_time = 3))
        self.dither()

class MatrixToBlank(Scene):
    def construct(self):
        matrix = Matrix([[3, 1], [0, 2]])
        arrow = Arrow(LEFT, RIGHT)
        matrix.to_edge(LEFT)
        arrow.next_to(matrix, RIGHT)
        matrix.add(arrow)
        self.play(Write(matrix))
        self.dither()

class ExampleTransformation(LinearTransformationScene):
    def construct(self):
        self.setup()
        self.apply_transposed_matrix([[1, 2], [-1, 2]])
        self.dither(2)
