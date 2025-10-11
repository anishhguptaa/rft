"""
AI Routes
Handles all AI-related endpoints
"""

from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import CreateCompleteWorkoutRequest, WorkoutPlanResponse
from ai.services import AIService
from core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
service = AIService()


@router.post("/generate-workout-plan", response_model=WorkoutPlanResponse)
async def generate_workout_plan(request: CreateCompleteWorkoutRequest):
    """
    Generate a personalized workout plan based on user parameters

    This endpoint takes user fitness information and generates a comprehensive
    workout plan using AI, including weekly schedule, exercises, nutrition guidelines,
    and safety considerations.
    """
    logger.info(
        f"Received workout plan generation request for user: age={request.age}, "
        f"gender={request.gender}, goal={request.workout_goal}, "
        f"experience={request.experience_level}"
    )
    try:
        workout_plan = await service.generate_workout_plan(request)
        return workout_plan
    except Exception as e:
        logger.error(f"Failed to generate workout plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/edit-weekly-workout-plan", response_model=WorkoutPlanResponse)
# async def edit_weekly_workout_plan(request: EditWeeklyWorkoutPlanRequest):
#     """
#     Edit a weekly workout plan based on user parameters
#     """
#     logger.info(f"Received weekly workout plan edit request for user: {request.user_id}")
#     try:
#         workout_plan = await service.edit_weekly_workout_plan(request)
#         return workout_plan
#     except Exception as e:
#         logger.error(f"Failed to edit weekly workout plan: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/edit-daily-workout-plan", response_model=WorkoutPlanResponse)
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