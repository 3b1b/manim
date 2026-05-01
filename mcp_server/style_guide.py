"""
3Blue1Brown-inspired style guide and visual pedagogy principles.

Distilled from studying 74,000+ lines of production 3b1b video code
spanning 2015–2026.
"""
from __future__ import annotations

STYLE_GUIDE = r"""
# ManimGL Visual Style Guide

## Core Animation Patterns

### Progressive Revelation
Build complexity one layer at a time. Never dump everything on screen at once.

```python
# GOOD: Build up step by step
self.play(ShowCreation(axes))
self.wait(0.5)
self.play(ShowCreation(graph))
self.wait(0.5)
self.play(Write(label))

# BAD: Everything at once
self.add(axes, graph, label)
```

### Animation Timing
- `ShowCreation`: 1–2s for simple shapes, 2–3s for complex curves
- `Write`: 1–1.5s for short equations, 2–3s for long ones
- `FadeIn`/`FadeOut`: 0.5–1s
- `Transform`: 1.5–2s (the viewer needs time to track the change)
- `self.wait()`: 0.5–1s between related steps, 1–2s between concepts
- Camera rotations: 4–8s (slow enough to follow)

### Color as Meaning
Assign colors to mathematical objects consistently throughout a video:

```python
# Variables get specific colors
t2c = {"x": BLUE, "y": RED, "z": GREEN}
equation = Tex(R"f(x, y) = x^2 + y^2", t2c=t2c)

# Common conventions:
# - Input variables: BLUE family
# - Output/result: YELLOW family
# - Auxiliary/parameter: RED family
# - Positive: GREEN, Negative: RED
# - Real part: BLUE, Imaginary part: YELLOW
```

### Text and Equations
- Use `Text()` for plain labels (no LaTeX needed)
- Use `Tex()` for LaTeX math (requires LaTeX installed)
- Use raw strings for LaTeX: `Tex(R"\frac{d}{dx}")`
- Use `t2c` for coloring parts of equations
- Use `font_size` parameter (default 48, use 36 for labels, 60–72 for emphasis)
- Position equations with `to_edge(UP)` or `to_corner(UL)` to keep them visible
- Use `fix_in_frame()` for equations that should not move with 3D camera
- Use `set_backstroke(BLACK, width)` to make text readable over busy backgrounds

### Camera Work (3D Scenes)
```python
# Set initial orientation with euler angles (theta, phi)
self.frame.reorient(20, 70)  # theta=20°, phi=70°

# Animate camera rotation
self.play(self.frame.animate.reorient(160, 65), run_time=6)

# For 2D scenes that need a slight 3D feel:
self.frame.reorient(0, 0)  # Reset to flat
```

### Grouping and Layout
```python
# Use VGroup for related objects
formula_parts = VGroup(lhs, equals, rhs)
formula_parts.arrange(RIGHT, buff=0.2)

# Use arrange for grids
items = VGroup(*[Square() for _ in range(12)])
items.arrange_in_grid(3, 4, buff=0.5)

# Position relative to other objects
label.next_to(graph, UP, buff=0.3)
```

### Updaters for Dynamic Relationships
```python
# Keep a label attached to a moving point
dot = Dot(color=RED)
label = Text("P")
label.add_updater(lambda m: m.next_to(dot, UR, buff=0.1))

# Track a value
tracker = ValueTracker(0)
dot.add_updater(
    lambda m: m.move_to(axes.c2p(tracker.get_value(), func(tracker.get_value())))
)
self.play(tracker.animate.set_value(3), run_time=2)
```

### Staggered Animations
```python
# Fade in a group of objects one by one
self.play(LaggedStartMap(FadeIn, objects, lag_ratio=0.15))

# Stagger with custom animations
self.play(LaggedStart(
    ShowCreation(line1),
    ShowCreation(line2),
    ShowCreation(line3),
    lag_ratio=0.3,
))
```

## Scene Structure Template

```python
class ConceptScene(Scene):
    def construct(self):
        # 1. Setup: Create coordinate system or base objects
        # 2. Introduce: Show the first concrete example
        # 3. Animate: Demonstrate the key transformation/concept
        # 4. Label: Add equations or text explaining what happened
        # 5. Generalize: Show how this extends (optional)
        # 6. Conclude: Clean transition or final state
        pass
```

## Common Pitfalls
- Don't use `Tex()` if LaTeX is not installed — use `Text()` instead
- Always call `self.play()` or `self.add()` — creating objects alone won't show them
- For 3D scenes, inherit from `ThreeDScene` not `Scene`
- Use `np.array([x, y, 0])` for 2D points (manim uses 3D internally)
- `self.wait()` defaults to 1 second; use `self.wait(0.5)` for quick pauses
"""

PEDAGOGY_GUIDE = r"""
# Visual Mathematics Pedagogy

## The 3Blue1Brown Approach

The goal is to make the viewer *feel* the math, not just see symbols.
Every animation should answer: "What does this look like?"

## Five Principles

### 1. Concrete Before Abstract
Start with a specific, tangible example. Then generalize.

- To teach derivatives: First show a car's position graph, draw a tangent line,
  show the slope changing. THEN introduce f'(x) notation.
- To teach eigenvalues: First show a specific matrix stretching a specific vector.
  THEN define the general concept.

### 2. Geometry Before Algebra
Show the shape, the motion, the spatial relationship first.
Equations come after the viewer already has visual intuition.

- Area of a circle: Show concentric rings unwrapping into a triangle.
  The formula pi*r^2 emerges from the picture.
- Determinant: Show how a matrix scales area. The number is the scaling factor.

### 3. Animation Shows Process
Static images show states. Animation shows *how you get there*.

- Don't just show a Fourier series approximation — animate each term being added,
  watching the approximation improve.
- Don't just show a transformed grid — animate the grid deforming smoothly.

### 4. One Concept Per Scene
Each scene should have exactly one "aha moment." If you're explaining two things,
split into two scenes.

### 5. Let the Eye Follow
Guide attention through motion. The viewer's eye naturally follows:
- Moving objects
- Color changes
- Growing/shrinking
- Objects appearing/disappearing

Use this to direct attention to the important part of the frame.

## Video Structure Patterns

### The "What Does It Look Like?" Pattern
1. State the concept verbally (text on screen)
2. Show the simplest possible visual example
3. Animate the key transformation
4. Show how changing parameters changes the visual
5. Connect back to the formal definition

### The "Build Up" Pattern
1. Start with a simple case (n=1 or 2D)
2. Show it works
3. Add complexity (n=2, or 3D)
4. Show the pattern holds
5. Generalize

### The "Dual View" Pattern
Show two representations side by side:
- Time domain ↔ Frequency domain
- Position space ↔ Phase space
- Algebraic ↔ Geometric
Animate changes in one and show the effect in the other.

## Color Conventions for Math Domains

### Calculus
- Function: BLUE
- Derivative: YELLOW or GREEN
- Integral/area: BLUE with opacity 0.3
- dx, dt: RED (small quantities)

### Linear Algebra
- Basis vector i-hat: GREEN
- Basis vector j-hat: RED
- Transformed vectors: YELLOW
- Eigenvalues/vectors: PURPLE

### Complex Analysis
- Real part: BLUE
- Imaginary part: YELLOW
- Modulus: WHITE
- Argument/angle: RED

### Differential Geometry
- Surface: BLUE with gradient
- Tangent vectors: YELLOW
- Normal vectors: GREEN
- Curvature: RED
"""
