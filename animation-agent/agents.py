"""
Core agents for the animation system.
Each agent uses LLMs for intelligent decision making.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from .llm_providers import BaseLLMProvider, create_llm_provider

class ContentPlan(BaseModel):
    concept: str = Field(description="The mathematical concept being explained")
    audience_level: str = Field(description="Target audience level")
    prerequisites: List[str] = Field(description="List of prerequisite concepts")
    learning_objectives: List[str] = Field(description="List of learning objectives")

class NarrativePlan(BaseModel):
    story_flow: List[str] = Field(description="Sequence of narrative elements")
    examples: List[str] = Field(description="List of examples to use")
    timing: Dict[str, float] = Field(description="Timing for each story element")

class VisualPlan(BaseModel):
    scenes: List[Dict[str, Any]] = Field(description="List of scenes with their configurations")
    transitions: List[str] = Field(description="List of transitions between scenes")
    objects: List[Dict[str, Any]] = Field(description="List of required objects")
    timing: Dict[str, float] = Field(description="Timing for visual elements")

class BaseAgent:
    def __init__(
        self,
        knowledge_base,
        llm_provider: str = "openai",
        model_name: Optional[str] = None,
        temperature: float = 0.7,
        device: str = "auto"
    ):
        self.knowledge_base = knowledge_base
        self.llm = create_llm_provider(
            provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            device=device
        )

class ContentPlanningAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert mathematics educator. Your task is to create a 
        content plan for teaching a mathematical concept. Consider the audience level 
        and create appropriate learning objectives.
        
        Available Manim capabilities:
        {capabilities}
        """
        
        self.human_prompt = """Create a content plan for teaching {concept} to {audience_level} students.
        The plan should include:
        1. Prerequisites needed for understanding the concept
        2. Clear learning objectives
        3. Key points to cover
        
        Format your response as a JSON object with these fields:
        {
            "concept": "the concept name",
            "audience_level": "the target audience level",
            "prerequisites": ["list", "of", "prerequisites"],
            "learning_objectives": ["list", "of", "objectives"]
        }
        """

    def plan(self, concept: str, audience_level: str) -> ContentPlan:
        """Create a content plan using LLM."""
        capabilities = self.knowledge_base.get_all_capabilities()
        
        # Construct full prompt
        prompt = self.system_prompt.format(capabilities=capabilities) + "\n" + \
                self.human_prompt.format(concept=concept, audience_level=audience_level)
        
        # Get LLM response
        response = self.llm.generate(prompt)
        
        # Parse response into ContentPlan
        # Note: You might need to add error handling here
        import json
        plan_dict = json.loads(response)
        return ContentPlan(**plan_dict)

class NarrativeDesignAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert in creating educational narratives. Your task is 
        to design a narrative flow for teaching a mathematical concept. Consider the 
        content plan and available visualization capabilities.
        
        Available Manim capabilities:
        {capabilities}
        """
        
        self.human_prompt = """Design a narrative for the following content plan:
        {content_plan}
        
        Create a narrative that:
        1. Follows a logical progression
        2. Includes relevant examples
        3. Has appropriate timing for each section
        
        Format your response as a JSON object with these fields:
        {
            "story_flow": ["list", "of", "narrative", "elements"],
            "examples": ["list", "of", "examples"],
            "timing": {"element": seconds_duration}
        }
        """

    def design(self, content_plan: ContentPlan) -> NarrativePlan:
        """Create a narrative plan using LLM."""
        capabilities = self.knowledge_base.get_all_capabilities()
        
        # Construct full prompt
        prompt = self.system_prompt.format(capabilities=capabilities) + "\n" + \
                self.human_prompt.format(content_plan=content_plan.model_dump())
        
        # Get LLM response
        response = self.llm.generate(prompt)
        
        # Parse response into NarrativePlan
        import json
        plan_dict = json.loads(response)
        return NarrativePlan(**plan_dict)

class VisualPlanningAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are an expert in creating mathematical visualizations. Your task 
        is to plan the visual elements and animations for teaching a mathematical concept.
        Consider the narrative plan and available Manim capabilities.
        
        Available Manim capabilities:
        {capabilities}
        """
        
        self.human_prompt = """Create a visual plan for the following narrative:
        {narrative_plan}
        
        Plan the visuals including:
        1. Required scenes and their configurations
        2. Transitions between scenes
        3. Objects needed for each scene
        4. Timing for visual elements
        
        Format your response as a JSON object with these fields:
        {
            "scenes": [{"name": "scene_name", "config": {}}],
            "transitions": ["list", "of", "transitions"],
            "objects": [{"type": "object_type", "properties": {}}],
            "timing": {"element": seconds_duration}
        }
        """

    def plan(self, narrative_plan: NarrativePlan) -> VisualPlan:
        """Create a visual plan using LLM."""
        capabilities = self.knowledge_base.get_all_capabilities()
        
        # Construct full prompt
        prompt = self.system_prompt.format(capabilities=capabilities) + "\n" + \
                self.human_prompt.format(narrative_plan=narrative_plan.model_dump())
        
        # Get LLM response
        response = self.llm.generate(prompt)
        
        # Parse response into VisualPlan
        import json
        plan_dict = json.loads(response)
        return VisualPlan(**plan_dict) 