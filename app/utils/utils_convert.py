import rasterio
from rasterio.transform import from_bounds
from PIL import Image
import numpy as np
import os
from typing import List


def convert_image_to_geotiff(image_filename: str, tif_filename: str, bbox: List[float]):
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
            dst.write(image_array[:, :, 0], 1)  # Red channel
            dst.write(image_array[:, :, 1], 2)  # Green channel
            dst.write(image_array[:, :, 2], 3)  # Blue channel

        print(f"Converted {image_filename} to {tif_filename} with bbox: {bbox}")
        return tif_filename

    except Exception as e:
        print(f"Error converting image to GeoTIFF: {str(e)}")
        raise
