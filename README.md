# SAMGEO API

This application is an API service for SAMGEO, utilizing SAM and SAM2. It enables interaction with the SAM modules through API requests  https://samgeo.gishub.org/

## Build and run the container

```sh
docker build -t samgeo-service .
docker run -d --gpus all --env-file .env.example -v $(pwd)/app:/app -p 80:80 samgeo-service
```

Base in https://github.com/developmentseed/segment-anything-services