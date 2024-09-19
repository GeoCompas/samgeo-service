from pydantic import BaseModel, field_validator
from typing import List, Tuple, Optional


class SegmentRequest(BaseModel):
    bbox: List[float]
    point_labels: Optional[List[int]] = None
    point_coords: Optional[List[Tuple[float, float]]] = None
    crs: str
    zoom: float
    id: str
    project: str

    # @field_validator("bbox", mode="before")
    # def validate_bbox(cls, bbox):
    #     if len(bbox) != 4:
    #         raise ValueError(
    #             "Bounding box must contain exactly 4 values: [min_lon, min_lat, max_lon, max_lat]"
    #         )
    #     if not (
    #         -180 <= bbox[0] <= 180
    #         and -90 <= bbox[1] <= 90
    #         and -180 <= bbox[2] <= 180
    #         and -90 <= bbox[3] <= 90
    #     ):
    #         raise ValueError(
    #             "Bounding box coordinates must be within valid ranges: [-180, 180] for longitude and [-90, 90] for latitude"
    #         )
    #     return bbox

    # @field_validator("zoom", mode="before")
    # def validate_zoom(cls, zoom):
    #     if zoom < 0 or zoom >= 20:
    #         raise ValueError("Zoom level must be between 0 and 20")
    #     return zoom

    # @field_validator("point_coords", "point_labels", mode="before")
    # def validate_points_and_labels(cls, v, values, info):
    #     if info.field_name == "point_coords":
    #         if len(v) != len(values.get('point_labels', [])):
    #             raise ValueError("The number of point coordinates must match the number of point labels")
    #     return v
