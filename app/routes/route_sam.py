import asyncio
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils_sam import detect_segment_objects, detect_segment_point_input_prompts
from utils import check_gpu
from schemas import SegmentRequest

router = APIRouter()


@router.get("/gpu-check")
async def gpu_check():
    result = await asyncio.to_thread(check_gpu)
    return result


@router.post("/segment")
async def segment_image(request: SegmentRequest):
    zoom_int = int(request.zoom)

    result = await asyncio.to_thread(
        detect_segment_objects,
        bbox=request.bbox,
        zoom=zoom_int,
        id=request.id,
        project=request.project,
    )
    if isinstance(result, dict) and "error" in result:
        return result
    return JSONResponse(content=result)


@router.post("/segment_points_prompts")
async def segment_image_points_prompts(request: SegmentRequest):
    zoom_int = int(request.zoom)

    result = await asyncio.to_thread(
        detect_segment_point_input_prompts,
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
