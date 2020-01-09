from manimlib.constants import *
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.config_ops import digest_config
import math


def _symmetrize(dic: dict):
    symm = {}
    for key, value in dic.items():
        symm[value] = key

    symm.update(dic)
    return symm


class ImplicitFunction(VMobject):
    """
    Graphs an implicit function defined by f(x,y) = 0
    """
    CONFIG = {
        "res": 50
    }

    def __init__(self, function=None, **kwargs):
        """
        :param function: Function of k and y to graph isocontour f(x,y)=0
        """
        digest_config(self, kwargs)
        self.function = function

        VMobject.__init__(self, **kwargs)

    def get_function(self):
        return self.function

    def get_function_val_at_point(self, x, y):
        return self.function(x, y)

    def sample_function_mask(self):
        """
        :return: A mask over the plane at the specified resolution capturing function
                 values at each point.
        """
        delta_x = self.x_max - self.x_min
        delta_y = self.y_max - self.y_min
        mask = []  # format: [point, val]
        for yi in range(0, self.res):
            dy = delta_y*(yi/self.res)
            y = self.y_min + dy
            vals = []
            for xi in range(0, self.res):
                dx = delta_x*(xi/self.res)
                x = self.x_min + dx
                point = np.array([x, y, 0])
                val = self.get_function_val_at_point(x, y)
                if val > 0:
                    vals.append([point, 1])
                elif val <= 0:
                    vals.append([point, 0])
            mask.append(vals)
        return mask

    def get_contours(self):
        """
        :return: A dictionary consisting of start -> list(end) points to generate contours.
        """
        mask = self.sample_function_mask()
        contours = {}
        for yi in range(0, len(mask)-1):
            yarr = mask[yi]
            nyarr = mask[yi+1]
            for xi in range(0, len(yarr)-1):
                tl = yarr[xi]
                tr = yarr[xi+1]
                bl = nyarr[xi]
                br = nyarr[xi+1]

                tlp = tl[0]
                tlv = tl[1]

                trp = tr[0]
                trv = tr[1]

                blp = bl[0]
                blv = bl[1]

                brp = br[0]
                brv = br[1]

                vals = [tlv, trv, brv, blv]  # change order to match marching squares order.
                vals_strs = list(map(lambda i: str(i), vals))
                vals_str = "".join(vals_strs)

                def calc_lin_interp(fc, fe, cv, ev):
                    """
                    :param fc: Function value at 'center' vertex
                    :param fe: Function value at 'edge' vertex
                    :param cv: The 'location' of the 'center' vertex (x or y depending)
                    :param ev: Similar to above for 'edge' vertex
                    :return: The x or y coordinate of the linear interpolation
                    """
                    return -(fc/(fe-fc))*(ev-cv) + cv

                def calc_lin_interp_diag(cent, side, vert):
                    """
                    :param cent: 'Center' point
                    :param side: 'Side' point w.r.t. cent
                    :param vert: 'Vertical' point w.r.t. cent
                    :return: Dict detailing path to follow of linear interpolation.
                    """
                    centx, centy = cent[:2]

                    sidex, sidey = side[:2]

                    vertx, verty = vert[:2]

                    qx = vertx
                    py = sidey

                    f_cent = self.get_function_val_at_point(centx, centy)
                    f_vert = self.get_function_val_at_point(vertx, verty)
                    f_side = self.get_function_val_at_point(sidex, sidey)

                    qy = calc_lin_interp(f_cent, f_vert, centy, verty)
                    px = calc_lin_interp(f_cent, f_side, centx, sidex)

                    p = (px, py, 0)
                    q = (qx, qy, 0)
                    return _symmetrize({p:q})

                def calc_lin_interp_sides():
                    """
                    :return: Horizontal linear interpolation
                    """
                    tlx, tly = tlp[:2]
                    trx, tr_y = trp[:2]
                    blx, bly = blp[:2]
                    brx, bry = brp[:2]

                    ftl = self.get_function_val_at_point(tlx, tly)
                    ftr = self.get_function_val_at_point(trx, tr_y)
                    fbl = self.get_function_val_at_point(blx, bly)
                    fbr = self.get_function_val_at_point(brx, bry)

                    px = tlx
                    qx = trx

                    py = calc_lin_interp(fbl, ftl, bly, tly)
                    qy = calc_lin_interp(fbr, ftr, bry, tr_y)

                    p = (px, py, 0)
                    q = (qx, qy, 0)

                    return _symmetrize({p:q})

                def calc_lin_interp_vert():
                    """
                    :return: Vertical linear interpolation
                    """
                    tlx, tly = tlp[:2]
                    trx, tr_y = trp[:2]
                    blx, bly = blp[:2]
                    brx, bry = brp[:2]

                    ftl = self.get_function_val_at_point(tlx, tly)
                    ftr = self.get_function_val_at_point(trx, tr_y)
                    fbl = self.get_function_val_at_point(blx, bly)
                    fbr = self.get_function_val_at_point(brx, bry)

                    py = bly
                    qy = tly

                    px = calc_lin_interp(fbl, fbr, blx, brx)
                    qx = calc_lin_interp(ftl, ftr, tlx, trx)

                    p = (px, py, 0)
                    q = (qx, qy, 0)

                    return _symmetrize({p:q})

                m_sqrs_dict = {
                    "0000": {},
                    "0001": calc_lin_interp_diag(blp, brp, tlp),
                    "0010": calc_lin_interp_diag(brp, blp, trp),
                    "0011": calc_lin_interp_sides(),
                    "0100": calc_lin_interp_diag(trp, tlp, brp),
                    "0101": {**calc_lin_interp_diag(tlp, trp, blp), **calc_lin_interp_diag(brp, blp, trp)},
                    "0110": calc_lin_interp_vert(),
                    "0111": calc_lin_interp_diag(tlp, trp, blp),
                    "1000": calc_lin_interp_diag(tlp, trp, blp),
                    "1001": calc_lin_interp_vert(),
                    "1010": {**calc_lin_interp_diag(trp, tlp, brp), **calc_lin_interp_diag(blp, brp, tlp)},
                    "1011": calc_lin_interp_diag(trp, tlp, brp),
                    "1100": calc_lin_interp_sides(),
                    "1101": calc_lin_interp_diag(brp, blp, trp),
                    "1110": calc_lin_interp_diag(blp, brp, tlp),
                    "1111": {}
                }
                # Dictionary describing how to form path given the binary signature.
                dic = m_sqrs_dict[vals_str]
                for k, v in dic.items():
                    if k in contours.keys() and v not in contours[k]:
                        contours[k].append(v)
                    elif k not in contours.keys():
                        contours[k] = [v]

        return contours

    def generate_points(self):
        contours = self.get_contours()

        def try_rem(arr, val):
            if val in arr:
                arr.remove(val)
            return arr

        def len_filter(dic):
            return {k: arr for k, arr in dic.items() if len(arr) > 0}
        """
        This generates path basically in a follow-the-points sort of manner.
        It starts at the 'first points' in the dictionary, starts a path at the
        'start' point and iteratively follows the path from the current point 
        to the first point in the current point's list of adjacent points.
        It does this until there is nowhere else to go for that curve and then
        proceeds to the next curve. At every point, current points are removed from
        the contours just to ensure no vertices are visited more than once.
        """
        while len(len_filter(contours).keys()) > 0:
            sptt, eptts = next(iter(len_filter(contours).items()))
            eptt = eptts[0]
            spta = np.array(sptt)
            epta = np.array(eptt)
            contours[sptt] = try_rem(contours[sptt], eptt)
            contours = {k: try_rem(arr, sptt) for k, arr in contours.items()}
            self.start_new_path(spta)
            cur_pt = epta
            pts = []
            while cur_pt is not None:
                pts.append(cur_pt)
                cur_ptt = tuple(cur_pt)
                if len(contours[cur_ptt])>0:
                    next_ptt = contours[cur_ptt][0]
                    next_pt = np.array(next_ptt)
                    cur_pt = next_pt
                    contours[cur_ptt] = try_rem(contours[cur_ptt], next_ptt)
                    contours = {k: try_rem(arr, cur_ptt) for k, arr in contours.items()}
                else:
                    cur_pt = None
            self.add_points_as_corners(pts)
        self.make_smooth()
        return self


class ParametricFunction(VMobject):
    CONFIG = {
        "t_min": 0,
        "t_max": 1,
        "step_size": 0.01,  # Use "auto" (lowercase) for automatic step size
        "dt": 1e-8,
        # TODO, be smarter about figuring these out?
        "discontinuities": [],
        "tol_point": 1e5,
        "tol_del_mult": 1e-2
    }

    def __init__(self, function=None, **kwargs):
        # either get a function from __init__ or from CONFIG
        self.function = function or self.function
        VMobject.__init__(self, **kwargs)

    def get_function(self):
        return self.function

    def get_point_from_function(self, t):
        return self.function(t)

    def get_step_size(self, t=None):
        if self.step_size == "auto":
            """
            for x between -1 to 1, return 0.01
            else, return log10(x) (rounded)
            e.g.: 10.5 -> 0.1 ; 1040 -> 10
            """
            if t == 0:
                scale = 0
            else:
                scale = math.log10(abs(t))
                if scale < 0:
                    scale = 0

                scale = math.floor(scale)

            scale -= 2
            return math.pow(10, scale)
        else:
            return self.step_size

    """
    tol_point is the tolerance level for the coordinates of points.
        If either the x coordinate or y coordinate are greater than
        the tolerance then that point is considered a discontinuity.
        This treats infinite discontinuities.
    
    tol_del_mult is a bit more complicated.
        A function is continuous if for any specified change in the
        function you can find a change in the input that gives rise
        to a change in the function less than the specified change.
        To test if the function is continuous, we test if the change
        in the function at different resolutions for changes in x
        get smaller as the change gets smaller, or if the changes
        become constant. If they get smaller, the function is 
        continuous at the point, if they level off then it is
        discontinuous.
        This treats break discontinuities.
    """
    
    def point_is_finite(self, point):
        x,y = point[:2]
        mag = np.sqrt(x**2 + y**2)
        return mag <= self.tol_point
    
    def get_discontinuities(self):
        disconts = []
        for t in np.arange(self.t_min-2*self.step_size, self.t_max+2*self.step_size, self.step_size):
            p1 = self.function(t)
            x1,y1 = p1[:2]
            if not self.point_is_finite(p1):
                disconts.append(t)
                continue

            ss1 = self.get_step_size(t)
            ss2 = ss1/2
            ss3 = ss1/10
            
            t2 = t + ss1
            t3 = t + ss2
            t4 = t + ss3
            
            p2 = self.function(t2)
            p3 = self.function(t3)
            p4 = self.function(t4)
            
            def calc_delta_mag(p1, p2):
              delta = p2-p1
              return np.sqrt(delta.dot(delta))
            
            d1 = calc_delta_mag(p1,p2)
            d2 = calc_delta_mag(p1,p3)
            d3 = calc_delta_mag(p1,p4)
            #Seeing delta at different resulotions
            
            if np.abs(d2-d1)<self.tol_del_mult*ss2 or np.abs(d3-d1)<self.tol_del_mult*ss3:
              disconts.append(t)
            
        return disconts

    def generate_points(self):
        t_min, t_max = self.t_min, self.t_max
        dt = self.dt
        
        self.discontinuities = self.get_discontinuities()
        discontinuities = np.array(list(self.discontinuities))
        
        boundary_times = [
            self.t_min, self.t_max,
            *(discontinuities - dt),
            *(discontinuities + dt),
        ]
        boundary_times.sort()
        for t1, t2 in zip(boundary_times[0::2], boundary_times[1::2]):
            t_range = list(np.arange(t1, t2, self.get_step_size(t1)))
            if t_range[-1] != t2:
                t_range.append(t2)
            points_l = []
            for t in t_range:
                point = self.function(t)
                if self.point_is_finite(point):
                    points_l.append(point)
            points = np.array(points_l)
            if len(points) > 0:
                self.start_new_path(points[0])
                self.add_points_as_corners(points[1:])
        self.make_smooth()
        return self


class FunctionGraph(ParametricFunction):
    CONFIG = {
        "color": YELLOW,
        "x_min": -FRAME_X_RADIUS,
        "x_max": FRAME_X_RADIUS,
    }

    def __init__(self, function, **kwargs):
        digest_config(self, kwargs)
        self.parametric_function = \
            lambda t: np.array([t, function(t), 0])
        ParametricFunction.__init__(
            self,
            self.parametric_function,
            t_min=self.x_min,
            t_max=self.x_max,
            **kwargs
        )
        self.function = function

    def get_function(self):
        return self.function

    def get_point_from_function(self, x):
        return self.parametric_function(x)

