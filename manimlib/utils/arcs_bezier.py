import numpy as np
from manimlib.constants import *

# This methods are based on a npm library from Colin Meinke
# https://github.com/colinmeinke/svg-arc-to-cubic-bezier, which is based on
# a function from https://github.com/fontello/svgpath, I just transcipted
# everything to python

def map_to_ellipse(point, rx, ry, cosphi, sinphi, centerx, centery):
    x = point[0]
    y = point[1]
    x = x * rx
    y = y * ry
    xp = cosphi * x - sinphi * y
    yp = sinphi * x + cosphi * y
    return [xp + centerx, yp + centery]

def approx_unit_arc(ang1, ang2):
    # If 90 degree circular arc, use a constant
    # as derived from http://spencermortensen.com/articles/bezier-circle
    a = 0.551915024494 if ang2 == 1.5707963267948966 else (-0.551915024494 if ang2 == -1.5707963267948966 else 4/3 * np.tan(ang2/4))

    x1 = np.cos(ang1)
    y1 = np.sin(ang1)
    x2 = np.cos(ang1 + ang2)
    y2 = np.sin(ang1 + ang2)

    return [
        [x1 - y1 * a, y1 + x1 * a],
        [x2 + y2 * a, y2 - x2 * a],
        [x2, y2]
    ]


def vector_angle(ux, uy, vx, vy):
    sign = -1 if (ux * vy - uy * vx < 0) else 1
    dot = ux * vx + uy * vy
    if (dot > 1):
        dot = 1
    if (dot < -1):
        dot = -1
    return sign * np.arccos(dot)

def get_arc_center(px, py, cx, cy, rx, ry, largeArcFlag, sweepFlag, sinphi, cosphi, pxp, pyp):
    rxsq = rx**2
    rysq = ry**2
    pxpsq = pxp**2
    pypsq = pyp**2

    radicant = (rxsq * rysq) - (rxsq * pypsq) - (rysq * pxpsq)

    if (radicant < 0):
        radicant = 0

    radicant = radicant / ((rxsq * pypsq) + (rysq * pxpsq))
    radicant = np.sqrt(radicant) * (-1 if largeArcFlag == sweepFlag else 1)

    centerxp = radicant * rx / ry * pyp
    centeryp = radicant * -ry / rx * pxp

    centerx = cosphi * centerxp - sinphi * centeryp + (px + cx) / 2
    centery = sinphi * centerxp + cosphi * centeryp + (py + cy) / 2

    vx1 = ( pxp - centerxp) / rx
    vy1 = ( pyp - centeryp) / ry
    vx2 = (-pxp - centerxp) / rx
    vy2 = (-pyp - centeryp) / ry

    ang1 = vector_angle(  1,   0, vx1, vy1)
    ang2 = vector_angle(vx1, vy1, vx2, vy2)

    if sweepFlag == 0 and ang2 > 0:
        ang2 = ang2 - TAU

    if sweepFlag == 1 and ang2 < 0:
        ang2 = ang2 + TAU

    return [ centerx, centery, ang1, ang2 ]


def arc_to_bezier(px, py, cx, cy, rx, ry, xAxisRotation = 0, largeArcFlag = 0, sweepFlag = 0):
    curves = []

    if rx == 0 or ry == 0:
        return []

    sinphi = np.sin(xAxisRotation * TAU / 360)
    cosphi = np.cos(xAxisRotation * TAU / 360)

    pxp =  cosphi * (px - cx) / 2 + sinphi * (py - cy) / 2
    pyp = -sinphi * (px - cx) / 2 + cosphi * (py - cy) / 2

    if (pxp == 0 and pyp == 0):
        return []

    rx = np.abs(rx)
    ry = np.abs(ry)

    lambda_v = pxp**2/rx**2 + pyp**2/ry**2

    if lambda_v > 1:
        rx = rx * np.sqrt(lambda_v)
        ry = ry * np.sqrt(lambda_v)

    [ centerx, centery, ang1, ang2 ] = get_arc_center(
        px,
        py,
        cx,
        cy,
        rx,
        ry,
        largeArcFlag,
        sweepFlag,
        sinphi,
        cosphi,
        pxp,
        pyp
    )

    # If 'ang2' == 90.0000000001, then `ratio` will evaluate to
    # 1.0000000001. This causes `segments` to be greater than one, which is an
    # unecessary split, and adds extra points to the bezier curve. To alleviate
    # this issue, we round to 1.0 when the ratio is close to 1.0.
    ratio = np.abs(ang2) / (TAU / 4)
    if np.abs(1.0 - ratio) < 0.0000001:
        ratio = 1.0

    segments = np.max([np.ceil(ratio), 1])

    ang2 = ang2 / segments

    for i in range(int(segments)):
        curves.append(approx_unit_arc(ang1, ang2))
        ang1 = ang1 + ang2

    output_curves = []

    for curve in curves:
        [x1, y1] = map_to_ellipse(curve[0], rx, ry, cosphi, sinphi, centerx, centery)
        [x2, y2] = map_to_ellipse(curve[1], rx, ry, cosphi, sinphi, centerx, centery)
        [ x,  y] = map_to_ellipse(curve[2], rx, ry, cosphi, sinphi, centerx, centery)
        output_curves.append([[x1, y1, 0], [x2, y2, 0], [x, y, 0]])

    return output_curves