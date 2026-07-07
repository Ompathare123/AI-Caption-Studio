from pydantic import BaseModel, Field


class AudioExtractRequest(BaseModel):
    video_id: str = Field(..., description="The unique database ID of the uploaded video")


class AudioExtractResponse(BaseModel):
    audio_id: str
    audio_path: str
    duration: float
    sample_rate: int
    channels: int
    status: str
