from dotenv import load_dotenv
import os
import logging
from pathlib import Path

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# API Keys
GORK_API_KEY = os.getenv("GORK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API Keys
if not GORK_API_KEY:
    logging.error("Gork AI API key not found! Please set GORK_API_KEY in .env file")
    raise ValueError("Gork AI API key not found!")

if not OPENAI_API_KEY:
    logging.error("OpenAI API key not found! Please set OPENAI_API_KEY in .env file")
    raise ValueError("OpenAI API key not found!")

# Base URLs
GORK_BASE_URL = "https://api.x.ai/v1"
OPENAI_BASE_URL = "https://api.openai.com/v1"

# File paths
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Model configurations
GROK_MODEL = "grok-1"
OPENAI_MODEL = "gpt-4-vision-preview" 