# AI Analysis API

A FastAPI-based API service that provides AI-powered analysis for various types of content including text, images, PDFs, webpages, vehicle damage assessment, and audio processing. This project integrates multiple AI services and provides a unified interface for content analysis and processing.

## Features

### Core Analysis Features
- **Text Analysis**: 
  - Natural language processing
  - Sentiment analysis
  - Key information extraction
  - Summary generation

- **Image Analysis**: 
  - Object detection
  - Scene understanding
  - Text extraction (OCR)
  - Content moderation

- **PDF Analysis**: 
  - Text extraction
  - Document structure analysis
  - Table detection
  - Form field recognition

- **Webpage Analysis**: 
  - Content extraction
  - Metadata analysis
  - Link structure analysis
  - SEO insights

### Specialized Features

- **Vehicle Damage Assessment**: 
  - Multi-image damage analysis
  - Damage severity classification
  - Cost estimation
  - Detailed PDF report generation
  - Affected areas identification
  - Repair recommendations
  - Integration with insurance systems

- **Audio Processing**:
  - Secure audio file download
  - Metadata extraction (duration, format)
  - Basic authentication support
  - File management
  - Integration with external services
  - Support for various audio formats

## Detailed Project Structure

```
openai-api/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── audio_models.py      # Audio processing models
│   │   └── vehicle_damage.py    # Vehicle damage models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analysis_routes.py   # General analysis endpoints
│   │   ├── audio_routes.py      # Audio processing endpoints
│   │   └── vehicle_info_routes.py # Vehicle analysis endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── analysis_service.py  # Core analysis logic
│   │   ├── audio_service/
│   │   │   └── audio_processor.py # Audio processing implementation
│   │   └── pdf_report_generator.py # PDF generation service
│   └── core/
│       ├── __init__.py
│       └── config.py            # Application configuration
├── static/
│   ├── css/                    # Stylesheets
│   ├── js/                     # JavaScript files
│   └── reports/                # Generated PDF reports
├── templates/
│   └── vehicle_report.html     # PDF report template
├── uploads/
│   ├── audio/                  # Audio file storage
│   └── temp/                   # Temporary file storage
├── tests/
│   ├── __init__.py
│   ├── test_audio.py          # Audio processing tests
│   ├── test_vehicle.py        # Vehicle analysis tests
│   └── test_analysis.py       # General analysis tests
├── docs/
│   ├── api.md                 # API documentation
│   ├── setup.md               # Setup guide
│   └── development.md         # Development guide
├── scripts/
│   ├── setup.sh              # Setup script
│   └── test.sh               # Test runner script
├── .env.example              # Example environment variables
├── .gitignore               # Git ignore rules
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker compose configuration
└── README.md              # Project documentation
```

## Technical Details

### API Response Formats

#### Vehicle Damage Analysis Response
```json
{
    "success": true,
    "message": "Analysis completed successfully",
    "order_id": "ORDER123",
    "analysis": {
        "damage_detected": true,
        "severity": "moderate",
        "affected_areas": ["front_bumper", "hood"],
        "estimated_cost": "$1500-2000",
        "recommendations": [
            "Replace front bumper",
            "Repair and repaint hood"
        ]
    },
    "pdf_report": {
        "filename": "damage_report_ORDER123.pdf",
        "url": "/static/reports/damage_report_ORDER123.pdf"
    }
}
```

#### Audio Processing Response
```json
{
    "filename": "ORDER123_SRN456.mp3",
    "size_bytes": 2048576,
    "duration_seconds": 120.5,
    "api_response": {
        "status": "success",
        "message": "Audio processed successfully",
        "metadata": {
            "format": "MP3",
            "bitrate": "128kbps",
            "channels": 2
        }
    }
}
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
# Production dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

4. Create required directories:
```bash
mkdir -p static/reports uploads/audio uploads/temp
```

5. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
```
OPENAI_API_KEY=your_openai_api_key
API_HOST=0.0.0.0
API_PORT=8001
DEBUG_MODE=True
LOG_LEVEL=INFO
UPLOAD_DIR=uploads
REPORTS_DIR=static/reports
MAX_UPLOAD_SIZE=10485760
```

## Development Setup

1. Install development tools:
```bash
pip install black pytest pytest-cov flake8
```

2. Set up pre-commit hooks:
```bash
pre-commit install
```

3. Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_vehicle.py
```

4. Format code:
```bash
# Format all Python files
black .

# Check formatting
black . --check
```

## Docker Deployment

1. Build the image:
```bash
docker build -t ai-analysis-api .
```

2. Run the container:
```bash
docker run -p 8001:8001 -v uploads:/app/uploads ai-analysis-api
```

Or using docker-compose:
```bash
docker-compose up -d
```

## API Documentation

Detailed API documentation is available at:
- Swagger UI: `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`

### Authentication
- Basic authentication for audio endpoints
- API key authentication for analysis endpoints

### Rate Limiting
- 100 requests per minute per IP
- 1000 requests per day per API key

### Error Handling
All errors follow the format:
```json
{
    "detail": "Error message",
    "error_code": "ERROR_CODE",
    "timestamp": "2024-03-04T12:00:00Z"
}
```

## Monitoring and Logging

- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: `logs/access.log`

Log format:
```
[TIMESTAMP] [LEVEL] [MODULE] Message
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`pytest`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Create a Pull Request

### Coding Standards
- Follow PEP 8
- Use type hints
- Write docstrings for all functions
- Maintain test coverage above 80%

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please:
1. Check the documentation in the `docs` directory
2. Open an issue on GitHub
3. Contact the development team

## Acknowledgments

- OpenAI for AI capabilities
- FastAPI framework
- ReportLab for PDF generation
- All contributors 