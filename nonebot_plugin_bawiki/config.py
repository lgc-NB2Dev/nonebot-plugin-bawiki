from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel, validator


class Cfg(BaseModel):
    ba_proxy: Optional[str] = None
    ba_gacha_cool_down: int = 0
    ba_voice_use_card: bool = False
    ba_screenshot_timeout: int = 60
    ba_disable_classic_gacha: bool = False
    ba_gacha_max: int = 200

    ba_gamekee_url: str = "https://ba.gamekee.com/"
    ba_schale_url: str = "https://schale.gg/"
    ba_bawiki_db_url: str = "https://bawiki.lgc2333.top/"
    ba_arona_api_url: str = "https://arona.diyigemt.com/"
    ba_arona_cdn_url: str = "https://arona.cdn.diyigemt.com/"

    ba_clear_req_cache_interval: int = 3
    ba_auto_clear_arona_cache: bool = False

    @validator(
        "ba_gamekee_url",
        "ba_schale_url",
        "ba_bawiki_db_url",
        "ba_arona_api_url",
        "ba_arona_cdn_url",
    )
    def _(cls, v: str):  # noqa: N805
        if not (v.startswith(("https://", "http://")) and v.endswith("/")):
            raise ValueError('自定义的 URL 请以 "http(s)://" 开头，以 "/" 结尾')
        return v


config = Cfg.parse_obj(get_driver().config.dict())
