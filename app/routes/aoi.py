import os
import time
import json
import base64
from samgeo import tms_to_geotiff

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from schemas.aoi import AOIRequestBase, AOIResponseBase
from utils.convert import convert_image_to_geotiff
from utils.logger_config import log

router = APIRouter()
PUBLIC_DIR = "public/"
os.makedirs(PUBLIC_DIR, exist_ok=True)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000") + "files"


@router.post(
    "/aoi",
    tags=["Encoder"],
    response_model=AOIResponseBase,
    description="Process canvas file and save it in the format required by SAM2",
)
async def save_image(request: AOIRequestBase):
    if not request.canvas_image and not request.tms_source:
        raise HTTPException(
            status_code=400, detail="Either 'canvas_image' or 'tms_source' must be provided."
        )
    os.makedirs(f"{PUBLIC_DIR}/{request.project}", exist_ok=True)
    image_filename = f"{request.project}/{request.id}.png"
    tif_filename = f"{request.project}/{request.id}.tif"
    json_filename = f"{request.project}/{request.id}.json"

    image_filepath = os.path.join(PUBLIC_DIR, image_filename)
    tif_filepath = os.path.join(PUBLIC_DIR, tif_filename)
    json_filepath = os.path.join(PUBLIC_DIR, json_filename)

    try:
        if request.canvas_image:
            image_data = request.canvas_image

            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]

            image_bytes = base64.b64decode(image_data)

            with open(image_filepath, "wb") as image_file:
                image_file.write(image_bytes)

            convert_image_to_geotiff(image_filepath, tif_filepath, request.bbox)

            image_url = f"{BASE_URL}/{image_filename}"
            tif_url = f"{BASE_URL}/{tif_filename}"
            log.info(image_url)
            log.info(tif_url)
            data_to_save = AOIResponseBase(
                project=request.project,
                id=request.id,
                bbox=request.bbox,
                zoom=request.zoom,
                image_url=image_url,
                tif_url=tif_url,
            )
            with open(json_filepath, "w") as json_file:
                json.dump(data_to_save.dict(), json_file)

            return data_to_save

        # TODO, implement in case we request AOI using TMS layer
        # elif request.tms_source:
        #     tms_id = request.tms_source

        #     if len(request.bbox) != 4:
        #         raise HTTPException(
        #             status_code=400, detail="Bounding box (bbox) must contain exactly 4 floats."
        #         )

        #     bbox = request.bbox
        #     zoom = request.zoom
        #     try:
        #         tms_to_geotiff(
        #             output=tif_filepath, bbox=bbox, zoom=zoom, source=tms_id, overwrite=True
        #         )
        #         tif_url = f"{BASE_URL}/{tif_filename}"

        #         data_to_save = AOIResponseBase(
        #             project=request.project,
        #             id=request.id,
        #             bbox=request.bbox,
        #             zoom=request.zoom,
        #             tif_url=tif_url,
        #         )
        #         with open(json_filepath, "w") as json_file:
        #             json.dump(data_to_save.dict(), json_file)

        #         return data_to_save

        #     except Exception as e:
        #         raise HTTPException(status_code=500, detail=f"Error processing TMS: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
