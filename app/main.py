import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import logging
from routes.files import router as files_router
from routes.segment import router as segment_router

app = FastAPI()
app.mount("/files", StaticFiles(directory="public"), name="public")
logging.basicConfig(level=logging.INFO)
app.include_router(files_router, prefix="/browse")
app.include_router(segment_router)

@app.get("/")
def read_root():
    return {"state": "ok"}
