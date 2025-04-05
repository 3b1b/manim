"""
Knowledge base for the animation system.
Contains information about available animations and objects.
"""

from typing import List, Dict, Any, Optional

class ManimKnowledgeBase:
    def __init__(self):
        self.animation_capabilities = {
            "transitions": {
                "FadeIn": {
                    "description": "Gradually makes object visible",
                    "parameters": ["mobject", "duration"],
                    "suitable_for": ["introducing_new_elements", "emphasis"]
                },
                "Transform": {
                    "description": "Morphs one object into another",
                    "parameters": ["source", "target", "duration"],
                    "suitable_for": ["showing_changes", "concept_evolution"]
                },
                "Write": {
                    "description": "Simulates writing/drawing of an object",
                    "parameters": ["mobject", "duration"],
                    "suitable_for": ["equations", "step_by_step_construction"]
                },
                "GrowFromCenter": {
                    "description": "Object grows from its center",
                    "parameters": ["mobject", "duration"],
                    "suitable_for": ["emphasis", "geometric_construction"]
                }
            },
            "objects": {
                "geometric": {
                    "Circle": {
                        "description": "A circle shape",
                        "properties": ["radius", "color", "fill_opacity"],
                        "common_uses": ["points", "sets", "cycles"]
                    },
                    "Square": {
                        "description": "A square shape",
                        "properties": ["side_length", "color", "fill_opacity"],
                        "common_uses": ["areas", "grids", "boundaries"]
                    },
                    "Arrow": {
                        "description": "An arrow shape",
                        "properties": ["start", "end", "color", "tip_length"],
                        "common_uses": ["vectors", "directions", "transformations"]
                    },
                    "Axes": {
                        "description": "Coordinate axes",
                        "properties": ["x_range", "y_range", "axis_config"],
                        "common_uses": ["coordinate_systems", "graphs", "plots"]
                    }
                },
                "text": {
                    "Text": {
                        "description": "Regular text",
                        "properties": ["content", "font_size", "color"],
                        "common_uses": ["labels", "explanations", "titles"]
                    },
                    "MathTex": {
                        "description": "LaTeX formatted mathematical text",
                        "properties": ["tex_string", "font_size", "color"],
                        "common_uses": ["equations", "formulas", "mathematical_expressions"]
                    }
                }
            }
        }

    def get_all_capabilities(self) -> Dict[str, Any]:
        """Get all available animation capabilities."""
        return self.animation_capabilities

    def get_object_info(self, obj_type: str) -> Dict[str, Any]:
        """Get information about a specific object type."""
        for category in self.animation_capabilities["objects"].values():
            if obj_type in category:
                return category[obj_type]
        return {}

    def get_transition_info(self, transition_type: str) -> Dict[str, Any]:
        """Get information about a specific transition type."""
        return self.animation_capabilities["transitions"].get(transition_type, {}) 