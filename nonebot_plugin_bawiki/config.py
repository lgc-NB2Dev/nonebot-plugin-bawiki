from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel, validator


class Cfg(BaseModel):
    ba_proxy: Optional[str] = None
    ba_gacha_cool_down: int = 0
    ba_voice_use_card: bool = False

    ba_gamekee_url: str = "https://ba.gamekee.com/"
    ba_schale_url: str = "https://schale.lgc.cyberczy.xyz/"
    ba_schale_mirror_url: str = "https://schale.lgc.cyberczy.xyz/"
    ba_bawiki_db_url: str = "https://bawiki.lgc.cyberczy.xyz/"
    ba_arona_api_url: str = "https://arona.diyigemt.com/"
    ba_arona_cdn_url: str = "https://arona.cdn.diyigemt.com/"

    ba_clear_req_cache_interval: int = 3
    ba_auto_clear_arona_cache: bool = True

    @validator(
        "ba_gamekee_url",
        "ba_schale_url",
        "ba_schale_mirror_url",
        "ba_bawiki_db_url",
        "ba_arona_api_url",
        "ba_arona_cdn_url",
    )
    def _(cls, val: str):  # noqa: N805
        if not (val.startswith(("https://", "http://")) and val.endswith("/")):
            raise ValueError('自定义的 URL 请以 "http(s)://" 开头，以 "/" 结尾')
        return val


config = Cfg.parse_obj(get_driver().config.dict())
