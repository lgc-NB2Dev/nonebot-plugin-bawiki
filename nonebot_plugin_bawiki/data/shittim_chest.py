import asyncio
import shutil
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
)
from typing_extensions import Unpack

import anyio
import jinja2
from nonebot import logger
from playwright.async_api import ViewportSize
from pydantic import BaseModel, Field, parse_obj_as, validator

from ..config import config
from ..resource import CACHE_DIR, RES_SHITTIM_TEMPLATES_DIR
from ..util import AsyncReqKwargs, RespType, async_req, camel_case
from .playwright import get_routed_page

if not config.ba_shittim_key:
    logger.warning("API Key 未配置，关于什亭之匣的功能将会不可用！")
    logger.warning("请访问 https://arona.icu/about 查看获取 API Key 的方式！")


T = TypeVar("T")


SHITTIM_CACHE_DIR = CACHE_DIR / "shittim"
if config.ba_auto_clear_cache_path and SHITTIM_CACHE_DIR.exists():
    shutil.rmtree(SHITTIM_CACHE_DIR)
if not SHITTIM_CACHE_DIR.exists():
    SHITTIM_CACHE_DIR.mkdir(parents=True)


template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(RES_SHITTIM_TEMPLATES_DIR),
    enable_async=True,
)


SERVER_NAME_MAP = {
    1: "官服",
    2: "B服",
}
RANK_DATA_TYPE_NAME_MAP = {
    1: "排名",
    2: "档线",
}
HARD_FULLNAME_MAP = {
    "EX": "Extreme",
    "HC": "Hardcore",
    "VH": "VeryHard",
    "H": "Hard",
    "N": "Normal",
}


# region Pagination


class PaginationCallable(Protocol, Generic[T]):
    # (resp, is_last_page)
    async def __call__(self, page: int, size: int) -> Tuple[Optional[List[T]], bool]:
        ...


class IterPFKwargs(TypedDict, total=False):
    page: int
    size: int
    delay: float


def iter_pagination_func(**kwargs: Unpack[IterPFKwargs]):
    page = kwargs.get("page", 1)
    size = kwargs.get("size", 100)
    delay = kwargs.get("delay", 0.0)

    def decorator(func: PaginationCallable[T]) -> Callable[[], AsyncIterable[T]]:
        async def wrapper():
            while True:
                resp, last_page = await func(page, size)
                if resp:
                    for x in resp:
                        yield x
                if last_page:
                    break
                if delay:
                    await asyncio.sleep(delay)

        return wrapper

    return decorator


async def async_iter_all(iterator: AsyncIterable[T]) -> List[T]:
    return [x async for x in iterator]


# endregion


# region enums


class ServerType(Enum):
    Official = 1
    Bilibili = 2


class RankDataType(Enum):
    Rank = 1
    Score = 2


# endregion


# region models


def time_validator(v: str):
    try:
        return datetime.strptime(v, "%Y-%m-%d %H:%M")
    except ValueError as e:
        raise ValueError(f"Time `{v}` format error") from e


class CamelAliasModel(BaseModel):
    class Config:
        alias_generator = camel_case


class PaginationModel(CamelAliasModel):
    page: int
    size: int
    total_pages: int
    last_page: bool


class SeasonMap(CamelAliasModel):
    key: str
    value: str


class Season(CamelAliasModel):
    season: int
    season_map: SeasonMap = Field(alias="map")
    boss_id: int
    boss: str
    start_time: datetime
    end_time: datetime

    _validator_time = validator(
        "start_time",
        "end_time",
        pre=True,
        allow_reuse=True,
    )(time_validator)


class Character(CamelAliasModel):
    has_weapon: bool
    is_assist: bool
    level: int
    slot_index: int
    star_grade: int
    unique_id: int
    bullet_type: str
    tactic_role: str


class TryNumberInfo(CamelAliasModel):
    try_number: int
    main_characters: List[Character]
    support_characters: List[Character]


class RankSummary(CamelAliasModel):
    rank: int
    best_ranking_point: int
    hard: str
    battle_time: str

    @property
    def hard_fullname(self) -> str:
        return HARD_FULLNAME_MAP.get(self.hard, self.hard)


class RankRecord(RankSummary):
    level: int
    nickname: str
    represent_character_unique_id: int
    tier: int
    boss_id: int
    try_number_infos: List[TryNumberInfo]
    record_time: datetime


class Rank(PaginationModel):
    records: List[RankRecord]


class RaidChart(CamelAliasModel):
    data: Dict[int, List[int]]
    time: List[datetime]


# endregion


# region api


request_lock = asyncio.Lock()


async def shittim_get(url: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    if not config.ba_shittim_key:
        raise ValueError("`BA_SHITTIM_KEY` not set")

    kwargs = kwargs.copy()
    kwargs["base_urls"] = config.ba_shittim_api_url
    kwargs["proxies"] = config.ba_shittim_proxy

    headers = kwargs.get("headers") or {}
    headers["Authorization"] = f"ba-token {config.ba_shittim_key}"
    kwargs["headers"] = headers

    limit_qps = config.ba_shittim_request_delay > 0
    if limit_qps:
        kwargs["sleep"] = config.ba_shittim_request_delay
        await request_lock.acquire()

    try:
        resp = await async_req(url, **kwargs)
    finally:
        if limit_qps and request_lock.locked():
            request_lock.release()

    # if ((code := resp.get("code")) is not None) and (code != 200):
    #     raise ValueError(f"Shittim API returned an error response: {resp}")

    return resp["data"]


async def get_season_list() -> List[Season]:
    return parse_obj_as(List[Season], await shittim_get("api/season/list"))


def get_rank_list(
    server: ServerType,
    data_type: RankDataType,
    season: int,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[RankRecord]:
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page: int, size: int):
        ret = parse_obj_as(
            Rank,
            await shittim_get(
                f"api/rank/list/{server.value}/{data_type.value}/{season}",
                params={"page": page, "size": size},
            ),
        )
        return ret.records, True if (not ret.records) else ret.last_page

    return iterator()


async def get_rank_list_top(
    server: ServerType,
    season: int,
) -> List[RankSummary]:
    return parse_obj_as(
        List[RankSummary],
        await shittim_get(
            "api/rank/list_top",
            params={"server": server.value, "season": season},
        ),
    )


async def get_rank_list_by_last_rank(
    server: ServerType,
    season: int,
) -> List[RankSummary]:
    return parse_obj_as(
        List[RankSummary],
        await shittim_get(
            "api/rank/list_by_last_rank",
            params={"server": server.value, "season": season},
        ),
    )


async def get_raid_chart_data(server: ServerType, season: int) -> RaidChart:
    return parse_obj_as(
        RaidChart,
        await shittim_get(f"raid/new/charts/{server.value}", params={"s": season}),
    )


async def get_alice_friends(server: ServerType) -> Dict[int, RankRecord]:
    return parse_obj_as(
        Dict[int, RankRecord],
        await shittim_get("api/rank/list_20001", params={"server": server}),
    )


async def get_involute_dogs(server: ServerType) -> Dict[int, RankRecord]:
    return parse_obj_as(
        Dict[int, RankRecord],
        await shittim_get("api/rank/list_1", params={"server": server}),
    )


async def get_student_icon(student_id: int) -> bytes:
    filename = f"{student_id}.png"
    path = anyio.Path(SHITTIM_CACHE_DIR / filename)

    if await path.exists():
        return await path.read_bytes()

    resp = await async_req(
        f"web_students_original_icon/{filename}",
        base_urls=config.ba_shittim_data_url,
        resp_type=RespType.BYTES,
        headers={"Referer": config.ba_shittim_api_url},
    )
    await path.write_bytes(resp)
    return resp


# endregion


# region render


async def render_html(html: str) -> bytes:
    # Path("debug.html").write_text(html, encoding="u8")
    async with get_routed_page(viewport=ViewportSize(width=840, height=800)) as page:
        await page.set_content(html)
        main_elem = await page.query_selector(".main")
        assert main_elem
        return await main_elem.screenshot(type="jpeg")


async def render_raid_rank(
    server_name: str,
    data_type_name: str,
    season: Season,
    rank_list_top: List[RankSummary],
    rank_list_by_last_rank: List[RankSummary],
    rank_list: List[RankRecord],
) -> bytes:
    template = template_env.get_template("content_raid_rank.html.jinja")
    html = await template.render_async(
        server_name=server_name,
        data_type_name=data_type_name,
        season=season,
        rank_list_top=rank_list_top,
        rank_list_by_last_rank=rank_list_by_last_rank,
        rank_list=rank_list,
    )
    return await render_html(html)


# endregion
