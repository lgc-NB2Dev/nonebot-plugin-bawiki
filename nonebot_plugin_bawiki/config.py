from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel, validator


class Cfg(BaseModel):
    proxy: Optional[str] = None
    gamekee_url = "https://ba.gamekee.com/"
    schale_url = "https://schale.lgc.cyberczy.xyz/"
    schale_mirror_url = "https://schale.lgc.cyberczy.xyz/"
    bawiki_db_url = "https://bawiki.lgc.cyberczy.xyz/"

    @validator("gamekee_url", allow_reuse=True)
    @validator("schale_url", allow_reuse=True)
    @validator("schale_mirror_url", allow_reuse=True)
    @validator("bawiki_db_url", allow_reuse=True)
    def _(cls, val: str):
        if not (
            (val.startswith("https://") or val.startswith("http://"))
            and val.endswith("/")
        ):
            raise ValueError('自定义的 URL 请以 "http(s)://" 开头，以 "/" 结尾')


config = Cfg.parse_obj(get_driver().config.dict())
