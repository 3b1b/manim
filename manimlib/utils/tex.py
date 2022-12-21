import re

def num_tex_symbols(tex: str) -> int:
    """
    This function attempts to estimate the number of symbols that
    a given string of tex would produce.
    
    No guarantees this is accurate.
    """
    count_to_subtrs = [
        (0, [
            "emph", "textbf", "big", "Big", "small", "Small",
            "quad", "qquad", ",", ";", "ghost",
            *"^{} \n\t_",
        ]),
        (2, ["sqrt", "ne"]),
        (6, ["underbrace"]),
        # Replace all other \expressions (like "\pi") with a single character
        # Deliberately put this last.
        (1, ["[a-zA-Z]+"])
    ]
    for count, substrs in count_to_subtrs:
        # Replace occurances of the given substrings with `count` characters
        pattern = "|".join((R"\\" + s for s in substrs ))
        tex = re.sub(pattern, "X" * count, tex)
    # Ignore various control characters
    return sum(map(lambda c: c not in "^{} \n\t_", tex))
