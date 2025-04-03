# AI Analysis API

A FastAPI-based API service that provides AI-powered analysis for various types of content including text, images, PDFs, webpages, vehicle damage assessment, and audio processing.

## Features

- **Text Analysis**: Analyze text content using AI
- **Image Analysis**: Process and analyze images
- **PDF Analysis**: Extract and analyze PDF content
- **Webpage Analysis**: Analyze web content
- **Vehicle Damage Assessment**: 
  - Process vehicle damage images
  - Generate detailed PDF reports
  - Damage severity estimation
  - Cost estimation
- **Audio Processing**:
  - Download and process audio files
  - Extract audio metadata
  - Integration with external services

## Project Structure

```
openai-api/
├── app/
│   ├── main.py                  # FastAPI application entry point
│   ├── models/                  # Pydantic models
│   ├── routes/                  # API routes
│   ├── services/               # Business logic
│   └── core/                   # Core configurations
├── static/                     # Static files
├── templates/                  # HTML templates
├── uploads/                    # Upload directory
└── requirements.txt           # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd openai-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create required directories:
```bash
mkdir -p static/reports uploads/audio
```

5. Create a `.env` file with your configuration:
```
OPENAI_API_KEY=your_api_key
```

## Running the Application

Start the server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at:
- API Documentation: http://localhost:8001/docs
- ReDoc Documentation: http://localhost:8001/redoc

## API Endpoints

### Analysis Endpoints
- `GET /`: Home endpoint
- `POST /analyze/text`: Text analysis
- `POST /analyze/image`: Image analysis
- `POST /analyze/pdf`: PDF analysis
- `POST /analyze/webpage`: Webpage analysis

### Vehicle Analysis Endpoints
- `POST /vehicle/analyze/damage`: Vehicle damage analysis

### Audio Processing Endpoints
- `POST /audio/process`: Audio file processing

## Example Requests

### Vehicle Damage Analysis
```bash
curl -X 'POST' \
  'http://localhost:8001/vehicle/analyze/damage' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "order_id": "ORDER123",
    "image_urls": [
        "https://example.com/damage1.jpg",
        "https://example.com/damage2.jpg"
    ]
}'
```

### Audio Processing
```bash
curl -X 'POST' \
  'http://localhost:8001/audio/process' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "url": "https://example.com/audio.mp3",
    "username": "your_username",
    "password": "your_password",
    "srn_number": "SRN123",
    "order_id": "ORDER123"
}'
```

## Dependencies

- FastAPI
- Uvicorn
- OpenAI
- ReportLab
- Mutagen
- And more (see requirements.txt)

## Development

1. Install development dependencies:
```bash
pip install black pytest
```

2. Format code:
```bash
black .
```

3. Run tests:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 