import os
import time
import torch
import logging
import geopandas as gpd
import json
import psutil
from datetime import datetime
from samgeo import tms_to_geotiff
from shapely.geometry import Polygon, MultiPolygon
from utils.logger_config import log


def group_files_by_base_name(public_dir: str, base_url: str) -> list:
    """
    Groups files in the specified directory by their base name and modification time.

    Args:
        public_dir (str): The path to the directory containing the files.
        base_url (str): The base URL used to generate file URLs.

    Returns:
        list: A list of dictionaries, each containing the base name, files, and modification time.
    """
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
    """
    Checks if a GPU is available on the system and returns CPU and memory information.

    Returns:
        dict: A dictionary containing GPU, CPU, and memory information.
    """
    if torch.cuda.is_available():
        gpu_info = {"gpu": True, "device": torch.cuda.get_device_name(0)}
    else:
        gpu_info = {"gpu": False, "message": "No GPU available, using CPU"}

    cpu_info = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(logical=False),
        "cpu_logical_cores": psutil.cpu_count(logical=True),
    }

    memory_info = psutil.virtual_memory()
    memory_usage = {
        "total_memory": memory_info.total / (1024**3),
        "used_memory": memory_info.used / (1024**3),
        "free_memory": memory_info.available / (1024**3),
        "memory_percent": memory_info.percent,
    }

    return {"gpu": gpu_info, "cpu": cpu_info, "memory": memory_usage}


def save_geojson(json_data, output_geojson_path):
    """
    Saves the provided JSON data as a GeoJSON file at the specified path.

    Args:
        json_data (dict): The JSON data to be saved.
        output_geojson_path (str): The file path where the GeoJSON will be saved.

    Raises:
        Exception: If an error occurs while saving the GeoJSON file.
    """
    try:
        with open(output_geojson_path, "w", encoding="utf-8") as geojson_file:
            json.dump(json_data, geojson_file, ensure_ascii=False, indent=4)
        log.info(f"GeoJSON data successfully saved to {output_geojson_path}")
    except Exception as e:
        log.error(f"Failed to save GeoJSON data: {e}")
        raise e


def generate_geojson(gpkg_file_path, output_geojson_path):
    """
    Converts a GeoPackage file to GeoJSON format and saves it at the specified path.

    Args:
        gpkg_file_path (str): The path to the GeoPackage file.
        output_geojson_path (str): The path where the GeoJSON will be saved.

    Returns:
        dict: The generated GeoJSON data.

    Raises:
        Exception: If an error occurs during GeoJSON generation.
    """
    try:
        log.info(f"Converting segmentation results to GeoJSON at {output_geojson_path}")
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
        log.error(f"Error generating GeoJSON: {e}")
        return None


def download_tif_if_not_exists(bbox, zoom, project, id, output_dir="public"):
    """
    Downloads a TIFF image using tms_to_geotiff if it doesn't already exist.

    Args:
        bbox (list): The bounding box for the image.
        zoom (int): The zoom level for the image.
        project (str): The project name.
        id (str): The unique identifier for the image.
        output_dir (str): The directory where the image will be saved. Defaults to "public".

    Returns:
        str: The path to the downloaded or existing TIFF image.
    """
    output_image_name = f"{project}/{id}_a.tif"
    output_image_path = os.path.join(output_dir, output_image_name)
    if os.path.exists(output_image_path):
        log.info(f"Satellite image already exists at: {output_image_path}. Skipping download.")
    else:
        log.info(f"Downloading satellite imagery for bbox: {bbox} at zoom level: {zoom}")
        tms_to_geotiff(
            output=output_image_path, bbox=bbox, zoom=int(zoom), source="Satellite", overwrite=True
        )

    return output_image_path


def date_minute_str():
    """
    Returns the current date and time in the format YYYYMMDD_HHMM.

    Returns:
        str: The current date and time formatted as YYYYMMDD_HHMM.
    """
    return datetime.now().strftime("%Y%m%d_%H%M")
