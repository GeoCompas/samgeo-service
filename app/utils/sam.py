import os
from samgeo import SamGeo, tms_to_geotiff
import torch

# Initialize the SAM 1 model
device = "cuda" if torch.cuda.is_available() else "cpu"

sam = SamGeo(
    checkpoint="sam_vit_h_4b8939.pth",
    model_type="vit_h",
    device=device,
    erosion_kernel=(3, 3),
    mask_multiplier=255,
    sam_kwargs=None,
)

samPredictor = SamGeo(
    model_type="vit_h",
    automatic=False,
    sam_kwargs=None,
)
