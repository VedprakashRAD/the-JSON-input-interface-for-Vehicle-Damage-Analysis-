from app.core.ai_clients import grok_client, openai_client
from app.config.settings import GROK_MODEL, OPENAI_MODEL
import logging
from typing import Dict, Any, Optional, List
import base64
from pathlib import Path
import PyPDF2
import tempfile
import shutil
import uuid
import httpx
from app.models.vehicle_damage import VehicleDamageRequest
import aiohttp
import os

class AnalysisService:
    @staticmethod
    async def analyze_text(text: str) -> Dict[str, Any]:
        try:
            response = await grok_client.chat.completions.create(
                model=GROK_MODEL,
                messages=[{"role": "user", "content": text}]
            )
            return {"analysis": response.choices[0].message.content}
        except Exception as e:
            logging.error(f"Error in text analysis: {str(e)}")
            raise

    @staticmethod
    async def analyze_image(image_data: bytes) -> Dict[str, Any]:
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            response = await openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image and provide a detailed description."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return {"analysis": response.choices[0].message.content}
        except Exception as e:
            logging.error(f"Error in image analysis: {str(e)}")
            raise

    @staticmethod
    async def analyze_pdf(pdf_file: bytes) -> Dict[str, Any]:
        try:
            # Create a temporary file to store the PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                temp_file.write(pdf_file)
                temp_path = temp_file.name

            # Extract text from PDF
            text_content = []
            with open(temp_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content.append(page.extract_text())

            # Clean up temporary file
            Path(temp_path).unlink()

            # Analyze the extracted text
            combined_text = "\n".join(text_content)
            return await AnalysisService.analyze_text(combined_text)
        except Exception as e:
            logging.error(f"Error in PDF analysis: {str(e)}")
            raise

    @staticmethod
    async def analyze_webpage(url: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                content = response.text

            # Analyze the webpage content
            return await AnalysisService.analyze_text(content)
        except Exception as e:
            logging.error(f"Error in webpage analysis: {str(e)}")
            raise

    @staticmethod
    async def analyze_vehicle_damage(request: VehicleDamageRequest) -> Dict[str, Any]:
        """
        Analyze vehicle damage from provided image URLs
        """
        try:
            # Initialize results
            analysis_results = []
            
            # Process each image URL
            async with aiohttp.ClientSession() as session:
                for image_url in request.image_urls:
                    try:
                        # Download image
                        async with session.get(image_url) as response:
                            if response.status != 200:
                                logging.error(f"Failed to download image from {image_url}")
                                continue
                                
                            image_data = await response.read()
                            
                            # Analyze image using OpenAI Vision
                            analysis = await AnalysisService._analyze_image_with_openai(image_data)
                            
                            analysis_results.append({
                                "image_url": image_url,
                                "analysis": analysis
                            })
                            
                    except Exception as e:
                        logging.error(f"Error processing image {image_url}: {str(e)}")
                        continue
            
            # Compile final result
            return {
                "order_id": request.order_id,
                "total_images": len(request.image_urls),
                "processed_images": len(analysis_results),
                "results": analysis_results
            }
            
        except Exception as e:
            logging.error(f"Error in vehicle damage analysis: {str(e)}")
            raise

    @staticmethod
    async def _analyze_image_with_openai(image_data: bytes) -> Dict[str, Any]:
        """
        Analyze image using OpenAI Vision API
        """
        try:
            # TODO: Implement OpenAI Vision analysis
            # For now, return mock response
            return {
                "damage_detected": True,
                "damage_severity": "moderate",
                "affected_areas": ["front bumper", "hood"],
                "estimated_repair_cost": "$1500-2000",
                "recommendations": [
                    "Replace front bumper",
                    "Repair and repaint hood"
                ]
            }
        except Exception as e:
            logging.error(f"Error in OpenAI Vision analysis: {str(e)}")
            raise 