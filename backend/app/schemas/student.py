from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class InterestInput(BaseModel):
    interest_id: Optional[int] = Field(default=None, gt=0)
    other_interest: Optional[str] = Field(default=None, min_length=1, max_length=150)

    def validate_interest(self):
        """Ensure exactly one of interest_id or other_interest is provided."""
        has_interest_id = self.interest_id is not None
        has_other = self.other_interest is not None and self.other_interest.strip() != ""
        if has_interest_id == has_other:  # XOR - exactly one must be true
            raise ValueError("Provide exactly one of interest_id or other_interest")


class StudentCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr | None = None
    preferred_career: str | None = Field(default=None, max_length=100)
    interests: list[InterestInput] = Field(min_length=1)

    def validate_interests(self):
        for interest in self.interests:
            interest.validate_interest()


class StudentResponse(BaseModel):
    id: int
    full_name: str
    email: str | None
    preferred_career: str | None

    model_config = ConfigDict(from_attributes=True)