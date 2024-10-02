from pydantic import BaseModel, field_validator, root_validator, ValidationError
from typing import List, Tuple, Optional


class AOIRequestBase(BaseModel):
    project: str
    id: str
    canvas_image: Optional[str]
    bbox: List[float]
    zoom: float
    crs: str = "EPSG:4326"

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
        if zoom < 0 or zoom >= 20:
            raise ValueError("Zoom level must be between 0 and 20")
        return zoom
