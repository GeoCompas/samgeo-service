from pydantic import BaseModel, field_validator, root_validator, ValidationError, Field
from typing import List, Optional


class AOIRequestBase(BaseModel):
    project: str = Field(..., description="Project ID identifier")
    id: str = Field(..., description="AOI random ID")
    bbox: List[float] = Field(
        ..., description="Bounding box with exactly 4 floats", min_items=4, max_items=4
    )
    zoom: int = Field(..., description="Zoom level for the image")
    crs: str = "EPSG:4326"
    canvas_image: str = Field(..., description="Base64 encoded image")

    @root_validator(pre=True)
    def check_canvas_image(cls, values):
        canvas_image = values.get("canvas_image")
        if not canvas_image:
            raise ValueError("canvas_image must be provided")
        return values

    @field_validator("bbox", mode="before")
    def validate_bbox(cls, bbox):
        if len(bbox) != 4:
            raise ValueError(
                "Bounding box must contain exactly 4 values: [min_lon, min_lat, max_lon, max_lat]"
            )
        if not (
            -180 <= bbox[0] <= 180
            and -90 <= bbox[1] <= 90
            and -180 <= bbox[2] <= 180
            and -90 <= bbox[3] <= 90
        ):
            raise ValueError(
                "Bounding box coordinates must be within valid ranges: [-180, 180] for longitude and [-90, 90] for latitude"
            )
        return bbox

    @field_validator("zoom", mode="before")
    def validate_zoom(cls, zoom):
        if zoom < 0 or zoom >= 22:
            raise ValueError("Zoom level must be between 0 and 20")
        return zoom

    class Config:
        json_schema_extra = {
            "example": {
                "canvas_image": "data:image/jpeg;base64,/9j/xxxx",
                "bbox": [
                    11.373392997813642,
                    44.51513515076891,
                    11.39311700326368,
                    44.53040540797642,
                ],
                "zoom": 15,
                "crs": "EPSG:4326",
                "id": "f08",
                "project": "bologna",
            }
        }


class AOIResponseBase(BaseModel):
    project: str = Field(..., description="Project ID identifier")
    id: str = Field(..., description="Unique identifier for the request")
    bbox: List[float] = Field(
        ..., description="Bounding box with exactly 4 floats", min_items=4, max_items=4
    )
    zoom: int = Field(..., description="Zoom level for the image")
    image_url: Optional[str] = Field(..., description="URL of the saved image file")
    tif_url: Optional[str] = Field(..., description="URL of the saved GeoTIFF file")
