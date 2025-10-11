"""
Gemini AI Service
Handles workout plan generation using Google's Gemini AI
"""

from ai.prompts import get_workout_prompt
from core.config import settings
from typing import Dict, Any
from google import genai
from google.genai import types
from pydantic import BaseModel

from schemas.ai_schemas import WorkoutPlanResponse, CreateCompleteWorkoutRequest


class GeminiService:
    """Service class for Gemini AI operations"""

    def __init__(self):
        """Initialize Gemini service with API key"""
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        self.client = genai.Client(api_key=api_key)

    def ask_gemini(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash",
        thinking_budget: bool = False,
        output_schema: BaseModel = None,
    ) -> Dict[str, Any]:
        """
        Ask Gemini a question with structured output and thinking
        """
        if output_schema and thinking_budget:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=output_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=-1),
            )
        elif output_schema and not thinking_budget:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=output_schema,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )
        elif not output_schema and thinking_budget:
            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=-1)
            )
        else:
            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )

        response = self.client.models.generate_content(
            model=model, contents=prompt, config=config
        )
        if output_schema:
            return response.parsed.model_dump()
        else:
            return response.text

    async def generate_workout_plan(
        self,
        request_data: CreateCompleteWorkoutRequest,
        model: str = "gemini-2.5-flash",
    ) -> Dict[str, Any]:
        """
        Generate a personalized workout plan based on user parameters

        Args:
            request_data: Dictionary containing user parameters from CreateCompleteWorkoutRequest

        Returns:
            Dictionary containing the generated workout plan
        """
        try:
            prompt = get_workout_prompt(request_data.model_dump())
            workout_plan = self.ask_gemini(
                prompt=prompt,
                model=model,
                thinking_budget=True,
                output_schema=WorkoutPlanResponse,
            )

            return workout_plan

        except Exception as e:
            return {
                "error": f"Failed to process response: {str(e)}",
                "raw_response": workout_plan,
                "generated_at": "2024-01-01T00:00:00Z",
                "ai_model": "gemini-2.5-flash",
            }
