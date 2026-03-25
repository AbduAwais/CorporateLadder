from pydantic import BaseModel, Field, field_validator
import re


class ScoreSubmission(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    score: int = Field(..., ge=0)
    rank: str = Field("", max_length=30)
    words: int = Field(0, ge=0)
    streak: int = Field(0, ge=0)

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be blank")
        # Allow only alphanumeric, spaces, hyphens, underscores
        if not re.match(r"^[\w\s\-]+$", v):
            raise ValueError("Name contains invalid characters")
        return v


class LeaderboardEntry(BaseModel):
    name: str
    score: int
    rank: str
    words: int
    streak: int
    updated_at: str
