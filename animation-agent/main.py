"""
Main entry point for the animation system.
Orchestrates the interaction between different agents.
"""

from typing import Dict, Any, Optional
from knowledge_base import ManimKnowledgeBase
from agents import ContentPlanningAgent, NarrativeDesignAgent, VisualPlanningAgent
from code_generator import ManimCodeGenerator

class AnimationSystem:
    def __init__(self):
        self.knowledge_base = ManimKnowledgeBase()
        self.content_agent = ContentPlanningAgent(self.knowledge_base)
        self.narrative_agent = NarrativeDesignAgent(self.knowledge_base)
        self.visual_agent = VisualPlanningAgent(self.knowledge_base)
        self.code_generator = ManimCodeGenerator()

    def create_animation(
        self, 
        concept: str, 
        audience_level: str,
        output_file: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create an animation for a given concept.
        
        Args:
            concept: The mathematical concept to explain
            audience_level: Target audience level (e.g., "high_school", "college")
            output_file: Optional path to save the generated Manim code
            
        Returns:
            Dictionary containing the complete animation plan and generated code
        """
        # Content Planning Phase
        print("Planning content...")
        content_plan = self.content_agent.plan(concept, audience_level)
        
        # Narrative Design Phase
        print("Designing narrative...")
        narrative_plan = self.narrative_agent.design(content_plan)
        
        # Visual Planning Phase
        print("Planning visuals...")
        visual_plan = self.visual_agent.plan(narrative_plan)
        
        # Code Generation Phase
        print("Generating Manim code...")
        manim_code = self.code_generator.generate_code(visual_plan, concept)
        
        # Save code if output file specified
        if output_file:
            self.code_generator.save_to_file(manim_code, output_file)
            print(f"Manim code saved to {output_file}")
        
        # Combine all plans into final output
        return {
            "content": content_plan,
            "narrative": narrative_plan,
            "visual": visual_plan,
            "code": manim_code
        }

def main():
    # Example usage
    system = AnimationSystem()
    
    # Create an animation for explaining derivatives to high school students
    animation_plan = system.create_animation(
        concept="derivative_introduction",
        audience_level="high_school",
        output_file="derivative_animation.py"
    )
    
    # Print the generated plan
    print("\nAnimation Plan Generated:")
    print(f"Content Plan: {animation_plan['content']}")
    print(f"Narrative Plan: {animation_plan['narrative']}")
    print(f"Visual Plan: {animation_plan['visual']}")
    
    # Print example of how to run the animation
    print("\nTo render the animation, run:")
    print("manim derivative_animation.py DerivativeIntroductionScene -pql")

if __name__ == "__main__":
    main() 