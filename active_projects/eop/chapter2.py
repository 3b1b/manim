from big_ol_pile_of_manim_imports import *

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
    free_indices = range(n)
    free_indices_p1 = range(1,n + 1)
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





N = 5

index_list = []
for i in range(1, N + 1):
    index_list.append(i)
    for j in range(1, N):
        index_list.append(j)
        for k in range(1, N - 1):
            index_list.append(k)
            for l in range(1, N - 2):
                index_list.append(l)
                for m in range(1, N - 3):
                    index_list.append(m)
                    print print_permutation(index_list)
                    index_list.pop()
                index_list.pop()
            index_list.pop()
        index_list.pop()
    index_list.pop()
















