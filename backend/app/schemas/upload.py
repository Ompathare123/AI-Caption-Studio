from pydantic import BaseModel


class VideoUploadResponse(BaseModel):
    id: str
    filename: str
    size: int
    duration: float
    status: str

    model_config = {
        "from_attributes": True
    }
