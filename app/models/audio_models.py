from pydantic import BaseModel, HttpUrl, validator
from typing import Dict, Any

class AudioDownloadRequest(BaseModel):
    url: str
    username: str
    password: str
    srn_number: str
    order_id: str

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith('https://recordings.exotel.com/'):
            raise ValueError('URL must be from recordings.exotel.com domain')
        return v

class AudioDownloadResponse(BaseModel):
    filename: str
    size_bytes: int
    duration_seconds: float
    api_response: Dict[str, Any] 