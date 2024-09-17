# SAMGEO API

This app is base on https://samgeo.gishub.org/

## Run using docker

```sh
docker build -t samgeo-service .
docker run --gpus all -v $(pwd)/app:/app -p 8000:8000 samgeo-service
```


## Testing the edpoints

- Segment the image


```sh
curl -X POST "http://100.27.252.176:8000/sam/segment" \
-H "Content-Type: application/json" \
-d '{
  "bbox": [-74.224144, -13.150200, -74.216339, -13.145901],
  "crs": "EPSG:4326",
  "zoom": 18,
  "id": "7069",
  "project": "Farms - Sentinel2"
}'
```

- Segment the image with coords input prompts

```sh
curl -X POST "http://100.27.252.176:8000/sam/segment_points_prompts" \
-H "Content-Type: application/json" \
-d '{
  "bbox": [-74.224144, -13.150200, -74.216339, -13.145901],
  "point_labels": [1,1,1,0,0],
  "point_coords": [[-74.219279, -13.148008], [-74.218833, -13.147298], [-74.219690, -13.147226], [-74.219716, -13.147771], [-74.218953, -13.148197]],
  "crs": "EPSG:4326",
  "zoom": 18,
  "id": "222",
  "project": "point-points"
}'
```