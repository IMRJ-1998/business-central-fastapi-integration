from abc import ABC, abstractmethod
from typing import Any

class BCAuthProvider(ABC):
    @abstractmethod
    async def build_request_kwargs(self) -> dict[str, Any]:
        raise NotImplementedError
