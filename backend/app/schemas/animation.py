from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from backend.app.schemas.caption_style import StyleProperties, SubtitleSegment


class AnimationKeyframe(BaseModel):
    time: float = Field(
        ..., description="Timestamp of the keyframe in absolute seconds", ge=0.0
    )
    scale: float = Field(1.0, description="Scale multiplier of the word element")
    opacity: float = Field(
        1.0, description="Opacity level of the word element", ge=0.0, le=1.0
    )
    rotation: float = Field(
        0.0, description="Rotation angle of the word in degrees"
    )
    position_x: float = Field(
        0.0, description="Horizontal position coordinate offset in pixels"
    )
    position_y: float = Field(
        0.0, description="Vertical position coordinate offset in pixels"
    )
    color: str = Field(..., description="HEX color code format at this frame")


class AnimatedWord(BaseModel):
    word: str = Field(..., description="The spoken word text")
    start: float = Field(
        ..., description="Spoken start time in seconds", ge=0.0
    )
    end: float = Field(..., description="Spoken end time in seconds", ge=0.0)
    animation_type: str = Field(
        ..., description="Active animation preset profile code"
    )
    scale: float = Field(1.0, description="Default scale multiplier")
    opacity: float = Field(1.0, description="Default opacity level")
    rotation: float = Field(0.0, description="Default rotation in degrees")
    position_x: float = Field(
        0.0, description="Default horizontal position coordinate in pixels"
    )
    position_y: float = Field(
        0.0, description="Default vertical position coordinate in pixels"
    )
    color: str = Field(..., description="Default text HEX color code")
    highlight_color: Optional[str] = Field(
        None, description="Active highlighted HEX color code"
    )
    shadow_color: Optional[str] = Field(
        None, description="HEX shadow color code if shadows are rendered"
    )
    keyframes: List[AnimationKeyframe] = Field(
        ...,
        description="Keyframe list mapping transitions during word spoken state",
    )


class AnimatedSegment(BaseModel):
    index: int = Field(..., description="Caption segment sequential index")
    start: float = Field(
        ..., description="Caption segment start time in seconds", ge=0.0
    )
    end: float = Field(
        ..., description="Caption segment end time in seconds", ge=0.0
    )
    text: str = Field(..., description="Full text content of the caption block")
    words: List[AnimatedWord] = Field(
        ...,
        description="List of animated word elements constituting the segment block",
    )


class ApplyAnimationRequest(BaseModel):
    subtitles: List[SubtitleSegment] = Field(
        ..., description="The segment list containing word alignments"
    )
    style: StyleProperties = Field(
        ..., description="Visual styling configuration properties"
    )
    animation_preset: str = Field(
        "word_highlight", description="Animation preset profile name"
    )

    @field_validator("animation_preset")
    @classmethod
    def validate_preset(cls, v: str) -> str:
        allowed = {
            "word_highlight",
            "word_pop",
            "word_scale",
            "word_fade",
            "word_bounce",
            "word_slide",
            "word_rotate",
            "word_blur",
            "letter_animation",
            "character_animation",
            "sentence_fade",
            "sentence_pop",
            "karaoke_highlight",
            "progress_fill",
            "opacity_fade",
            "zoom_in",
            "zoom_out",
        }
        if v not in allowed:
            return "word_highlight"
        return v


class ApplyAnimationResponse(BaseModel):
    animation_preset: str = Field(..., description="Animation profile preset applied")
    duration: float = Field(
        ...,
        description="Total duration of subtitle sequence in seconds",
        ge=0.0,
    )
    animated_subtitles: List[AnimatedSegment] = Field(
        ..., description="Resultant list of animated caption segments"
    )
