import os
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

def calculate_ndvi(red_band, green_band):
    ndvi = (green_band - red_band) / (green_band + red_band)
    return ndvi

def apply_colormap(ndvi_array):
    colors = [(0.7, 0, 0), (1, 0.5, 0), (1, 1, 0), (0.5, 1, 0.5), (0, 0.8, 0)]
    cmap = LinearSegmentedColormap.from_list("dry_to_green", colors, N=256)
    norm = plt.Normalize(vmin=-1, vmax=1)
    colored_ndvi = cmap(norm(ndvi_array))
    return (colored_ndvi[:, :, :3] * 255).astype(np.uint8)

def blend_with_original(colored_ndvi, original_rgb, alpha=0.6):
    blended_image = (alpha * colored_ndvi + (1 - alpha) * original_rgb).astype(np.uint8)
    return blended_image

def process_image(image_path):
    output_path = image_path.replace('.tiff', '_ndvi_blended.tiff')
    with rasterio.open(image_path) as src:
        red = src.read(1).astype(float)
        green = src.read(2).astype(float)
        original_rgb = np.stack([src.read(i).astype(float) for i in range(1, 4)], axis=-1)

    ndvi = calculate_ndvi(red, green)
    colored_ndvi = apply_colormap(ndvi)
    blended_image = blend_with_original(colored_ndvi, original_rgb)
    meta = src.meta.copy()
    meta.update(dtype=rasterio.uint8, count=3, photometric='RGB')
    with rasterio.open(output_path, 'w', **meta) as dst:
        for i in range(3):
            dst.write(blended_image[:, :, i], i + 1)

    print(f"NDVI blended with original saved to {output_path}")

def main(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            image_path = os.path.join(directory, filename)
            process_image(image_path)

if __name__ == "__main__":
    directory = '/data/drive'
    main(directory)
