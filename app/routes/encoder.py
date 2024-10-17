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
from utils.utils import base_files_names
router = APIRouter()

@router.post(
    "/aoi",
    tags=["Encoder"],
    response_model=AOIResponseBase,
    description="Process canvas file and save it in the format required by SAM2",
)
async def save_image(request: AOIRequestBase):

    project = request.project
    id = request.id
    bbox = request.bbox
    zoom = int(request.zoom)

    # Generate file names and paths
    png_file_path, json_file_path, tif_file_path, _, _, _, png_file_url, tif_file_url, _ = base_files_names(project, id)

    try:
        if request.canvas_image:
            image_data = request.canvas_image

            # Handle base64 encoded image
            if image_data.startswith("data:image"):
                image_data = image_data.split(",")[1]

            # Decode and save the image
            image_bytes = base64.b64decode(image_data)
            with open(png_file_path, "wb") as image_file:
                image_file.write(image_bytes)

            # Convert PNG to GeoTIFF
            convert_image_to_geotiff(png_file_path, tif_file_path, bbox)

            # Improved logging with more details
            log.info(f"Image saved at: {png_file_path}")
            log.info(f"GeoTIFF saved at: {tif_file_path}")
            log.info(f"Image URL: {png_file_url}")
            log.info(f"GeoTIFF URL: {tif_file_url}")

            # Prepare response
            resp_info = AOIResponseBase(
                project=project,
                id=id,
                bbox=bbox,
                zoom=zoom,
                image_url=png_file_url,
                tif_url=tif_file_url,
            )

            # Save response as JSON
            with open(json_file_path, "w") as json_file:
                json.dump(resp_info.dict(), json_file)

            return resp_info

    except Exception as e:
        # Log the error and return a 500 HTTP error
        log.error(f"Error processing request for project '{project}', id '{id}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")