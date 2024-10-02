import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from routes.predictions import router as predictions_routes
from routes.sam2 import router as sam2_routes
from routes.aoi import router as aoi_routes

from utils.utils import check_gpu
from middleware import log_request_middleware

app = FastAPI()
app.title = "SAMGEO API"
app.version = "0.1.0"

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_request_middleware)


@app.get("/")
async def status():
    """
    Route to check the GPU status.

    This route uses the check_gpu utility to verify if the GPU is available
    on the system. The result is returned asynchronously.
    """
    result = await asyncio.to_thread(check_gpu)
    return result


app.include_router(aoi_routes)
app.include_router(sam2_routes)
app.mount("/files", StaticFiles(directory="public"), name="public")
app.include_router(predictions_routes)


@app.on_event("startup")
async def startup_event():
    os.makedirs("public", exist_ok=True)
    os.makedirs("tmp", exist_ok=True)
