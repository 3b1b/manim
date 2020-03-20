Geometry
========
In the file geometry.py are contained several helpers to create shapes and different objects.

Arc
---
Draws an arc.
Inherits from *TipableVMobject*.

Parameters :

*radius* \: float, optional, default: 1.0
        distance from *arc_center* to the arc

*arc_center* \: numpy array of dimension 3, optional, default: ORIGIN
        point to which all points in the arc are equidistants
*start_angle* \: float (in radians), optional, default: 0
        the angle at which to start the arc
*angle* \: float (in radians), optional, default: TAU/4 (equal to PI/2)
        total angle between the point in start angle and the last point in the arc

ArcBewteenPoints
----------------
Draws an arc between two points.
Inherits from *Arc*.

Parameters :

- **start** : numpy array of dimension 3,
  start point
- **end** : end point
- **angle** :

CurvedArrow
-----------

CurvedDoubleArrow
-----------------

Circle
------
Draws a circle

Dot
---

SmallDot
--------

Ellipse
-------

AnnularSector
-------------

Sector
------

Annulus
-------

Line
----

DashedLine
----------

TangentLine
-----------

Elbow
-----

Arrow
-----

Vector
------

DoubleArrow
-----------

CubicBezier
-----------

Polygon
-------

RegularPolygon
--------------

Triangle
--------

ArrowTip
--------

Rectangle
---------

Square
------

RoundedRectangle
----------------
