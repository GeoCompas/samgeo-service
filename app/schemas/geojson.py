from pydantic import BaseModel, field_validator, root_validator, ValidationError
from typing import List, Tuple, Optional


class JSONDataBase(BaseModel):
    project: str
    id: str
    data: str
