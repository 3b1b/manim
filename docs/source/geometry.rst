Geometry
========
In the file geometry.py are contained several classes to create shapes and other objects.
This is a list of commonly used classes.
The most useful constructor parameters are listed under the description of the classes.
However, these lists are not exhaustive and for example many objects can be passed the following arguments :

*color* \:
        color to draw and fill the object with

*fill_opacity* \: float (between 0 and 1)
        the object is filled with the given opacity

.. _Arc:

Arc
---

Represents an arc.
Inherits from *TipableVMobject*.

Parameters :

*radius* \: float, optional, default: 1.0
        distance from *arc_center* to the arc

*arc_center* \: numpy array of dimension 3, optional, default: ORIGIN
        point to which all points in the arc are equidistants

*start_angle* \: float (in radians), optional, default: 0
        the angle at which to start the arc

*angle* \: float (in radians), optional, default: TAU/4 (equal to PI/2)
        total angle between the point in start angle and the last point in the arc, measured from the arc_center

.. _ArcBetweenPoints:

ArcBetweenPoints
----------------
Represents an arc between two points.
Inherits from Arc_.
The arc center is computed as being on the left side of the perpendicular of the line from *start* to *end*.

Parameters :

*start* \: numpy array of dimension 3
        start point

*end* \: numpy array of dimension 3
        end point

*angle* \: float (in radians), optional, default: TAU/4 (equal to PI/2)
        total angle between the start point and the end point, measured from the arc_center

.. _CurvedArrow:

CurvedArrow
-----------
Represents a curved arrow between two points.
Inherits from ArcBetweenPoints_.
Behaviour very close from its parent class.

Parameters :

*start_point* \: numpy array of dimension 3
        start point

*end_point* \: numpy array of dimension 3
        end point

*angle* \: float (in radians), optional, default: TAU/4 (equal to PI/2)
        total angle between the start point and the end point, measured from the arc_center

.. _CurvedDoubleArrow:

CurvedDoubleArrow
-----------------
Represents a double curved arrow between two points.
Inherits from CurvedArrow_.
Behaviour very close from its parent class.
When playing the animation *ShowCreation*, first draws the curved arrow from *start_point* to *end_point* and then draws the tip at *start_point*.

Parameters :

*start_point* \: numpy array of dimension 3
        start point

*end_point* \: numpy array of dimension 3
        end point

*angle* \: float (in radians), optional, default: TAU/4 (equal to PI/2)
        total angle between the start point and the end point, measured from the arc_center

.. _Circle:

Circle
------
Represents a circle.
Inherits from Arc_.
Default color is red.

Parameters :

*radius* \: float, optional, default: 1.0
        distance from *arc_center* to the arc

*arc_center* \: numpy array of dimension 3, optional, default: ORIGIN
        point to which all points in the arc are equidistants

.. _Dot:

Dot
---
Represents a dot.
Inherits from Circle_.
Default color is white.

Parameters :

*point* \: numpy array of dimension 3, optional, default: ORIGIN
        center of the dot

*radius* \: float, optional, default: DEFAULT_DOT_RADIUS
        size of the dot

.. _SmallDot:

SmallDot
--------
Represents a small dot.
Inherits from Dot_.
It has exactly the same behaviour as *Dot* except its *radius* is set to DEFAULT_SMALL_DOT_RADIUS.

.. _Ellipse:

Ellipse
-------
Represents an ellipse.
Inherits from Circle_.
The ellipse is built by passing the dimensions of the rectangle in which the ellipse is inscribed.

Parameters :

*width* \: float, optional, default: 2
        width of the rectangle in which the ellipse is inscribed

*height* \: float, optional, default: 1
        height of the rectangle in which the ellipse is inscribed

*arc_center* \: numpy array of dimension 3, optional, default: ORIGIN
        center of the ellipse

.. _AnnularSector:

AnnularSector
-------------
Represents an annular sector.
Inherits from Arc_.
Default color is white.

Parameters :

*inner_radius* \: float, optional, default: 1
        radius of the inner arc

*outer_radius* \: float, optional, default: 2
        radius of the outer arc

*start_angle* \: float (in radians), optional, default: 0
        start angle of the two arcs

*angle* \: float (in radians), optional, default: TAU/4 (equal PI/2)
        angle between the start angle and the last point of the two arcs

*arc_center* \: numpy array of dimension 3, optional, default: ORIGIN
        center of the annular sector

.. _Sector:

Sector
------
Represents a sector, like a part of a pie.
Inherits from AnnularSector_.

Parameters :

*outer_radius* \: float, optional, default: 1
        radius of the arc

*start_angle* \: float (in radians), optional, default: 0
        start angle of the arc

*angle* \: float (in radians), optional, default: TAU/4 (equal PI/2)
        angle between the start angle and the last point of the arc

*arc_center* \: numpy array of dimension 3, optional, default: ORIGIN
        center of the sector

.. _Annulus:

Annulus
-------
Represents an annulus (ring shape).
Inherits from Circle_.
Default color is white.

Parameters :

*inner_radius* \: float, optional, default: 1
        radius of the inner circle

*outer_radius* \: float, optional, default: 2
        radius of the outer circle

*arc_center* \: numpy array of dimension 3, optional, default: ORIGIN
        center of the two circles

.. _Line:

Line
----
Represents a line.
Inherits from *TipableVMobject*.

Parameters :

*start* \: numpy array of dimension 3, optional, default: LEFT
        start point of the line

*end* \: numpy array of dimension 3, optional, default: RIGHT
        end point of the line

*path_arc* \: float (in radians), optional, default: None
        if set to None, the line is a straight line.
        Otherwise, the line is a curved line between *start* and *end* with the angle specified.
        Behaviour becomes similar to ArcBetweenPoints_.

.. _DashedLine:

DashedLine
----------
Represents a dashed line.
Inherits from Line_.

Parameters :

*start* \: numpy array of dimension 3, optional, default: LEFT
        start point of the line

*end* \: numpy array of dimension 3, optional, default: RIGHT
        end point of the line

*path_arc* \: float (in radians), optional, default: None
        if set to None, the line is a straight line.
        Otherwise, the line is a curved line between *start* and *end* with the angle specified.
        Behaviour becomes similar to ArcBetweenPoints_.

*dash_length* \: float, optional, default: DEFAULT_DASH_LENGTH
        length of each dash

*positive_space_ratio* \: float (> 0 and <= 1), optional, default: 0.5
        ratio in one unit of space the length of one dash.
        This means that one dash and one blank space occupy *dash_length*/*positive_space_ratio*.

.. _TangentLine:

TangentLine
-----------
Represents a straight line tangent to a given object.
Inherits from Line_.

Parameters :

*vmob* \:
        object to which the line is tangent

*alpha* \: float (between 0 and 1)
        indicates the position of the tangent line.
        On the circle 0 represents tangent at point at angle 0 and 0.5 represents tangent at point at angle PI.

*length* \: float, optional, default:1
        length of the line

.. _Elbow:

Elbow
-----
Represents the perpendicular symbol.
Inherits from *VMobject*.

Parameters :

*width* \: float, optional, default: 0.2
        length from each side of the symbol

Methods :

*set_points_as_corners(points)* \:
        set the points corners to the three points passed as arguments

*set_width(width, about_point=ORIGIN)* \:
        set the length from each side of the symbol and centers the symbol at *about_point*

Example :

Here is an example on how to place the elbow in a triangle.

.. code-block:: python

        class ElbowExample(Scene):
            def construct(self):
                triangle = Polygon(ORIGIN, RIGHT, RIGHT+UP)
                elbow = Elbow(color=RED)
                elbow.set_points_as_corners([ORIGIN, RIGHT, RIGHT+UP])
                elbow.set_width(elbow.width, about_point=RIGHT+np.array([-0.1, 0.1, 0.0]))
                self.add(triangle)
                self.add(elbow)
                self.wait(2)

.. _Arrow:

Arrow
-----
Represents an arrow.
Inherits from Line_.

Parameters :

*start* \: numpy array of dimension 3, optional, default: LEFT
        start point of the arrow

*end* \: numpy array of dimension 3, optional, default: RIGHT
        end point of the arrow

.. _Vector:

Vector
------
Represents an arrow from the origin to another point.
Inherits from Arrow_.

Parameters :

*direction* \: numpy array of dimension 3, optional, default: RIGHT
        point towards which the arrow goes

.. _DoubleArrow:

DoubleArrow
-----------
Represents a double arrow.
Inherits from Arrow_.

Parameters :

*start* \: numpy array of dimension 3, optional, default: LEFT
        start point of the arrow

*end* \: numpy array of dimension 3, optional, default: RIGHT
        end point of the arrow

.. _Polygon:

Polygon
-------
Represents a polygon.
Inherits from *VMobject*.
Default color is blue.

Parameters :

*\*vertices* \: numpy array of dimension 3
        all the vertices defining the polygon

Example :

.. code-block:: python

        class PolygonExample(Scene):
            def construct(self):
                pentagon = Polygon(2*UP, RIGHT+UP, RIGHT+DOWN, LEFT+DOWN, LEFT+UP)
                self.play(ShowCreation(pentagon))
                self.wait(2)

.. _RegularPolygon:

RegularPolygon
--------------
Represents a regular polygon.
Inherits from Polygon_.

Parameters :

*n* \: int, optional, default:6
        number of polygon's edges

.. _Triangle:

Triangle
--------
Represents a equiteral triangle.
Inherits from RegularPolygon_.

.. _ArrowTip:

ArrowTip
--------
Represents an arrow tip.
Inherits from Triangle_.

.. _Rectangle:

Rectangle
---------
Represents a rectangle.
Inherits from Polygon_.

Parameters :

*height* \: float, optional, default: 2.0
        height of the rectangle

*width* \: float, optional, default: 4.0
        width of the rectangle

.. _Square:

Square
------
Represents a square.
Inherits from Rectangle_.

Parameters :

*side_length* \: float, optional, default: 2.0

.. _RoundedRectangle:

RoundedRectangle
----------------
Represents a rectangle with rounded corners.
Inherits from Rectangle_.

Parameters :

*height* \: float, optional, default: 2.0
        height of the rectangle

*width* \: float, optional, default: 4.0
        width of the rectangle

*corner_radius* \: float, optional, default: 0.5
        radius of the arcs composing the corners
