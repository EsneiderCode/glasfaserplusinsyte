from typing import Optional
import httpx
import time
from config import settings


class AuthService:
    def __init__(self):
        self._token: Optional[str] = None
        self._valid_until: float = 0
        self._token_type: str = "Bearer"

    @property
    def is_valid(self) -> bool:
        return self._token is not None and time.time() < (self._valid_until - 60)

    async def authenticate(self) -> str:
        async with httpx.AsyncClient(verify=False, timeout=settings.request_timeout) as client:
            # Step 1: Login (returns APP_ID 1 token)
            resp = await client.post(
                f"{settings.portal_api_url}/api/authorize",
                json={"usuario": settings.username, "password": settings.password, "remember": True},
            )
            resp.raise_for_status()
            data = resp.json()
            token1 = data["token"]["access_token"]
            token_type = data["token"].get("token_type", "Bearer")

            # Step 2: Switch to APP_ID 10 (workorders module)
            resp2 = await client.post(
                f"{settings.portal_api_url}/session/switch-app",
                json={"APP_ID": 10, "channel": "backend"},
                headers={"Authorization": f"{token_type} {token1}"},
            )
            resp2.raise_for_status()
            data2 = resp2.json()
            token_data = data2["token"]
            self._token = token_data["access_token"]
            self._token_type = token_data.get("token_type", "Bearer")
            self._valid_until = float(token_data["valid_until"])
            return self._token

    async def get_token(self) -> str:
        if not self.is_valid:
            await self.authenticate()
        return self._token

    async def get_headers(self) -> dict:
        token = await self.get_token()
        return {
            "Authorization": f"{self._token_type} {token}",
            "X-Requested-With": "XMLHttpRequest",
        }


auth_service = AuthService()
