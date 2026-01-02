"""Base interface for LLM providers with structured output"""
from abc import ABC, abstractmethod
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class LLMProvider(ABC):
    """Abstract base class for LLM providers that generate structured outputs"""
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> T:
        """
        Generate structured output using LLM
        
        Args:
            prompt: The user prompt/instruction
            response_model: Pydantic model class for the expected response structure
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0.0-2.0)
            max_retries: Maximum number of retry attempts on validation failure
            
        Returns:
            Instance of response_model with validated data
            
        Raises:
            ValueError: If generation fails after retries
            ValidationError: If response doesn't match schema after retries
        """
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """
        Get the name/identifier of the LLM model
        
        Returns:
            Model name string
        """
        pass
