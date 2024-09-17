import asyncio
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Tuple
from utils_detection import detect_all_objects,check_gpu

router = APIRouter()

class SegmentRequest(BaseModel):
    bbox: List[float]
    image_shape: Tuple[int, int]
    input_label: int
    input_point: Tuple[int, int]
    crs: str
    zoom: float
    id: str
    project: str

@router.get("/gpu-check")
async def gpu_check():
    result = await asyncio.to_thread(check_gpu)
    return result

@router.post("/segment")
async def segment_image(request: SegmentRequest):
    if len(request.bbox) != 4:
        return {"error": "Bounding box must contain exactly 4 values: [min_lon, min_lat, max_lon, max_lat]"}

    if not (-180 <= request.bbox[0] <= 180 and -90 <= request.bbox[1] <= 90 and 
            -180 <= request.bbox[2] <= 180 and -90 <= request.bbox[3] <= 90):
        return {"error": "Bounding box coordinates must be within valid ranges."}

    zoom_int = int(request.zoom)
    result = await asyncio.to_thread(
        detect_all_objects,
        bbox=request.bbox,
        zoom=zoom_int,
        id=request.id,
        project=request.project
    )
    if isinstance(result, dict) and "error" in result:
        return result
    return JSONResponse(content=result)
