import os
import time
import base64
from samgeo import tms_to_geotiff

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from schemas import ImageRequest

from app.utils.utils_convert import convert_image_to_geotiff

router = APIRouter()
PUBLIC_DIR = "public/"
os.makedirs(PUBLIC_DIR, exist_ok=True)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

@router.post("/encode_image")
async def save_image(request: ImageRequest):
    if not request.canvas_image and not request.tms_source:
        raise HTTPException(status_code=400, detail="Either 'canvas_image' or 'tms_source' must be provided.")
    
    image_filename = f"{request.project_id}_{request.aoi_id}.png"
    tif_filename = f"{request.project_id}_{request.aoi_id}.tif"
    image_filepath = os.path.join(PUBLIC_DIR, image_filename)
    tif_filepath = os.path.join(PUBLIC_DIR, tif_filename)

    try:
        if request.canvas_image:
            image_data = request.canvas_image

            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]

            image_bytes = base64.b64decode(image_data)

            with open(image_filepath, "wb") as image_file:
                image_file.write(image_bytes)

            convert_image_to_geotiff(image_filepath, tif_filepath, request.bbox)

            image_url = f"{BASE_URL}/{image_filename}"
            tif_url = f"{BASE_URL}/{tif_filename}"

            return JSONResponse(content={"message": "Image saved successfully", "tif_url": tif_url}, status_code=200)

        elif request.tms_source:
            tms_id = request.tms_source

            if len(request.bbox) != 4:
                raise HTTPException(status_code=400, detail="Bounding box (bbox) must contain exactly 4 floats.")

            bbox = request.bbox
            zoom = request.zoom
            try:
                tms_to_geotiff(output=tif_filepath, bbox=bbox, zoom=zoom, source=tms_id, overwrite=True)
                tif_url = f"{BASE_URL}/{tif_filename}"
                return JSONResponse(content={"message": f"TMS Source {tms_id} processed", "tif_url": tif_url}, status_code=200)

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing TMS: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")