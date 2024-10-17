from pydantic import BaseModel, Field, field_validator
from typing import List, Tuple, Optional, Any, Dict, Literal


class SegmentRequestBase(BaseModel):
    project: str = Field(..., description="Project ID identifier")
    id: str = Field(..., description="Unique identifier for AOI segmentation request")
    bbox: List[float] = Field(
        ...,
        description="Bounding box defined by four coordinates: [min_lon, min_lat, max_lon, max_lat]",
    )
    point_labels: Optional[List[int]] = Field(
        None,
        description="Optional list of integer labels for each point coordinate, not applicable for /segment_automatic",
    )
    point_coords: Optional[List[Tuple[float, float]]] = Field(
        None,
        description="Optional list of tuples representing (x, y) coordinates of points, not applicable for /segment_automatic",
    )
    crs: str = Field(
        "EPSG:4326", description="Coordinate reference system, default is EPSG:4326 (WGS84)"
    )
    zoom: float = Field(..., description="Zoom level of the map, must be between 0 and 22")
    action_type: str = Field(
        None,
        description="Type of action requested (e.g., single_point or multi_point segmentation), default is None",
    )
    return_format: Literal["geojson", "url"] = Field(
        "geojson", description="Return format, must be 'geojson' or 'url'. Default is 'geojson'."
    )

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
        if zoom < 0 or zoom > 22:
            raise ValueError("Zoom level must be between 0 and 22")
        return zoom


class SegmentResponseBase(BaseModel):
    type: str = Field(
        "FeatureCollection", description="Defines the GeoJSON type, typically 'FeatureCollection'"
    )
    features: List[Dict[str, Any]] = Field(
        ..., description="A list of GeoJSON features containing geometries and properties"
    )
