import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Tuple
import logging
from utils_detection import detect_all_objects
from utils import group_files_by_base_name

import time

app = FastAPI()
app.mount("/files", StaticFiles(directory="public"), name="public")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000/files")
logging.basicConfig(level=logging.INFO)
class SegmentRequest(BaseModel):
    bbox: List[float]
    image_shape: Tuple[int, int]
    input_label: int
    input_point: Tuple[int, int]
    crs: str
    zoom: float
    id: str
    project: str

@app.get("/")
def read_root():
    return {"state": "ok"}

@app.get("/files")
def list_files():
    public_dir = "public"
    grouped_files = group_files_by_base_name(public_dir, BASE_URL)
    return {"file_groups": grouped_files}


@app.post("/segment")
async def segment_image(request: SegmentRequest):
    # Validate bbox has 4 values
    if len(request.bbox) != 4:
        return {"error": "Bounding box must contain exactly 4 values: [min_lon, min_lat, max_lon, max_lat]"}

    # Validate coordinates
    if not (-180 <= request.bbox[0] <= 180 and -90 <= request.bbox[1] <= 90 and 
            -180 <= request.bbox[2] <= 180 and -90 <= request.bbox[3] <= 90):
        return {"error": "Bounding box coordinates must be within valid ranges."}
    zoom_int = int(request.zoom)
    result = await asyncio.to_thread(
        detect_all_objects,
        bbox=request.bbox,
        crs=request.crs,
        zoom=zoom_int,
        id=request.id,
        project=request.project
    )
    if isinstance(result, dict) and "error" in result:
        return result
    return JSONResponse(content=result)