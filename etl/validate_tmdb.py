
from pydantic import BaseModel, Field, field_validator


class AuthorDetails(BaseModel):
    rating: float | None = Field(
        default=None, ge=0, le=10
    )


class Review(BaseModel):
    id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    author_details: AuthorDetails = Field(
        default_factory=AuthorDetails
    )

    @field_validator("author_details", mode="before")
    @classmethod
    def handle_missing_details(cls, value):
        return value or {}

    @field_validator("id", "content")
    @classmethod
    def validate_text(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Value cannot be empty")

        return value


class MovieReview(BaseModel):
    movie_id: int = Field(gt=0)
    movie_title: str = Field(min_length=1)
    review: Review

    @field_validator("movie_title")
    @classmethod
    def validate_title(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Movie title cannot be empty")

        return value
