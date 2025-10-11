"""
AI Services
Business logic for AI operations
"""

from schemas.ai_schemas import CreateCompleteWorkoutRequest, WorkoutPlanResponse
from ai.gemini import GeminiService


class AIService:
    """Service class for AI operations"""

    def __init__(self):
        self.gemini_service = GeminiService()

    async def generate_workout_plan(
        self, request: CreateCompleteWorkoutRequest
    ) -> WorkoutPlanResponse:
        """
        Generate a personalized workout plan using AI

        Args:
            request: CreateCompleteWorkoutRequest containing user parameters

        Returns:
            WorkoutPlanResponse containing the generated workout plan
        """
        try:
            request_data = request.model_dump()
            workout_plan_data = await self.gemini_service.generate_workout_plan(
                request_data
            )
            return WorkoutPlanResponse(**workout_plan_data)

        except Exception as e:
            raise Exception(f"Failed to generate workout plan: {str(e)}")
