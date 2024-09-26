import os
import time
import torch
import logging
import geopandas as gpd
import json
import psutil
from fastapi import FastAPI
from samgeo import tms_to_geotiff
from shapely.geometry import Polygon, MultiPolygon

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def group_files_by_base_name(public_dir: str, base_url: str) -> list:
    if not os.path.exists(public_dir):
        return {"error": "The public directory does not exist."}

    file_groups = {}

    for file in os.listdir(public_dir):
        modification_time = os.path.getmtime(os.path.join(public_dir, file))
        base_name, _ = os.path.splitext(file)
        file_url = f"{base_url}/{file}"

        if base_name not in file_groups:
            file_groups[base_name] = {
                "base_name": base_name,
                "files": [],
                "modification_time": modification_time,
            }

        file_groups[base_name]["files"].append({"file_name": file, "url": file_url})

        if modification_time > file_groups[base_name]["modification_time"]:
            file_groups[base_name]["modification_time"] = modification_time

    grouped_files = list(file_groups.values())
    sorted_grouped_files = sorted(grouped_files, key=lambda x: x["modification_time"], reverse=True)

    for group in sorted_grouped_files:
        group["modification_time"] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(group["modification_time"])
        )

    return sorted_grouped_files


def check_gpu():
    # Check GPU availability and details
    if torch.cuda.is_available():
        gpu_info = {"gpu": True, "device": torch.cuda.get_device_name(0)}
    else:
        gpu_info = {"gpu": False, "message": "No GPU available, using CPU"}

    # Check CPU information
    cpu_info = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_logical_cores": psutil.cpu_count(logical=True),
    }

    # Check Memory information
    memory_info = psutil.virtual_memory()
    memory_usage = {
        "total_memory": memory_info.total / (1024**3),
        "used_memory": memory_info.used / (1024**3),
        "free_memory": memory_info.available / (1024**3),
        "memory_percent": memory_info.percent,
    }

    return {"gpu": gpu_info, "cpu": cpu_info, "memory": memory_usage}


def save_geojson(json_data, output_geojson_path):
    try:
        with open(output_geojson_path, "w", encoding="utf-8") as geojson_file:
            json.dump(json_data, geojson_file, ensure_ascii=False, indent=4)
        logger.info(f"GeoJSON data successfully saved to {output_geojson_path}")
    except Exception as e:
        logger.error(f"Failed to save GeoJSON data: {e}")
        raise e


def generate_geojson(gpkg_file_path, output_geojson_path):
    try:
        logging.info(f"Converting segmentation results to GeoJSON at {output_geojson_path}")
        gdf = gpd.read_file(gpkg_file_path)
        gdf_wgs84 = gdf.to_crs(epsg=4326)
        gdf_wgs84["geometry"] = gdf_wgs84["geometry"].apply(
            lambda geom: (
                geom
                if isinstance(geom, Polygon)
                else geom.convex_hull if isinstance(geom, MultiPolygon) else geom
            )
        )
        gdf_wgs84.to_file(output_geojson_path, driver="GeoJSON")
        geojson_data = json.loads(gdf_wgs84.to_json())
        return geojson_data

    except Exception as e:
        logging.error(f"Error generating GeoJSON: {e}")
        return None


def download_tif_if_not_exists(bbox, zoom, project, id, output_dir="public"):
    """
    Downloads a TIFF image using tms_to_geotiff if it doesn't already exist.
    """

    output_image_name = f"{project}/{id}_a.tif"
    output_image_path = os.path.join(output_dir, output_image_name)

    print(output_image_path)
    if os.path.exists(output_image_path):
        logging.info(f"Satellite image already exists at: {output_image_path}. Skipping download.")
    else:
        logging.info(f"Downloading satellite imagery for bbox: {bbox} at zoom level: {zoom}")
        tms_to_geotiff(
            output=output_image_path, bbox=bbox, zoom=int(zoom), source="Satellite", overwrite=True
        )

    return output_image_path
