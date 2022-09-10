from nonebot import get_driver
from pydantic import BaseModel


class PluginConfig(BaseModel):
    proxy: str = None


config = PluginConfig(**get_driver().config.dict())
