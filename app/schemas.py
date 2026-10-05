from typing import Literal
from pydantic import BaseModel, Field, field_validator

AuthType = Literal["entra_id", "basic"]

class BCConfigUpdate(BaseModel):
    bc_api_base_url: str = Field(min_length=1, max_length=1000)
    bc_auth_type: AuthType = "entra_id"
    bc_company_id: str = Field(default="", max_length=200)
    entra_tenant_id: str = Field(default="", max_length=300)
    entra_client_id: str = Field(default="", max_length=300)
    entra_client_secret: str = Field(default="", max_length=1000)
    entra_scope: str = Field(
        default="https://api.businesscentral.dynamics.com/.default",
        max_length=1000,
    )
    basic_username: str = Field(default="", max_length=300)
    basic_password: str = Field(default="", max_length=1000)

    @field_validator("bc_api_base_url")
    @classmethod
    def normalize_url(cls, value: str) -> str:
        return value.rstrip("/")
