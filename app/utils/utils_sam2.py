import os
from samgeo import SamGeo2
import geopandas as gpd
import logging
import json
import torch
from utils.utils import generate_geojson, download_tif_if_not_exists

# Initialize the SAM model
device = "cuda" if torch.cuda.is_available() else "cpu"

sam2 = SamGeo2(
    model_id="sam2-hiera-large",
    device=device,
    apply_postprocessing=False,
    points_per_side=32,
    points_per_batch=64,
    pred_iou_thresh=0.7,
    stability_score_thresh=0.92,
    stability_score_offset=0.7,
    crop_n_layers=1,
    box_nms_thresh=0.7,
    crop_n_points_downscale_factor=2,
    min_mask_region_area=25.0,
    use_m2m=True,
)

sam2Predictor = SamGeo2(
    model_id="sam2-hiera-large",
    device=device,
    automatic=False,
)


def detect_automatic_sam2(bbox, zoom, id, project):
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
        sam2.generate(output_image_path, output=mask_file_path)
        sam2.raster_to_vector(mask_file_path, gpkg_file_path)
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


def detect_predictor_sam2(bbox, zoom, point_coords, point_labels, id, project):
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
        sam2Predictor.set_image(output_image_path)
        sam2Predictor.predict(
            point_coords, point_labels=point_labels, point_crs="EPSG:4326", output=mask_file_path
        )
        sam2.raster_to_vector(mask_file_path, gpkg_file_path)
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
