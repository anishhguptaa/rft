"""
AI Routes
Handles all AI-related endpoints
"""

from fastapi import APIRouter, HTTPException
from schemas.ai_schemas import CreateCompleteWorkoutRequest, WorkoutPlanResponse
from ai.services import AIService

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
    try:
        workout_plan = await service.generate_workout_plan(request)
        return workout_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
