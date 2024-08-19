import os
import rasterio
import pandas as pd
image_dir = '/data/drive/'
image_info_list = []
for filename in os.listdir(image_dir):
    if filename.endswith('.tiff') or filename.endswith('.tif'):
        file_path = os.path.join(image_dir, filename)
        with rasterio.open(file_path) as src:
            info = {
                'filename': filename,
                'width': src.width,
                'height': src.height,
                'crs': src.crs,
                'transform': src.transform,
                'count': src.count,
                'driver': src.driver,
                'colorinterp': [str(src.colorinterp[i]) for i in range(src.count)]
            }
            image_info_list.append(info)
df = pd.DataFrame(image_info_list)
df['colorinterp'] = df['colorinterp'].apply(lambda x: ', '.join(x))
csv_output_path = '/data/image_info.csv'
df.to_csv(csv_output_path, index=False)
print(f"Saved to {csv_output_path}")
