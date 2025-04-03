from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.analysis_service import AnalysisService
from app.models.vehicle_damage import VehicleDamageRequest, VehicleDamageResponse
from app.services.pdf_report_generator import VehicleDamageReportGenerator
from app.services.pdf_report_generator_v2 import VehicleDamageReportGeneratorV2
from pathlib import Path
import logging
import os

router = APIRouter(prefix="/vehicle", tags=["Vehicle Information"])

@router.post("/analyze/damage")
async def analyze_vehicle_damage(request: VehicleDamageRequest):
    """
    Analyze vehicle damage from provided images and generate a report
    """
    try:
        # Get analysis result
        result = await AnalysisService.analyze_vehicle_damage(request)
        
        # Create output directory if it doesn't exist
        output_dir = Path("static/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PDF report
        report_generator = VehicleDamageReportGenerator()
        pdf_path = report_generator.generate_report(result, str(output_dir))
        
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
                "url": f"/static/reports/{pdf_filename}"
            }
        })
        
    except Exception as e:
        logging.error(f"Error in vehicle damage analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/damage/v2")
async def analyze_vehicle_damage_v2(request: VehicleDamageRequest):
    """
    Analyze vehicle damage and generate a report using the alternate PDF format
    """
    try:
        # Get analysis result
        result = await AnalysisService.analyze_vehicle_damage(request)
        
        # Create output directory if it doesn't exist
        output_dir = Path("static/reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PDF report using V2 generator
        report_generator = VehicleDamageReportGeneratorV2()
        pdf_path = report_generator.generate_report(result, str(output_dir))
        
        # Get the relative path for the PDF
        pdf_filename = os.path.basename(pdf_path)
        
        # Log the generated PDF path
        logging.info(f"Generated V2 PDF report at: {pdf_path}")
        
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
                "url": f"/static/reports/{pdf_filename}"
            }
        })
        
    except Exception as e:
        logging.error(f"Error in vehicle damage analysis V2 endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 