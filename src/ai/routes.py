"""
AI Routes
Handles all AI-related endpoints
"""

from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import CreateCompleteWorkoutRequest, WorkoutPlanResponse, AdjustWorkoutPlanRequest
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
        f"Received workout plan generation request for user: user_token={request.user_token}, age={request.age}, "
        f"gender={request.gender}, goal={request.workout_goal}, "
        f"experience={request.experience_level}, first_workout={request.first_workout}"
    )
    is_first_workout = request.first_workout == True
    try:
        if is_first_workout:
            workout_plan = await service.generate_first_workout_plan(request)
        else:
            workout_plan = await service.generate_workout_plan(request)
        return workout_plan
    except Exception as e:
        logger.error(f"Failed to generate workout plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/adjust-workout-plan", response_model=WorkoutPlanResponse)
async def adjust_workout_plan(request: AdjustWorkoutPlanRequest):
    """
    Adjust a workout plan based on user parameters
    """
    logger.info(f"Received workout plan adjustment request for user: {request.user_token}")
    try:
        workout_plan = await service.adjust_workout_plan(request)
        return workout_plan
    except Exception as e:
        logger.error(f"Failed to adjust workout plan: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

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


