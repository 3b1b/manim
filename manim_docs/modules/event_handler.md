# Event Handler Module README

## Overview
The event handler module manages user interactions and events in Manim. It provides a system for handling keyboard and mouse events, allowing for interactive animations and user input.

## Key Components

### 1. Event Dispatcher (`event_dispatcher.py`)
- **Purpose**: Central event management system
- **Key Features**:
  - Registers and manages event listeners
  - Dispatches events to appropriate handlers
  - Handles event propagation
- **Usage**:
  ```python
  dispatcher = EventDispatcher()
  dispatcher.add_listener(event_type, handler)
  ```

### 2. Event Listener (`event_listner.py`)
- **Purpose**: Handles individual event subscriptions
- **Key Features**:
  - Manages event callbacks
  - Handles event priority
  - Controls event propagation
- **Usage**:
  ```python
  listener = EventListener(handler, priority=0)
  ```

### 3. Event Types (`event_type.py`)
- **Purpose**: Defines different types of events
- **Key Features**:
  - Keyboard events
  - Mouse events
  - Custom event types
- **Usage**:
  ```python
  class CustomEvent(EventType):
      pass
  ```

## Event Types

### 1. Keyboard Events
- Key press events
- Key release events
- Special key combinations

### 2. Mouse Events
- Mouse movement
- Mouse clicks
- Mouse drag
- Mouse wheel

### 3. Custom Events
- Scene-specific events
- Animation events
- State change events

## Interaction with Other Modules

1. **Scene Module**:
   - Scenes register event handlers
   - Events can trigger scene changes
   - Interactive scenes use event system

2. **Animation Module**:
   - Events can control animations
   - Animation state changes trigger events
   - Interactive animations use event system

3. **Mobject Module**:
   - Mobjects can respond to events
   - Events can modify mobject properties
   - Interactive mobjects use event system

## Best Practices

1. **Event Handling**:
   - Keep handlers focused and simple
   - Use appropriate event priorities
   - Handle event propagation carefully

2. **Performance**:
   - Minimize event handler complexity
   - Use event filtering when possible
   - Consider event frequency

3. **Code Organization**:
   - Group related event handlers
   - Use event types appropriately
   - Document event dependencies

## Example Usage

```python
class InteractiveExample(Scene):
    def construct(self):
        # Create interactive mobject
        circle = Circle()
        self.add(circle)
        
        # Define event handlers
        def on_key_press(event):
            if event.key == "LEFT":
                circle.shift(LEFT)
            elif event.key == "RIGHT":
                circle.shift(RIGHT)
        
        # Register event handler
        self.add_key_press_handler(on_key_press)
        
        # Interactive loop
        self.wait()
``` 