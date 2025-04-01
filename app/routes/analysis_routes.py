from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from app.services.analysis_service import AnalysisService
from app.config.settings import UPLOAD_DIR
from app.models.vehicle_damage import VehicleDamageRequest
from pathlib import Path
import logging

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/analyze/text")
async def analyze_text(text: str = Form(...)):
    try:
        result = await AnalysisService.analyze_text(text)
        return JSONResponse(content=result)
    except Exception as e:
        logging.error(f"Error in text analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/image")
async def analyze_image(image: UploadFile = File(...)):
    try:
        image_data = await image.read()
        result = await AnalysisService.analyze_image(image_data)
        return JSONResponse(content=result)
    except Exception as e:
        logging.error(f"Error in image analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/pdf")
async def analyze_pdf(pdf: UploadFile = File(...)):
    try:
        pdf_data = await pdf.read()
        result = await AnalysisService.analyze_pdf(pdf_data)
        return JSONResponse(content=result)
    except Exception as e:
        logging.error(f"Error in PDF analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/webpage")
async def analyze_webpage(url: str = Form(...)):
    try:
        result = await AnalysisService.analyze_webpage(url)
        return JSONResponse(content=result)
    except Exception as e:
        logging.error(f"Error in webpage analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/vehicle-damage")
async def analyze_vehicle_damage(request: VehicleDamageRequest):
    """
    Analyze vehicle damage from image URLs
    
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
        result = await AnalysisService.analyze_vehicle_damage(request)
        return JSONResponse(content=result)
    except Exception as e:
        logging.error(f"Error in vehicle damage analysis endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 