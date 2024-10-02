import asyncio
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from utils.sam2 import detect_automatic_sam2, detect_predictor_sam2
from schemas.segment import SegmentRequestBase
from utils.logger_config import log

router = APIRouter()


@router.post(
    "/segment_automatic", tags=["Decoder"], description="Segment the images using automatic options"
)
async def automatic_detection(request: SegmentRequestBase):
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


@router.post(
    "/segment_predictor",
    tags=["Decoder"],
    description="Segment the images using point input prompts",
)
async def predictor_promts(request: SegmentRequestBase):
    log.info("Received request for predictor prompts with the following data: %s", request)

    result = await asyncio.to_thread(
        detect_predictor_sam2,
        request=request,
    )

    if isinstance(result, dict) and "error" in result:
        return result
    return JSONResponse(content=result)
