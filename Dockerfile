FROM nvidia/cuda:12.2.0-runtime-ubuntu20.04
USER root
RUN apt-get update && apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3.9-distutils \
    wget \
    libgl1-mesa-glx \
    libegl1-mesa \
    libgles2-mesa \
    libopengl0 && \
    rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y gdal-bin libgdal-dev && \
    rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN wget https://bootstrap.pypa.io/get-pip.py && python3.9 get-pip.py
RUN pip3.9 install --no-cache-dir --root-user-action=ignore torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip3.9 install numpy=<2.0
RUN pip3.9 install --no-cache-dir GDALWORKDIR /app

COPY ./app/requirements.txt /app/requirements.txt
RUN pip3.9 install --no-cache-dir -r /app/requirements.txt

COPY ./app /app
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]