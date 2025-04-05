"""
Code generator for converting visual plans into Manim animations using LLM.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .llm_providers import create_llm_provider

@dataclass
class ManimCode:
    imports: List[str]
    scene_class: str
    construct_method: str

class ManimCodeGenerator:
    def __init__(
        self,
        llm_provider: str = "huggingface",  # Default to HuggingFace for code generation
        model_name: Optional[str] = "bigcode/starcoder",  # Default to a code-specialized model
        temperature: float = 0.3,  # Lower temperature for more precise code generation
        device: str = "auto"
    ):
        self.llm = create_llm_provider(
            provider=llm_provider,
            model_name=model_name,
            temperature=temperature,
            device=device
        )
        
        self.system_prompt = """You are an expert in creating animations using the Manim library. 
        Your task is to generate Manim code based on a visual plan. The code should be 
        well-structured and follow Manim best practices.
        
        Available Manim capabilities:
        {capabilities}
        """
        
        self.human_prompt = """Generate Manim code for the following visual plan:
        {visual_plan}
        
        The code should create a scene named {scene_name} that implements the 
        specified animations and transitions. Use the exact object types and 
        properties from the visual plan.
        
        Return the code in three parts, each prefixed with PART n: where n is 1, 2, or 3:
        
        PART 1: Import statements
        - Include all necessary imports from manim
        - Add any other required imports (numpy, etc.)
        
        PART 2: Scene class definition
        - Define the scene class that inherits from Scene
        - Add any necessary class-level attributes
        
        PART 3: Construct method implementation
        - Implement the construct method
        - Create and configure all objects
        - Add all animations in the correct sequence
        - Handle timing and transitions
        """

    def generate_code(self, visual_plan: Dict[str, Any], concept_name: str) -> ManimCode:
        """Generate Manim code using LLM."""
        # Format scene name
        scene_name = f"{concept_name.title().replace('_', '')}Scene"
        
        # Construct full prompt
        prompt = self.system_prompt.format(
            capabilities=visual_plan.get("capabilities", {})
        ) + "\n" + self.human_prompt.format(
            visual_plan=visual_plan,
            scene_name=scene_name
        )
        
        # Get LLM response
        response = self.llm.generate(prompt)
        
        # Parse response into code parts
        parts = self._parse_code_parts(response)
        
        return ManimCode(
            imports=self._clean_imports(parts.get("PART 1", "")),
            scene_class=parts.get("PART 2", ""),
            construct_method=parts.get("PART 3", "")
        )

    def _parse_code_parts(self, response: str) -> Dict[str, str]:
        """Parse the LLM response into code parts."""
        parts = {}
        current_part = None
        current_content = []
        
        for line in response.split("\n"):
            if line.startswith("PART"):
                if current_part:
                    parts[current_part] = "\n".join(current_content).strip()
                current_part = line.split(":")[0]
                current_content = []
            elif current_part:
                current_content.append(line)
        
        if current_part:
            parts[current_part] = "\n".join(current_content).strip()
        
        return parts

    def _clean_imports(self, imports_str: str) -> List[str]:
        """Clean and validate import statements."""
        imports = []
        for line in imports_str.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                imports.append(line)
        return imports

    def save_to_file(self, code: ManimCode, filename: str):
        """Save generated code to a file."""
        with open(filename, 'w') as f:
            # Write imports
            for imp in code.imports:
                f.write(f"{imp}\n")
            f.write("\n\n")
            
            # Write scene class
            f.write(f"{code.scene_class}\n")
            f.write(f"{code.construct_method}\n") 