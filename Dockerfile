FROM giswqs/segment-geospatial:latest

USER root
RUN apt-get update && apt-get install -y libgl1-mesa-glx libegl1-mesa libgles2-mesa libopengl0
WORKDIR /app
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY ./app /app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]