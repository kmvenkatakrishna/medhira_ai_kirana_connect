import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from mangum import Mangum

from routers import inventory, whatsapp_simulator, analytics

app = FastAPI(
    title="KiranaConnect API",
    description="Backend API for KiranaConnect Inventory AI Agent",
    version="1.0.0",
)

# Allow CORS for the frontend React app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(inventory.router, prefix="/api/v1/stores/{store_id}/inventory", tags=["Inventory"])
app.include_router(analytics.router, prefix="/api/v1/stores/{store_id}/analytics", tags=["Analytics"])
app.include_router(whatsapp_simulator.router, prefix="/api/v1/whatsapp", tags=["WhatsApp Simulator"])

@app.get("/")
def read_root():
    return {"message": "Welcome to KiranaConnect API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "details": str(exc)},
    )

# Wrapper for AWS Lambda
handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
