# Camera Module README

## Overview
The camera module handles all aspects of viewing and rendering in Manim. It manages the virtual camera that captures the scene, handles perspective, and controls the final output.

## Key Components

### 1. Camera Class (`camera.py`)
- **Purpose**: Main camera class that handles rendering and viewport management
- **Key Features**:
  - Manages OpenGL context and rendering
  - Handles frame buffering and composition
  - Controls resolution and quality settings
- **Properties**:
  - `frame_width`, `frame_height`: Viewport dimensions
  - `frame_rate`: Frames per second
  - `background_color`: Scene background color
  - `samples`: Anti-aliasing samples
- **Usage**:
  ```python
  camera = Camera(
      frame_width=16,
      frame_height=9,
      frame_rate=30,
      samples=4
  )
  ```

### 2. CameraFrame Class (`camera_frame.py`)
- **Purpose**: Manages the camera's frame and orientation
- **Key Features**:
  - Controls camera position and orientation
  - Handles 3D transformations
  - Manages field of view and perspective
- **Methods**:
  - `reorient`: Changes camera orientation
  - `set_euler_angles`: Sets Euler angles
  - `make_orientation_default`: Resets orientation
- **Usage**:
  ```python
  camera_frame = CameraFrame()
  camera_frame.reorient(30, 70, 0)  # Set orientation
  ```

## Camera Features

### 1. Viewport Management
- Controls what portion of the scene is visible
- Handles aspect ratio and scaling
- Manages zoom levels and focus

### 2. 3D Support
- Handles perspective projection
- Manages depth testing
- Supports 3D transformations

### 3. Rendering Options
- Anti-aliasing
- Background color
- Frame rate control
- Resolution settings

## Interaction with Other Modules

1. **Scene Module**:
   - Scenes create and manage camera instances
   - Camera renders the scene's mobjects
   - Scene controls camera movement and transitions

2. **Mobject Module**:
   - Mobjects are rendered through the camera
   - Camera transforms affect mobject appearance
   - 3D mobjects interact with camera perspective

3. **Animation Module**:
   - Camera movements are handled as animations
   - Animations can affect camera properties
   - Camera transitions are animated

## Best Practices

1. **Camera Setup**:
   - Set appropriate frame dimensions
   - Configure quality settings based on needs
   - Consider performance impact of high samples

2. **3D Scenes**:
   - Use appropriate camera angles
   - Consider depth and perspective
   - Plan camera movements carefully

3. **Performance**:
   - Balance quality and performance
   - Use appropriate frame rates
   - Consider rendering time for high-quality output

## Example Usage

```python
class CameraExample(ThreeDScene):
    def construct(self):
        # Set up camera
        self.camera.frame.set_euler_angles(
            theta=-30 * DEGREES,
            phi=70 * DEGREES
        )
        
        # Create 3D objects
        cube = Cube()
        sphere = Sphere()
        
        # Animate camera movement
        self.play(
            self.camera.frame.animate.set_euler_angles(
                theta=60 * DEGREES,
                phi=30 * DEGREES
            ),
            run_time=2
        )
        
        # Add objects with proper depth
        self.play(
            ShowCreation(cube),
            ShowCreation(sphere)
        )
``` 