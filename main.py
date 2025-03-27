from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv
import os
from openai import AsyncOpenAI
import logging
from typing import Optional, List, Dict
import shutil
import uuid
from pathlib import Path
import base64
from datetime import datetime
import httpx
import json
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Load environment variables
load_dotenv()

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.error("OpenAI API key not found! Please set OPENAI_API_KEY in .env file")
    raise ValueError("OpenAI API key not found!")

# Initialize OpenAI client with proper configuration
client = AsyncOpenAI(
    api_key=api_key,
    base_url="https://api.openai.com/v1",  # Explicitly set the base URL
    http_client=httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=5.0, read=30.0, write=30.0),
        limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        transport=httpx.AsyncHTTPTransport(retries=3)
    )
)

# Initialize FastAPI app
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

COMPANY_INFO = {
    "name": "Sundaravijayam Automobile Services Private Limited",
    "address": "839/2, 24th Main Rd, Behind Thirumala Theatre, 1st Sector, HSR Layout, Bengaluru, Karnataka 560102",
    "website": "www.readyassist.in"
}

async def analyze_image(image_path: str) -> Optional[Dict]:
    try:
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
            
            logging.info("Making API call to OpenAI Vision...")
            for attempt in range(3):  # Try up to 3 times
                try:
                    response = await client.chat.completions.create(
                        model="gpt-4-vision-preview",  # Current stable version that supports vision
                        max_tokens=4096,
                        temperature=0.7,
                        messages=[
                            {
                                "role": "system",
                                "content": """You are an expert vehicle damage assessor with deep knowledge of Indian vehicles, repair costs, and RTO regulations. 
                                Analyze the image in detail and provide comprehensive information about the vehicle's condition, damage assessment, and repair estimates in INR."""
                            },
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": """Please analyze this vehicle image and provide a detailed report with the following information:

1. Vehicle Details:
   - Make and model
   - Year of manufacture
   - Odometer reading (if visible)
   - Vehicle color
   - Vehicle registration number (if visible)
   - Registered state
   - RTO name (if identifiable)
   - Claims reported location

2. Vehicle Dashboard & Condition:
   - Warning lights status
   - Fuel level
   - Engine temperature
   - Speedometer reading
   - Tachometer reading

3. Stickers & Signs:
   - Number plate sticker details
   - Rear windshield stickers
   - Body stickers
   - Any other visible markings

4. Damage Analysis:
   Exterior Damage:
   - Front bumper & grille condition
   - Headlights & fender status
   - Hood alignment & latch
   - Other visible exterior damage
   
   Mechanical & Structural:
   - Engine bay condition (if visible)
   - Battery & electrical issues
   - Suspension & underbody condition

5. Dashboard Warning Lights:
   - Check engine light status
   - Battery warning light
   - Oil pressure warning
   - Power steering warning
   - Brake system warning
   - Fuel warning light

6. Repair Recommendations:
   Exterior Work:
   - Body repair needs
   - Paint work required
   - Parts replacement needed
   
   Mechanical Repairs:
   - Engine-related repairs
   - Electrical system fixes
   - Suspension work
   - Other mechanical needs

7. Cost Estimates (in INR):
   - Itemized repair costs
   - Labor charges
   - Parts replacement costs
   - Total estimated repair cost

8. Market Valuation:
   - Estimated current market value
   - Post-repair value estimate
   - Similar vehicle market rates

Format the response as JSON with these exact keys:
{
    "vehicle_info": {
        "make_model": "",
        "year": "",
        "odometer": "",
        "color": "",
        "registration": "",
        "state": "",
        "rto": "",
        "location": ""
    },
    "dashboard_condition": {
        "warning_lights": {},
        "fuel_level": "",
        "engine_temp": "",
        "speedometer": "",
        "tachometer": ""
    },
    "stickers_signs": {
        "number_plate": "",
        "windshield": [],
        "body": []
    },
    "damage_assessment": {
        "exterior": {},
        "mechanical": {},
        "structural": {}
    },
    "warning_lights": {
        "check_engine": "",
        "battery": "",
        "oil": "",
        "power_steering": "",
        "brake": "",
        "fuel": ""
    },
    "repair_recommendations": {
        "exterior_work": [],
        "mechanical_work": []
    },
    "cost_estimates": {
        "parts": {},
        "labor": {},
        "total": ""
    },
    "market_valuation": {
        "current_value": "",
        "post_repair_value": "",
        "market_rates": {}
    }
}"""
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_base64}"
                                        }
                                    }
                                ]
                            }
                        ]
                    )
                    logging.info("Successfully received response from OpenAI")
                    
                    # Parse the response into JSON format
                    content = response.choices[0].message.content
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as je:
                        logging.error(f"Failed to parse JSON response: {je}")
                        return {"raw_analysis": content}
                        
                except httpx.ConnectError as ce:
                    if attempt < 2:  # If not the last attempt
                        wait_time = (attempt + 1) * 2  # Progressive backoff
                        logging.warning(f"Connection error, retrying in {wait_time} seconds... (Attempt {attempt + 1}/3)")
                        await asyncio.sleep(wait_time)
                        continue
                    logging.error(f"Failed after 3 attempts: {str(ce)}")
                    raise  # Re-raise the last error if all attempts failed
                except Exception as api_error:
                    logging.error(f"OpenAI API Error: {str(api_error)}")
                    raise
                    
    except Exception as e:
        logging.error(f"Error analyzing image: {str(e)}")
        return None

def generate_html_report(analyses: List[Dict], company_info: Dict) -> str:
    try:
        # Initialize combined data structure
        combined_data = {
            "vehicle_info": {},
            "dashboard_condition": {
                "warning_lights": {},
                "fuel_level": "",
                "engine_temp": "",
                "speedometer": "",
                "tachometer": ""
            },
            "stickers_signs": {
                "number_plate": "",
                "windshield": [],
                "body": []
            },
            "damage_assessment": {
                "exterior": {},
                "mechanical": {},
                "structural": {}
            },
            "warning_lights": {
                "check_engine": "",
                "battery": "",
                "oil": "",
                "power_steering": "",
                "brake": "",
                "fuel": ""
            },
            "repair_recommendations": {
                "exterior_work": [],
                "mechanical_work": []
            },
            "cost_estimates": {
                "parts": {},
                "labor": {},
                "total": ""
            },
            "market_valuation": {
                "current_value": "",
                "post_repair_value": "",
                "market_rates": {}
            }
        }
        
        # Combine all analyses
        for analysis in analyses:
            if isinstance(analysis, dict):
                for key in combined_data.keys():
                    if key in analysis:
                        if isinstance(combined_data[key], dict):
                            combined_data[key].update(analysis[key])
                        elif isinstance(combined_data[key], list):
                            if isinstance(analysis[key], list):
                                combined_data[key].extend(analysis[key])
                            else:
                                combined_data[key].append(analysis[key])
        
        # Generate HTML report
        report = f"""
        <div class="report-container">
            <div class="header">
                <h1>{company_info['name']}</h1>
                <p>{company_info['address']}</p>
                <p>{company_info['website']}</p>
                <h2>Comprehensive Vehicle Damage Report</h2>
                <p class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <section class="vehicle-details">
                <h3>Vehicle Information</h3>
                <table>
                    {generate_table_rows(combined_data['vehicle_info'])}
                </table>
            </section>
            
            <section class="dashboard-condition">
                <h3>Dashboard & Vehicle Condition</h3>
                <table>
                    <tr>
                        <td>Fuel Level</td>
                        <td>{combined_data['dashboard_condition']['fuel_level']}</td>
                    </tr>
                    <tr>
                        <td>Engine Temperature</td>
                        <td>{combined_data['dashboard_condition']['engine_temp']}</td>
                    </tr>
                    <tr>
                        <td>Speedometer Reading</td>
                        <td>{combined_data['dashboard_condition']['speedometer']}</td>
                    </tr>
                    <tr>
                        <td>Tachometer Reading</td>
                        <td>{combined_data['dashboard_condition']['tachometer']}</td>
                    </tr>
                </table>
            </section>
            
            <section class="stickers-signs">
                <h3>Stickers & Signs</h3>
                <h4>Number Plate Sticker</h4>
                <p>{combined_data['stickers_signs']['number_plate']}</p>
                <h4>Windshield Stickers</h4>
                <ul>
                    {generate_list_items(combined_data['stickers_signs']['windshield'])}
                </ul>
                <h4>Body Stickers</h4>
                <ul>
                    {generate_list_items(combined_data['stickers_signs']['body'])}
                </ul>
            </section>
            
            <section class="damage-assessment">
                <h3>Damage Assessment</h3>
                <h4>Exterior Damage</h4>
                <table>
                    {generate_table_rows(combined_data['damage_assessment']['exterior'])}
                </table>
                <h4>Mechanical Issues</h4>
                <table>
                    {generate_table_rows(combined_data['damage_assessment']['mechanical'])}
                </table>
                <h4>Structural Assessment</h4>
                <table>
                    {generate_table_rows(combined_data['damage_assessment']['structural'])}
                </table>
            </section>
            
            <section class="warning-lights">
                <h3>Warning Lights Status</h3>
                <table>
                    {generate_table_rows(combined_data['warning_lights'])}
                </table>
            </section>
            
            <section class="repair-recommendations">
                <h3>Repair Recommendations</h3>
                <h4>Exterior Work</h4>
                <ul>
                    {generate_list_items(combined_data['repair_recommendations']['exterior_work'])}
                </ul>
                <h4>Mechanical Work</h4>
                <ul>
                    {generate_list_items(combined_data['repair_recommendations']['mechanical_work'])}
                </ul>
            </section>
            
            <section class="cost-estimates">
                <h3>Cost Estimates</h3>
                <h4>Parts</h4>
                <table>
                    {generate_table_rows(combined_data['cost_estimates']['parts'])}
                </table>
                <h4>Labor</h4>
                <table>
                    {generate_table_rows(combined_data['cost_estimates']['labor'])}
                </table>
                <h4>Total Estimated Cost</h4>
                <p class="total-cost">₹{combined_data['cost_estimates']['total']}</p>
            </section>
            
            <section class="market-valuation">
                <h3>Market Valuation</h3>
                <table>
                    <tr>
                        <td>Current Market Value</td>
                        <td>₹{combined_data['market_valuation']['current_value']}</td>
                    </tr>
                    <tr>
                        <td>Post-Repair Value</td>
                        <td>₹{combined_data['market_valuation']['post_repair_value']}</td>
                    </tr>
                </table>
                <h4>Market Rates Comparison</h4>
                <table>
                    {generate_table_rows(combined_data['market_valuation']['market_rates'])}
                </table>
            </section>
        </div>
        """
        return report
    except Exception as e:
        logging.error(f"Error generating HTML report: {str(e)}")
        return f"<div class='error'>Error generating report: {str(e)}</div>"

def generate_table_rows(data: Dict) -> str:
    return "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in data.items()])

def generate_list_items(items: List) -> str:
    return "".join([f"<li>{item}</li>" for item in items if item])

def generate_repair_costs_table(costs: List[Dict]) -> str:
    try:
        total = 0
        rows = []
        
        for cost_dict in costs:
            if isinstance(cost_dict, dict):
                for item, cost in cost_dict.items():
                    # Extract numeric value from cost string
                    if isinstance(cost, str):
                        cost_value = float(''.join(filter(str.isdigit, cost)))
                    elif isinstance(cost, (int, float)):
                        cost_value = float(cost)
                    else:
                        continue
                    
                    total += cost_value
                    rows.append(f"<tr><td>{item}</td><td>₹{cost_value:,.2f}</td></tr>")
        
        rows.append(f"<tr class='total'><td>Total Estimated Cost</td><td>₹{total:,.2f}</td></tr>")
        return "".join(rows)
    except Exception as e:
        logging.error(f"Error generating repair costs table: {str(e)}")
        return "<tr><td colspan='2'>Error calculating repair costs</td></tr>"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze_files")
async def handle_file_uploads(files: List[UploadFile] = File(...)):
    try:
        if not files:
            logging.error("No files were uploaded")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No files were uploaded"}
            )

        analyses = []
        file_urls = []
        
        logging.info(f"Received {len(files)} files for analysis")
        
        for file in files:
            logging.info(f"Processing file: {file.filename}")
            
            # Validate file type
            file_extension = file.filename.split('.')[-1].lower()
            if file_extension not in ['jpg', 'jpeg', 'png']:
                logging.warning(f"Skipping unsupported file type: {file.filename}")
                continue
            
            try:
                # Read file content to validate it's a real image
                content = await file.read()
                if len(content) == 0:
                    logging.error(f"Empty file received: {file.filename}")
                    continue
                
                # Reset file position for later use
                await file.seek(0)
                
                # Generate unique filename
                unique_filename = f"{uuid.uuid4()}.{file_extension}"
                file_path = UPLOAD_DIR / unique_filename
                
                # Save the uploaded file
                logging.info(f"Saving file to: {file_path}")
                with file_path.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                
                # Get the file's public URL
                file_url = f"/static/uploads/{unique_filename}"
                file_urls.append(file_url)
                
                # Analyze the image
                logging.info(f"Starting analysis for: {file.filename}")
                analysis = await analyze_image(str(file_path))
                if analysis:
                    analyses.append(analysis)
                    logging.info(f"Successfully analyzed: {file.filename}")
                else:
                    logging.error(f"Failed to analyze: {file.filename}")
            
            except Exception as e:
                logging.error(f"Error processing file {file.filename}: {str(e)}")
                continue
        
        if not analyses:
            logging.error("No valid images were successfully analyzed")
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No valid images to analyze. Please ensure you upload supported image files (JPG, JPEG, PNG)."}
            )
        
        # Generate HTML report
        logging.info("Generating HTML report")
        report_html = generate_html_report(analyses, COMPANY_INFO)
        
        return {
            "success": True,
            "report_html": report_html,
            "file_urls": file_urls
        }
    
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"An error occurred while processing the files: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print("Error: Port 8080 is already in use.")
            print("Please try the following:")
            print("1. Kill any existing processes using the port:")
            print("   lsof -i :8080 | grep LISTEN")
            print("   kill <PID>")
            print("2. Or use a different port:")
            print("   uvicorn main:app --reload --port 8081")
        else:
            raise e 