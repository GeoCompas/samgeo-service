import os
from samgeo import SamGeo, tms_to_geotiff
import geopandas as gpd
import logging
import json
import torch

# Initialize the SAM model
device = "cuda" if torch.cuda.is_available() else "cpu"
sam = SamGeo(
    checkpoint="sam_vit_h_4b8939.pth",
    model_type="vit_h",
    device=device,
    erosion_kernel=(3, 3),
    mask_multiplier=255,
    sam_kwargs=None,
)

samPredictor = SamGeo(
    model_type="vit_h",
    automatic=False,
    sam_kwargs=None,
)


def check_gpu():
    if torch.cuda.is_available():
        return {"gpu": True, "device": torch.cuda.get_device_name(0)}
    else:
        return {"gpu": False, "message": "No GPU available, using CPU"}


def generate_geojson(mask_file_path, output_geojson_path):
    """
    Function to generate a GeoJSON file from a TIFF mask.
    """
    try:
        logging.info(f"Converting segmentation results to GeoJSON at {output_geojson_path}")
        # TODO , change with uid temp file
        sam.tiff_to_gpkg(mask_file_path, "temp.gpkg", simplify_tolerance=None)
        gdf = gpd.read_file("temp.gpkg")
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


def detect_segment_objects(bbox, zoom, id, project):
    """
    Function to handle object detect all objects
    """
    bbox_str = f"{bbox[0]:.6f}_{bbox[1]:.6f}_{bbox[2]:.6f}_{bbox[3]:.6f}".replace(",", "_")
    project_str = project.replace(" ", "_")
    zoom_str = f"{int(zoom)}"

    mask_file_name = f"mask_{bbox_str}_zoom{zoom_str}_{project_str}.tif"
    geojson_file_name = f"segment_{bbox_str}_zoom{zoom_str}_{project_str}.geojson"

    public_dir = "public"
    mask_file_path = os.path.join(public_dir, mask_file_name)
    geojson_file_path = os.path.join(public_dir, geojson_file_name)

    try:
        # Download or reuse TIFF
        output_image_path = download_tif_if_not_exists(bbox, zoom, project)

        logging.info(f"Segmenting the image using SAM for project {project} with ID {id}")
        sam.generate(
            output_image_path,
            mask_file_path,
            batch=True,
            foreground=True,
            erosion_kernel=(3, 3),
            mask_multiplier=255,
        )

        geojson_data = generate_geojson(mask_file_path, geojson_file_path)

    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")
        return {"error": str(e)}

    return {
        "geojson": geojson_data,
        "image_path": output_image_path,
        "mask_path": mask_file_path,
        "geojson_path": geojson_file_path,
    }


def detect_segment_point_input_prompts(bbox, zoom, point_coords, point_labels, id, project):
    """
    Function to handle segmentation based on point input prompts.
    """
    bbox_str = f"{bbox[0]:.6f}_{bbox[1]:.6f}_{bbox[2]:.6f}_{bbox[3]:.6f}".replace(",", "_")
    project_str = project.replace(" ", "_")
    zoom_str = f"{int(zoom)}"

    mask_file_name = f"mask_{bbox_str}_zoom{zoom_str}_points_{project_str}.tif"
    geojson_file_name = f"segment_{bbox_str}_zoom{zoom_str}_points_{project_str}.geojson"

    public_dir = "public"
    mask_file_path = os.path.join(public_dir, mask_file_name)
    geojson_file_path = os.path.join(public_dir, geojson_file_name)

    try:

        # Download or reuse TIFF
        output_image_path = download_tif_if_not_exists(bbox, zoom, project)

        logging.info(
            f"Segmenting image based on point inputs at {output_image_path} for project {project} with ID {id}"
        )
        samPredictor.set_image(output_image_path)
        samPredictor.predict(
            point_coords, point_labels=point_labels, point_crs="EPSG:4326", output=mask_file_path
        )

        geojson_data = generate_geojson(mask_file_path, geojson_file_path)

    except Exception as e:
        logging.error(f"An error occurred during point-based segmentation: {e}")
        return {"error": str(e)}

    return {
        "geojson": geojson_data,
        "image_path": output_image_path,
        "mask_path": mask_file_path,
        "geojson_path": geojson_file_path,
    }
