from typing import Any
from .base import BCAuthProvider

class BasicAuthProvider(BCAuthProvider):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    async def build_request_kwargs(self) -> dict[str, Any]:
        return {"auth": (self.username, self.password)}
