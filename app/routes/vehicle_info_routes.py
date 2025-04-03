from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.analysis_service import AnalysisService
from app.models.vehicle_damage import VehicleDamageRequest
from app.services.pdf_report_generator import VehicleDamageReportGenerator
from pathlib import Path
import logging
import os

router = APIRouter(prefix="/vehicle", tags=["Vehicle Information"])

@router.post("/analyze/damage")
async def analyze_vehicle_damage(request: VehicleDamageRequest):
    """
    Analyze vehicle damage from image URLs and generate PDF report
    
    Example request body:
    {
        "order_id": "ORDER123",
        "image_urls": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg"
        ]
    }
    """
    try:
        # Get analysis result
        result = await AnalysisService.analyze_vehicle_damage(request)
        
        # Generate PDF report
        report_generator = VehicleDamageReportGenerator()
        pdf_path = report_generator.generate_report(result, str(Path("static/reports")))
        
        # Get the relative path for the PDF
        pdf_filename = os.path.basename(pdf_path)
        
        # Log the generated PDF path
        logging.info(f"Generated PDF report at: {pdf_path}")
        
        # Verify the PDF exists
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Failed to generate PDF report")
        
        return JSONResponse(content={
            "success": True,
            "message": "Analysis completed successfully",
            "order_id": request.order_id,
            "analysis": result,
            "pdf_report": {
                "filename": pdf_filename,
                "path": pdf_path,
                "url": f"/static/reports/{pdf_filename}"
            }
        })
        
    except Exception as e:
        logging.error(f"Error in vehicle damage analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 