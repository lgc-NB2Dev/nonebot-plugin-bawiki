from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel, validator


class Cfg(BaseModel):
    ba_proxy: Optional[str] = None
    ba_gamekee_url = "https://ba.gamekee.com/"
    ba_schale_url = "https://schale.lgc.cyberczy.xyz/"
    ba_schale_mirror_url = "https://schale.lgc.cyberczy.xyz/"
    ba_bawiki_db_url = "https://bawiki.lgc.cyberczy.xyz/"

    @validator("gamekee_url", allow_reuse=True, check_fields=False)
    @validator("schale_url", allow_reuse=True, check_fields=False)
    @validator("schale_mirror_url", allow_reuse=True, check_fields=False)
    @validator("bawiki_db_url", allow_reuse=True, check_fields=False)
    def _(cls, val: str):
        if not (
            (val.startswith("https://") or val.startswith("http://"))
            and val.endswith("/")
        ):
            raise ValueError('自定义的 URL 请以 "http(s)://" 开头，以 "/" 结尾')


config = Cfg.parse_obj(get_driver().config.dict())
