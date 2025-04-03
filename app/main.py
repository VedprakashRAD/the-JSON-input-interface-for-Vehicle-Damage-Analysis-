from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.analysis_routes import router as analysis_router
from app.routes.api_status_routes import router as status_router
from app.routes.audio_routes import router as audio_router

app = FastAPI(title="AI Analysis API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(analysis_router)
app.include_router(status_router)
app.include_router(audio_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 