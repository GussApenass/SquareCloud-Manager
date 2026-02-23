from pydantic import BaseModel, Field
from typing import List

class FileContentDataModel(BaseModel):
    type: str
    data: List[int]

class AppFileContentModel(BaseModel):
    status: str = "success"
    response: FileContentDataModel