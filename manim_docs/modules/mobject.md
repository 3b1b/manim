# Mobject Module README

## Overview
The mobject (Mathematical Object) module is the core of Manim's visual system. It provides the base classes and implementations for all visual elements that can be displayed and animated in Manim.

## Key Components

### 1. Base Mobject Class (`mobject.py`)
- **Purpose**: Base class for all visual objects
- **Key Features**:
  - Manages object properties and state
  - Handles transformations and updates
  - Provides core functionality for all mobjects
- **Properties**:
  - `color`, `opacity`, `shading`
  - `position`, `scale`, `rotation`
  - `submobjects`: Child mobjects
- **Usage**:
  ```python
  class CustomMobject(Mobject):
      def __init__(self):
          super().__init__()
          self.init_points()
  ```

### 2. Geometry Mobjects (`geometry.py`)
- **Purpose**: Basic geometric shapes
- **Key Classes**:
  - `Circle`, `Square`, `Rectangle`
  - `Line`, `Arrow`, `Polygon`
  - `Arc`, `CurvedArrow`
- **Usage**:
  ```python
  circle = Circle(radius=2)
  square = Square(side_length=3)
  line = Line(start=LEFT, end=RIGHT)
  ```

### 3. Text and LaTeX Mobjects (`text.py`)
- **Purpose**: Text and mathematical notation
- **Key Classes**:
  - `Text`: Regular text
  - `Tex`: LaTeX math
  - `MathTex`: Mathematical expressions
- **Usage**:
  ```python
  text = Text("Hello World")
  equation = Tex(r"\frac{d}{dx}f(x) = \lim_{h \to 0} \frac{f(x+h)-f(x)}{h}")
  ```

### 4. Coordinate Systems (`coordinate_systems.py`)
- **Purpose**: Mathematical coordinate systems
- **Key Classes**:
  - `NumberLine`: One-dimensional number line
  - `Axes`: 2D coordinate system
  - `ThreeDAxes`: 3D coordinate system
- **Usage**:
  ```python
  axes = Axes(
      x_range=[-3, 3],
      y_range=[-3, 3]
  )
  ```

### 5. Vectorized Mobjects (`types/vectorized_mobject.py`)
- **Purpose**: Efficient rendering of complex shapes
- **Key Classes**:
  - `VMobject`: Vector-based mobject
  - `VGroup`: Group of vectorized mobjects
  - `DashedVMobject`: Dashed line version
- **Usage**:
  ```python
  vgroup = VGroup(circle, square, line)
  dashed_line = DashedVMobject(line)
  ```

### 6. 3D Mobjects (`three_dimensions.py`)
- **Purpose**: Three-dimensional objects
- **Key Classes**:
  - `Sphere`, `Cube`, `Cylinder`
  - `Surface`: Parametric surfaces
  - `ThreeDScene`: 3D scene support
- **Usage**:
  ```python
  sphere = Sphere(radius=2)
  cube = Cube(side_length=3)
  ```

### 7. Interactive Mobjects (`interactive.py`)
- **Purpose**: User-interactive elements
- **Key Classes**:
  - `ValueTracker`: Tracks numerical values
  - `Button`: Clickable buttons
  - `Slider`: Value sliders
- **Usage**:
  ```python
  tracker = ValueTracker(0)
  slider = Slider(min_value=0, max_value=10)
  ```

## Mobject Features

### 1. Transformations
- Position changes
- Scaling and rotation
- Color and opacity changes
- Complex transformations

### 2. Grouping
- Parent-child relationships
- Group transformations
- Layering and z-index

### 3. Animation Support
- Property interpolation
- Path following
- Complex animations

## Interaction with Other Modules

1. **Animation Module**:
   - Mobjects are animated
   - Properties can be interpolated
   - Supports complex transformations

2. **Scene Module**:
   - Mobjects are added to scenes
   - Scene manages mobject updates
   - Handles mobject rendering

3. **Camera Module**:
   - Mobjects are rendered through camera
   - 3D mobjects use camera perspective
   - Camera affects mobject appearance

## Best Practices

1. **Mobject Creation**:
   - Use appropriate mobject types
   - Consider performance implications
   - Plan for animation needs

2. **Organization**:
   - Group related mobjects
   - Use appropriate layering
   - Manage z-index carefully

3. **Performance**:
   - Minimize complex mobjects
   - Use vectorized mobjects when possible
   - Consider rendering complexity

## Example Usage

```python
class MobjectExample(Scene):
    def construct(self):
        # Create basic shapes
        circle = Circle(radius=2, color=BLUE)
        square = Square(side_length=3, color=RED)
        
        # Create text
        text = Text("Example", font_size=24)
        
        # Create coordinate system
        axes = Axes(
            x_range=[-3, 3],
            y_range=[-3, 3]
        )
        
        # Group mobjects
        group = VGroup(circle, square, text)
        
        # Transform and animate
        self.play(
            ShowCreation(axes),
            FadeIn(group)
        )
        self.play(
            group.animate.shift(UP),
            group.animate.scale(1.5)
        )
``` 