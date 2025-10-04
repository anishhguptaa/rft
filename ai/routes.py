"""
AI Routes
Handles all AI-related endpoints
"""

from fastapi import APIRouter
# from typing import List
# from schemas.ai_schemas import (
#     PredictionRequest,
#     PredictionResponse,
#     ModelInfoResponse,
# )
from ai.services import AIService

router = APIRouter()

# @router.get("/health")
# async def ai_health_check():
#     """Check AI service health"""
#     try:
#         service = AIService()
#         status = await service.health_check()
#         return {"status": "healthy", "details": status}
#     except Exception as e:
#         return {"status": "unhealthy", "error": str(e)}

