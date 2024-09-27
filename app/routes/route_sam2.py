import asyncio
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.utils_sam2 import detect_automatic_sam2, detect_predictor_sam2
from schemas import SegmentRequest
from utils.utils import logger

router = APIRouter()

@router.post("/segment_automatic")
async def automatic_detection(request: SegmentRequest):
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
    logger.info("Received request for predictor prompts with the following data: %s", request)

    result = await asyncio.to_thread(
        detect_predictor_sam2,
        request=request,
    )

    if isinstance(result, dict) and "error" in result:
        return result
    return JSONResponse(content=result)
