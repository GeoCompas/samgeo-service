# SAMGEO API

The **SAMGEO API** is an API service designed to facilitate interactions with SAM2 module. This service allows you to interact with SAM functionalities through simple API requests. Learn more at [SAMGEO](https://samgeo.gishub.org/).

## Build and Run the Container

To build and run the SAMGEO service container with GPU support, follow these steps:

1. **Build the Docker container:**

   ```sh
   docker build -t samgeo-service .
   ```

2. **Run the container with GPU support:**

   ```sh
   docker run -d --gpus all --env-file .env.example -v $(pwd)/app:/app -p 80:80 samgeo-service
   ```

   - The container is started in detached mode (`-d`).
   - GPU support is enabled using `--gpus all`.
   - Environment variables are loaded from the `.env.example` file.
   - The application code is mounted from your current directory (`$(pwd)/app`) to the `/app` directory in the container.
   - The API is exposed on port 80 (`-p 80:80`).


**Note:** The above steps are used for development mode. In case you are running in production, it is highly recommended to use Kubernetes. For more details, refer to [ds-k8s-gpu](https://github.com/developmentseed/ds-k8s-gpu).

## References

This project is based on the [Segment Anything Services](https://github.com/developmentseed/segment-anything-services) repository from Development Seed.




# Frontend

There are currently two user interfaces/frontends that support the API:

1. **Web Interface:** [ds-annotate](https://github.com/developmentseed/ds-annotate) - https://developmentseed.org/ds-annotate
2. **JOSM Plugin:** [JosmMagicWand](https://github.com/developmentseed/JosmMagicWand)

