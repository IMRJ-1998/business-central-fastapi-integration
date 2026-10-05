from dataclasses import dataclass
from typing import Any
import httpx
from sqlalchemy.orm import Session
from ..config_manager import get_config
from .bc_auth.basic_auth import BasicAuthProvider
from .bc_auth.entra_id import EntraIDAuthProvider

@dataclass
class BCResult:
    ok: bool
    status_code: int | None
    message: str
    data: Any = None

class BusinessCentralClient:
    def __init__(self, db: Session):
        config = get_config(db)
        self.base_url = config.bc_api_base_url.rstrip("/")
        self.company_id = config.bc_company_id.strip()

        if config.bc_auth_type == "entra_id":
            self.auth_provider = EntraIDAuthProvider(
                config.entra_tenant_id, config.entra_client_id,
                config.entra_client_secret, config.entra_scope
            )
        elif config.bc_auth_type == "basic":
            self.auth_provider = BasicAuthProvider(
                config.basic_username, config.basic_password
            )
        else:
            raise ValueError(f"Unsupported BC authentication type: {config.bc_auth_type}")

    def _url(self, resource: str = "") -> str:
        return f"{self.base_url}/{resource.lstrip('/')}"

    def _params(self) -> dict[str, str]:
        params = {"$top": "20"}
        if self.company_id:
            params["company"] = self.company_id
        return params

    async def request(self, method: str, resource: str = "", **kwargs) -> BCResult:
        if not self.base_url:
            return BCResult(False, None, "Business Central API URL is not configured.")
        try:
            kwargs.update(await self.auth_provider.build_request_kwargs())
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(15.0), follow_redirects=True
            ) as client:
                response = await client.request(method, self._url(resource), **kwargs)
            content_type = response.headers.get("content-type", "")
            data = response.json() if "application/json" in content_type else response.text
            if response.is_success:
                return BCResult(True, response.status_code, "OK", data)
            return BCResult(False, response.status_code, f"HTTP {response.status_code}", data)
        except httpx.HTTPError as exc:
            return BCResult(False, None, f"Network/API error: {exc}")
        except (KeyError, ValueError) as exc:
            return BCResult(False, None, f"Authentication/configuration error: {exc}")

    async def health_check(self) -> BCResult:
        return await self.request("GET", "")

    async def get_companies(self) -> BCResult:
        return await self.request("GET", "companies", params=self._params())

    async def get_items(self) -> BCResult:
        return await self.request("GET", "items", params=self._params())
