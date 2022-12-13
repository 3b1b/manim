# from @有一种悲伤叫颓废

"""
注：
    1. 视频讲解：https://www.bilibili.com/video/BV1JV411B7T1、https://www.bilibili.com/video/BV15y4y1J7K7
    2. 主要用来多边形布尔运算的问题，可以套娃，存在bug，一般情况应该够用，如发现bug请联系颓废
    3. 支持的多边形有，Polygon, RegularPolygon, Circle, Ellipse, ParametricCurve, Dot, Line, VGroup
    4. 但主要用于Polygon, VGroup应该有很多bug
    5. 只需导入三个函数：PolygonIntersection(求交)，PolygonUnion(求加)，PolygonSubtraction(求减)
"""


from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import *
from manimlib.scene.scene import Scene
from manimlib.mobject.functions import ParametricCurve
from manimlib.constants import PI
from manimlib.utils.config_ops import digest_config
#from manimlib.imports import *
#from manim_sandbox.utils.imports import *
#import time

# 以下比例建议2不要乱改，精度大，或者小，都有可能出bug
# 小于误差则等
ev = np.exp(1)**PI/10000000
ev_sq = ev**2
# 刁钻比例，在(0,1)内找一个比例
cunning_proportion = np.exp(np.exp(1)/PI)/PI

# b在向量pq左为正，右为负，O(1)
def cross2(p, q, b):
    '''
    叉积公式
    \begin{align}
    ToLeft(p, q, b)=\begin{vmatrix}
    x_p & y_p & 1\\
    x_q & y_q & 1\\
    x_b & y_b & 1\\
    \end{vmatrix}\end{align}
    '''
    return p[0]*q[1] - p[1]*q[0] + \
           q[0]*b[1] - q[1]*b[0] + \
           b[0]*p[1] - b[1]*p[0]

# 忽略误差，b在向量pq左为正，右为负，O(1)
def ToLeft(p, q, b):
    a = cross2(p, q, b)
    # 小于误差，认为在向量上
    if abs(a) < ev:
        return 0
    # 隐含else abs(a) >= ev:
    return a

# 凸包，O(nlogn)
def Graham(points):
    points.sort(key=lambda m: m[0])
    convex = []
    for i in range(len(points)):
        while len(convex) > 1 and ToLeft(convex[-1], convex[-2], points[i]) >= 0:
            convex.pop()
        convex.append(points[i])

    mark = len(convex)

    for i in range(len(points) - 2, -1, -1):
        while len(convex) > mark and ToLeft(convex[-1], convex[-2], points[i]) >= 0:
            convex.pop()
        convex.append(points[i])
    return convex

# 判断两个点是否相等，小于误差的平方，则相等，O(1)
def point_is_equal(p, q):
    p, q = np.array(p), np.array(q)
    # 两点距离的平方小于误差的平方，则相等
    if np.dot(q-p, q-p) < ev_sq:
        return True
    return False

# 忽略误差的多边形面积，O(n)
def polygon_area(polygon):
    '''
    即对每一个多边形做叉积
    \begin{align}
    S_{\Omega}=\sum_{k=0}^{\infty}S_{\triangle OP_kP_{k+1}}
    \end{align}
    也就是S = 1 / 2 * abs(sum([cross2(a[i], a[(i + 1) % l], ORIGIN) for i in range(l)]))
    '''
    a = polygon.get_vertices()
    l = len(a)
    ans = 1 / 2 * abs(sum([a[i][0] * a[(i + 1) % l][1] - a[(i + 1) % l][0] * a[i][1] for i in range(l)]))
    if ans < ev:
        return 0
    return ans

# 线段存在交点，求线段交点，O(1)
def get_intersection_of_2segments(seg1, seg2):
    '''
    \begin{align}
    & 求线段AB和线段CD交点，前提是交点存在\\
    & d_1 = |\overrightarrow{CA}\times\overrightarrow{CB}|\\
    & d_2 = |\overrightarrow{DA}\times\overrightarrow{DB}|\\
    & IntersectionPoint = \overrightarrow{OC}+\frac{d_1}{d_1+d_2}\overrightarrow{CD}
    \end{align}
    '''
    seg1, seg2 = np.array(seg1), np.array(seg2)
    d1 = abs(cross2(seg1[0], seg1[1], seg2[0]))
    d2 = abs(cross2(seg1[0], seg1[1], seg2[1]))
    return seg2[0]+(seg2[1]-seg2[0])*d1/(d1+d2)

# 求直线交点，O(1)
def get_intersection_of_2lines(line1, line2):
    '''
    \begin{align}
    \begin{cases}
    & a_1x+b_1y=c_1\\
    & a_2x+b_2y=c_2
    \end{cases}\Longrightarrow(x,y)=(
    \frac{\begin{vmatrix}c_1&b_1\\c_2&b_2\end{vmatrix}}{\begin{vmatrix}a_1&b_1\\a_2&b_2\end{vmatrix}},
    \frac{\begin{vmatrix}a_1&c_1\\a_2&c_2\end{vmatrix}}{\begin{vmatrix}a_1&b_1\\a_2&b_2\end{vmatrix}})
    \end{align}
    '''
    # 直线方程为Ax+By=C,A=y2-y1,B=x1-x2,C=x1*y2-x2*y1
    a1, b1, c1 = line1[1][1]-line1[0][1], line1[0][0]-line1[1][0], line1[0][0]*line1[1][1]-line1[1][0]*line1[0][1]
    a2, b2, c2 = line2[1][1]-line2[0][1], line2[0][0]-line2[1][0], line2[0][0]*line2[1][1]-line2[1][0]*line2[0][1]
    # 克拉默法则解交点
    c = a1 * b2 - b1 * a2
    # 平行无交点
    if abs(c) < ev:
        #print("直线平行或重合")
        return [False, a1, b1, c1, a2, b2, c2, c]
    # 隐含else不平行
    return np.array([(c1 * b2 - b1 * c2)/c, (a1 * c2 - c1 * a2)/c, 0])

# 线段是否重合，部分重合，O(1)
def segment_is_overlap(seg1, seg2):
    # seg2的顶点都在seg1上，且其在两坐标轴的投影在seg1投影的内部（非严格）
    return ToLeft(seg1[0], seg1[1], seg2[0]) == 0 and ToLeft(seg1[0], seg1[1], seg2[1]) == 0 and \
           (seg1[0][0]-ev < seg2[0][0] < seg1[1][0]+ev or seg1[0][0]-ev < seg2[1][0] < seg1[1][0]+ev) and \
           (seg1[0][1]-ev < seg2[0][1] < seg1[1][1]+ev or seg1[0][1]-ev < seg2[1][1] < seg1[1][1]+ev)

# 线段是否重合，部分重合，不能只重合顶点，O(1)
def segment_is_overlap2(seg1, seg2):
    # seg2的顶点都在seg1上，且其在两坐标轴的投影在seg1投影的内部（非严格）
    return ToLeft(seg1[0], seg1[1], seg2[0]) == 0 and ToLeft(seg1[0], seg1[1], seg2[1]) == 0 and \
           (seg1[0][0]+ev < seg2[0][0] < seg1[1][0]-ev or seg1[0][0]+ev < seg2[1][0] < seg1[1][0]-ev) and \
           (seg1[0][1]+ev < seg2[0][1] < seg1[1][1]-ev or seg1[0][1]+ev < seg2[1][1] < seg1[1][1]-ev)

# 线段是否重合，严格重合，即线段相等（误差内相等），O(1)
def segment_is_strict_overlap(seg1, seg2):
    # 两线段相等，即两顶点相等或交换相等
    return point_is_equal(seg1[0], seg2[0]) and point_is_equal(seg1[1], seg2[1]) or \
           point_is_equal(seg1[1], seg2[0]) and point_is_equal(seg1[0], seg2[1])

# 线段1包含线段2，可以相等，O(1)
def segment1_contains_segment2(seg1, seg2):
    # seg2的顶点都在seg1上，且其在两坐标轴的投影在seg1投影的上面（非严格），两线段（在误差内）可以相等
    if ToLeft(seg1[0], seg1[1], seg2[0]) == 0 and ToLeft(seg1[0], seg1[1], seg2[1]) == 0:
        if seg1[0][0] > seg1[1][0]:
            seg1[0][0], seg1[1][0] = seg1[1][0], seg1[0][0]
        if seg1[0][1] > seg1[1][1]:
            seg1[0][1], seg1[1][1] = seg1[1][1], seg1[0][1]
        return seg1[0][0]-ev < seg2[0][0] < seg1[1][0]+ev and seg1[0][0]-ev < seg2[1][0] < seg1[1][0]+ev and \
               seg1[0][1]-ev < seg2[0][1] < seg1[1][1]+ev and seg1[0][1]-ev < seg2[1][1] < seg1[1][1]+ev
    # 隐含两线段不重合
    return False

# 线段1严格包含线段2，不能相等，O(1)
def segment1_strict_contains_segment2(seg1, seg2):
    # seg2的顶点都在seg1内，且其在两坐标轴的投影在seg1投影的内部（严格），两线段（在误差内）不能相等
    if ToLeft(seg1[0], seg1[1], seg2[0]) == 0 and ToLeft(seg1[0], seg1[1], seg2[1]) == 0:
        if seg1[0][0] > seg1[1][0]:
            seg1[0][0], seg1[1][0] = seg1[1][0], seg1[0][0]
        if seg1[0][1] > seg1[1][1]:
            seg1[0][1], seg1[1][1] = seg1[1][1], seg1[0][1]
        return seg1[0][0]+ev < seg2[0][0] < seg1[1][0]-ev and seg1[0][0]+ev < seg2[1][0] < seg1[1][0]-ev and \
               seg1[0][1]+ev < seg2[0][1] < seg1[1][1]-ev and seg1[0][1]+ev < seg2[1][1] < seg1[1][1]-ev
    # 隐含两线段不重合
    return False

# 交点可以在端点，O(1)
def segment_is_intersect(seg1, seg2):
    '''
    \begin{align}
    & 跨立实验：两条线段在坐标轴上的投影不重合，则不可能相交\\
    & 快速排斥实验：点A和B在CD的两边，并且点C和D在AB的两边，则相交，取等表示可以在端点或线段上相交\\
    & 即\overrightarrow{AC}\times\overrightarrow{CD}\cdot\overrightarrow{BC}\times\overrightarrow{CD}<=0,
    \overrightarrow{CA}\times\overrightarrow{AB}\cdot\overrightarrow{DA}\times\overrightarrow{AB}<=0
    \end{align}
    '''
    seg1, seg2 = np.array(seg1), np.array(seg2)
    # 快速排斥实验
    if min(seg2[0][0], seg2[1][0]) - max(seg1[0][0], seg1[1][0]) > ev or \
            min(seg1[0][0], seg1[1][0]) - max(seg2[0][0], seg2[1][0]) > ev or \
            min(seg2[0][1], seg2[1][1]) - max(seg1[0][1], seg1[1][1]) > ev or \
            min(seg1[0][1], seg1[1][1]) - max(seg2[0][1], seg2[1][1]) > ev:
        return False
    # 跨立实验
    if ToLeft(seg1[0], seg1[1], seg2[0]) * ToLeft(seg1[0], seg1[1], seg2[1]) <= 0 and \
            ToLeft(seg2[0], seg2[1], seg1[0]) * ToLeft(seg2[0], seg2[1], seg1[1]) <= 0:
        return True
    # 未通过跨立实验
    return False

# 交点不能是端点，也不能在线段内，O(1)
def segment_is_strict_intersect(seg1, seg2):
    '''
    \begin{align}
    & 跨立实验：两条线段在坐标轴上的投影不重合，则不可能相交\\
    & 快速排斥实验：点A和B在CD的两边，并且点C和D在AB的两边，则相交，不取等表示不可以在端点或线段上相交\\
    & 即\overrightarrow{AC}\times\overrightarrow{CD}\cdot\overrightarrow{BC}\times\overrightarrow{CD}<0,
    \overrightarrow{CA}\times\overrightarrow{AB}\cdot\overrightarrow{DA}\times\overrightarrow{AB}<0
    \end{align}
    '''
    seg1, seg2 = np.array(seg1), np.array(seg2)
    # 快速排斥实验
    if min(seg2[0][0], seg2[1][0]) - max(seg1[0][0], seg1[1][0]) > ev or \
            min(seg1[0][0], seg1[1][0]) - max(seg2[0][0], seg2[1][0]) > ev or \
            min(seg2[0][1], seg2[1][1]) - max(seg1[0][1], seg1[1][1]) > ev or \
            min(seg1[0][1], seg1[1][1]) - max(seg2[0][1], seg2[1][1]) > ev:
        return False
    # 严格的跨立实验
    if ToLeft(seg1[0], seg1[1], seg2[0]) * ToLeft(seg1[0], seg1[1], seg2[1]) < 0 and \
            ToLeft(seg2[0], seg2[1], seg1[0]) * ToLeft(seg2[0], seg2[1], seg1[1]) < 0:
        return True
    # 未通过严格的跨立实验
    return False

# 交点不能是端点，但是可以在线段内，也就是端点不重合，但是端点可以在线段上，O(1)
def segment_is_strict_intersect2(seg1, seg2):
    '''
    \begin{align}
    & 跨立实验：两条线段在坐标轴上的投影不重合，则不可能相交\\
    & 判断不是顶点相交
    & 快速排斥实验：点A和B在CD的两边，并且点C和D在AB的两边，则相交，取等表示可以在端点或线段上相交\\
    & 即\overrightarrow{AC}\times\overrightarrow{CD}\cdot\overrightarrow{BC}\times\overrightarrow{CD}<=0,
    \overrightarrow{CA}\times\overrightarrow{AB}\cdot\overrightarrow{DA}\times\overrightarrow{AB}<=0
    \end{align}
    '''
    seg1, seg2 = np.array(seg1), np.array(seg2)
    # 快速排斥实验
    if min(seg2[0][0], seg2[1][0]) - max(seg1[0][0], seg1[1][0]) > ev or \
            min(seg1[0][0], seg1[1][0]) - max(seg2[0][0], seg2[1][0]) > ev or \
            min(seg2[0][1], seg2[1][1]) - max(seg1[0][1], seg1[1][1]) > ev or \
            min(seg1[0][1], seg1[1][1]) - max(seg2[0][1], seg2[1][1]) > ev:
        return False
    if point_is_equal(seg1[0], seg2[0]) or point_is_equal(seg1[0], seg2[1]) or \
            point_is_equal(seg1[1], seg2[0]) or point_is_equal(seg1[1], seg2[1]):
        return False
    # 跨立实验
    if ToLeft(seg1[0], seg1[1], seg2[0]) * ToLeft(seg1[0], seg1[1], seg2[1]) <= 0 and \
            ToLeft(seg2[0], seg2[1], seg1[0]) * ToLeft(seg2[0], seg2[1], seg1[1]) <= 0:
        return True
    # 未通过跨立实验
    return False

# 交点可以在端点，算法2，O(1)
def segment_is_intersect2(seg1, seg2):
    seg1, seg2 = np.array(seg1), np.array(seg2)
    # 快速排斥实验
    if min(seg2[0][0], seg2[1][0]) - max(seg1[0][0], seg1[1][0]) > ev or \
            min(seg1[0][0], seg1[1][0]) - max(seg2[0][0], seg2[1][0]) > ev or \
            min(seg2[0][1], seg2[1][1]) - max(seg1[0][1], seg1[1][1]) > ev or \
            min(seg1[0][1], seg1[1][1]) - max(seg2[0][1], seg2[1][1]) > ev:
        return False
    intersection = get_intersection_of_2lines(seg1, seg2)
    if isinstance(intersection[0], bool):
        # 重合
        a1, b1, c1, a2, b2, c2, c = intersection[1:]
        if abs(a1*c2-c1*a2) < ev:
            return True
        # 平行
        return False
    # 隐含不平行也不重合，即直线严格相交，只有一个交点
    # 交点的在坐标轴的投影在线段在坐标轴投影内
    if seg1[0][0] - ev < intersection[0] < seg1[1][0] + ev and seg2[0][0] - ev < intersection[0] < seg2[1][0] + ev or \
            seg1[0][1] - ev < intersection[1] < seg1[1][1] + ev and seg2[0][1] - ev < intersection[1] < seg2[1][1] + ev:
        return True
    # 存在在投影外的情况
    return False

# 交点不能是端点，也不能在线段内，算法2，O(1)
def segment_is_strict_intersect3(seg1, seg2):
    seg1, seg2 = np.array(seg1), np.array(seg2)
    # 快速排斥实验
    if min(seg2[0][0], seg2[1][0]) - max(seg1[0][0], seg1[1][0]) > ev or \
            min(seg1[0][0], seg1[1][0]) - max(seg2[0][0], seg2[1][0]) > ev or \
            min(seg2[0][1], seg2[1][1]) - max(seg1[0][1], seg1[1][1]) > ev or \
            min(seg1[0][1], seg1[1][1]) - max(seg2[0][1], seg2[1][1]) > ev:
        return False
    intersection = get_intersection_of_2lines(seg1, seg2)
    if isinstance(intersection[0], bool):
        # 重合
        a1, b1, c1, a2, b2, c2, c = intersection[1:]
        if abs(a1*c2-c1*a2) < ev:
            return True
        # 平行
        return False
    # 隐含不平行也不重合，即直线严格相交，只有一个交点
    # 交点的在坐标轴的投影在线段在坐标轴投影内（严格）
    if seg1[0][0] + ev < intersection[0] < seg1[1][0] - ev and seg2[0][0] + ev < intersection[0] < seg2[1][0] - ev or \
            seg1[0][1] + ev < intersection[1] < seg1[1][1] - ev and seg2[0][1] + ev < intersection[1] < seg2[1][1] - ev:
        return True
    # 存在在投影外的情况（严格）
    return False

# 点是否在线段上，可以在端点，O(1)
def point_is_on_segment(point, seg):
    if ToLeft(point, seg[0], seg[1]) == 0 and min(seg[0][0], seg[1][0]) - ev < point[0] < max(seg[0][0], seg[1][0]) + ev\
            and min(seg[0][1], seg[1][1]) - ev < point[1] < max(seg[0][1], seg[1][1]) + ev:
        return True
    return False

# 点是否严格在线段上，不可以在端点，O(1)
def point_is_strict_on_segment(point, seg):
    # 点与端点重合
    if point_is_equal(point, seg[0]) or point_is_equal(point, seg[1]):
        return False
    # 点在线段上，隐含不是端点
    if point_is_on_segment(point, seg):
        return True
    return False

# 点在多边形内，可以在边界，O(n)
def point_is_inside_polygon(point, polygon):
    x_min = min(point[0], *[v[0] for v in polygon.get_vertices()])-10
    # 扫描线
    radial_seg = [[x_min, point[1] + cunning_proportion, 0], point]
    # 记录交点数
    intersect_n = 0
    for seg in zip(polygon.get_vertices(), [*polygon.get_vertices()[1:], polygon.get_vertices()[0]]):
        # 点在多边形上
        if point_is_on_segment(point, seg):
            return True
        # 隐含点不在多边形上
        if segment_is_strict_intersect(radial_seg, seg):
            intersect_n = intersect_n+1
    # 扫描线交多边形于奇数点，则点在多边形内部
    if intersect_n % 2 == 1:
        return True
    # 扫描线交多边形于偶数点，则点在多边形外部
    return False

# 点在多边形外，不可以在边界，O(n)
def point_is_strict_outside_polygon(point, polygon):
    return not point_is_inside_polygon(point, polygon)

# 点在多边形内，不可以在边界，O(n)
def point_is_strict_inside_polygon(point, polygon):
    x_min = min(point[0], *[v[0] for v in polygon.get_vertices()])-10
    # 扫描线
    radial_seg = [[x_min, point[1] + cunning_proportion, 0], point]
    # 记录交点数
    intersect_n = 0
    for seg in zip(polygon.get_vertices(), [*polygon.get_vertices()[1:], polygon.get_vertices()[0]]):
        # 点在多边形上
        if point_is_on_segment(point, seg):
            return False
        # 隐含点不在多边形上
        if segment_is_strict_intersect(radial_seg, seg):
            intersect_n = intersect_n+1
    # 扫描线交多边形于奇数点，则点在多边形内部
    if intersect_n % 2 == 1:
        return True
    # 扫描线交多边形于偶数点，则点在多边形外部
    return False

# 点在多边形外，可以在边界，O(n)
def point_is_outside_polygon(point, polygon):
    return not point_is_strict_inside_polygon(point, polygon)

# 点在多边形边上，O(n)
def point_is_on_polygon(point, polygon):
    for seg in zip(polygon.get_vertices(), [*polygon.get_vertices()[1:], polygon.get_vertices()[0]]):
        # 点在多边形上
        if point_is_on_segment(point, seg):
            return True
    # 隐含点不在多边形上
    return False

# pol1包含pol2，可以相切于一点或者一边，算法1，O(n^2)
def polygon1_contains_polygon2(pol1, pol2):
    # 遍历pol1的每条边seg1
    for seg1 in zip(pol1.get_vertices(), [*pol1.get_vertices()[1:], pol1.get_vertices()[0]]):
        # 遍历pol2的每条边seg2
        for seg2 in zip(pol2.get_vertices(), [*pol2.get_vertices()[1:], pol2.get_vertices()[0]]):
            # 严格相交，交点不能是端点，包括端点交在线段内
            if segment_is_strict_intersect(seg1, seg2):
                return False
    for v in pol2.get_vertices():
        # 点严格在多边形内
        if point_is_strict_inside_polygon(v, pol1):
            return True
        # 点严格在多边形外
        if point_is_strict_outside_polygon(v, pol1):
            return False
    # 多边形相等
    return True

# pol1包含pol2，可以相切于一点或者一边，算法2，慢于第一种算法，O(n^2)
def polygon1_contains_polygon2_2(pol1, pol2):
    # pol1包含pol2的充要条件是：pol1的每一个顶点都在pol2外，且pol2的每一个顶点都在pol1内
    # pol1的每一个顶点都在pol2外
    internal1, external1 = 0, 0
    for v1 in pol1.get_vertices():
        if point_is_outside_polygon(v1, pol2):
            external1 = external1+1
        else:
            internal1 = internal1+1
        # 多边形相交
        if external1&internal1:
            return False
    # pol2的每一个顶点都在pol1内
    internal2, external2 = 0, 0
    for v2 in pol2.get_vertices():
        if point_is_inside_polygon(v2, pol1):
            internal2 = internal2+1
        else:
            external2 = external2 + 1
        # 多边形相交
        if external2&internal2:
            return False
    # 隐含满足充要条件
    return True

# pol1严格包含pol2，不可以相切于一点或者一边，O(n^2)
def polygon1_strict_contains_polygon2(pol1, pol2):
    # 遍历pol1的每条边seg1
    for seg1 in zip(pol1.get_vertices(), [*pol1.get_vertices()[1:], pol1.get_vertices()[0]]):
        # 遍历pol2的每条边seg2
        for seg2 in zip(pol2.get_vertices(), [*pol2.get_vertices()[1:], pol2.get_vertices()[0]]):
            # 严格相交，交点不能是端点，包括端点交在线段内
            if segment_is_strict_intersect(seg1, seg2):
                return False
    for v in pol2.get_vertices():
        # 点在多边形上
        if point_is_on_polygon(v, pol1):
            return False
        # 点严格在多边形内
        if point_is_strict_inside_polygon(v, pol1):
            return True
        # 点严格在多边形外
        if point_is_strict_outside_polygon(v, pol1):
            return False
    # 多边形相等
    return True

# pol1是否在pol2外部，可以外切，不能包含，即外离，O(n^2)
def polygon1_is_outside_polygon2(pol1, pol2):
    # pol1外离pol2的充要条件是：pol1的每一个顶点都在pol2外，且pol2的每一个顶点都在pol1外
    # pol1的每一个顶点都在pol2外
    internal1, external1 = 0, 0
    for v1 in pol1.get_vertices():
        if point_is_strict_outside_polygon(v1, pol2):
            external1 = external1+1
        elif point_is_strict_inside_polygon(v1, pol2):
            internal1 = internal1+1
        # 多边形相交
        if external1 != 0 and internal1 != 0:
            return False
    # pol2的每一个顶点都在pol1外
    internal2, external2 = 0, 0
    for v2 in pol2.get_vertices():
        if point_is_strict_outside_polygon(v2, pol1):
            external2 = external2 + 1
        elif point_is_strict_inside_polygon(v2, pol1):
            internal2 = internal2 + 1
        # 多边形相交
        if external2 != 0 and internal2 != 0:
            return False
    # pol1在pol2外且pol2在pol1外
    if external1 != 0 and external2 != 0:
        return True
    # 否则
    return False

# pol1是否在pol2外部，不可以外切，不能包含，即严格外离，O(n^2)
def polygon1_is_strict_outside_polygon2(pol1, pol2):
    # pol1外离pol2的充要条件是：pol1的每一个顶点都在pol2外，且pol2的每一个顶点都在pol1外
    # pol1的每一个顶点都在pol2外
    internal1, external1 = 0, 0
    for v1 in pol1.get_vertices():
        if point_is_strict_outside_polygon(v1, pol2):
            external1 = external1 + 1
        else:
            internal1 = internal1 + 1
        # 多边形相交
        if external1 != 0 and internal1 != 0:
            return False
    # pol2的每一个顶点都在pol1外
    internal2, external2 = 0, 0
    for v2 in pol2.get_vertices():
        if point_is_strict_outside_polygon(v2, pol1):
            external2 = external2 + 1
        else:
            internal2 = internal2 + 1
        # 多边形相交
        if external2 != 0 and internal2 != 0:
            return False
    # pol1在pol2外且pol2在pol1外
    if external1 != 0 and external2 != 0:
        return True
    # 否则
    return False

# pol1与pol2是否相交，交于一点，或一边也算，O(n^2)
def polygon_is_intersect(pol1, pol2):
    # pol1相交pol2的充要条件是：一个多边形存在点在另一个多边形内，也存在点在另一个多边形外
    internal1, external1 = 0, 0
    for v1 in pol1.get_vertices():
        if point_is_strict_outside_polygon(v1, pol2):
            external1 = external1 + 1
        else:
            internal1 = internal1 + 1
        # 多边形相交
        if external1 != 0 and internal1 != 0:
            return True
    # pol2的每一个顶点都在pol1外
    internal2, external2 = 0, 0
    for v2 in pol2.get_vertices():
        if point_is_strict_outside_polygon(v1, pol2):
            external2 = external2 + 1
        else:
            internal2 = internal2 + 1
        # 多边形相交
        if external2 != 0 and internal2 != 0:
            return True
    # 隐含满足充要条件
    return False

# pol1与pol2是否一个相交，交集面积不能为0，O(n^2)
def polygon_is_strict_intersect(pol1, pol2):
    # pol1相交pol2的充要条件是：一个多边形存在点在另一个多边形内，也存在点在另一个多边形外
    internal1, external1 = 0, 0
    for v1 in pol1.get_vertices():
        if point_is_strict_outside_polygon(v1, pol2):
            external1 = external1 + 1
        elif point_is_strict_inside_polygon(v1, pol2):
            internal1 = internal1 + 1
        # 多边形相交
        if external1 != 0 and internal1 != 0:
            return True
    # pol2的每一个顶点都在pol1外
    internal2, external2 = 0, 0
    for v2 in pol2.get_vertices():
        if point_is_strict_outside_polygon(v2, pol1):
            external2 = external2 + 1
        elif point_is_strict_inside_polygon(v2, pol1):
            internal2 = internal2 + 1
        # 多边形相交
        if external2 != 0 and internal2 != 0:
            return True
    # 隐含满足充要条件
    return False

# 得到多边形的带符号面积，对于不自交的多边形，正表示逆时针多边形，负表示顺时针多边形，特殊考虑0，O(n)
def get_polygon_directed_area(polygon):
    a = polygon.get_vertices()
    l = len(a)
    return 1 / 2 * sum([a[i][0] * a[(i + 1) % l][1] - a[(i + 1) % l][0] * a[i][1] for i in range(l)])

# 线段集互相clip（碎片化），得到互相被clip的线段集，O(n^2)
def segmentset_interclip(seg1s, seg2s):
    seg1clips, seg2clips = [], []
    #clip seg1s
    for seg1 in seg1s:
        intersecters = [seg1[0]]
        for seg2 in seg2s:
            # 线段严格相交
            if segment_is_strict_intersect2(seg1, seg2):
                # 线段重合
                if segment_is_overlap(seg1, seg2):
                    if point_is_strict_on_segment(seg2[0], seg1):
                        intersecters.append(seg2[0])
                    if point_is_strict_on_segment(seg2[1], seg1):
                        intersecters.append(seg2[1])
                # 线段相交
                else:
                    isp = get_intersection_of_2segments(seg1, seg2)
                    if not point_is_equal(isp, seg1[0]) and not point_is_equal(isp, seg1[1]):
                        intersecters.append(isp)
        intersecters.append(seg1[1])
        if seg1[0][0] < seg1[1][0]:
            intersecters.sort(key=lambda m: m[0])
        elif seg1[0][0] > seg1[1][0]:
            intersecters.sort(key=lambda m: m[0], reverse=True)
        else:
            if seg1[0][1] < seg1[1][1]:
                intersecters.sort(key=lambda m: m[1])
            elif seg1[0][1] > seg1[1][1]:
                intersecters.sort(key=lambda m: m[1], reverse=True)
        for i in range(len(intersecters)-1):
            seg1clips.append([intersecters[i], intersecters[i+1]])
    #clip seg2s
    for seg2 in seg2s:
        intersecters = [seg2[0]]
        for seg1 in seg1s:
            # 线段严格相交
            if segment_is_strict_intersect2(seg1, seg2):
                # 线段重合
                if segment_is_overlap(seg1, seg2):
                    if point_is_strict_on_segment(seg1[0], seg2):
                        intersecters.append(seg1[0])
                    if point_is_strict_on_segment(seg1[1], seg2):
                        intersecters.append(seg1[1])
                # 线段相交
                else:
                    isp = get_intersection_of_2segments(seg1, seg2)
                    if not point_is_equal(isp, seg2[0]) and not point_is_equal(isp, seg2[1]):
                        intersecters.append(isp)
        intersecters.append(seg2[1])
        if seg2[0][0] < seg2[1][0]:
            intersecters.sort(key=lambda m: m[0])
        elif seg2[0][0] > seg2[1][0]:
            intersecters.sort(key=lambda m: m[0], reverse=True)
        else:
            if seg2[0][1] < seg2[1][1]:
                intersecters.sort(key=lambda m: m[1])
            elif seg2[0][1] > seg2[1][1]:
                intersecters.sort(key=lambda m: m[1], reverse=True)
        for i in range(len(intersecters)-1):
            seg2clips.append([intersecters[i], intersecters[i+1]])
    return seg1clips, seg2clips

# 对于mobs这个list，返回所有非VGroup的vmob的list
# For Instance: mobs = [VGroup(a, b), c], 则返回[a, b, c]，O(|VGroup.mob|)
def get_all_not_VGroup_VMobject(mobs):
    ans = []
    while mobs:
        flag = mobs[0]
        if type(flag) == VGroup:
            for each in flag:
                mobs.append(each)
        else:
            ans.append(flag)
        mobs.pop(0)
    return ans

# 获取相交的孔的下标，进行合并，若无相交的孔，返回-1，O(n^2)
def get_pwh_intersect_holes_index(holes):
    for i in range(len(holes)):
        for j in range(len(holes) - i - 1):
            if polygon_is_strict_intersect(holes[i], holes[j + i + 1]):
                return i, j + i + 1
    return -1, -1

# 合并相交带孔
def merge_intersectant_holes(holes):
    hsi, hsj = get_pwh_intersect_holes_index(holes)
    while hsi != -1:
        new_hole = PolygonBooleanOperations().Union_Polygon_and_Polygon(holes[hsi], holes[hsj])
        holes.pop(hsi)
        holes.pop(hsj - 1)
        holes.append(new_hole)
        hsi, hsj = get_pwh_intersect_holes_index(holes)
    return holes

# 曲线转直线段
class CurveClip(VGroup):
    CONFIG = {
        "resolution": 10,
    }
    def __init__(self, curve=None, **kwargs):
        digest_config(self, kwargs)
        if not curve:
            VGroup.__init__(self, **kwargs)
            return
        # 隐含非空
        # 确定步长
        pace = 0.5
        step = curve.point_from_proportion(pace) - curve.point_from_proportion(0)
        limit = 1 / self.resolution ** 2  # 长度为1，细分resolution步
        while np.dot(step, step) > limit:
            pace = pace / 2
            step = curve.point_from_proportion(pace) - curve.point_from_proportion(0)
        # 曲线微分集
        self.mobjects = []
        for i in range(int(1 / pace)):
            self.mobjects.append(
                Line(
                    curve.point_from_proportion(i * pace),
                    curve.point_from_proportion((i+1) * pace),
                ))
        VGroup.__init__(self, *self.mobjects, **kwargs)

    def point_is_on_curve(self, point):
        for each in self:
            # 点在曲线上
            if point_is_on_segment(point, [each.get_start(), each.get_end()]):
                return True
        # 隐含点不在曲线上
        return False

# 将闭合曲线连成多边形
class ConstructingIrregularPolygon(Polygon):
    CONFIG = {
        "resolution": 10,
        "stroke_width": 0,
        "fill_opacity": 1,
    }
    def __init__(self, *parts, **kwargs):
        digest_config(self, kwargs)
        parts = list(parts)
        points = [parts[0].point_from_proportion(0)]
        while parts:
            mark = True
            for index in range(len(parts)):
                # 确定步长
                pace = 0.5
                step = parts[index].point_from_proportion(pace)-parts[index].point_from_proportion(0)
                limit = 1/self.resolution**2# 长度为1，细分resolution步
                while np.dot(step, step) > limit:
                    pace = pace/2
                    step = parts[index].point_from_proportion(pace)-parts[index].point_from_proportion(0)
                # 链接
                if point_is_equal(points[-1], parts[index].point_from_proportion(0)):
                    for i in range(int(1 / pace)):
                        points.append(parts[index].point_from_proportion((i+1)*pace))
                    parts.pop(index)
                    mark = False
                    break
                if point_is_equal(points[-1], parts[index].point_from_proportion(1)):
                    for i in range(int(1 / pace))[::-1]:
                        points.append(parts[index].point_from_proportion(i*pace))
                    parts.pop(index)
                    mark = False
                    break
            if mark:
                break
        Polygon.__init__(self, *points, **kwargs)

# 椭圆转多边形（包括特殊的椭圆——圆）
class ellipse_to_polygon(Polygon):
    CONFIG = {
        "resolution": 10,
    }
    def __init__(self, ellipse, **kwargs):
        digest_config(self, kwargs)
        # 椭圆两轴
        a, b = ellipse.get_width()/2, ellipse.get_height()/2
        # 椭圆周长
        perimeter = 2*PI*b+4*(a-b)
        # 初始化多边形
        k = int(perimeter*self.resolution)
        Polygon.__init__(self, *[ellipse.point_from_proportion(i/k) for i in range(k)], **kwargs)
        self.move_to(ellipse)

# 带孔多边形
class PolygonWithHoles(VMobject):
    CONFIG = {
        "fill_color": YELLOW,
        "fill_opacity": 0,
    }
    def __init__(self, vertices, *holes, **kwargs):
        digest_config(self, kwargs)
        self.point_pharos = [0]
        self.vertices, self.holes = vertices, holes
        Hull = Polygon(*vertices)
        VMobject.__init__(self, **kwargs)
        # 保证壳逆时针
        if self.get_directed_area(Hull) < 0:
            Hull = Polygon(*vertices[::-1])
        for v1, v2, v3, v4 in zip(*[Hull.points[i::4] for i in range(4)]):
            self.append_points([v1, v2, v3, v4])
        self.point_pharos.append(self.point_pharos[-1]+len(vertices))
        for hole in holes:
            Hole = Polygon(*hole)
            #保证孔顺时针
            if self.get_directed_area(Hole) > 0:
                Hole = Polygon(*hole[::-1])
            for v1, v2, v3, v4 in zip(*[Hole.points[i::4] for i in range(4)]):
                self.append_points([v1, v2, v3, v4])
            self.point_pharos.append(self.point_pharos[-1]+len(hole))

    def get_vertices(self):
        pharos = self.point_pharos
        anchors = self.get_start_anchors()
        # vertices是外轮廓，一个list；holes是孔，*holes是多个孔，每个孔一个list
        return [anchors[pharos[i]:pharos[i+1]] for i in range(len(pharos)-1)]

    def get_directed_area(self, polygon):
        # 正表示逆时针，负表示顺时针
        a = polygon.get_vertices()
        l = len(a)
        return 1 / 2 * sum([a[i][0] * a[(i + 1) % l][1] - a[(i + 1) % l][0] * a[i][1] for i in range(l)])

    def get_area(self, polygon):
        return abs(self.get_directed_area(polygon))

    def get_polygon_by_sequence(self, i):
        return Polygon(*self.get_vertices()[i])

    def point_is_inside_PolygonWithHoles(self, point):
        # 点在壳外，返回False
        if point_is_strict_outside_polygon(point, self.get_polygon_by_sequence(0)):
            return False
        # 点在孔内，返回Fasle
        for i in range(len(pharos)-2):
            if point_is_strict_inside_polygon(point, self.get_polygon_by_sequence(i+1)):
                return False
        # 逃过上述劫难，点即在带孔多边形内
        return True


# ——关于点、曲线、多边形、以及带孔多边形的bool运算——
# 关于点的bool运算
class DotBooleanOperations:
    def Intersection_Dot_and_Dot(self, dot1, dot2):
        #dot1, dot2 = dot1.copy(), dot2.copy()
        # 两点相同，交集择一
        if point_is_equal(dot1.get_center(), dot2.get_center()):
            return dot1
        # 隐含两点不同，交集为空
        return VMobject()

    def Intersection_Dot_and_Curve(self, dot, cur):
        #dot, cur = dot.copy(), cur.copy()
        # 曲线未微分为线段，先微分
        if type(cur) != CurveClip:
            cur = CurveClip(cur)
        # 点在曲线上
        if cur.point_is_on_curve(dot.get_center()):
            return dot
        # 隐含点不在曲线上
        return VMobject()

    def Intersection_Dot_and_Polygon(self, dot, pol):
        #dot, pol = dot.copy(), pol.copy()
        # 点在多边形上
        if point_is_inside_polygon(dot.get_center(), pol):
            return dot
        # 隐含点不在多边形上
        return VMobject()

    def Union_Dot_and_Dot(self, dot1, dot2):
        #dot1, dot2 = dot1.copy(), dot2.copy()
        # 两点相同，加集择一
        if point_is_equal(dot1.get_center(), dot2.get_center()):
            return dot1
        # 隐含两点不同，加集择二
        return VGroup(dot1, dot2)

    def Union_Dot_and_Curve(self, dot, cur):
        #dot, cur = dot.copy(), cur.copy()
        # 曲线未微分为线段，先微分
        if type(cur) != CurveClip:
            cur = CurveClip(cur)
        # 点在曲线上
        if cur.point_is_on_curve(dot.get_center()):
            return cur
        # 隐含点不在曲线上
        return VGroup(dot, cur)

    def Union_Dot_and_Polygon(self, dot, pol):
        #dot, pol = dot.copy(), pol.copy()
        # 点在多边形上
        if point_is_inside_polygon(dot.get_center(), pol):
            return pol
        # 隐含点不在多边形上
        return VGroup(dot, pol)

    def Subtraction_Dot_and_Dot(self, dot1, dot2):
        #dot1, dot2 = dot1.copy(), dot2.copy()
        # 两点相同，减集为空
        if point_is_equal(dot1.get_center(), dot2.get_center()):
            return VMobject()
        # 隐含两点不同，减集为dot1
        return dot1

    def Subtraction_Dot_and_Curve(self, dot, cur):
        #dot, cur = dot.copy(), cur.copy()
        # 曲线未微分为线段，先微分
        if type(cur) != CurveClip:
            cur = CurveClip(cur)
        # 点在曲线上
        if cur.point_is_on_curve(dot.get_center()):
            return VMobject()
        # 隐含点不在曲线上
        return dot

    def Subtraction_Dot_and_Polygon(self, dot, pol):
        #dot, pol = dot.copy(), pol.copy()
        # 点在多边形上
        if point_is_inside_polygon(dot.get_center(), pol):
            return VMobject()
        # 隐含点不在多边形上
        return dot

# 关于曲线的bool运算
class CurveBooleanOperations:
    def Intersection_Line_and_Line(self, line1, line2):
        #line1, line2 = line1.copy(), line2.copy()
        seg1, seg2 = [line1.get_start(), line1.get_end()], [line2.get_start(), line2.get_end()]
        # 线段严格重合
        if segment_is_strict_overlap(seg1, seg2):
            return line1
        # 线段重合
        if segment_is_overlap(seg1, seg2):
            # 只重合一点
            if point_is_equal(seg1[0], seg2[0]) and point_is_strict_on_segment(seg1[0], [seg1[1], seg2[1]]) or\
                    point_is_equal(seg1[0], seg2[1]) and point_is_strict_on_segment(seg1[0], [seg1[1], seg2[0]]):
                return Dot(seg1[0])
            if point_is_equal(seg1[1], seg2[0]) and point_is_strict_on_segment(seg1[1], [seg1[0], seg2[1]]) or\
                    point_is_equal(seg1[1], seg2[1]) and point_is_strict_on_segment(seg1[1], [seg1[0], seg2[0]]):
                return Dot(seg1[1])
            # 重合一部分线段
            isl = []
            if point_is_strict_on_segment(seg1[0], seg2):
                isl.append(seg1[0])
            if point_is_strict_on_segment(seg1[1], seg2):
                isl.append(seg1[1])
            if point_is_strict_on_segment(seg2[0], seg1):
                isl.append(seg2[0])
            if point_is_strict_on_segment(seg2[1], seg1):
                isl.append(seg2[1])
            if len(isl) == 2:
                return Line(*isl)
        # 只交于一点
        if segment_is_intersect(seg1, seg2):
            return Dot(get_intersection_of_2segments(seg1, seg2))
        return VMobject()

    def Intersection_Curve_and_Dot(self, cur, dot):
        return DotBooleanOperations().Intersection_Dot_and_Curve(dot, cur)

    def Intersection_Curve_and_Curve(self, cur1, cur2):
        #cur1, cur2 = cur1.copy(), cur2.copy()

        # 曲线未微分为线段，先微分
        if type(cur1) != CurveClip:
            cur1 = CurveClip(cur1)
        if type(cur2) != CurveClip:
            cur2 = CurveClip(cur2)
        # inter-clip
        curclip1, curclip2 = segmentset_interclip(
            [[each.get_start(), each.get_end()] for each in cur1],
            [[each.get_start(), each.get_end()] for each in cur2],
        )
        cur1 = CurveClip().add(*[Line(each[0], each[1]) for each in curclip1])
        cur2 = CurveClip().add(*[Line(each[0], each[1]) for each in curclip2])

        isvg1 = VGroup()
        isvg2 = VGroup()
        for dcur1 in cur1:
            for dcur2 in cur2:
                isv = self.Intersection_Line_and_Line(dcur1, dcur2)
                if isinstance(isv, Line):
                    isvg1.add(isv)
                if isinstance(isv, Dot):
                    isvg2.add(isv)
        for eachdot in isvg2:
            mark = True
            for eachline in isvg1.copy():
                if point_is_on_segment(eachdot.get_center(), [eachline.get_start(), eachline.get_end()]):
                    mark = False
                    break
            if mark:
                isvg1.add(eachdot)
        # 无交点
        if len(isvg1) == 0:
            return VMobject()
        # 交于一点
        if len(isvg1) == 1:
            return isvg1[0]
        # 隐含交于多点
        return isvg1

    def Intersection_Curve_and_Polygon(self, cur, pol):
        #cur, pol = cur.copy(), pol.copy()
        # 曲线未微分为线段，先微分
        if type(cur) != CurveClip:
            cur = CurveClip(cur)
        pol_vs = pol.get_vertices()
        seg1s = [[each.get_start(), each.get_end()] for each in cur]
        seg2s = [[v1, v2] for v1, v2 in zip(pol_vs, [*pol_vs[1:], pol_vs[0]])]
        # 获取互相分割的线段集
        seg1clips, seg2clips = segmentset_interclip(seg1s, seg2s)
        # 判断和拼接
        isvg = VGroup()
        isv = CurveClip()
        for seg1 in seg1clips:
            mark = True
            # 线段在多边形内
            if point_is_strict_inside_polygon(seg1[0]+cunning_proportion*(seg1[1]-seg1[0]), pol):
                isv.add(Line(*seg1))
                mark = False
            else:
                mark = True
            if mark and len(isv) != 0:
                isvg.add(isv)
                isv = CurveClip()
        # 无交点
        if len(isvg) == 0:
            return VMobject()
        # 交于一段线段
        if len(isvg) == 1:
            return isvg[0]
        # 隐含交于多段线段
        return isvg

    def Union_Curve_and_Dot(self, cur, dot):
        return DotBooleanOperations().Union_Dot_and_Curve(dot, cur)

    def Union_Curve_and_Curve(self, cur1, cur2):
        return VGroup(cur1, cur2)
    
    def Union_Curve_and_Polygon(self, cur, pol):
        return VGroup(cur, pol)

    def Subtraction_Curve_and_Dot(self, cur, dot):
        return cur

    def Subtraction_Curve_and_Curve(self, cur1, cur2):
        return cur1

    def Subtraction_Curve_and_Polygon(self, cur, pol):
        #cur, pol = cur.copy(), pol.copy()
        # 曲线未微分为线段，先微分
        if type(cur) != CurveClip:
            cur = CurveClip(cur)
        # inter-clip
        pol_vs = pol.get_vertices()
        seg1s = [[each.get_start(), each.get_end()] for each in cur]
        seg2s = [[v1, v2] for v1, v2 in zip(pol_vs, [*pol_vs[1:], pol_vs[0]])]
        # 获取互相分割的线段集
        seg1clips, seg2clips = segmentset_interclip(seg1s, seg2s)
        # 取减集
        cutset = []
        for seg1 in seg1clips:
            # 线段在多边形外
            if not point_is_strict_inside_polygon(seg1[0]+cunning_proportion*(seg1[1]-seg1[0]), pol):
                cutset.append(seg1)
        # 拼接
        isvg = VGroup()
        isv = CurveClip()
        # 拼接
        for seg1 in cutset:
            if len(isv) == 0:
                isv.add(Line(*seg1))
            elif point_is_equal(isv[-1].get_end(), seg1[0]):
                isv.add(Line(*seg1))
            else:
                isvg.add(isv)
                isv = CurveClip()
        if len(isv) > 0:
            isvg.add(isv)
        # 无交点
        if len(isvg) == 0:
            return VMobject()
        # 交于一段线段
        if len(isvg) == 1:
            return isvg[0]
        # 隐含交于多段线段
        return isvg

# 关于多边形的bool运算
class PolygonBooleanOperations:
    def Intersection_Polygon_and_Dot(self, pol, dot):
        return DotBooleanOperations().Intersection_Dot_and_Polygon(dot, pol)

    def Intersection_Polygon_and_Curve(self, pol, cur):
        return CurveBooleanOperations().Intersection_Curve_and_Polygon(cur, pol)

    def Intersection_Polygon_and_Polygon(self, pol1, pol2):
        pol1, pol2 = pol1.stretch(0.99943, 0), pol2.stretch(0.999, 1)

        # 保证多边形都是逆时针
        if get_polygon_directed_area(pol1) < 0:
            pol1 = Polygon(*pol1.get_vertices()[::-1])
        if get_polygon_directed_area(pol2) < 0:
            pol2 = Polygon(*pol2.get_vertices()[::-1])

        # pol2在pol1里
        if polygon1_contains_polygon2(pol1, pol2):
            return pol2
        # pol1在pol2里
        if polygon1_contains_polygon2(pol2, pol1):
            return pol1
        # pol1与pol2相离，无交集
        if polygon1_is_strict_outside_polygon2(pol1, pol2):
            return VMobject()

        # 隐含多边形相交
        # 获取线段集
        pol1_vs, pol2_vs = pol1.get_vertices(), pol2.get_vertices()
        seg1s = [[v1, v2] for v1, v2 in zip(pol1_vs, [*pol1_vs[1:], pol1_vs[0]])]
        seg2s = [[v1, v2] for v1, v2 in zip(pol2_vs, [*pol2_vs[1:], pol2_vs[0]])]
        # 获取互相分割的线段集
        seg1clips, seg2clips = segmentset_interclip(seg1s, seg2s)
        # 取交集轮廓
        isset = []
        for seg1clip in seg1clips:
            if point_is_inside_polygon(seg1clip[0] + cunning_proportion * (seg1clip[1] - seg1clip[0]), pol2):
                isset.append(seg1clip)
        for seg2clip in seg2clips:
            if point_is_inside_polygon(seg2clip[0] + cunning_proportion * (seg2clip[1] - seg2clip[0]), pol1):
                isset.append(seg2clip)

        # 无交线段，看看是否有交点，有bug，放弃
        #if len(isset) == 0:
        #    return CurveBooleanOperations().Intersection_Curve_and_Curve(
        #        CurveClip().add(*[Line(*each) for each in seg1clips]),
        #        CurveClip().add(*[Line(*each) for each in seg2clips]),
        #    )
        # 交集为空
        if len(isset) == 0:
            return VMobject()

        # 隐含有交集
        # 对线段集做拼接
        hullVGroup, subhull = VGroup(), [isset[0]]
        isset.pop(0)
        # memindex 为记录上一次索引位置，上一次索引位置的下一个位置很可能是下一个需要拼接的线段
        memindex = 0
        while isset:
            mark = True
            isset_l = len(isset)
            for index in range(isset_l):
                if point_is_equal(isset[(index+memindex) % isset_l][0], subhull[-1][1]):
                    subhull.append(isset[(index+memindex) % isset_l])
                    isset.pop((index+memindex) % isset_l)
                    memindex = index
                    mark = False
                    break
            if mark:
                hullVGroup.add(Polygon(*[sh[0] for sh in subhull]))
                if len(isset) > 0:
                    subhull = [isset[0]]
                    isset.pop(0)
                    memindex = 0

        if len(subhull) > 0:
            hullVGroup.add(Polygon(*[sh[0] for sh in subhull]))
        if len(hullVGroup) == 1:
            return hullVGroup[0]
        # 隐含交集不为空，且只有一个元素
        return hullVGroup

    def Union_Polygon_and_Dot(self, pol, dot):
        return DotBooleanOperations().Union_Dot_and_Polygon(dot, pol)

    def Union_Polygon_and_Curve(self, pol, cur):
        return CurveBooleanOperations().Union_Curve_and_Polygon(cur, pol)

    def Union_Polygon_and_Polygon(self, pol1, pol2):
        pol1, pol2 = pol1, pol2.stretch(0.99975, 0).stretch(0.999, 1)
        # 保证多边形都是逆时针
        if get_polygon_directed_area(pol1) < 0:
            pol1 = Polygon(*pol1.get_vertices()[::-1])
        if get_polygon_directed_area(pol2) < 0:
            pol2 = Polygon(*pol2.get_vertices()[::-1])

        # pol2在pol1里
        if polygon1_contains_polygon2(pol1, pol2):
            return pol1
        # pol1在pol2里
        if polygon1_contains_polygon2(pol2, pol1):
            return pol2
        # pol1与pol2相离
        if polygon1_is_strict_outside_polygon2(pol1, pol2):
            return VGroup(pol1, pol2)

        # 隐含多边形相交
        # 获取线段集
        pol1_vs, pol2_vs = pol1.get_vertices(), pol2.get_vertices()
        seg1s = [[v1, v2] for v1, v2 in zip(pol1_vs, [*pol1_vs[1:], pol1_vs[0]])]
        seg2s = [[v1, v2] for v1, v2 in zip(pol2_vs, [*pol2_vs[1:], pol2_vs[0]])]
        # 获取互相分割的线段集
        seg1clips, seg2clips = segmentset_interclip(seg1s, seg2s)
        # 取加集轮廓
        unionset = []
        for seg1clip in seg1clips:
            if not point_is_inside_polygon(seg1clip[0] + cunning_proportion * (seg1clip[1] - seg1clip[0]), pol2):
                unionset.append(seg1clip)
        for seg2clip in seg2clips:
            if not point_is_inside_polygon(seg2clip[0] + cunning_proportion * (seg2clip[1] - seg2clip[0]), pol1):
                unionset.append(seg2clip)

        # 对线段集做拼接
        hullVGroup, subhull = VGroup(), [unionset[0]]
        unionset.pop(0)
        # memindex 为记录上一次索引位置，上一次索引位置的下一个位置很可能是下一个需要拼接的线段
        memindex = 0
        while unionset:
            mark = True
            unionset_l = len(unionset)
            for index in range(unionset_l):
                if point_is_equal(unionset[(index+memindex) % unionset_l][0], subhull[-1][1]):
                    subhull.append(unionset[(index+memindex) % unionset_l])
                    unionset.pop((index+memindex) % unionset_l)
                    memindex = index
                    mark = False
                    break
            if mark:
                hullVGroup.add(Polygon(*[sh[0] for sh in subhull]))
                if len(unionset) > 0:
                    subhull = [unionset[0]]
                    unionset.pop(0)
                    memindex = 0

        if len(subhull) > 0:
            hullVGroup.add(Polygon(*[sh[0] for sh in subhull]))
        # 判断是否是带孔多边形的情况
        union_hulls = []
        union_holes = []
        for hull in hullVGroup:
            # 正的多边形为壳，负的多边形为孔
            if get_polygon_directed_area(hull) > 0:
                union_hulls.append(hull)
            else:
                union_holes.append(hull)
        # 如果存在多边形+多边形=带孔多边形的情况
        # 即存在孔
        if len(union_holes) > 0:
            return PolygonWithHoles(union_hulls[0].get_vertices(), *[hole.get_vertices() for hole in union_holes])
        # 隐含不存在孔
        if len(hullVGroup) == 1:
            return hullVGroup[0]
        return hullVGroup

    def Subtraction_Polygon_and_Dot(self, pol, dot):
        return pol

    def Subtraction_Polygon_and_Curve(self, pol, cur):
        return pol

    def Subtraction_Polygon_and_Polygon(self, pol1, pol2):
        pol1, pol2 = pol1.stretch(0.99936, 0), pol2.stretch(0.99984, 1)
        # 保证pol1逆时针，pol2顺时针
        if get_polygon_directed_area(pol1) < 0:
            pol1 = Polygon(*pol1.get_vertices()[::-1])
        if get_polygon_directed_area(pol2) > 0:
            pol2 = Polygon(*pol2.get_vertices()[::-1])

        # pol2在pol1里
        if polygon1_contains_polygon2(pol1, pol2):
            return PolygonWithHoles(pol1.get_vertices(), pol2.get_vertices())
        # pol1在pol2里
        if polygon1_contains_polygon2(pol2, pol1):
            return PolygonWithHoles(pol2.get_vertices(), pol1.get_vertices())
        # pol1与pol2相离
        if polygon1_is_outside_polygon2(pol1, pol2):
            return pol1

        # 隐含多边形相交，即不相离也不包含
        # 获取线段集
        pol1_vs, pol2_vs = pol1.get_vertices(), pol2.get_vertices()
        seg1s = [[v1, v2] for v1, v2 in zip(pol1_vs, [*pol1_vs[1:], pol1_vs[0]])]
        seg2s = [[v1, v2] for v1, v2 in zip(pol2_vs, [*pol2_vs[1:], pol2_vs[0]])]
        # 获取互相分割的线段集
        seg1clips, seg2clips = segmentset_interclip(seg1s, seg2s)
        # 取加集轮廓
        cutset = []
        for seg1clip in seg1clips:
            if not point_is_strict_inside_polygon(seg1clip[0] + cunning_proportion * (seg1clip[1] - seg1clip[0]), pol2):
                cutset.append(seg1clip)
        for seg2clip in seg2clips:
            if point_is_inside_polygon(seg2clip[0] + cunning_proportion * (seg2clip[1] - seg2clip[0]), pol1):
                cutset.append(seg2clip)
        # 减集为空
        if len(cutset) == 0:
            return VMobject()
        # 隐含有交集
        # 对线段集做拼接
        hullVGroup, subhull = VGroup(), [cutset[0]]
        cutset.pop(0)
        # memindex 为记录上一次索引位置，上一次索引位置的下一个位置很可能是下一个需要拼接的线段
        memindex = 0
        while cutset:
            mark = True
            cutset_l = len(cutset)
            for index in range(cutset_l):
                if point_is_equal(cutset[(index+memindex) % cutset_l][0], subhull[-1][1]):
                    subhull.append(cutset[(index+memindex) % cutset_l])
                    cutset.pop((index+memindex) % cutset_l)
                    memindex = index
                    mark = False
                    break
            if mark:
                hullVGroup.add(Polygon(*[sh[0] for sh in subhull]))
                if len(cutset) > 0:
                    subhull = [cutset[0]]
                    cutset.pop(0)
                    memindex = 0

        if len(subhull) > 0:
            hullVGroup.add(Polygon(*[sh[0] for sh in subhull]))
        # 只有一个mob，返回VGroup[0]就行
        if len(hullVGroup) == 1:
            return hullVGroup[0]
        return hullVGroup

# 关于带孔多边形的bool运算
class PolygonWithHolesBooleanOperations:
    def Intersection_PolygonWithHoles_and_Dot(self, pwh, dot):
        #pwh, dot = pwh.copy(), dot.copy()
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 壳
        hull = Polygon(*pwh_vs[0])
        # 点在壳外，则交集为空
        if point_is_strict_outside_polygon(dot.get_center(), hull):
            return VMobject()
        # 点在孔内，则交集为空
        for i in range(len(pwh_vs)-1):
            hole = Polygon(*pwh_vs[i+1])
            if point_is_strict_inside_polygon(dot.get_center(), hole):
                return VMobject()
        # 隐含孔在多边形内，即壳内，且孔外
        return dot

    def Intersection_PolygonWithHoles_and_Curve(self, pwh, cur):
        #pwh, cur = pwh.copy(), cur.copy()
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 壳
        hull = Polygon(*pwh_vs[0])
        # 壳和曲线先求交
        isc = PolygonBooleanOperations().Intersection_Polygon_and_Curve(hull, cur)
        # 如果交集为空，则结果必空
        if type(isc) == VMobject:
            return VMobject()
        # 隐含曲线与壳交集非空
        # 则遍历每一个孔，做减法
        isc = [isc]
        for i in range(len(pwh_vs) - 1):
            # 做减
            hole = Polygon(*pwh_vs[i + 1])
            for j in range(len(isc)):
                isc[j] = CurveBooleanOperations().Subtraction_Curve_and_Polygon(isc[j], hole)
            # 如果isc中有VGroup，则取出所有的mob
            isc = get_all_not_VGroup_VMobject(isc)
        if len(isc) == 1:
            return isc[0]
        return VGroup(*isc)

    def Intersection_PolygonWithHoles_and_Polygon(self, pwh, pol):
        ## 可恶，好难啊
        pwh, pol = pwh.stretch(0.9993, 0), pol.stretch(0.99965, 1)
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 拿壳
        hull = Polygon(*pwh_vs[0])
        # 拿孔
        holes = []
        for each in pwh_vs[1:]:
            holes.append(Polygon(*each))
        # 多边形与壳严格外离，交集为空
        if polygon1_is_strict_outside_polygon2(pol, hull):
            return VMobject()
        # 多边形包含壳，交集为带孔多边形
        if polygon1_contains_polygon2(pol, hull):
            return pwh
        # 多边形在孔内，交集为空
        for hole in holes:
            if polygon1_strict_contains_polygon2(hole, pol):
                return VMobject()
        # 壳包含多边形，则交为多边形pol减去pwh的所有的孔
        if polygon1_contains_polygon2(hull, pol):
            isc = [pol]
        # 隐含pwh的壳和pol相交
        # 则带孔的多边形和多边形的交为
        # pwh的壳和pol的交减去所有的孔
        else:
            ish = PolygonBooleanOperations().Intersection_Polygon_and_Polygon(hull, pol)
            isc = [ish]
        # 对于每一个孔，判断是否与新壳相交
        for hole in holes:
            # 孔与新壳相交，用新壳减去孔
            for j in range(len(isc)):
                if polygon_is_strict_intersect(isc[j], hole):
                    isc[j] = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(isc[j], hole)
            # 如果isc中有VGroup，则取出所有的mob
            isc = get_all_not_VGroup_VMobject(isc)
        # 得到了所有的交集多边形的壳，接下来把孔放进去吧可恶
        for i in range(len(isc)):
            if isinstance(isc[i], Polygon):
                cres_hole = []
                for hole in holes:
                    if polygon1_contains_polygon2(isc[i], hole):
                        cres_hole.append(hole)
                if len(cres_hole) > 0:
                    isc[i] = PolygonWithHoles(isc[i].get_vertices(), *[each.get_vertices() for each in cres_hole])
        if len(isc) == 1:
            return isc[0]
        return VGroup(*isc)

    def Intersection_PolygonWithHoles_and_PolygonWithHoles(self, pwh1, pwh2):
        ## 这个超级难的，可恶，救命啊啊啊
        pwh1, pwh2 = pwh1.stretch(0.99953, 1), pwh2.stretch(0.99984, 0)
        # 拿点集
        pwh1_vs, pwh2_vs = pwh1.get_vertices(), pwh2.get_vertices()
        # 拿壳
        hull1, hull2 = Polygon(*pwh1_vs[0]), Polygon(*pwh2_vs[0])
        # 拿孔
        holes1, holes2 = [], []
        for each in pwh1_vs[1:]:
            holes1.append(Polygon(*each))
        for each in pwh2_vs[1:]:
            holes2.append(Polygon(*each))
        # 两壳外离，交集为空
        if polygon1_is_strict_outside_polygon2(hull1, hull2):
            return VMobject()
        # 一多边形的壳在另一个多边形的孔内，交集为空
        for hole1 in holes1:
            if polygon1_strict_contains_polygon2(hole1, hull2):
                return VMobject()
        for hole2 in holes2:
            if polygon1_strict_contains_polygon2(hole2, hull1):
                return VMobject()
        # 隐含下面的都不是壳在孔内，也不是外离的情况
        # 壳存在包含，则新壳为被包含的带孔多边形的壳
        if polygon1_contains_polygon2(hull1, hull2):
            isc = [hull2]
        elif polygon1_contains_polygon2(hull2, hull1):
            isc = [hull1]
        # 隐含两壳相交
        # 新壳为两壳的交
        else:
            ish = PolygonBooleanOperations().Intersection_Polygon_and_Polygon(hull1, hull2)
            isc = [ish]
        # 对于两个多边形的每一个孔，判断是否与新壳相交
        holes = [*holes1, * holes2]
        # 如果孔相交，则合并孔
        holes = merge_intersectant_holes(holes)
        holes = get_all_not_VGroup_VMobject(holes)
        # 对于每一个孔
        for hole in holes:
            # 孔与新壳相交，用新壳减去孔
            for j in range(len(isc)):
                if polygon_is_strict_intersect(isc[j], hole):
                    isc[j] = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(isc[j], hole)
            # 如果isc中有VGroup，则取出所有的mob
            isc = get_all_not_VGroup_VMobject(isc)
        # 得到了所有的交集多边形的壳，接下来把孔放进去吧可恶
        for i in range(len(isc)):
            if isinstance(isc[i], Polygon):
                cres_hole = []
                for hole in holes:
                    if polygon1_contains_polygon2(isc[i], hole):
                        cres_hole.append(hole)
                if len(cres_hole) > 0:
                    isc[i] = PolygonWithHoles(isc[i].get_vertices(), *[each.get_vertices() for each in cres_hole])
        if len(isc) == 1:
            return isc[0]
        return VGroup(*isc)

    def Union_PolygonWithHoles_and_Dot(self, pwh, dot):
        ## 终于到简单的了，我去
        #pwh, dot = pwh.copy(), dot.copy()
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 壳
        hull = Polygon(*pwh_vs[0])
        # 点在壳外，则加集取VGroup
        if point_is_strict_outside_polygon(dot.get_center(), hull):
            return VGroup(pwh, dot)
        # 点在孔内，则加集取VGroup
        for i in range(len(pwh_vs)-1):
            hole = Polygon(*pwh_vs[i+1])
            if point_is_strict_inside_polygon(dot.get_center(), hole):
                return VGroup(pwh, dot)
        # 隐含孔在多边形内，即壳内，且孔外
        return pwh

    def Union_PolygonWithHoles_and_Curve(self, pwh, cur):
        # 懒得写了，基本不会用到吧，可恶
        return VGroup(pwh, cur)

    def Union_PolygonWithHoles_and_Polygon(self, pwh, pol):
        ## 只是一个小boss，下一个才难搞，加油，可恶
        pwh, pol = pwh.stretch(0.99987, 0), pol.stretch(0.99962, 1)
        # 保证多边形pol逆时针（大于0）
        if get_polygon_directed_area(pol) < 0:
            pol = Polygon(*pol.get_vertices()[::-1])
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 拿壳
        hull = Polygon(*pwh_vs[0])
        # 拿孔
        holes = []
        for each in pwh_vs[1:]:
            holes.append(Polygon(*each))
        # 壳与多边形外离，加集取VGroup
        if polygon1_is_strict_outside_polygon2(pol, hull):
            return VGroup(pwh, pol)
        # 多边形在孔内，加集取VGroup
        for hole in holes:
            if polygon1_strict_contains_polygon2(hole, pol):
                return VGroup(pwh, pol)
        # 隐含下面的都不是多边形在壳外，也不是在孔内的情况
        # 多边形包含壳，加集为多边形
        if polygon1_contains_polygon2(pol, hull):
            return pol
        # 壳包含多边形，新壳为多边形，把多边形充满的孔补上
        elif polygon1_contains_polygon2(hull, pol):
            mark_hull = hull
        # 隐含pwh的壳和pol相交
        # 则带孔的多边形和多边形的加为
        # 新壳为pwh的壳和pol相加，并且把pol充满的孔补上
        else:
            # 注意这里有一个坑，就是可能出现，多边形+多边形=带孔多边形
            union_hull = PolygonBooleanOperations().Union_Polygon_and_Polygon(hull, pol)
            if type(union_hull) == PolygonWithHoles:
                union_hull_vs = union_hull.get_vertices()
                mark_hull = Polygon(*union_hull_vs[0])
                for each in union_hull_vs[1:]:
                    holes.append(Polygon(*each))
            else:
                mark_hull = union_hull
        # 把多边形充满的孔补上
        new_holes = []
        for hole in holes:
            # 被多边形包含的孔，直接补上，没被补的，加入新集
            if polygon1_is_outside_polygon2(pol, hole):
                new_holes.append(hole)
            # 和多边形相交的孔，减去相交部分
            elif polygon_is_strict_intersect(pol, hole):
                cutpol = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(hole, pol)
                cutpol = get_all_not_VGroup_VMobject([cutpol])
                for each in cutpol:
                    new_holes.append(each)
        # 孔被填完，返回壳就行
        if len(new_holes) == 0:
            return mark_hull
        # 构造多边形为，新壳和未补上孔
        return PolygonWithHoles(mark_hull.get_vertices(), *[hole.get_vertices() for hole in new_holes])

    def Union_PolygonWithHoles_and_PolygonWithHoles(self, pwh1, pwh2):
        ## 这个超级难的，可恶极了
        pwh1, pwh2 = pwh1.stretch(0.9996, 1), pwh2.stretch(0.99974, 0)
        # 拿点集
        pwh1_vs, pwh2_vs = pwh1.get_vertices(), pwh2.get_vertices()
        # 拿壳
        hull1, hull2 = Polygon(*pwh1_vs[0]), Polygon(*pwh2_vs[0])
        # 拿孔
        holes1, holes2 = [], []
        for each in pwh1_vs[1:]:
            holes1.append(Polygon(*each))
        for each in pwh2_vs[1:]:
            holes2.append(Polygon(*each))
        # 两个壳外离，加集取VGroup
        if polygon1_is_outside_polygon2(hull1, hull2):
            return VGroup(pwh1, pwh2)
        # 多边形的壳在另一个多边形的孔内，加集取VGroup
        for hole1 in holes1:
            if polygon1_strict_contains_polygon2(hole1, hull2):
                return VGroup(pwh1, pwh2)
        for hole2 in holes2:
            if polygon1_strict_contains_polygon2(hole2, hull1):
                return VGroup(pwh1, pwh2)
        # 隐含下面的都不是壳在壳外，也不是壳在孔内的情况
        # 先考虑壳包含壳的情况，再考虑壳相交的情况
        # hull1包含hull2，则加集为，hull1，减去hull2没有包含的孔，减去(hole1减去hull2)，减去hull2包含的孔和hull1的孔的交，
        if polygon1_contains_polygon2(hull2, hull1):
            hull1, hull2 = hull2, hull1
            holes1, holes2 = holes2, holes1
        if polygon1_contains_polygon2(hull1, hull2):
            new_hull = hull1
            mark = False
        # 只剩下两壳相交的情况
        # hull1和hull2相交，则加集为，hull1+hull2，减去hull1或hull2没有包含的孔，减去hull2包含的孔和hull1的孔的交
        else:
            new_hull = PolygonBooleanOperations().Union_Polygon_and_Polygon(hull1, hull2)
            mark = True
        new_holes = []
        # 构造孔和壳
        for hole1 in holes1:
            # hull2没有包含的孔
            if polygon1_is_outside_polygon2(hole1, hull2):
                new_holes.append(hole1)
            # hole1减去hull2
            elif polygon_is_strict_intersect(hole1, hull2):
                cutpol = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(hole1, hull2)
                cutpol = get_all_not_VGroup_VMobject([cutpol])
                for each in cutpol:
                    if isinstance(each, Polygon):
                        new_holes.append(each)
            # 两孔的交
            for hole2 in holes2:
                ishole = PolygonBooleanOperations().Intersection_Polygon_and_Polygon(hole1, hole2)
                if type(ishole) == VMobject:
                    continue
                else:
                    ishole = get_all_not_VGroup_VMobject([ishole])
                    for each in ishole:
                        new_holes.append(each)
        # 两壳相交的情况
        if mark:
            for hole2 in holes2:
                # hull1没有包含的孔
                if polygon1_is_outside_polygon2(hole2, hull1):
                    new_holes.append(hole2)
                # hole2减去hull1
                elif polygon_is_strict_intersect(hole2, hull1):
                    cutpol = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(hole2, hull1)
                    cutpol = get_all_not_VGroup_VMobject([cutpol])
                    for each in cutpol:
                        if isinstance(each, Polygon):
                            new_holes.append(each)
        if len(new_holes) == 0:
            return new_hull
        else:
            return PolygonWithHoles(new_hull.get_vertices(), *[hole.get_vertices() for hole in new_holes])

    def Subtraction_PolygonWithHoles_and_Dot(self, pwh, dot):
        #return pwh.copy()
        return pwh

    def Subtraction_Dot_and_PolygonWithHoles(self, dot, pwh):
        # 点在带孔多边形内，则返回空，否则返回点
        if pwh.point_is_inside_PolygonWithHoles(dot.get_center()):
            return VMobject()
        #return dot.copy()
        return dot

    def Subtraction_PolygonWithHoles_and_Curve(self, pwh, cur):
        #return pwh.copy()
        return pwh

    def Subtraction_Curve_and_PolygonWithHoles(self, cur, pwh):
        #cur, pwh = cur.copy(), pwh.copy()
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 拿壳
        hull = Polygon(*pwh_vs[0])
        # 拿孔
        holes = []
        for each in pwh_vs[1:]:
            holes.append(Polygon(*each))
        # 等于曲线减壳，加曲线和孔的交
        cutset = VGroup()
        cutset.add(CurveBooleanOperations().Subtraction_Curve_and_Polygon(cur, hull))
        for hole in holes:
            cutcur = CurveBooleanOperations().Intersection_Curve_and_Polygon(cur, hole)
            if type(cutcur) != VMobject:
                cutset.add(cutcur)
        cutset = get_all_not_VGroup_VMobject([cutset])
        # 减集只有一条曲线
        if len(cutset) == 1:
            return cutset[0]
        # 隐含多条
        return VGroup(*cutset)

    def Subtraction_PolygonWithHoles_and_Polygon(self, pwh, pol):
        ## 加油，可恶，这个简单极了
        pwh, pol = pwh, pol.stretch(0.99927, 0).stretch(0.9992, 1)
        # 保证多边形pol逆时针（大于0）
        if get_polygon_directed_area(pol) < 0:
            pol = Polygon(*pol.get_vertices()[::-1])
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 拿壳
        hull = Polygon(*pwh_vs[0])
        # 拿孔
        holes = []
        for each in pwh_vs[1:]:
            holes.append(Polygon(*each))
        # 壳与多边形外离，减集为pwh
        if polygon1_is_outside_polygon2(pol, hull):
            return pwh
        # 多边形在孔内，减集为pwh
        for hole in holes:
            if polygon1_strict_contains_polygon2(hole, pol):
                return pwh
        # 隐含下面的都不是多边形在壳外，也不是在孔内的情况
        # 多边形包含壳，减集为空
        if polygon1_contains_polygon2(pol, hull):
            return VMobject()
        # 壳包含多边形，新壳为多边形，多边形为新孔，并合并孔
        elif polygon1_contains_polygon2(hull, pol):
            holes.append(pol)
            # 如果孔相交，则合并孔
            holes = merge_intersectant_holes(holes)
            holes = get_all_not_VGroup_VMobject(holes)
            return PolygonWithHoles(hull.get_vertices(), *[hole.get_vertices() for hole in holes])
        # 隐含壳与多边形相交
        new_hulls = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(hull, pol)
        new_hulls = get_all_not_VGroup_VMobject([new_hulls])
        new_pwhs = []
        for each_hull in new_hulls:
            resp_holes = []
            for hole in holes:
                if polygon1_contains_polygon2(each_hull, hole):
                    resp_holes.append(hole)
                elif polygon_is_strict_intersect(each_hull, hole):
                    cut_holes = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(hole, pol)
                    cut_holes = get_all_not_VGroup_VMobject([cut_holes])
                    for each_cut_holes in cut_holes:
                        resp_holes.append(each_cut_holes)
            if len(resp_holes) == 0:
                new_pwhs.append(each_hull)
            else:
                new_pwhs.append(PolygonWithHoles(each_hull.get_vertices(), *[hole.get_vertices() for hole in resp_holes]))
        if len(new_pwhs) == 1:
            return new_pwhs[0]
        else:
            return VGroup(*new_pwhs)

    def Subtraction_Polygon_and_PolygonWithHoles(self, pol, pwh):
        ## 加油，可恶，这个简单极了
        pwh, pol = pwh, pol.stretch(0.9996, 0).stretch(0.99935, 1)
        # 保证多边形pol逆时针（大于0）
        if get_polygon_directed_area(pol) < 0:
            pol = Polygon(*pol.get_vertices()[::-1])
        # 拿点集
        pwh_vs = pwh.get_vertices()
        # 拿壳
        hull = Polygon(*pwh_vs[0])
        # 拿孔
        holes = []
        for each in pwh_vs[1:]:
            holes.append(Polygon(*each))
        # 壳与多边形外离，减集为pol
        if polygon1_is_outside_polygon2(pol, hull):
            return pol
        # 多边形在孔内，减集为pol
        for hole in holes:
            if polygon1_strict_contains_polygon2(hole, pol):
                return pol
        # 隐含下面的都不是多边形在壳外，也不是在孔内的情况
        # 多边形包含壳
        if polygon1_contains_polygon2(pol, hull):
            return VGroup(PolygonWithHoles(pol.get_vertices(), hull.get_vertices()), *holes)
        # 壳包含多边形，减集为在多边形内的孔
        if polygon1_contains_polygon2(hull, pol):
            cutpol = []
        # 隐含壳与多边形相交
        else:
            cutpol = []
            pol_cut_pwh = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(pol, hull)
            pol_cut_pwh = get_all_not_VGroup_VMobject([pol_cut_pwh])
            for each in pol_cut_pwh:
                cutpol.append(each)
        for hole in holes:
            cut_holes = PolygonBooleanOperations().Intersection_Polygon_and_Polygon(hole, pol)
            cut_holes = get_all_not_VGroup_VMobject([cut_holes])
            for each_cut_holes in cut_holes:
                if type(each_cut_holes) != VMobject:
                    cutpol.append(each_cut_holes)
        if len(cutpol) == 0:
            return VMobject()
        elif len(cutpol) == 1:
            return cutpol[0]
        else:
            return VGroup(*cutpol)

    def Subtraction_PolygonWithHoles_and_PolygonWithHoles(self, pwh1, pwh2):
        ## 这个敲难，又是一个大boss，加油，我是最胖的！
        pwh1, pwh2 = pwh1.stretch(0.9998, 1), pwh2
        # 拿点集
        pwh1_vs, pwh2_vs = pwh1.get_vertices(), pwh2.get_vertices()
        # 拿壳
        hull1, hull2 = Polygon(*pwh1_vs[0]), Polygon(*pwh2_vs[0])
        # 拿孔
        holes1, holes2 = [], []
        for each in pwh1_vs[1:]:
            holes1.append(Polygon(*each))
        for each in pwh2_vs[1:]:
            holes2.append(Polygon(*each))
        # 两个壳外离，加集取VGroup
        if polygon1_is_outside_polygon2(hull1, hull2):
            return pwh1
        # 多边形的壳在另一个多边形的孔内，加集取VGroup
        for hole1 in holes1:
            if polygon1_contains_polygon2(hole1, hull2):
                return pwh1
        for hole2 in holes2:
            if polygon1_contains_polygon2(hole2, hull1):
                return pwh1
        # 隐含下面的都不是壳在壳外，也不是壳在孔内的情况
        # 壳1包含壳2，则减集为，pwh1减去hull2，加上对于2的每一个孔，减去1的所有孔的结果
        if polygon1_contains_polygon2(hull1, hull2):
            cut_pwh = PolygonWithHolesBooleanOperations().Subtraction_PolygonWithHoles_and_Polygon(pwh1, hull2)
            new_holes = [*holes2]
            for hole1 in holes1:
                frag2 = []
                for each in new_holes:
                    if polygon_is_strict_intersect(each, hole1):
                        spp = PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(each, hole1)
                        spp = get_all_not_VGroup_VMobject([spp])
                        for sppf in spp:
                            frag2.append(sppf)
                    else:
                        frag2.append(each)
                new_holes = frag2
            if len(new_holes) == 0:
                return cut_pwh
            else:
                return VGroup(cut_pwh, *new_holes)

        # 壳2包含壳1，则减集为，
        elif polygon1_contains_polygon2(hull2, hull1):
            cut_pwh1 = []
            for hole2 in holes2:
                hole2_cut_phw = PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Polygon(pwh1, hole2)
                hole2_cut_phw = get_all_not_VGroup_VMobject([hole2_cut_phw])
                for each in hole2_cut_phw:
                    cut_pwh1.append(each)
            if len(cut_pwh1) == 0:
                return VMobject()
            if len(cut_pwh1) == 1:
                return cut_pwh1[0]
            else:
                return VGroup(*cut_pwh1)

        # 隐含壳与多边形相交
        else:
            pwh_cut_pol = PolygonWithHolesBooleanOperations().Subtraction_PolygonWithHoles_and_Polygon(pwh1, hull2)
            pwh_cut_pol = get_all_not_VGroup_VMobject([pwh_cut_pol])
            cut_pwh1 = pwh_cut_pol
            for hole2 in holes2:
                hole2_cut_phw = PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Polygon(pwh1, hole2)
                hole2_cut_phw = get_all_not_VGroup_VMobject([hole2_cut_phw])
                for each in hole2_cut_phw:
                    cut_pwh1.append(each)
            if len(cut_pwh1) == 0:
                return VMobject()
            if len(cut_pwh1) == 1:
                return cut_pwh1[0]
            else:
                return VGroup(*cut_pwh1)

# 关于VGroup的bool运算
class VGroupBooleanOperations:
    def Intersection(self, vgp1, vgp2):
        #vgp1, vgp2 = vgp1.copy(), vgp2.copy()
        mob1s = get_all_not_VGroup_VMobject([vgp1])
        mob2s = get_all_not_VGroup_VMobject([vgp2])
        isgps = []
        for mob1 in mob1s:
            for mob2 in mob2s:
                ismob = PolygonIntersection(mob1, mob2)
                if type(ismob) != VMobject:
                    isgps.append(ismob)
        if len(isgps) == 0:
            return VMobject()
        if len(isgps) == 1:
            return isgps[0]
        else:
            return VGroup(*isgps)

    def Union(self, vgp1, vgp2):
        #vgp1, vgp2 = vgp1.copy(), vgp2.copy()
        mob1s = get_all_not_VGroup_VMobject([vgp1])
        mob2s = get_all_not_VGroup_VMobject([vgp2])
        mobs = []
        for each in mob1s:
            if type(each) != VMobject:
                mobs.append(each)
        for each in mob2s:
            if type(each) != VMobject:
                mobs.append(each)
        if len(mobs) == 0:
            return VMobject()
        if len(mobs) == 1:
            return mobs[0]
        if len(mobs) == 2:
            return PolygonUnion(mobs[0], mobs[1])
        # 考虑合并多边形吧
        # 分为三类，多边形，带孔多边形，这里把多边形转为带孔多边形
        pwh_mobs, ippwh_mobs = [], []
        for each in mobs:
            if isinstance(each, Polygon):
                pwh_mobs.append(PolygonWithHoles(each.get_vertices()))
            elif type(each) == PolygonWithHoles:
                pwh_mobs.append(each)
            else:
                ippwh_mobs.append(each)

        def get_intersect_2pwh_index(pwhs):
            for i in range(len(pwhs)):
                for j in range(len(pwhs) - i - 1):
                    is2pwh = PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_PolygonWithHoles(pwhs[i], pwhs[j + i + 1])
                    if type(is2pwh) != VGroup:
                        return i, j + i + 1, is2pwh
            return -1, -1, VMobject()

        def merge_pwhs(pwhs):
            ispwhi, ispwhj, new_pwh = get_intersect_2pwh_index(pwhs)
            while ispwhi != -1:
                pwhs.pop(ispwhi)
                pwhs.pop(ispwhj - 1)
                pwhs.append(new_pwh)
                ispwhi, ispwhj, new_pwh = get_intersect_2pwh_index(pwhs)
            return pwhs

        pwh_mobs = merge_pwhs(pwh_mobs)
        mobs = [*pwh_mobs, *ippwh_mobs]
        if len(mobs) == 0:
            return VMobject()
        if len(mobs) == 1:
            return mobs[0]
        else:
            return VGroup(*mobs)

    def Subtraction(self, vgp1, vgp2):
        #vgp1, vgp2 = vgp1.copy(), vgp2.copy()
        mob1s = get_all_not_VGroup_VMobject([vgp1])
        mob2s = get_all_not_VGroup_VMobject([vgp2])
        cutgps = []
        for mob1 in mob1s:
            cutmob = mob1
            for mob2 in mob2s:
                cutmob = PolygonSubtraction(cutmob, mob2)
                if type(cutmob) != VMobject:
                    cutgps.append(cutmob)
        if len(cutgps) == 0:
            return VMobject()
        if len(cutgps) == 1:
            return cutgps[0]
        else:
            return VGroup(*cutgps)
    

# pol1∩pol2
def PolygonIntersection(pol1, pol2):
    pol1, pol2 = pol1.copy(), pol2.copy()

    # 一方为VGroup
    if type(pol1) == VGroup or type(pol2) == VGroup:
        return VGroupBooleanOperations().Intersection(VGroup(pol1), VGroup(pol2))

    # 一方为空，交集为空
    if type(pol1) == VMobject or type(pol2) == VMobject:
        return VMobject()

    # 圆或椭圆转多边形
    if isinstance(pol1, Circle):
        pol1 = ellipse_to_polygon(pol1)
    if isinstance(pol2, Circle):
        pol2 = ellipse_to_polygon(pol2)

    # 直线转CurveClip曲线
    if isinstance(pol1, Line):
        pol1 = CurveClip().add(pol1)
    if isinstance(pol2, Line):
        pol2 = CurveClip().add(pol2)

    # 曲线转CurveClip曲线
    if isinstance(pol1, ParametricCurve):
        pol1 = CurveClip(pol1)
    if isinstance(pol2, ParametricCurve):
        pol2 = CurveClip(pol2)
    
    # polygon 带孔
    # pol1 带孔
    if isinstance(pol1, PolygonWithHoles):
        # pol2为一点
        if isinstance(pol2, Dot):
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Curve(pol1, pol2)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Polygon(pol1, pol2)
        # pol2为带孔多边形
        if isinstance(pol2, PolygonWithHoles):
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_PolygonWithHoles(pol1, pol2)

    # pol2 带孔
    if isinstance(pol2, PolygonWithHoles):
        # pol1为一点
        if isinstance(pol1, Dot):
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Dot(pol2, pol1)
        # pol1为曲线
        if type(pol1) == CurveClip:
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Curve(pol2, pol1)
        # pol1为多边形
        if isinstance(pol1, Polygon):
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_Polygon(pol2, pol1)
        # pol1为带孔多边形
        if isinstance(pol1, PolygonWithHoles):
            return PolygonWithHolesBooleanOperations().Intersection_PolygonWithHoles_and_PolygonWithHoles(pol2, pol1)

    # pol1为一点
    if isinstance(pol1, Dot):
        # pol2为一点
        if isinstance(pol2, Dot):
            return DotBooleanOperations().Intersection_Dot_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return DotBooleanOperations().Intersection_Dot_and_Curve(pol1, pol2)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return DotBooleanOperations().Intersection_Dot_and_Polygon(pol1, pol2)

    # pol1为一曲线
    if type(pol1) == CurveClip:
        # pol2为一点
        if isinstance(pol2, Dot):
            return CurveBooleanOperations().Intersection_Curve_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return CurveBooleanOperations().Intersection_Curve_and_Curve(pol2, pol1)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return CurveBooleanOperations().Intersection_Curve_and_Polygon(pol1, pol2)

    # pol1为一多边形
    if isinstance(pol1, Polygon):
        # pol2为一点
        if isinstance(pol2, Dot):
            return PolygonBooleanOperations().Intersection_Polygon_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return PolygonBooleanOperations().Intersection_Polygon_and_Curve(pol1, pol2)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return PolygonBooleanOperations().Intersection_Polygon_and_Polygon(pol1, pol2)

    # 出错
    print("出bug了，请联系颓废，私信bilibili有一种悲伤叫颓废")
    return None

# pol1+pol2
def PolygonUnion(pol1, pol2):
    pol1, pol2 = pol1.copy(), pol2.copy()

    # 一方为VGroup
    if type(pol1) == VGroup or type(pol2) == VGroup:
        return VGroupBooleanOperations().Union(VGroup(pol1), VGroup(pol2))

    # 一方为空，加集为另一个
    if type(pol1) == VMobject:
        return pol2
    if type(pol2) == VMobject:
        return pol1

    # 圆或椭圆转多边形
    if isinstance(pol1, Circle):
        pol1 = ellipse_to_polygon(pol1)
    if isinstance(pol2, Circle):
        pol2 = ellipse_to_polygon(pol2)

    # 直线转CurveClip曲线
    if isinstance(pol1, Line):
        pol1 = CurveClip().add(pol1)
    if isinstance(pol2, Line):
        pol2 = CurveClip().add(pol2)

    # 曲线转CurveClip曲线
    if isinstance(pol1, ParametricCurve):
        pol1 = CurveClip(pol1)
    if isinstance(pol2, ParametricCurve):
        pol2 = CurveClip(pol2)

    # polygon 带孔
    # pol1 带孔
    if isinstance(pol1, PolygonWithHoles):
        # pol2为一点
        if isinstance(pol2, Dot):
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_Curve(pol1, pol2)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_Polygon(pol1, pol2)
        # pol2为带孔多边形
        if isinstance(pol2, PolygonWithHoles):
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_PolygonWithHoles(pol1, pol2)

    # pol2 带孔
    if isinstance(pol2, PolygonWithHoles):
        # pol1为一点
        if isinstance(pol1, Dot):
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_Dot(pol2, pol1)
        # pol1为曲线
        if type(pol1) == CurveClip:
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_Curve(pol2, pol1)
        # pol1为多边形
        if isinstance(pol1, Polygon):
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_Polygon(pol2, pol1)
        # pol1为带孔多边形
        if isinstance(pol1, PolygonWithHoles):
            return PolygonWithHolesBooleanOperations().Union_PolygonWithHoles_and_PolygonWithHoles(pol2, pol1)

    # pol1为一点
    if isinstance(pol1, Dot):
        # pol2为一点
        if isinstance(pol2, Dot):
            return DotBooleanOperations().Union_Dot_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return DotBooleanOperations().Union_Dot_and_Curve(pol1, pol2)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return DotBooleanOperations().Union_Dot_and_Polygon(pol1, pol2)

    # pol1为一曲线
    if type(pol1) == CurveClip:
        # pol2为一点
        if isinstance(pol2, Dot):
            return CurveBooleanOperations().Union_Curve_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return CurveBooleanOperations().Union_Curve_and_Curve(pol2, pol1)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return CurveBooleanOperations().Union_Curve_and_Polygon(pol1, pol2)

    # pol1为一多边形
    if isinstance(pol1, Polygon):
        # pol2为一点
        if isinstance(pol2, Dot):
            return PolygonBooleanOperations().Union_Polygon_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return PolygonBooleanOperations().Union_Polygon_and_Curve(pol2, pol1)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return PolygonBooleanOperations().Union_Polygon_and_Polygon(pol1, pol2)

    # 出错
    print("出bug了，请联系颓废，私信bilibili有一种悲伤叫颓废")
    return None

# pol1-pol2
def PolygonSubtraction(pol1, pol2):
    pol1, pol2 = pol1.copy(), pol2.copy()

    # 一方为VGroup
    if type(pol1) == VGroup or type(pol2) == VGroup:
        return VGroupBooleanOperations().Subtraction(VGroup(pol1), VGroup(pol2))

    # 一方为空
    if type(pol1) == VMobject:
        return VMobject()
    if type(pol2) == VMobject:
        return pol1

    # 圆或椭圆转多边形
    if isinstance(pol1, Circle):
        pol1 = ellipse_to_polygon(pol1)
    if isinstance(pol2, Circle):
        pol2 = ellipse_to_polygon(pol2)

    # 直线转CurveClip曲线
    if isinstance(pol1, Line):
        pol1 = CurveClip().add(pol1)
    if isinstance(pol2, Line):
        pol2 = CurveClip().add(pol2)

    # 曲线转CurveClip曲线
    if isinstance(pol1, ParametricCurve):
        pol1 = CurveClip(pol1)
    if isinstance(pol2, ParametricCurve):
        pol2 = CurveClip(pol2)

    # polygon 带孔
    # pol1 带孔
    if isinstance(pol1, PolygonWithHoles):
        # pol2为一点
        if isinstance(pol2, Dot):
            return PolygonWithHolesBooleanOperations().Subtraction_PolygonWithHoles_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return PolygonWithHolesBooleanOperations().Subtraction_PolygonWithHoles_and_Curve(pol1, pol2)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return PolygonWithHolesBooleanOperations().Subtraction_PolygonWithHoles_and_Polygon(pol1, pol2)
        # pol2为带孔多边形
        if isinstance(pol2, PolygonWithHoles):
            return PolygonWithHolesBooleanOperations().Subtraction_PolygonWithHoles_and_PolygonWithHoles(pol1, pol2)

    # pol2 带孔
    if isinstance(pol2, PolygonWithHoles):
        # pol1为一点
        if isinstance(pol1, Dot):
            return PolygonWithHolesBooleanOperations().Subtraction_Dot_and_PolygonWithHoles(pol1, pol2)
        # pol1为曲线
        if type(pol1) == CurveClip:
            return PolygonWithHolesBooleanOperations().Subtraction_Curve_and_PolygonWithHoles(pol1, pol2)
        # pol1为多边形
        if isinstance(pol1, Polygon):
            return PolygonWithHolesBooleanOperations().Subtraction_Polygon_and_PolygonWithHoles(pol1, pol2)
        # pol1为带孔多边形
        if isinstance(pol1, PolygonWithHoles):
            return PolygonWithHolesBooleanOperations().Subtraction_PolygonWithHoles_and_PolygonWithHoles(pol1, pol2)

    # pol1为一点
    if isinstance(pol1, Dot):
        # pol2为一点
        if isinstance(pol2, Dot):
            return DotBooleanOperations().Subtraction_Dot_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return CurveBooleanOperations().Subtraction_Curve_and_Dot(pol2, pol1)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return DotBooleanOperations().Subtraction_Dot_and_Polygon(pol1, pol2)

    # pol1为一曲线
    if type(pol1) == CurveClip:
        # pol2为一点
        if isinstance(pol2, Dot):
            return CurveBooleanOperations().Subtraction_Curve_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return CurveBooleanOperations().Subtraction_Curve_and_Curve(pol2, pol1)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return CurveBooleanOperations().Subtraction_Curve_and_Polygon(pol1, pol2)

    # pol1为一多边形
    if isinstance(pol1, Polygon):
        # pol2为一点
        if isinstance(pol2, Dot):
            return PolygonBooleanOperations().Subtraction_Polygon_and_Dot(pol1, pol2)
        # pol2为曲线
        if type(pol2) == CurveClip:
            return PolygonBooleanOperations().Subtraction_Polygon_and_Curve(pol1, pol2)
        # pol2为多边形
        if isinstance(pol2, Polygon):
            return PolygonBooleanOperations().Subtraction_Polygon_and_Polygon(pol1, pol2)

    # 出错
    print("出bug了，请联系颓废，私信bilibili有一种悲伤叫颓废")
    return None

# 测试类
class PolygonBooleanTest(Scene):
    def construct(self):
        pwh1 = PolygonWithHoles(
            Polygon(RIGHT*0.7, UR, UL, DL, DR).scale(2).stretch(0.6, 1).get_vertices(),
            RegularPolygon(3).get_vertices(),
        )
        pwh2 = pwh1.copy().shift(UL)
        pwh3 = pwh1.copy().shift(DR)
        pwh4 = pwh1.copy().shift(DL)
        boolpol = PolygonUnion(
            VGroup(pwh1, pwh2, pwh3, pwh4), VMobject()
        ).set_stroke(color=YELLOW, width=0).set_fill(color=YELLOW, opacity=0.7)
        self.add(pwh1, pwh2, pwh3, pwh4, boolpol)
        '''
        pol1 = RegularPolygon(9).scale(2).shift(LEFT)
        pol2 = RegularPolygon(9).scale(2).shift(RIGHT)
        start = time.perf_counter()
        boolpol = PolygonSubtraction(
            PolygonUnion(pol1, pol2), PolygonIntersection(pol1, pol2)
        ).set_stroke(color=YELLOW, width=0).set_fill(color=YELLOW, opacity=0.5)
        end = time.perf_counter()
        print(end - start)
        self.add(pol1, pol2, boolpol)
        '''
        '''
        pol1 = RegularPolygon(16).scale(2)
        pol2 = Circle().stretch(1.2, 1).stretch(0.8, 0)
        pol3 = RegularPolygon(5).scale(2).shift(LEFT*0.9)
        pol4 = RegularPolygon(3).stretch(3, 1).shift(LEFT)
        pol5 = Ellipse().scale(0.6).shift(LEFT).stretch(2, 0)
        #start = time.perf_counter()
        boolpol = PolygonSubtraction(
            PolygonUnion(
                PolygonIntersection(
                    PolygonSubtraction(
                        pol1, pol2), pol3), pol4), pol5) \
            .set_stroke(color=YELLOW, width=0).set_fill(color=YELLOW, opacity=0.5)
        #end = time.perf_counter()
        #print(end - start)#0.49910769999999993
        self.add(pol1, pol2, pol3, pol4, pol5, boolpol)
        '''