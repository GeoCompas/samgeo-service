from pydantic import BaseModel, field_validator, root_validator, ValidationError
from typing import List, Tuple, Optional


class SegmentRequest(BaseModel):
    bbox: List[float]
    point_labels: Optional[List[int]] = None
    point_coords: Optional[List[Tuple[float, float]]] = None
    crs: str = "EPSG:4326"
    zoom: float
    id: str
    project: str
    action_type: str = None

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


class ImageRequest(BaseModel):
    canvas_image: Optional[str] = None
    tms_source: Optional[str] = None
    project: str
    id: str
    bbox: List[float]
    zoom: float
    crs: str = "EPSG:4326"

    @root_validator(pre=True)
    def check_canvas_or_tms_source(cls, values):
        canvas_image = values.get("canvas_image")
        tms_source = values.get("tms_source")
        if not canvas_image and not tms_source:
            raise ValueError("Either canvas_image or tms_source must be provided")

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


class SaveGeojson(BaseModel):
    data: str
    project: str
    id: str
