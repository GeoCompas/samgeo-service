import rasterio
from rasterio.transform import from_bounds
from PIL import Image
import numpy as np
import os
import geopandas as gpd
import json
from shapely.geometry import shape
from typing import List,Optional,Dict
from utils.logger_config import log


def convert_image_to_geotiff(image_filename: str, tif_filename: str, bbox: List[float]):
    """
    Converts an image file to a GeoTIFF format using the provided bounding box (bbox).

    Args:
        image_filename (str): Path to the input image file.
        tif_filename (str): Path to save the output GeoTIFF file.
        bbox (List[float]): Bounding box for the GeoTIFF in the format [minx, miny, maxx, maxy].

    Returns:
        str: The path to the generated GeoTIFF file.

    Raises:
        Exception: If an error occurs during the conversion process.
    """
    try:
        image = Image.open(image_filename)
        image = image.convert("RGB")
        image_array = np.array(image)
        height, width = image_array.shape[:2]
        minx, miny, maxx, maxy = bbox
        transform = from_bounds(minx, miny, maxx, maxy, width, height)
        os.makedirs(os.path.dirname(tif_filename), exist_ok=True)

        with rasterio.open(
            tif_filename,
            "w",
            driver="GTiff",
            height=height,
            width=width,
            count=3,
            dtype=image_array.dtype,
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(image_array[:, :, 0], 1)
            dst.write(image_array[:, :, 1], 2)
            dst.write(image_array[:, :, 2], 3)

        log.info(f"Converted {image_filename} to {tif_filename} with bbox: {bbox}")
        return tif_filename

    except Exception as e:
        log.error(f"Error converting image to GeoTIFF: {str(e)}", exc_info=True)
        raise


def read_simplify_and_filter_by_area(gpkg_file_path: Optional[str] = None, 
                                     geojson_obj: Optional[dict] = None, 
                                     simplify_tolerance: float = 0, 
                                     area_val: float = 0, 
                                     geojson_file_path: Optional[str] = None) -> Dict:
    
    if gpkg_file_path:
        log.info(f"Reading GeoPackage from {gpkg_file_path}.")
        gdf = gpd.read_file(gpkg_file_path)
    elif geojson_obj:
        log.info("Reading GeoJSON object.")
        gdf = gpd.GeoDataFrame.from_features(geojson_obj["features"])
    else:
        raise ValueError("Either 'gpkg_file_path' or 'geojson_obj' must be provided.")
    
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326)
    
    if simplify_tolerance > 0:
        log.info(f"Simplifying geometries with tolerance {simplify_tolerance}.")
        gdf['geometry'] = gdf['geometry'].simplify(simplify_tolerance, preserve_topology=True)
    
    gdf_projected = gdf.to_crs(epsg=3395)
    
    gdf_projected['area_m2'] = gdf_projected['geometry'].area
    
    if area_val > 0:
        log.info(f"Filtering geometries with area greater than {area_val} m².")
        gdf_filtered = gdf_projected[gdf_projected['area_m2'] > area_val]
    else:
        gdf_filtered = gdf_projected
    
    gdf_filtered = gdf_filtered.to_crs(epsg=4326)
    
    geojson_result = json.loads(gdf_filtered.to_json())
    
    if geojson_file_path:
        log.info(f"Saving the result as GeoJSON to {geojson_file_path}.")
        gdf_filtered.to_file(geojson_file_path, driver="GeoJSON")
        
    return geojson_result
