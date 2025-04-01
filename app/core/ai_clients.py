from openai import AsyncOpenAI
from app.config.settings import (
    GORK_API_KEY,
    OPENAI_API_KEY,
    GORK_BASE_URL,
    OPENAI_BASE_URL
)

# Initialize OpenAI client for Grok
grok_client = AsyncOpenAI(
    api_key=GORK_API_KEY,
    base_url=GORK_BASE_URL
)

# Initialize OpenAI client
openai_client = AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL
) 