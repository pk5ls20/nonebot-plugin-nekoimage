from pydantic import BaseModel


class ConfigModel(BaseModel):
    NEKOIMAGE_API: str = "http://127.0.0.1:8000"
    NEKOIMAGE_SECRET: str = None
    NEKOIMAGE_AT_MSG: bool = True
    NEKOIMAGE_BETTER_URL: bool = False
    NEKOIMAGE_HTTPX_TIMEOUT: int = 30
