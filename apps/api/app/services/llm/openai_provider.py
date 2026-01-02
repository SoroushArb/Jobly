"""OpenAI LLM provider implementation with structured output"""
import os
import json
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from openai import AsyncOpenAI
from .base import LLMProvider

T = TypeVar('T', bound=BaseModel)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider using GPT-4 with JSON mode for structured outputs"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI LLM provider
        
        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
            model: Model name to use (default: gpt-4o-mini for cost efficiency)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY env var")
        
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: str = None,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> T:
        """
        Generate structured output using OpenAI with JSON mode
        
        Uses response_format="json_object" and includes schema in the prompt
        to enforce structured output. Implements retry logic for validation failures.
        """
        if not system_prompt:
            system_prompt = "You are a helpful assistant that generates structured data."
        
        # Get JSON schema from Pydantic model
        schema = response_model.model_json_schema()
        
        # Enhance prompt with schema information
        enhanced_prompt = f"""{prompt}

You must respond with valid JSON that matches this exact schema:

{json.dumps(schema, indent=2)}

Ensure all required fields are present and types match exactly. Return only the JSON object, no additional text."""
        
        last_error = None
        for attempt in range(max_retries):
            try:
                # Call OpenAI with JSON mode
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": enhanced_prompt}
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                # Extract JSON from response
                content = response.choices[0].message.content
                json_data = json.loads(content)
                
                # Validate against Pydantic model
                validated_response = response_model.model_validate(json_data)
                return validated_response
                
            except (json.JSONDecodeError, ValidationError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    # Retry with adjusted temperature (lower = more deterministic)
                    temperature = max(0.3, temperature * 0.8)
                    continue
                else:
                    raise ValueError(
                        f"Failed to generate valid structured output after {max_retries} attempts. "
                        f"Last error: {str(e)}"
                    )
            except Exception as e:
                raise ValueError(f"LLM generation failed: {str(e)}")
        
        # Should not reach here, but just in case
        raise ValueError(f"Failed to generate structured output: {last_error}")
    
    def get_model_name(self) -> str:
        """Get the model name"""
        return self.model
