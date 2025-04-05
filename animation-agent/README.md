# Animation Agent

An AI-powered system for creating mathematical animations using the Manim library.

## Project Structure

```
animation-agent/
├── knowledge_base.py  # Contains animation capabilities and patterns
├── agents.py         # Core agent implementations
├── main.py          # Main orchestration logic
└── requirements.txt  # Project dependencies
```

## Components

1. **Knowledge Base**
   - Animation capabilities
   - Mathematical visualization patterns
   - Object properties and uses
   - Common narrative structures

2. **Agents**
   - ContentPlanningAgent: Plans the educational content
   - NarrativeDesignAgent: Designs the story flow
   - VisualPlanningAgent: Plans the visual elements

3. **Main System**
   - Orchestrates agent interactions
   - Manages the animation creation process
   - Provides the main interface

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # Create .env file with:
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the main script:
```bash
python main.py
```

Example code:
```python
from main import AnimationSystem

system = AnimationSystem()
animation_plan = system.create_animation(
    concept="derivative_introduction",
    audience_level="high_school"
)
```

## Development

- The system uses a modular design for easy extension
- Each agent can be enhanced independently
- Knowledge base can be expanded with new patterns

## Future Enhancements

1. Add more mathematical patterns
2. Implement feedback loops
3. Add quality checking
4. Integrate voice-over generation
5. Add more animation templates 