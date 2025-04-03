from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.routes.analysis_routes import router as analysis_router
from app.routes.api_status_routes import router as status_router
from app.routes.audio_routes import router as audio_router
from app.routes.vehicle_info_routes import router as vehicle_router

app = FastAPI(title="AI Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(analysis_router)
app.include_router(status_router)
app.include_router(audio_router)
app.include_router(vehicle_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 