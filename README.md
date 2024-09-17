# SAM API

base in https://samgeo.gishub.org/

## Run using docker
```sh
docker stop samgeo-service
docker rm  samgeo-service
docker build -t samgeo-service .
docker run --gpus all -v $(pwd)/app:/app --name samgeo-service -p 8000:8000 samgeo-service
```