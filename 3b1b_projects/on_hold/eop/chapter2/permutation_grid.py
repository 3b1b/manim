from manimlib.imports import *

def print_permutation(index_list):


    n = max(max(index_list), len(index_list))
    for i in range(0,n):
        if index_list[i] > n - i:
            raise Exception("Impossible indices!")

    #print "given index list:", index_list
    perm_list = n * ["_"]
    alphabet = ["A", "B", "C", "D", "E", "F",
                "G", "H", "I", "J", "K", "L",
                "M", "N", "O", "P", "Q", "R",
                "S", "T", "U", "V", "W", "X",
                "Y", "Z"]
    free_indices = list(range(n))
    free_indices_p1 = list(range(1,n + 1))
    #print perm_list
    for i in range(n):
        findex = index_list[i] - 1
        #print "place next letter at", findex + 1, "th free place"
        tindex = free_indices[findex]
        #print "so at position", tindex + 1
        perm_list[tindex] = alphabet[i]
        free_indices.remove(tindex)
        free_indices_p1.remove(tindex + 1)
        #print "remaining free places:", free_indices_p1
        #print perm_list

    return "".join(perm_list)


class PermutationGrid(Scene):

    def text_box(self, str):
        box = TextMobject(str).scale(0.3)
        box.add(SurroundingRectangle(box, stroke_color = DARK_GREY))
        return box


    def construct(self):


        N = 5

        index_list = []
        perm5_box = VGroup()
        for i in range(1, N + 1):
            index_list.append(i)
            perm4_box = VGroup()
            for j in range(1, N):
                index_list.append(j)
                perm3_box = VGroup()
                for k in range(1, N - 1):
                    index_list.append(k)
                    perm2_box = VGroup()
                    for l in range(1, N - 2):
                        index_list.append(l)
                        index_list.append(1)
                        perm_box = self.text_box(print_permutation(index_list))
                        if l > 1:
                            perm_box.next_to(perm2_box[-1], DOWN, buff = 0)
                        perm2_box.add(perm_box)
                        index_list.pop()
                        index_list.pop()
                    if k > 1:
                        perm2_box.next_to(perm3_box[-1], RIGHT, buff = 0.08)
                    perm3_box.add(perm2_box)
                    index_list.pop()
                perm3_box.add(SurroundingRectangle(perm3_box, buff = 0.12, stroke_color = LIGHT_GRAY))
                if j > 1:
                    perm3_box.next_to(perm4_box[-1], DOWN, buff = 0)
                perm4_box.add(perm3_box)
                index_list.pop()
            if i > 1:
                perm4_box.next_to(perm5_box[-1], RIGHT, buff = 0.16)
            perm5_box.add(perm4_box)
            index_list.pop()

        perm5_box.move_to(ORIGIN)
        self.add(perm5_box)




















