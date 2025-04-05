"""
LLM providers for the animation system.
Supports both OpenAI and open-source models.
"""

from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from langchain.llms import HuggingFacePipeline
from langchain.chat_models import ChatOpenAI
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from prompt."""
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )

    def generate(self, prompt: str) -> str:
        """Generate text using OpenAI's API."""
        response = self.llm.invoke(prompt)
        return response.content

class HuggingFaceProvider(BaseLLMProvider):
    def __init__(
        self,
        model_name: str = "tiiuae/falcon-7b-instruct",
        temperature: float = 0.7,
        device: str = "auto",
        max_length: int = 2048
    ):
        # Determine device
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load model and tokenizer
        print(f"Loading model {model_name} on {device}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16 if device == "cuda" else torch.float32,
            device_map=device,
            trust_remote_code=True
        )
        
        # Create pipeline
        pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_length=max_length,
            temperature=temperature,
            device=device
        )
        
        # Create LangChain wrapper
        self.llm = HuggingFacePipeline(pipeline=pipe)

    def generate(self, prompt: str) -> str:
        """Generate text using Hugging Face model."""
        response = self.llm.invoke(prompt)
        return response

def create_llm_provider(
    provider: str = "openai",
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    device: str = "auto"
) -> BaseLLMProvider:
    """Factory function to create LLM provider."""
    if provider == "openai":
        return OpenAIProvider(
            model_name=model_name or "gpt-3.5-turbo",
            temperature=temperature
        )
    elif provider == "huggingface":
        return HuggingFaceProvider(
            model_name=model_name or "tiiuae/falcon-7b-instruct",
            temperature=temperature,
            device=device
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")

# Example open-source models that work well for this use case
RECOMMENDED_MODELS = {
    "instruction_following": [
        "tiiuae/falcon-7b-instruct",  # Good balance of size and quality
        "google/flan-t5-large",       # Smaller, faster, good for structured output
        "databricks/dolly-v2-3b",     # Good for instruction following
        "stabilityai/stablelm-tuned-alpha-7b"  # Good for code generation
    ],
    "code_generation": [
        "bigcode/starcoder",          # Specialized for code generation
        "codellama/codellama-7b-instruct",  # Good for Python code
        "stabilityai/stablelm-code-7b"  # Another good code option
    ]
} 