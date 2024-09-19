import asyncio
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.utils_sam2 import detect_automatic_sam2, detect_predictor_sam2
from schemas import SegmentRequest

router = APIRouter()


@router.post("/segment_automatic")
async def automatic_detection(request: SegmentRequest):
    print("========")
    print(request)
    zoom_int = int(request.zoom)

    result = await asyncio.to_thread(
        detect_automatic_sam2,
        bbox=request.bbox,
        zoom=zoom_int,
        id=request.id,
        project=request.project,
    )
    if isinstance(result, dict) and "error" in result:
        return result
    return JSONResponse(content=result)


@router.post("/segment_predictor")
async def predictor_promts(request: SegmentRequest):
    zoom_int = int(request.zoom)

    result = await asyncio.to_thread(
        detect_predictor_sam2,
        bbox=request.bbox,
        zoom=zoom_int,
        point_coords=request.point_coords,
        point_labels=request.point_labels,
        id=request.id,
        project=request.project,
    )
    if isinstance(result, dict) and "error" in result:
        return result
    return JSONResponse(content=result)
