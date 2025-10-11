"""
AI Services
Business logic for AI operations
"""

from ..schemas.ai_schemas import CreateCompleteWorkoutRequest
from .gemini import GeminiService


class AIService:
    """Service class for AI operations"""

    def __init__(self):
        self.gemini_service = GeminiService()

    async def generate_workout_plan(
        self, request: CreateCompleteWorkoutRequest
    ) -> dict:
        """
        Generate a personalized workout plan using AI

        Args:
            request: CreateCompleteWorkoutRequest containing user parameters

        Returns:
            dict containing the generated workout plan or feasibility response
        """
        try:
            request_data = request.model_dump()
            workout_generation_response = await self.gemini_service.generate_workout_plan(
                request_data
            )
            return workout_generation_response

        except Exception as e:
            raise Exception(f"Failed to generate workout plan: {str(e)}")
