import os
import time
import torch
import logging
import geopandas as gpd
import json
from fastapi import FastAPI


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
    if torch.cuda.is_available():
        return {"gpu": True, "device": torch.cuda.get_device_name(0)}
    else:
        return {"gpu": False, "message": "No GPU available, using CPU"}


def generate_geojson(gpkg_file_path, output_geojson_path):
    try:
        logging.info(f"Converting segmentation results to GeoJSON at {output_geojson_path}")
        gdf = gpd.read_file(gpkg_file_path)
        gdf_wgs84 = gdf.to_crs(epsg=4326)
        gdf_wgs84.to_file(output_geojson_path, driver="GeoJSON")
        geojson_data = json.loads(gdf_wgs84.to_json())
        return geojson_data
    except Exception as e:
        logging.error(f"Error generating GeoJSON: {e}")
        return None


def download_tif_if_not_exists(bbox, zoom, project, output_dir="public"):
    """
    Downloads a TIFF image using tms_to_geotiff if it doesn't already exist.
    """
    bbox_str = f"{bbox[0]:.6f}_{bbox[1]:.6f}_{bbox[2]:.6f}_{bbox[3]:.6f}".replace(",", "_")
    project_str = project.replace(" ", "_")
    zoom_str = f"{int(zoom)}"

    output_image_name = f"satellite_image_{bbox_str}_zoom{zoom_str}_{project_str}.tif"
    output_image_path = os.path.join(output_dir, output_image_name)

    if os.path.exists(output_image_path):
        logging.info(f"Satellite image already exists at: {output_image_path}. Skipping download.")
    else:
        logging.info(f"Downloading satellite imagery for bbox: {bbox} at zoom level: {zoom}")
        tms_to_geotiff(
            output=output_image_path, bbox=bbox, zoom=int(zoom), source="Satellite", overwrite=True
        )

    return output_image_path
