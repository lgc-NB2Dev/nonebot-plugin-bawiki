from typing import Optional
from typing_extensions import Annotated

from nonebot import get_plugin_config
from pydantic import BaseModel, Field, HttpUrl


class Cfg(BaseModel):
    ba_proxy: Optional[str] = None
    ba_shittim_proxy: Optional[str] = None
    ba_gacha_cool_down: int = 0
    ba_voice_use_card: bool = False
    ba_use_forward_msg: bool = True
    ba_screenshot_timeout: int = 60
    ba_disable_classic_gacha: bool = False
    ba_gacha_max: int = 200
    ba_illegal_limit: int = 3
    ba_arona_set_alias_only_su: bool = False

    ba_gamekee_url: Annotated[str, HttpUrl] = Field("https://ba.gamekee.com/")
    ba_schale_url: Annotated[str, HttpUrl] = Field("https://schale.gg/")
    ba_bawiki_db_url: Annotated[str, HttpUrl] = Field("https://bawiki.lgc2333.top/")
    ba_arona_api_url: Annotated[str, HttpUrl] = Field("https://arona.diyigemt.com/")
    ba_arona_cdn_url: Annotated[str, HttpUrl] = Field("https://arona.cdn.diyigemt.com/")
    ba_shittim_url: Annotated[str, HttpUrl] = Field("https://arona.icu/")
    ba_shittim_api_url: Annotated[str, HttpUrl] = Field("https://api.arona.icu/")
    ba_shittim_data_url: Annotated[str, HttpUrl] = Field("https://data.ba.benx1n.com/")

    ba_shittim_key: Optional[str] = None
    ba_shittim_request_delay: float = 0

    ba_req_retry: int = 1
    ba_req_cache_ttl: int = 10800  # 3 hrs
    ba_shittim_req_cache_ttl: int = 600  # 10 mins
    ba_req_timeout: Optional[float] = 10.0
    ba_auto_clear_cache_path: bool = False


config = get_plugin_config(Cfg)
