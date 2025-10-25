"""
AI Services
Business logic for AI operations
"""

from ai.gemini import GeminiService
from schemas.ai_schemas import CreateFirstWorkoutRequest


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

    async def continue_workout_plan(self, request: CreateFirstWorkoutRequest) -> dict:
        """
        Continue a personalized workout plan using AI (for non-first workouts)
        """
        pass

    # async def adjust_workout_plan(
    #     self, request: AdjustWorkoutPlanRequest
    # ) -> dict:
    #     """
    #     Adjust a workout plan using AI

    #     Args:
    #         request: AdjustWorkoutPlanRequest containing adjustment parameters

    #     Returns:
    #         dict containing the adjusted workout plan
    #     """
    #     try:
    #         request_data = request.model_dump()
    #         adjusted_workout_plan = await self.gemini_service.adjust_workout_plan(
    #             request_data
    #         )
    #         return adjusted_workout_plan

    #     except Exception as e:
    #         raise Exception(f"Failed to adjust workout plan: {str(e)}")
