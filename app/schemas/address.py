from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AddressCreate(BaseModel):
    """Schema for creating an address."""

    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    latitude: float = Field(..., ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(..., ge=-180, le=180, allow_inf_nan=False)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, min_length=1, max_length=20)

    @field_validator("street", "city", "country")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Value cannot be blank.")
        return cleaned_value

    @field_validator("name", "state", "postal_code")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Value cannot be blank.")
        return cleaned_value

    @model_validator(mode="after")
    def derive_name(self) -> "AddressCreate":
        if self.name is None:
            self.name = f"{self.street}, {self.city}"
        return self


class AddressUpdate(BaseModel):
    """Schema for partially updating an address."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    street: str | None = Field(default=None, min_length=1, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, min_length=1, max_length=20)
    country: str | None = Field(default=None, min_length=1, max_length=100)
    latitude: float | None = Field(default=None, ge=-90, le=90, allow_inf_nan=False)
    longitude: float | None = Field(default=None, ge=-180, le=180, allow_inf_nan=False)

    @field_validator("name", "street", "city", "state", "postal_code", "country")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value

        cleaned_value = value.strip()
        if not cleaned_value:
            raise ValueError("Value cannot be blank.")
        return cleaned_value

    @model_validator(mode="after")
    def validate_not_empty(self) -> "AddressUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update.")
        return self

    @model_validator(mode="after")
    def validate_non_nullable_updates(self) -> "AddressUpdate":
        non_nullable_fields = {"name", "street", "city", "country", "latitude", "longitude"}
        for field_name in non_nullable_fields.intersection(self.model_fields_set):
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null.")
        return self


class AddressRead(BaseModel):
    """Schema returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    street: str
    city: str
    state: str | None
    postal_code: str | None
    country: str
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime


class NearbyAddressRead(AddressRead):
    """Address schema with computed distance."""

    distance: float = Field(..., ge=0)
