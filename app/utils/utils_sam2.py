import os
from samgeo import SamGeo2
import geopandas as gpd
import logging
import json
import torch
from utils.utils import (
    generate_geojson,
    download_tif_if_not_exists,
    logger,
    save_geojson,
    date_minute_str,
)
from schemas import SegmentRequest

# Initialize the SAM model
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")
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
    Function to handle object detection for all objects.
    """
    date_time = date_minute_str()
    tif_file_name = f"{id}.tif"
    mask_file_name = f"tmp/mask_{id}.tif"
    geojson_file_name = f"{id}_{date_time}.geojson"
    gpkg_file_name = f"{id}_{date_time}.gpkg"
    public_dir = f"public/{project}"
    tif_file_path = os.path.join(public_dir, tif_file_name)
    mask_file_path = mask_file_name
    geojson_file_path = os.path.join(public_dir, geojson_file_name)
    gpkg_file_path = os.path.join(public_dir, gpkg_file_name)

    try:
        # Download or reuse TIFF
        logger.info(
            f"Processing detection for bbox: {bbox}, zoom: {zoom}, id: {id}, project: {project}"
        )
        sam2.generate(tif_file_path, output=mask_file_path)
        sam2.raster_to_vector(mask_file_path, gpkg_file_path)
        geojson_data = generate_geojson(gpkg_file_path, geojson_file_path)
    except Exception as e:
        logger.error(f"An error occurred during processing: {e}")
        return {"error": str(e)}
    return geojson_data


def detect_predictor_sam2(request: SegmentRequest):
    """
    Function to handle segmentation based on point input prompts.
    The entire request object is passed and used.
    """
    # Extract required fields from the request
    bbox = request.bbox
    zoom = int(request.zoom)
    point_coords = request.point_coords
    point_labels = request.point_labels
    id = request.id
    project = request.project
    action_type = request.action_type

    logger.info(
        f"Processing segmentation for bbox: {bbox}, zoom: {zoom}, id: {id}, project: {project}, action_type: {action_type}"
    )

    date_time = date_minute_str()
    tif_file_name = f"{id}.tif"
    mask_file_name = f"tmp/mask_{id}.tif"
    geojson_file_name = f"{id}_{date_time}.geojson"
    gpkg_file_name = f"{id}_{date_time}.gpkg"
    public_dir = f"public/{project}"
    tif_file_path = os.path.join(public_dir, tif_file_name)
    mask_file_path = mask_file_name
    geojson_file_path = os.path.join(public_dir, geojson_file_name)
    gpkg_file_path = os.path.join(public_dir, gpkg_file_name)

    geojson_data = {}

    try:
        sam2Predictor.set_image(tif_file_path)

        if action_type == "single_point":
            logger.info(f"Predicting single point for id: {id}")
            sam2Predictor.predict(
                point_coords,
                point_labels=point_labels,
                point_crs="EPSG:4326",
                output=mask_file_path,
            )
            sam2.raster_to_vector(mask_file_path, gpkg_file_path)
            geojson_data = generate_geojson(gpkg_file_path, geojson_file_path)

        elif action_type == "multi_point":
            geojson_array = []
            for index, p_coords in enumerate(point_coords):
                logger.info(f"Processing multi-point {p_coords} for id: {id}, point index: {index}")
                mask_file_path_tmp = f"tmp/mask_{id}_{index}.tif"
                gpkg_file_path_tmp = f"tmp/{id}_{index}.gpkg"
                geojson_file_path_tmp = f"tmp/{id}_{index}.geojson"
                sam2Predictor.predict(
                    [p_coords], point_labels=1, point_crs="EPSG:4326", output=mask_file_path_tmp
                )
                sam2.raster_to_vector(mask_file_path_tmp, gpkg_file_path_tmp)
                geojson_data = generate_geojson(gpkg_file_path_tmp, geojson_file_path_tmp)
                for feat in geojson_data["features"]:
                    geojson_array.append(feat)
            geojson_data["features"] = geojson_array
            save_geojson(geojson_data, geojson_file_path)
    except Exception as e:
        logger.error(f"An error occurred during point-based segmentation: {e}")
        return {"error": str(e)}
    return geojson_data
