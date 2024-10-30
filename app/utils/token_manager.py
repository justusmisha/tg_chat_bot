import aiohttp
from datetime import datetime, timedelta

from app.data.config import USERNAME, PASSWORD, BASE_URL


class TokenManager:
    def __init__(self, token_url, username, password):
        self.token_url = token_url
        self.username = username
        self.password = password
        self.token = None
        self.token_expiry = None

    async def get_headers(self) -> dict:
        """Возвращает заголовки с токеном авторизации."""
        token = await self.get_token()
        return {"Authorization": f"Bearer {token}"}

    async def get_token(self) -> str:
        """Возвращает действующий токен или запрашивает новый, если старый истек."""
        if self.token and self.token_expiry and datetime.utcnow() < self.token_expiry:
            return self.token

        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "password",
                "username": self.username,
                "password": self.password
            }
            async with session.post(self.token_url, data=data) as response:
                if response.status != 200:
                    raise Exception(f"Failed to obtain token: {await response.text()}")

                token_data = await response.json()
                self.token = token_data["access_token"]
                self.token_expiry = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 1000))
                return self.token


# Создание экземпляра TokenManager с нужными параметрами
token_manager = TokenManager(
    token_url=f"{BASE_URL}/admin/token",
    username=USERNAME,
    password=PASSWORD
)
