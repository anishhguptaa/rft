"""
AI Routes
Handles all AI-related endpoints
"""

from http import HTTPStatus
from fastapi import APIRouter, HTTPException, Response
from schemas.ai_schemas import CreateFirstWorkoutRequest, WorkoutPlanResponse
from ai.services import AIService
from core.logger import get_logger

from api.modules.ai_backend_integration.services import save_ai_workout_plan
logger = get_logger(__name__)

router = APIRouter()
service = AIService()


@router.post("/generate-workout-plan", response_model=WorkoutPlanResponse)
async def generate_first_workout_plan(request: CreateFirstWorkoutRequest):
    """
    Generate a personalized workout plan based on user parameters

    This endpoint takes user fitness information and generates a comprehensive
    workout plan using AI, including weekly schedule, exercises, nutrition guidelines,
    and safety considerations.
    """
    try:
        logger.info(
            f"Received workout plan generation request for user: user_token={request.user_token}, age={request.age}, "
            f"gender={request.gender}, goal={request.workout_goal}, "
            f"experience={request.experience_level}"
        )
        workout_plan = await service.generate_first_workout_plan(request)
        save_ai_workout_plan(user_token=request.user_token, workout_plan=workout_plan)
        return Response(status_code=HTTPStatus.CREATED, content="Workout plan generated successfully")

    except Exception as e:
        logger.error(f"Failed to generate workout plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))


# @router.post("/adjust-workout-plan", response_model=WorkoutPlanResponse)
# async def adjust_workout_plan(request: AdjustWorkoutPlanRequest):
#     """
#     Adjust a workout plan based on user parameters
#     """
#     logger.info(f"Received workout plan adjustment request for user: {request.user_token}")
#     try:
#         workout_plan = await service.adjust_workout_plan(request)
#         return workout_plan
#     except Exception as e:
#         logger.error(f"Failed to adjust workout plan: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/edit-daily-workout-plan", response_model=FirstWorkoutPlanResponse)
# async def edit_daily_workout_plan(request: EditDailyWorkoutPlanRequest):
#     """
#     Edit a daily workout plan based on user parameters
#     """
#     logger.info(f"Received daily workout plan edit request for user: {request.user_id}")
#     try:
#         workout_plan = await service.edit_daily_workout_plan(request)
#         return workout_plan
#     except Exception as e:
#         logger.error(f"Failed to edit daily workout plan: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/create-meal-plan", response_model=CreateMealPlanResponse)
# async def create_meal_plan(request: CreateFirstWorkoutRequest):
#     """
#     Create a personalized meal plan based on user parameters
#     """
#     pass