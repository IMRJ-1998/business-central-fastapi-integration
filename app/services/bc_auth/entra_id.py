from typing import Any
import httpx
from .base import BCAuthProvider

class EntraIDAuthProvider(BCAuthProvider):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, scope: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope

    async def build_request_kwargs(self) -> dict[str, Any]:
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
        token = response.json()["access_token"]
        return {"headers": {"Authorization": f"Bearer {token}"}}
