from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from app.services.api_status.status_checker import APIStatusChecker
import logging

router = APIRouter()

@router.get("/api/status")
async def get_api_status():
    """
    Get the operational status of all AI APIs
    Returns:
        JSON with status of OpenAI, Claude, Gemini, and Llama APIs
    """
    try:
        checker = APIStatusChecker()
        statuses = checker.get_all_statuses()
        return JSONResponse(content=statuses)
    except Exception as e:
        logging.error(f"Error in API status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 