from pydantic import BaseModel

class SuccessModel(BaseModel):
    status: str = "success"