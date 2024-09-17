import os
from samgeo import SamGeo, tms_to_geotiff
import geopandas as gpd
import logging
import json
import torch
from utils import generate_geojson, download_tif_if_not_exists

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


def detect_segment_objects(bbox, zoom, id, project):
    """
    Function to handle object detect all objects
    """
    bbox_str = f"{bbox[0]:.6f}_{bbox[1]:.6f}_{bbox[2]:.6f}_{bbox[3]:.6f}".replace(",", "_")
    project_str = project.replace(" ", "_")
    zoom_str = f"{int(zoom)}"

    mask_file_name = f"mask_{bbox_str}_zoom{zoom_str}_{project_str}.tif"
    geojson_file_name = f"segment_{bbox_str}_zoom{zoom_str}_{project_str}.geojson"
    gpkg_file_name = f"segment_{bbox_str}_zoom{zoom_str}_{project_str}.gpkg"

    public_dir = "public"
    mask_file_path = os.path.join(public_dir, mask_file_name)
    geojson_file_path = os.path.join(public_dir, geojson_file_name)
    gpkg_file_path = os.path.join(public_dir, gpkg_file_name)

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
        sam.tiff_to_gpkg(mask_file_path, gpkg_file_path, simplify_tolerance=None)
        geojson_data = generate_geojson(gpkg_file_path, geojson_file_path)

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
    gpkg_file_name = f"segment_{bbox_str}_zoom{zoom_str}_{project_str}.gpkg"

    public_dir = "public"
    mask_file_path = os.path.join(public_dir, mask_file_name)
    geojson_file_path = os.path.join(public_dir, geojson_file_name)
    gpkg_file_path = os.path.join(public_dir, gpkg_file_name)

    try:
        output_image_path = download_tif_if_not_exists(bbox, zoom, project)
        logging.info(
            f"Segmenting image based on point inputs at {output_image_path} for project {project} with ID {id}"
        )
        samPredictor.set_image(output_image_path)
        samPredictor.predict(
            point_coords, point_labels=point_labels, point_crs="EPSG:4326", output=mask_file_path
        )
        sam.tiff_to_gpkg(mask_file_path, gpkg_file_path, simplify_tolerance=None)
        geojson_data = generate_geojson(gpkg_file_path, geojson_file_path)

    except Exception as e:
        logging.error(f"An error occurred during point-based segmentation: {e}")
        return {"error": str(e)}

    return {
        "geojson": geojson_data,
        "image_path": output_image_path,
        "mask_path": mask_file_path,
        "geojson_path": geojson_file_path,
    }
