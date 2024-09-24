import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
from fastapi.middleware.cors import CORSMiddleware

from routes.files import router as files_router
from routes.route_sam import router as route_sam
from routes.route_sam2 import router as route_sam2
from utils.utils import check_gpu
from routes.route_images import router as route_images

logging.basicConfig(level=logging.INFO)


app = FastAPI()
app.title = "SAMGEO API"
app.version = "0.1.0"

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("public"):
    os.makedirs("public")


@app.get("/")
def status():
    return {"state": "ok"}


@app.get("/gpu-check")
async def gpu_check():
    result = await asyncio.to_thread(check_gpu)
    return result

app.include_router(route_sam, prefix="/sam")
app.include_router(route_sam2, prefix="/sam2")

app.mount("/files", StaticFiles(directory="public"), name="public")
app.include_router(files_router, prefix="/browse")
app.include_router(route_images)
