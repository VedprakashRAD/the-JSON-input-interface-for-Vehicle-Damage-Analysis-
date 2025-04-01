from pydantic import BaseModel, HttpUrl, Field
from typing import List
from datetime import datetime

class VehicleDamageRequest(BaseModel):
    order_id: str = Field(..., description="Unique identifier for the damage assessment order")
    image_urls: List[HttpUrl] = Field(..., description="List of URLs pointing to vehicle damage images", min_items=1)

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORDER123",
                "image_urls": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg"
                ]
            }
        } 