import re
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

HEX_COLOR_REGEX = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$")


class TextEffects(BaseModel):
    case: str = Field(
        "normal",
        description="Casing format to enforce: normal, uppercase, lowercase, titlecase",
    )
    word_highlight: str = Field(
        "none",
        description="Active word highlighting style: none, current, all",
    )
    auto_capitalization: bool = Field(
        True, description="Capitalize sentence starts automatically"
    )
    auto_emoji: bool = Field(
        False, description="Insert matching emojis automatically"
    )

    @field_validator("case")
    @classmethod
    def validate_case(cls, v: str) -> str:
        allowed = {"normal", "uppercase", "lowercase", "titlecase"}
        if v not in allowed:
            raise ValueError(f"case must be one of {allowed}")
        return v

    @field_validator("word_highlight")
    @classmethod
    def validate_highlight(cls, v: str) -> str:
        allowed = {"none", "current", "all"}
        if v not in allowed:
            raise ValueError(f"word_highlight must be one of {allowed}")
        return v


class StyleProperties(BaseModel):
    font_family: str = Field(
        ..., description="Font family name (e.g. Arial Black)"
    )
    font_size: float = Field(
        ..., description="Base font size in points", ge=1.0, le=200.0
    )
    font_weight: str = Field("normal", description="Font weight: normal, bold")
    text_color: str = Field(
        ..., description="HEX color code format for default text body"
    )
    highlight_color: str = Field(
        ..., description="HEX color code format for active/highlighted text"
    )
    outline_color: str = Field(
        ..., description="HEX color code format for outlines"
    )
    outline_width: float = Field(
        0.0, description="Outline width in pixels", ge=0.0, le=20.0
    )
    shadow_color: str = Field(
        "#000000", description="HEX color code format for shadows"
    )
    shadow_offset_x: float = Field(
        0.0, description="Shadow horizontal offset in pixels"
    )
    shadow_offset_y: float = Field(
        0.0, description="Shadow vertical offset in pixels"
    )
    background_box: bool = Field(
        False, description="Whether to draw a background box block behind text"
    )
    background_color: str = Field(
        "#000000", description="HEX color code format for background box"
    )
    background_opacity: float = Field(
        0.5, description="Background opacity value", ge=0.0, le=1.0
    )
    border_radius: float = Field(
        0.0, description="Background box border radius", ge=0.0, le=50.0
    )
    padding: float = Field(
        0.0, description="Background box inside padding", ge=0.0, le=100.0
    )
    line_spacing: float = Field(
        1.2, description="Line height spacing multiplier", ge=0.5, le=3.0
    )
    letter_spacing: float = Field(
        0.0, description="Letter spacing layout in pixels"
    )
    safe_margin: float = Field(
        20.0, description="Safe margin bounds in pixels", ge=0.0, le=200.0
    )
    vertical_position: str = Field(
        "bottom", description="Vertical align: top, center, bottom"
    )
    horizontal_position: str = Field(
        "center", description="Horizontal align: left, center, right"
    )
    max_width_pct: float = Field(
        80.0,
        description="Maximum caption block width percentage of frame",
        ge=10.0,
        le=100.0,
    )
    alignment: str = Field(
        "center", description="Text alignment: left, center, right"
    )
    opacity: float = Field(
        1.0, description="Overall caption layout opacity", ge=0.0, le=1.0
    )
    text_effects: TextEffects = Field(
        ..., description="Active casing and highlighting effects configurations"
    )

    @field_validator(
        "text_color",
        "highlight_color",
        "outline_color",
        "shadow_color",
        "background_color",
    )
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        if not HEX_COLOR_REGEX.match(v):
            raise ValueError(
                f"Color {v} must be a valid HEX code (#RRGGBB or #RRGGBBAA)"
            )
        return v

    @field_validator("font_weight")
    @classmethod
    def validate_weight(cls, v: str) -> str:
        allowed = {"normal", "bold"}
        if v not in allowed:
            raise ValueError(f"font_weight must be one of {allowed}")
        return v

    @field_validator("vertical_position")
    @classmethod
    def validate_vpos(cls, v: str) -> str:
        allowed = {"top", "center", "bottom"}
        if v not in allowed:
            raise ValueError(f"vertical_position must be one of {allowed}")
        return v

    @field_validator("horizontal_position")
    @classmethod
    def validate_hpos(cls, v: str) -> str:
        allowed = {"left", "center", "right"}
        if v not in allowed:
            raise ValueError(f"horizontal_position must be one of {allowed}")
        return v

    @field_validator("alignment")
    @classmethod
    def validate_align(cls, v: str) -> str:
        allowed = {"left", "center", "right"}
        if v not in allowed:
            raise ValueError(f"alignment must be one of {allowed}")
        return v


class SubtitleWord(BaseModel):
    word: str = Field(..., description="The spoken word text")
    start: float = Field(
        ..., description="Start timestamp of the word in seconds", ge=0.0
    )
    end: float = Field(
        ..., description="End timestamp of the word in seconds", ge=0.0
    )
    confidence: Optional[float] = Field(None, description="ASR confidence score")
    line_index: Optional[int] = Field(
        None, description="Offset line index inside the block segment"
    )
    caption_index: Optional[int] = Field(
        None, description="Offset caption block index"
    )


class SubtitleSegment(BaseModel):
    index: int = Field(..., description="Sequential caption segment index")
    start: float = Field(
        ..., description="Caption start timestamp in seconds", ge=0.0
    )
    end: float = Field(
        ..., description="Caption end timestamp in seconds", ge=0.0
    )
    text: str = Field(..., description="Text content of the subtitle block")
    words: List[SubtitleWord] = Field(
        ..., description="Constituent words of the block segment"
    )


class ApplyStyleRequest(BaseModel):
    style_name: str = Field(
        ...,
        description="Target style configuration name (e.g. 'tiktok') or custom",
    )
    width: int = Field(1080, description="Video width in pixels", ge=240, le=8192)
    height: int = Field(
        1920, description="Video height in pixels", ge=240, le=8192
    )
    aspect_ratio: str = Field(
        "vertical",
        description="Aspect ratio configuration: vertical, horizontal, square",
    )
    subtitles: List[SubtitleSegment] = Field(
        ..., description="The segment list to apply style configurations to"
    )

    @field_validator("aspect_ratio")
    @classmethod
    def validate_aspect_ratio(cls, v: str) -> str:
        allowed = {"vertical", "horizontal", "square"}
        if v not in allowed:
            raise ValueError(f"aspect_ratio must be one of {allowed}")
        return v


class ApplyStyleResponse(BaseModel):
    style_name: str = Field(..., description="Target style configuration name")
    width: int = Field(..., description="Video width in pixels")
    height: int = Field(..., description="Video height in pixels")
    aspect_ratio: str = Field(..., description="Aspect ratio layout used")
    style_properties: StyleProperties = Field(
        ..., description="Resultant scaled style configurations used"
    )
    styled_subtitles: List[SubtitleSegment] = Field(
        ..., description="Styled subtitle block segments list"
    )
