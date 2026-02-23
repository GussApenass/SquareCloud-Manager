from pydantic import BaseModel
from typing import Optional, Any

class SquareErrorModel(BaseModel):
    status: str = "error"
    code: Optional[Any] = None
    message: Optional[str] = None