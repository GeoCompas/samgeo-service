import os
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import UploadFile, File, Depends
from utils.utils import get_timestamp
from schemas.geojson import JSONDataBase

router = APIRouter()
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


@router.get(
    "/predictions",
    response_class=JSONResponse,
    tags=["Utils"],
    description="Decode the images, using automatic or point input prompts",
)
def list_files_in_project(project_id: str = ""):
    public_dir = Path("public").resolve() / Path(project_id)
    if not str(public_dir).startswith(str(Path("public").resolve())):
        raise HTTPException(status_code=403, detail="Access denied")

    if not public_dir.exists() or not public_dir.is_dir():
        raise HTTPException(status_code=404, detail="Project not found")

    files = [f for f in public_dir.iterdir() if f.suffix == ".json"]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    detections = {}

    for file in files:
        if file.is_file():
            base_name, ext = os.path.splitext(file.name)
            if base_name not in detections:
                detections[base_name] = {
                    "geojson_files": [],
                    "id": base_name,
                    "bbox": None,
                    "zoom": None,
                    "image_url": None,
                    "tif_url": None,
                }
            detections[base_name]["geojson_files"] = [
                f"{BASE_URL}/files/{project_id}/{f.name}"
                for f in public_dir.iterdir()
                if f.suffix == ".geojson" and base_name in f.stem
            ]
            if ext == ".json":
                try:
                    with open(file, "r") as json_file:
                        json_content = json.load(json_file)
                        detections[base_name]["bbox"] = json_content.get("bbox", [])
                        detections[base_name]["zoom"] = json_content.get("zoom", None)
                        detections[base_name]["image_url"] = json_content.get("image_url", None)
                        detections[base_name]["tif_url"] = json_content.get("tif_url", None)
                except Exception as e:
                    raise HTTPException(
                        status_code=500, detail=f"Error reading JSON file: {str(e)}"
                    )

    response_data = {"project_id": project_id or "/", "detection": detections}

    return JSONResponse(content=response_data)


@router.post(
    "/upload_geojson",
    tags=["Utils"],
    description="Save GeoJSON data format in order to open it in JOSM",
)
async def upload_geojson(request: JSONDataBase):
    public_dir = Path("public").resolve() / Path(request.project)
    if not public_dir.exists():
        public_dir.mkdir(parents=True)

    geojson_file_name = f"{request.id}_{get_timestamp()}_fixed.geojson"
    geojson_file_path = public_dir / geojson_file_name

    try:
        geojson_data = json.loads(request.data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in 'data' field")

    try:
        with open(geojson_file_path, "w") as geojson_file:
            json.dump(geojson_data, geojson_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    file_url = f"{BASE_URL}/files/{request.project}/{geojson_file_name}"
    return {"project": request.project, "file_url": file_url}
