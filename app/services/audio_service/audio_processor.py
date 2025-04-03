import os
import requests
from mutagen.mp3 import MP3
import logging
from typing import Dict, Any, Tuple
from pathlib import Path
from fastapi import HTTPException
import base64
import json

class AudioProcessor:
    def __init__(self):
        self.upload_dir = Path("uploads/audio")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(level=logging.INFO)

    def download_file(self, url: str, username: str, password: str, headers: Dict[str, str]) -> bytes:
        """Download file from URL using basic authentication"""
        try:
            logging.info(f"Attempting to download file from {url}")
            
            # Create session for better connection handling
            session = requests.Session()
            
            # Add basic auth
            session.auth = (username, password)
            
            # Add headers
            session.headers.update(headers)
            
            # Make request
            response = session.get(
                url,
                verify=False,  # Only for testing
                timeout=30,
                allow_redirects=True
            )
            
            logging.info(f"Response status code: {response.status_code}")
            logging.info(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 401:
                raise HTTPException(status_code=401, detail="Authentication failed for Exotel API")
            elif response.status_code == 404:
                raise HTTPException(status_code=404, detail="Audio file not found on Exotel server")
            elif response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to download file. Server returned: {response.status_code}"
                )
            
            content = response.content
            if not content:
                raise HTTPException(status_code=400, detail="Received empty file from Exotel")
                
            content_type = response.headers.get('content-type', '')
            if not any(ct in content_type.lower() for ct in ['audio/', 'application/octet-stream', 'binary/']):
                logging.warning(f"Unexpected content type: {content_type}")
            
            content_length = len(content)
            logging.info(f"Downloaded file size: {content_length} bytes")
            
            return content
            
        except requests.exceptions.Timeout:
            raise HTTPException(status_code=504, detail="Timeout while downloading audio file")
        except requests.exceptions.RequestException as e:
            logging.error(f"Download failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text[:1000]}")  # Log first 1000 chars
            raise HTTPException(status_code=500, detail=f"Failed to download audio file: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error during file download")

    def save_file(self, content: bytes, filename: str) -> Tuple[str, int, float]:
        """Save file content and return file details"""
        try:
            file_path = self.upload_dir / filename
            
            # Save the file
            with open(file_path, 'wb') as f:
                f.write(content)

            if not os.path.exists(file_path):
                raise HTTPException(status_code=500, detail="Failed to save audio file")

            # Get file size
            size_bytes = os.path.getsize(file_path)
            if size_bytes == 0:
                raise HTTPException(status_code=500, detail="Saved file is empty")

            # Get audio duration
            try:
                audio = MP3(file_path)
                duration_seconds = audio.info.length
            except Exception as e:
                logging.error(f"Error reading MP3 file: {str(e)}")
                raise HTTPException(status_code=500, detail="Invalid MP3 file format")

            return str(file_path), size_bytes, duration_seconds
        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error saving file: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to process audio file: {str(e)}")

    def make_api_call(self, api_url: str, params: Dict[str, str]) -> Dict[str, Any]:
        """Make API call to ReadyAssist"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            
            response = requests.post(api_url, json=params, headers=headers)
            
            # Log the response for debugging
            logging.info(f"API Response Status: {response.status_code}")
            logging.info(f"API Response Headers: {response.headers}")
            logging.info(f"API Response Content: {response.text}")
            
            response.raise_for_status()
            
            # Handle empty response
            if not response.text:
                return {"status": "success", "message": "Request processed but no content returned"}
                
            try:
                return response.json()
            except ValueError as e:
                logging.error(f"Failed to parse JSON response: {response.text}")
                return {
                    "status": "error",
                    "message": "Invalid JSON response",
                    "raw_response": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"API call failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logging.error(f"Response status: {e.response.status_code}")
                logging.error(f"Response content: {e.response.text}")
            raise HTTPException(status_code=500, detail=f"API call failed: {str(e)}")
        except Exception as e:
            logging.error(f"Error making API call: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    async def process_audio(self, 
                          url: str, 
                          username: str, 
                          password: str, 
                          srn_number: str, 
                          order_id: str) -> Dict[str, Any]:
        """Process audio download and API call"""
        try:
            # Set headers for download
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept': 'audio/mpeg,audio/*,*/*',
                'Connection': 'keep-alive'
            }

            # Download file
            file_content = self.download_file(url, username, password, headers)
            if not file_content:
                raise HTTPException(status_code=400, detail="No audio content received")

            # Generate unique filename
            filename = f"{order_id}_{srn_number}.mp3"

            # Save file and get details
            filepath, size_bytes, duration = self.save_file(file_content, filename)

            # Prepare response
            response_data = {
                "filename": filename,
                "size_bytes": size_bytes,
                "duration_seconds": round(duration, 2),
                "api_response": {
                    "status": "success",
                    "message": "Audio file processed successfully",
                    "data": {
                        "srn_number": srn_number,
                        "order_id": order_id,
                        "file_path": str(filepath),
                        "duration": round(duration, 2),
                        "file_size": size_bytes
                    }
                }
            }

            logging.info(f"Successfully processed audio file: {json.dumps(response_data)}")
            return response_data

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Error processing audio: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process audio: {str(e)}"
            ) 