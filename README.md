# SAMGEO API

This application is an API service for SAMGEO, utilizing SAM and SAM2. It enables interaction with the SAM modules through API requests  https://samgeo.gishub.org/

## Build and run the container

```sh
docker build -t samgeo-service .
docker run --gpus all --env-file .env.example -v $(pwd)/app:/app -p 80:80 samgeo-service
```
sudo docker build -t samgeo-service .
docker run -d --gpus all --env-file .env.example -v $(pwd)/app:/app -p 80:80 samgeo-service


## Example to request SAM endpoints

- Segment the image


```sh
curl -X POST "http://127.0.0.1:80/sam/segment_automatic" \
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
curl -X POST "http://127.0.0.1:80/sam/segment_predictor" \
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


## Example to request SAM2 endpoints

- Automatic


```sh
curl -X POST "http://127.0.0.1:80/sam2/segment_automatic" \
-H "Content-Type: application/json" \
-d '{
  "bbox": [-74.224144, -13.150200, -74.216339, -13.145901],
  "crs": "EPSG:4326",
  "zoom": 18,
  "id": "7069",
  "project": "sam2"
}'
```


- Predictor


```sh
curl -X POST "http://127.0.0.1:80/sam2/segment_predictor" \
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