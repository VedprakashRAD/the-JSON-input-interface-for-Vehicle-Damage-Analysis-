# OpenAI API Interface

A FastAPI application that provides a web interface for OpenAI's GPT-3.5 Turbo and GPT-4 Vision APIs.

## Features

- Report generation using GPT-3.5 Turbo
- Image analysis using GPT-4 Vision
- Modern UI with Tailwind CSS
- Error handling and logging
- Async API calls

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd OpenAI_API
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory and add your OpenAI API key:
```
OPENAI_API_KEY="your-api-key-here"
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## Usage

### Generate Report
1. Enter your text data in the text area
2. Specify the output format (default: "summary, findings, recommendations")
3. Click "Generate Report"

### Analyze Image
1. Enter an image URL in the input field
2. Click "Analyze Image"

## API Endpoints

- `GET /`: Home page with the web interface
- `POST /generate_report`: Generate a report from text data
- `POST /analyze_image`: Analyze an image from URL

## Error Handling

Errors are logged to `api_errors.log` in the root directory.

## Cost Considerations

- GPT-3.5 Turbo: ~$0.0015/1K tokens
- GPT-4 Vision: ~$0.01-$0.03/image 