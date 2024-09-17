import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
import time

router = APIRouter()


def format_file_size(size_in_bytes):
    """Convert bytes to a human-readable file size."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_in_bytes < 1024:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024
    return f"{size_in_bytes:.2f} TB"


@router.get("/", response_class=HTMLResponse)
def browse_files(directory: str = ""):
    public_dir = Path("public") / directory

    if not public_dir.exists():
        raise HTTPException(status_code=404, detail="Directory not found")

    if not public_dir.is_dir():
        return FileResponse(public_dir)

    files = list(public_dir.iterdir())
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    html_content = f"<h2>Index of /{directory}</h2><ul>"

    if directory:
        parent_dir = "/".join(directory.split("/")[:-1])
        html_content += (
            f'<li><a href="/browse?directory={parent_dir}">../ (Parent Directory)</a></li>'
        )

    for file in files:
        file_name = file.name
        modification_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(file.stat().st_mtime))
        file_size = format_file_size(file.stat().st_size)

        if file.is_dir():
            html_content += f'<li><a href="/browse?directory={directory}/{file_name}">{file_name}/</a> - {modification_time}</li>'
        else:
            html_content += f'<li><a href="/files/{directory}/{file_name}">{file_name}</a> - {modification_time} - {file_size}</li>'

    html_content += "</ul>"
    return HTMLResponse(content=html_content)


@router.get("/download/{file_path:path}")
def download_file(file_path: str):
    file_full_path = Path("public") / file_path
    if not file_full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_full_path, filename=file_full_path.name)
