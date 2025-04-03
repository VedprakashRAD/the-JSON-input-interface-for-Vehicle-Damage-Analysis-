from fastapi import APIRouter, HTTPException, Response
from app.models.audio_models import AudioDownloadRequest, AudioDownloadResponse
from app.services.audio_service.audio_processor import AudioProcessor
import logging
import json

router = APIRouter()
logging.basicConfig(level=logging.INFO)

@router.post("/audio/process")
async def process_audio(request: AudioDownloadRequest, response: Response):
    """
    Process audio file download and API call
    
    This endpoint:
    1. Downloads an audio file from the provided URL using basic authentication
    2. Saves the file locally
    3. Returns file details and success response
    """
    try:
        logging.info(f"Processing audio request for SRN: {request.srn_number}, Order ID: {request.order_id}")
        
        processor = AudioProcessor()
        result = await processor.process_audio(
            url=request.url,
            username=request.username,
            password=request.password,
            srn_number=request.srn_number,
            order_id=request.order_id
        )
        
        logging.info("Audio processing completed successfully")
        
        # Ensure the response is properly formatted
        response_data = {
            "filename": result.get("filename", ""),
            "size_bytes": result.get("size_bytes", 0),
            "duration_seconds": result.get("duration_seconds", 0.0),
            "api_response": result.get("api_response", {})
        }
        
        return response_data
        
    except HTTPException as he:
        logging.error(f"HTTP error in audio processing: {str(he)}")
        response.status_code = he.status_code
        return {"detail": he.detail}
    except Exception as e:
        logging.error(f"Unexpected error in audio processing: {str(e)}", exc_info=True)
        response.status_code = 500
        return {"detail": str(e)} 