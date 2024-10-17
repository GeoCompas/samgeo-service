import os
from samgeo import SamGeo2, choose_device
import torch
from utils.utils import (
    generate_geojson,
    save_geojson,
    get_timestamp,
)
from schemas.segment import SegmentRequestBase, SegmentResponseBase
from utils.logger_config import log
from utils.utils import base_files_names

# Initialize the SAM model
device = choose_device()
log.info(f"Using device: {device}")
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


def detect_automatic_sam2(request):
    """
    Detect objects automatically using SAM2 model based on the provided bounding box.
    """

    bbox = request.bbox
    zoom = int(request.zoom)
    id = request.id
    project = request.project
    return_format = request.return_format

    (
        _,
        _,
        tif_file_path,
        mask_file_path,
        geojson_file_path,
        gpkg_file_path,
        _,
        _,
        geojson_file_url,
    ) = base_files_names(project, id)

    try:
        log.info(
            f"Processing detection for bbox: {bbox}, zoom: {zoom}, id: {id}, project: {project}"
        )

        # Run SAM2 model and convert raster to vector
        sam2.generate(tif_file_path, output=mask_file_path)
        sam2.raster_to_vector(mask_file_path, gpkg_file_path)

        geojson_data = generate_geojson(gpkg_file_path, geojson_file_path)

        # Return response based on the requested format
        if return_format == "geojson":
            return SegmentResponseBase(**geojson_data)
        elif return_format == "url":
            return {"geojson_url": geojson_file_url}

    except Exception as e:
        log.error(f"An error occurred during processing: {e}")
        return {"error": str(e)}


def detect_predictor_sam2(request: SegmentRequestBase) -> SegmentResponseBase:
    """
    Handle segmentation based on point input prompts using SAM2 model.
    """

    bbox = request.bbox
    zoom = int(request.zoom)
    point_coords = request.point_coords
    point_labels = request.point_labels
    id = request.id
    project = request.project
    action_type = request.action_type
    return_format = request.return_format

    (
        _,
        _,
        tif_file_path,
        mask_file_path,
        geojson_file_path,
        gpkg_file_path,
        _,
        _,
        geojson_file_url,
    ) = base_files_names(project, id)

    geojson_data = {}

    try:
        sam2Predictor.set_image(tif_file_path)

        # Process single point
        if action_type == "single_point":
            log.info(
                f"Predicting single point for id: {id}, project: {project}, bbox: {bbox}, zoom: {zoom}"
            )
            sam2Predictor.predict(
                point_coords,
                point_labels=point_labels,
                point_crs="EPSG:4326",
                output=mask_file_path,
            )
            # Convert raster to vector and generate GeoJSON
            sam2.raster_to_vector(mask_file_path, gpkg_file_path)
            geojson_data = generate_geojson(gpkg_file_path, geojson_file_path)

        # Process multiple points
        elif action_type == "multi_point":
            geojson_array = []
            for index, p_coords in enumerate(point_coords):
                log.info(
                    f"Processing multi-point {p_coords} for id: {id}, project: {project}, point index: {index}"
                )

                # Temporary file paths for each point
                mask_file_path_tmp = f"tmp/mask_{id}_{index}.tif"
                gpkg_file_path_tmp = f"tmp/{id}_{index}.gpkg"
                geojson_file_path_tmp = f"tmp/{id}_{index}.geojson"

                sam2Predictor.predict(
                    [p_coords], point_labels=1, point_crs="EPSG:4326", output=mask_file_path_tmp
                )

                # Convert raster to vector and generate GeoJSON
                sam2.raster_to_vector(mask_file_path_tmp, gpkg_file_path_tmp)
                geojson_ = generate_geojson(gpkg_file_path_tmp, geojson_file_path_tmp)

                for feat in geojson_["features"]:
                    geojson_array.append(feat)

            geojson_data["features"] = geojson_array
            save_geojson(geojson_data, geojson_file_path)

        log.info(f"geojson_url: {geojson_file_url}")

        # Return response based on the requested format
        if return_format == "geojson":
            return SegmentResponseBase(**geojson_data)
        elif return_format == "url":
            return {"geojson_url": geojson_file_url}

    except Exception as e:
        log.error(
            f"An error occurred during point-based segmentation for id: {id}, project: {project}: {e}"
        )
        return {"error": str(e)}
