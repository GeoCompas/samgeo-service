import os
from samgeo import SamGeo, tms_to_geotiff
import geopandas as gpd
import logging
import json
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
sam = SamGeo(
    checkpoint="sam_vit_h_4b8939.pth",
    model_type='vit_h',
    device=device,
    erosion_kernel=(3, 3),
    mask_multiplier=255,
    sam_kwargs=None,
)

def check_gpu():
    if torch.cuda.is_available():
        device = torch.device("cuda")
        return {"gpu": True, "device": torch.cuda.get_device_name(0)}
    else:
        return {"gpu": False, "message": "No GPU available, using CPU"}


def detect_all_objects(
    bbox, zoom, id, project
):
    """
    Function to handle object detection based on the provided parameters.
    """
    bbox_str = f"{bbox[0]:.6f}_{bbox[1]:.6f}_{bbox[2]:.6f}_{bbox[3]:.6f}".replace(',', '_')
    project_str = project.replace(" ", "_")
    zoom_str = f"{int(zoom)}"

    # Create unique names for the output files using bbox, zoom, and project
    mask_file_name = f"mask_{bbox_str}_zoom{zoom_str}_{project_str}.tif"
    output_image_name = f"satellite_image_{bbox_str}_zoom{zoom_str}_{project_str}.tif"
    gpkg_file_name = f"segment_{bbox_str}_zoom{zoom_str}_{project_str}.gpkg"
    geojson_file_name = f"segment_{bbox_str}_zoom{zoom_str}_{project_str}.geojson"

    public_dir = "public"
    output_image_path = os.path.join(public_dir, output_image_name)
    mask_file_path = os.path.join(public_dir, mask_file_name)
    gpkg_file_path = os.path.join(public_dir, gpkg_file_name)
    geojson_file_path = os.path.join(public_dir, geojson_file_name)

    logging.info(f"Output Image Path: {output_image_path}")
    logging.info(f"Mask File Path: {mask_file_path}")
    logging.info(f"GeoPackage File Path: {gpkg_file_path}")
    logging.info(f"Geojson File Path: {geojson_file_path}")

    try:
        # Check if the satellite image already exists
        if not os.path.exists(output_image_path):
            logging.info(f"Downloading satellite imagery for bbox: {bbox} at zoom level: {zoom}")
            tms_to_geotiff(output=output_image_path, bbox=bbox, zoom=int(zoom), source="Satellite", overwrite=True)
        else:
            logging.info(f"Satellite image already exists at: {output_image_path}. Skipping download.")

        # Segment the image and save it with the dynamic mask file name
        logging.info(f"Segmenting the image using SAM for project {project} with ID {id}")
        sam.generate(output_image_path, mask_file_path, batch=True, foreground=True, erosion_kernel=(3, 3), mask_multiplier=255)

        logging.info(f"Converting segmentation results to GeoPackage")
        sam.tiff_to_gpkg(mask_file_path, gpkg_file_path, simplify_tolerance=None)
        gdf = gpd.read_file(gpkg_file_path)

        gdf_wgs84 = gdf.to_crs(epsg=4326)
        gdf_wgs84.to_file(geojson_file_path, driver='GeoJSON')
        geojson_data = json.loads(gdf_wgs84.to_json())

    except Exception as e:
        logging.error(f"An error occurred during processing: {e}")
        return {"error": str(e)}

    return {
        "geojson": geojson_data,
        "image_path": output_image_path,
        "mask_path": mask_file_path,
        "geojson_path": geojson_file_path
    }

