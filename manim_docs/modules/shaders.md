# Shaders in Manim

The shader system in Manim is a sophisticated component that enables high-performance rendering of various visual elements. This document provides a comprehensive overview of the shader system, its components, and how they interact with other parts of Manim.

## Overview

The shader system is implemented using OpenGL (GLSL) and is organized into several specialized components:

1. Core Shaders
2. Special Effects
3. Utility Components
4. Common Functions

## Directory Structure

```
manimlib/shaders/
├── image/              # Image rendering shaders
├── inserts/            # Shared shader code components
├── mandelbrot_fractal/ # Mandelbrot set visualization
├── newton_fractal/     # Newton fractal visualization
├── quadratic_bezier/   # Curve rendering
├── surface/            # Surface rendering
├── textured_surface/   # Textured surface handling
├── true_dot/          # Point/dot rendering
└── simple_vert.glsl    # Basic vertex shader
```

## Core Components

### 1. Basic Rendering (simple_vert.glsl)
- Provides fundamental vertex transformation
- Used as a base for more complex shaders
- Handles basic position calculations

### 2. Image Processing (image/)
- Handles texture mapping and image rendering
- Components:
  - `vert.glsl`: Vertex shader for image coordinates
  - `frag.glsl`: Fragment shader for texture sampling

### 3. Surface Rendering (surface/)
- Manages 3D surface visualization
- Features:
  - Normal calculation
  - Color interpolation
  - Lighting effects

### 4. Curve System (quadratic_bezier/)
- Implements sophisticated curve rendering
- Subcomponents:
  - `stroke/`: Handles curve outlines
  - `fill/`: Manages curve filling
  - `depth/`: Handles depth-based rendering

## Special Effects

### 1. Fractal Renderers
- **Mandelbrot Fractal**
  - Real-time Mandelbrot set visualization
  - Customizable coloring and iterations
  - Interactive zooming capabilities

- **Newton Fractal**
  - Complex polynomial root visualization
  - Color-coded root basins
  - Parameter space exploration

### 2. Textured Surfaces
- Supports multiple texture layers
- Light/dark texture blending
- Normal-based shading

### 3. True Dots
- High-quality point rendering
- Anti-aliasing support
- Size and glow effects

## Utility Components (inserts/)

### 1. Common Functions
- `complex_functions.glsl`: Complex number operations
- `finalize_color.glsl`: Color processing and lighting
- `get_xyz_to_uv.glsl`: Coordinate transformations
- `emit_gl_Position.glsl`: Position calculation

### 2. Shared Features
- Lighting calculations
- Matrix transformations
- Anti-aliasing utilities
- Color interpolation

## Key Features

### 1. Lighting System
- Phong lighting model
- Customizable parameters:
  - Reflectiveness
  - Gloss
  - Shadow intensity

### 2. Coordinate Systems
- Multiple coordinate space handling
- Smooth transitions between spaces
- Perspective and orthographic projections

### 3. Anti-aliasing
- Edge smoothing
- Adaptive width calculation
- Resolution-independent rendering

## Integration with Other Modules

### 1. Scene Interaction
- Works with the scene module for rendering
- Handles camera transformations
- Supports animation transitions

### 2. Mobject Integration
- Provides shading for mobjects
- Handles complex geometries
- Supports custom effects

### 3. Animation Support
- Real-time shader parameter updates
- Smooth transitions
- Effect interpolation

## Usage Examples

### 1. Basic Surface
```glsl
// Example of using surface shader
void main() {
    emit_gl_Position(point);
    vec3 unit_normal = normalize(d_normal_point - point);
    v_color = finalize_color(rgba, point, unit_normal);
}
```

### 2. Complex Effects
```glsl
// Example of fractal rendering
vec2 z = xyz_coords.xy;
for(int n = 0; n < int(n_steps); n++) {
    z = complex_mult(z, z) + c;
}
```

## Performance Considerations

1. **Optimization Techniques**
   - Efficient matrix operations
   - Minimal texture lookups
   - Smart branching

2. **Memory Management**
   - Vertex attribute optimization
   - Uniform buffer usage
   - Texture memory handling

3. **Rendering Pipeline**
   - Efficient draw calls
   - Batch processing
   - State management

## Development Guidelines

1. **Shader Creation**
   - Follow GLSL 330 standards
   - Use shared components via #INSERT
   - Maintain backward compatibility

2. **Best Practices**
   - Document uniform variables
   - Use consistent naming
   - Handle edge cases

3. **Testing**
   - Verify visual output
   - Check performance impact
   - Test cross-platform compatibility

## Troubleshooting

1. **Common Issues**
   - Shader compilation errors
   - Uniform binding problems
   - Version compatibility

2. **Debug Techniques**
   - Use debug uniforms
   - Check shader logs
   - Validate inputs

## Future Enhancements

1. **Planned Features**
   - Additional effect shaders
   - Performance optimizations
   - New visualization techniques

2. **Compatibility**
   - WebGL support
   - Mobile optimization
   - Modern GPU features 