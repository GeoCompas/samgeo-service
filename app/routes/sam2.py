import asyncio
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from schemas.segment import SegmentRequestBase, SegmentResponseBase
from utils.sam2 import detect_automatic_sam2, detect_predictor_sam2
from utils.logger_config import log

router = APIRouter()


@router.post(
    "/segment_automatic",
    tags=["Decoder"],
    description="Segment the images using automatic options"
    # response_model=SegmentResponseBase,
)
async def automatic_detection(request: SegmentRequestBase):
    zoom_int = int(request.zoom)
    result = await asyncio.to_thread(
        detect_automatic_sam2,
        request=request
    )

    # Check if an error occurred
    if isinstance(result, dict) and "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=jsonable_encoder(result))


@router.post(
    "/segment_predictor",
    tags=["Decoder"],
    description="Segment the images using point input prompts",
    response_model=SegmentResponseBase,
)
async def predictor_promts(request: SegmentRequestBase):
    log.info("Received request for predictor prompts with the following data: %s", request)

    result = await asyncio.to_thread(
        detect_predictor_sam2,
        request=request,
    )

    if isinstance(result, dict) and "error" in result:
        return JSONResponse(content=result, status_code=400)

    return JSONResponse(content=jsonable_encoder(result))
