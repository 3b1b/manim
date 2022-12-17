from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union, Tuple
    from colour import Color
    import numpy as np

    # Abbreviations for a common types
    ManimColor = Union[str, Color, None]
    RangeSpecifier = Tuple[float, float, float] | Tuple[float, float]

    # TODO, Nothing about these actually specifies length,
    # they are so far just about code readability
    np_vector = np.ndarray[int, np.dtype[np.float64]]
    Vect2 = np.ndarray[int, np.dtype[np.float64]]  # TODO, specify length of 2
    Vect3 = np.ndarray[int, np.dtype[np.float64]]  # TODO, specify length of 3
    Vect4 = np.ndarray[int, np.dtype[np.float64]]  # TODO, specify length of 4
    VectN = np.ndarray[int, np.dtype[np.float64]]
    Matrix3x3 = np.ndarray[int, np.dtype[np.float64]]  # TODO, specify output size