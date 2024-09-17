import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging
from routes.files import router as files_router
from routes.route_sam import router as route_sam

app = FastAPI()

if not os.path.exists("public"):
    os.makedirs("public")

app.mount("/files", StaticFiles(directory="public"), name="public")
logging.basicConfig(level=logging.INFO)
app.include_router(files_router, prefix="/browse")
app.include_router(route_sam, prefix="/sam")


@app.get("/")
def read_root():
    return {"state": "ok"}
