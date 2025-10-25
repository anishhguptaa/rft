"""
AI Services
Business logic for AI operations
"""

from api.modules.ai_backend_integration.services import (
    save_ai_workout_plan,
    save_ai_meal_plan,
)
from ai.gemini import GeminiService
from core.logger import get_logger
from schemas.ai_schemas import (
    CreateFirstWorkoutRequest,
    CreateMealPlanRequest,
    ContinueWorkoutRequest,
)
import json

logger = get_logger(__name__)


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
        logger.info(f"Generating first workout plan for user {request.user_id}")
        try:
            request_data = request.model_dump()
            logger.debug(f"Request data: {request_data}")
            
            workout_generation_response = await self.gemini_service.generate_first_workout_plan(request_data)
            logger.debug(f"AI response received for user {request.user_id}")
            
            save_ai_workout_plan(request.user_id, workout_generation_response)
            logger.info(f"First workout plan saved successfully for user {request.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate first workout plan for user {request.user_id}: {str(e)}")
            raise Exception(f"Failed to generate first workout plan: {str(e)}")

    async def continue_workout_plan(self, request: ContinueWorkoutRequest) -> dict:
        """
        Continue a personalized workout plan using AI (for non-first workouts)
        """
        logger.info(f"Continuing workout plan for user {request.user_id}")
        try:
            request_data = request.model_dump()
            logger.debug(f"Request data: {request_data}")
            
            workout_generation_response = await self.gemini_service.continue_workout_plan(request_data)
            logger.debug(f"AI response received for user {request.user_id}")
            
            save_ai_workout_plan(request.user_id, workout_generation_response)
            logger.info(f"Workout plan continuation saved successfully for user {request.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to continue workout plan for user {request.user_id}: {str(e)}")
            raise Exception(f"Failed to continue workout plan: {str(e)}")

    async def generate_meal_plan(self, request: CreateMealPlanRequest) -> dict:
        """
        Generate a personalized meal plan using AI

        Args:
            request: CreateMealPlanRequest containing meal plan parameters

        Returns:
            dict containing the generated meal plan
        """
        logger.info(f"Generating meal plan for user {request.user_id}")
        try:
            request_data = request.model_dump()
            logger.debug(f"Request data: {request_data}")
            
            meal_plan_response = await self.gemini_service.create_meal_plan(request_data)
            logger.debug(f"AI meal plan response received for user {request.user_id}")
            
            # Convert the meal plan response dictionary to JSON string
            meal_plan_json = json.dumps(meal_plan_response)
            
            # Save the meal plan to the database
            save_ai_meal_plan(request.user_id, meal_plan_json)
            logger.info(f"Meal plan saved successfully for user {request.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to generate meal plan for user {request.user_id}: {str(e)}")
            raise Exception(f"Failed to generate meal plan: {str(e)}")
