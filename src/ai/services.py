"""
AI Services
Business logic for AI operations
"""

from ai.gemini import GeminiService
from schemas.ai_schemas import (
    CreateFirstWorkoutRequest,
    CreateMealPlanRequest,
    ContinueWorkoutRequest,
)


class AIService:
    """Service class for AI operations"""

    def __init__(self):
        self.gemini_service = GeminiService()

    async def generate_first_workout_plan(
        self, request: CreateFirstWorkoutRequest
    ) -> dict:
        """
        Generate a personalized workout plan using AI

        Args:
            request: CreateFirstWorkoutRequest containing user parameters

        Returns:
            dict containing the generated workout plan or feasibility response
        """
        try:
            request_data = request.model_dump()
            workout_generation_response = (
                await self.gemini_service.generate_first_workout_plan(request_data)
            )
            return workout_generation_response
        except Exception as e:
            raise Exception(f"Failed to generate first workout plan: {str(e)}")

    async def continue_workout_plan(self, request: ContinueWorkoutRequest) -> dict:
        """
        Continue a personalized workout plan using AI (for non-first workouts)
        """
        pass

    async def generate_meal_plan(self, request: CreateMealPlanRequest) -> dict:
        """
        Generate a personalized meal plan using AI

        Args:
            request: CreateMealPlanRequest containing meal plan parameters

        Returns:
            dict containing the generated meal plan
        """
        pass
