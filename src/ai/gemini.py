"""
Gemini AI Service
Handles workout plan generation using Google's Gemini AI
"""

from .prompts import get_workout_prompt
from ..core.config import settings
from ..core.logger import get_logger
from typing import Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel
from ..schemas.ai_schemas import WorkoutPlanResponse, CreateCompleteWorkoutRequest

logger = get_logger(__name__)


class GeminiService:
    """Service class for Gemini AI operations"""

    def __init__(self):
        """Initialize Gemini service with API key"""
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable is not set")
            raise ValueError("GEMINI_API_KEY environment variable is required")

        self.client = genai.Client(api_key=api_key)

    def ask_gemini(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        thinking_budget: bool = True,  # Enable reasoning by default
        output_schema: BaseModel = None,
        temperature: float = 0.5,  # Balance creativity with consistency
    ) -> Dict[str, Any]:
        """
        Ask Gemini a question with structured output and thinking
        
        Args:
            prompt: The input prompt
            model: Gemini model to use
            thinking_budget: Enable internal reasoning (recommended for complex tasks)
            output_schema: Pydantic model for structured output
            temperature: Controls randomness (0.0-1.0, lower = more consistent)
        """
        try:
            if output_schema and thinking_budget:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=output_schema,
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),  # Enable reasoning
                    temperature=temperature,
                )
            elif output_schema and not thinking_budget:
                config = types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=output_schema,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    temperature=temperature,
                )
            elif not output_schema and thinking_budget:
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=-1),
                    temperature=temperature,
                )
            else:
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                    temperature=temperature,
                )

            response = self.client.models.generate_content(
                model=model, contents=prompt, config=config
            )

            if output_schema:
                result = response.parsed.model_dump()
            else:
                result = response.text

            return result

        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
            raise

    async def generate_workout_plan(
        self,
        request_data: CreateCompleteWorkoutRequest,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Generate a personalized workout plan based on user parameters

        Args:
            request_data: Dictionary containing user parameters from CreateCompleteWorkoutRequest
            model: Gemini model to use for generation
            temperature: Controls randomness (0.0-1.0, lower = more consistent)

        Returns:
            Dictionary containing the generated workout plan
        """
        try:
            prompt = get_workout_prompt(request_data)
            workout_plan = self.ask_gemini(
                prompt=prompt,
                model=model,
                output_schema=WorkoutPlanResponse,
                thinking_budget=True,  # Enable reasoning for complex planning
                temperature=temperature,
            )
            return workout_plan

        except Exception as e:
            logger.error(f"Failed to generate workout plan: {str(e)}", exc_info=True)
            raise
