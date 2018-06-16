from big_ol_pile_of_manim_imports import *
from scipy.cluster.vq import vq, kmeans, whiten
from scipy.stats import norm
import numpy.linalg as la
import re
from collections import defaultdict

class DynamicEquation(Group):
    def __init__(self, *tex_strings, **kwargs):
        tex_strings = list(tex_strings)
        self.tex_strings = map(lambda x: x.replace("&", ""), tex_strings)

        for i in range(len(tex_strings)):
            tex_strings[i] += "\\\\"
        aligned_equations_mobject = TexMobject("""
            {}
        """.format("\n".join(tex_strings)), **kwargs)

        locations = np.array([
            mob.get_center() 
            for mob in aligned_equations_mobject.submobjects[0].submobjects
        ])
        
        ## LOLOLOLOLOLOLOLOLOLOLOLOLOLOLOLOLOL
        #y_offsets = locations[:,[1]]
        #whitened_offsets = whiten(y_offsets)
        #means = kmeans(whitened_offsets, len(tex_strings))
        #means = np.flipud(np.sort(means[0], 0))

        #lines = np.argmin(
        #    np.abs(whitened_offsets - means.T), 1
        #)

        #aligned_equations = [TexMobject() for _ in tex_strings]
        #for i, mob in enumerate(aligned_equations_mobject.submobjects[0] \
        #                                                 .submobjects):
        #    aligned_equations[lines[i]].add(mob)
        ## LOLOLOLOLOLOLOLOLOLOLOLOLOLOLOLOLOL

        self.tex_chars = [[] for x in tex_strings]
        aligned_equations = [TexMobject() for _ in tex_strings]
        next_mobject = 0
        for i in range(len(self.tex_strings)):
            tokens = self.tex_strings[i].split()
            for j, token in enumerate(self.tex_strings[i].split()):
                aligned_equations[i] \
                        .add(aligned_equations_mobject \
                        .submobjects[0].submobjects[next_mobject])
                next_mobject += 1
                self.tex_chars[i].append(token)
                
        self.aligned_equations = aligned_equations
        self.current_equation_index = 0
        self.current_equation = \
                self.aligned_equations[self.current_equation_index].copy()
        Group.__init__(self, self.current_equation)

    # TODO: specify occurrence other than first
    def mob_from_char(self, equation_index, target, match_num=0, texmobject=None):
        for char_index, char in enumerate(self.tex_chars[equation_index]):
            if char == target:
                if texmobject:
                    return texmobject.submobjects[char_index]
                else:
                    return self.aligned_equations[equation_index] \
                               .submobjects[char_index]
        print "oops"
        print self.tex_chars[equation_index]
        print target
        import pdb; pdb.set_trace()

    def shift(self, *vectors):
        self.current_equation.shift(*vectors)
        for eq in self.aligned_equations:
            eq.shift(*vectors)

    def transform_equation(self,
                           target_equation_index,
                           align_char,
                           initial_groups,
                           target_groups,
                           scene):
        initial_equation_mob = self.current_equation
        target_equation_mob = self.equation_at_index(target_equation_index).copy()
        initial_equation_tex = self.tex_strings[self.current_equation_index]
        target_equation_tex = self.tex_strings[target_equation_index]

        # align initial and final equations
        difference_vec = \
            self.mob_from_char(
                self.current_equation_index,
                align_char,
                texmobject=self.current_equation).get_center() - \
            self.mob_from_char(
                target_equation_index,
                align_char
            ).get_center()
        target_equation_mob.shift(difference_vec)

        # map symbols to each other

        # regexes should be equal when groups are removed
        # TODO: do you only need one regex?
        assert(
            re.sub("\([^)]*\)", "", initial_groups) == \
            re.sub("\([^)]*\)", "", target_groups)
        )

        # regexes should match the entire equation
        initial_equation_match = re.match(initial_groups,
                initial_equation_tex)
        target_equation_match = re.match(target_groups,
                target_equation_tex)
        assert(initial_equation_match)
        assert(target_equation_match)
        assert(initial_equation_match.group(0) == initial_equation_tex)
        assert(target_equation_match.group(0) == target_equation_tex)

        # number of groups should be equal
        assert(len(initial_equation_match.groups()) == \
            len(target_equation_match.groups()))

        anims = []
        initial_counts = defaultdict(int)
        target_counts = defaultdict(int)
        group_regex = "\([^)]*\)"
        group_number = 1
        for token in initial_groups.split():
            if token[0] == "\\":
                token = token[1:]
            if re.match(group_regex, token):
                group1 = Group()
                for token in initial_equation_match.group(group_number).split():
                    group1.add(self.mob_from_char(
                        self.current_equation_index,
                        token,
                        match_num=initial_counts[token],
                        texmobject=initial_equation_mob,
                    ))
                    initial_counts[token] += 1
                group2 = VGroup()
                for token in target_equation_match.group(group_number).split():
                    group2.add(self.mob_from_char(
                        target_equation_index,
                        token,
                        match_num=target_counts[token],
                        texmobject=target_equation_mob,
                    ))
                    target_counts[token] += 1
                anims.append(ReplacementTransform(group1, group2))
                group_number += 1
            else:
                anims.append(ReplacementTransform(
                    self.mob_from_char(
                        self.current_equation_index,
                        token,
                        match_num=initial_counts[token],
                        texmobject=initial_equation_mob,
                    ),
                    self.mob_from_char(
                        target_equation_index,
                        token,
                        match_num=target_counts[token],
                        texmobject=target_equation_mob,
                    )
                ))
                initial_counts[token] += 1
                target_counts[token] += 1

        #anims.append(ReplacementTransform(
        #    initial_equation,
        #    target_equation,
        #))
        #for group1_indices, group2_indices in transform_list:
        #    group1 = Group(*map(
        #        lambda i: self.current_equation.submobjects[i],
        #        group1_indices
        #    ))
        #    group2 = Group(*map(
        #        lambda i: target_equation.submobjects[i],
        #        group2_indices
        #    ))
        #    # append the transformation
        #    transform = ReplacementTransform(group1, group2)
        #    anims.append(transform)

        # return the callback to fix instance variables
        def callback_generator():
            def callback():
                self.remove(self.current_equation)
                self.current_equation_index = target_equation_index
                self.current_equation = target_equation_mob
                self.add(self.current_equation.copy())
            return callback
        callback = callback_generator()
        return anims, callback

    def equation_at_index(self, index):
        return self.aligned_equations[index]

    def symbol_at_index(self, index):
        return self.current_equation.submobjects[index]

    def symbols_at_indices(self, *indices):
        return Group(*map(lambda x: self.symbol_at_index(x), indices))
        return self.current_equation.submobjects[index]

    def equation_from_tex(self, index):
        pass

    def indicate_equation(self, scene):
        for mob in self.current_equation.submobjects:
            scene.play(Indicate(mob))
