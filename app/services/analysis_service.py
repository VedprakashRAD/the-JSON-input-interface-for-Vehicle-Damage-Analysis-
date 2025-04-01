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
        try:
            # Download and analyze each image
            analysis_results = []
            async with httpx.AsyncClient() as client:
                for image_url in request.image_urls:
                    # Download image
                    response = await client.get(str(image_url))
                    response.raise_for_status()
                    image_data = response.content

                    # Analyze image
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    response = await openai_client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Analyze this vehicle image and provide a detailed description of any damage, including location, severity, and estimated repair cost."},
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
                    analysis_results.append(response.choices[0].message.content)

            # Combine all analyses
            combined_analysis = "\n\n".join(analysis_results)

            # Get a summary using Grok
            summary_response = await grok_client.chat.completions.create(
                model=GROK_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert vehicle damage assessor. Provide a concise summary of the damage analysis, including total estimated repair cost and any critical issues that need immediate attention."
                    },
                    {
                        "role": "user",
                        "content": f"Order ID: {request.order_id}\n\nDamage Analysis:\n{combined_analysis}"
                    }
                ]
            )

            return {
                "order_id": request.order_id,
                "detailed_analysis": analysis_results,
                "summary": summary_response.choices[0].message.content
            }

        except Exception as e:
            logging.error(f"Error in vehicle damage analysis: {str(e)}")
            raise 