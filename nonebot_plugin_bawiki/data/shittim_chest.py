import asyncio
import shutil
from base64 import b64encode
from datetime import datetime
from enum import Enum
from io import BytesIO
from typing import (
    Any,
    AsyncIterable,
    Callable,
    Dict,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
)
from typing_extensions import Unpack
from urllib.parse import urljoin

import anyio
import jinja2
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pytz
from matplotlib import pyplot
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from nonebot import logger
from nonebot.compat import PYDANTIC_V2, type_validate_python
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Route, ViewportSize
from pydantic import BaseModel, ConfigDict, Field
from yarl import URL

from ..compat import field_validator
from ..config import config
from ..resource import (
    CACHE_DIR,
    RES_SHITTIM_TEMPLATES_DIR,
    SHITTIM_UTIL_CSS_PATH,
    SHITTIM_UTIL_JS_PATH,
)
from ..util import (
    AsyncReqKwargs,
    RespType,
    base_async_req,
    camel_case,
    wrapped_alru_cache,
)
from .playwright import RES_ROUTE_URL, bawiki_router, get_template_renderer

if not config.ba_shittim_key:
    logger.warning("API Key 未配置，关于什亭之匣的功能将会不可用！")
    logger.warning("请访问 https://arona.icu/about 查看获取 API Key 的方式！")


SHITTIM_CACHE_DIR = CACHE_DIR / "shittim"
if config.ba_auto_clear_cache_path and SHITTIM_CACHE_DIR.exists():
    shutil.rmtree(SHITTIM_CACHE_DIR)
if not SHITTIM_CACHE_DIR.exists():
    SHITTIM_CACHE_DIR.mkdir(parents=True)


T = TypeVar("T")

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
RAID_ANALYSIS_URL = urljoin(config.ba_shittim_url, "raidAnalyse")
TIMEZONE_SHANGHAI = pytz.timezone("Asia/Shanghai")

async_req = wrapped_alru_cache(ttl=config.ba_shittim_req_cache_ttl, maxsize=None)(
    base_async_req,
)
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(RES_SHITTIM_TEMPLATES_DIR),
    enable_async=True,
    autoescape=True,
)


# region Pagination


class PaginationCallable(Protocol, Generic[T]):
    # (resp, is_last_page)
    async def __call__(
        self,
        page: int,
        size: int,
        delay: float,
    ) -> Tuple[Optional[List[T]], bool]:
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
                resp, last_page = await func(page, size, delay)
                if resp:
                    for x in resp:
                        yield x
                if last_page:
                    break

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


def validator_time(cls, v: str):  # noqa: ANN001, ARG001
    try:
        return (
            datetime.strptime(v, "%Y-%m-%d %H:%M")
            .replace(tzinfo=TIMEZONE_SHANGHAI)
            .astimezone()
        )
    except ValueError as e:
        raise ValueError(f"Time `{v}` format error") from e


def validator_time_as_local(cls, v: datetime) -> datetime:  # noqa: ANN001, ARG001
    return v.astimezone()


def each_item_validator(func: Callable[[Any, T], T]):
    def wrapper(cls, v: Iterable[T]) -> List[T]:  # noqa: ARG001, ANN001
        return [func(cls, x) for x in v]

    return wrapper


class CamelAliasModel(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(alias_generator=camel_case)
    else:

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

    _validator_time = field_validator(
        "start_time",
        "end_time",
        mode="before",
    )(validator_time)


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
    try_number_infos: Optional[List[TryNumberInfo]]
    record_time: datetime

    _validator_time = field_validator(
        "record_time",
    )(validator_time_as_local)


class Rank(PaginationModel):
    records: List[RankRecord]


class RaidChart(CamelAliasModel):
    data: Optional[Dict[int, List[Optional[int]]]] = None
    time: List[datetime]

    _validator_time = field_validator("time")(
        each_item_validator(validator_time_as_local),
    )


class ParticipationChart(CamelAliasModel):
    value: List[int]
    key: List[datetime]

    _validator_time = field_validator("key")(
        each_item_validator(validator_time_as_local),
    )


# endregion


# region api


request_lock = asyncio.Lock()


async def shittim_get(url: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    if not config.ba_shittim_key:
        raise ValueError("`BA_SHITTIM_KEY` not set")

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

    if (code := resp.get("code")) != 200:
        params = kwargs.get("params")
        logger.warning(
            f"Shittim API `{url}` returned error code {code}, {params=}, {resp=}",
        )

    return resp["data"]


async def get_season_list() -> List[Season]:
    return type_validate_python(List[Season], await shittim_get("api/season/list"))


def get_rank_list(
    server: ServerType,
    data_type: RankDataType,
    season: int,
    **pf_kwargs: Unpack[IterPFKwargs],
) -> AsyncIterable[RankRecord]:
    @iter_pagination_func(**pf_kwargs)
    async def iterator(page: int, size: int, delay: float):
        ret = type_validate_python(
            Rank,
            await shittim_get(
                f"api/rank/list/{server.value}/{data_type.value}/{season}",
                params={"page": page, "size": size},
                sleep=delay,
            ),
        )
        return ret.records, True if (not ret.records) else ret.last_page

    return iterator()


async def get_rank_list_top(
    server: ServerType,
    season: int,
) -> List[RankSummary]:
    return type_validate_python(
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
    return type_validate_python(
        List[RankSummary],
        await shittim_get(
            "api/rank/list_by_last_rank",
            params={"server": server.value, "season": season},
        ),
    )


async def get_raid_chart_data(server: ServerType, season: int) -> RaidChart:
    return type_validate_python(
        RaidChart,
        await shittim_get(f"raid/new/charts/{server.value}", params={"s": season}),
    )


async def get_participation_chart_data(
    server: ServerType,
    season: int,
) -> ParticipationChart:
    return type_validate_python(
        ParticipationChart,
        await shittim_get(
            "api/rank/season/lastRank/charts",
            params={"server": server.value, "season": season},
        ),
    )


async def get_alice_friends(server: ServerType) -> Dict[int, RankRecord]:
    return type_validate_python(
        Dict[int, RankRecord],
        await shittim_get("api/rank/list_20001", params={"server": server.value}),
    )


async def get_diligent_achievers(server: ServerType) -> Dict[int, RankRecord]:
    return type_validate_python(
        Dict[int, RankRecord],
        await shittim_get("api/rank/list_1", params={"server": server.value}),
    )


async def get_student_icon(student_id: Union[int, str]) -> bytes:
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


VIEWPORT_SIZE = ViewportSize(width=880, height=1080)

CHART_SHOW_RANKS = [1, 1000, 2000, 4000, 8000, 20000]
MULTIPLIER = 2
CHART_W = 760
CHART_H = 480
DATE_FORMAT = "%m-%d %H:%M"
NUM_FORMAT = "{x:,.0f}"
DATE_FORMATTER = mdates.DateFormatter(DATE_FORMAT)
NUM_FORMATTER = mticker.StrMethodFormatter(NUM_FORMAT)


def get_figure() -> Figure:
    figure = pyplot.figure()
    figure.set_dpi(figure.dpi * MULTIPLIER)
    figure.set_size_inches(
        CHART_W * MULTIPLIER / figure.dpi,
        CHART_H * MULTIPLIER / figure.dpi,
    )
    return figure


def save_figure(figure: Figure) -> bytes:
    bio = BytesIO()
    figure.savefig(bio, transparent=True, format="png")
    return bio.getvalue()


def ax_settings(ax: Axes) -> None:
    ax.grid()
    ax.legend(loc="lower right")
    ax.xaxis.set_major_formatter(DATE_FORMATTER)
    ax.yaxis.set_major_formatter(NUM_FORMATTER)
    ax.tick_params(axis="x", labelrotation=15)


def render_raid_chart(data: RaidChart) -> bytes:
    figure = get_figure()

    ax = figure.add_subplot()
    for key in CHART_SHOW_RANKS:
        if (not data.data) or (key not in data.data) or (not (y := data.data[key])):
            continue
        x = data.time[: len(y)]
        ax.plot(
            x,  # type: ignore
            y,  # type: ignore
            label=(
                f"{' ' * (10 - (len(str(key)) * 2))}{key} | "
                f"{x[-1].strftime(DATE_FORMAT)} | "
                f"{NUM_FORMAT.format(x=y[-1])}"
            ),
        )
    ax_settings(ax)

    figure.tight_layout()
    return save_figure(figure)


def render_participation_chart(data: ParticipationChart) -> bytes:
    figure = get_figure()

    ax = figure.add_subplot()
    ax.plot(
        data.key,  # type: ignore
        data.value,
        label=(
            "Participants | "
            f"{data.key[-1].strftime(DATE_FORMAT)} | "
            f"{NUM_FORMAT.format(x=data.value[-1])}"
        ),
    )
    ax_settings(ax)

    figure.tight_layout()
    return save_figure(figure)


def to_b64_url(data: bytes) -> str:
    return f"data:image/png;base64,{b64encode(data).decode()}"


async def render_raid_rank(
    server_name: str,
    data_type_name: str,
    season: Season,
    rank_list_top: List[RankSummary],
    rank_list_by_last_rank: List[RankSummary],
    rank_list: List[RankRecord],
    raid_chart: RaidChart,
    participation_chart: ParticipationChart,
) -> bytes:
    template = template_env.get_template("content_raid_rank.html.jinja")
    raid_chart_url = to_b64_url(render_raid_chart(raid_chart))
    participation_chart_url = to_b64_url(
        render_participation_chart(participation_chart),
    )
    return await get_template_renderer(
        template,
        selector=".wrapper",
        viewport=VIEWPORT_SIZE,
    )(
        server_name=server_name,
        data_type_name=data_type_name,
        season=season,
        rank_list_top=rank_list_top,
        rank_list_by_last_rank=rank_list_by_last_rank,
        rank_list=rank_list,
        raid_chart_url=raid_chart_url,
        participation_chart_url=participation_chart_url,
        shittim_url=config.ba_shittim_url,
    )


async def render_rank_detail(
    title: str,
    season_list: List[Season],
    rank_list: Dict[int, RankRecord],
) -> bytes:
    template = template_env.get_template("content_rank_detail.html.jinja")
    return await get_template_renderer(
        template,
        selector=".wrapper",
        viewport=VIEWPORT_SIZE,
    )(
        title=title,
        seasons={x.season: x for x in season_list},
        rank_list=sorted(rank_list.items(), key=lambda x: x[0], reverse=True),
        shittim_url=config.ba_shittim_url,
    )


async def render_raid_analysis() -> bytes:
    async with get_new_page(viewport=VIEWPORT_SIZE) as page:
        await page.goto(RAID_ANALYSIS_URL, wait_until="networkidle")

        await page.evaluate(SHITTIM_UTIL_JS_PATH.read_text(encoding="u8"))
        await page.add_style_tag(content=SHITTIM_UTIL_CSS_PATH.read_text(encoding="u8"))

        elem = await page.query_selector(".content")
        assert elem
        return await elem.screenshot(type="jpeg")


# endregion


RES_TYPE_SHITTIM_STUDENT_ICON = "shittim_student_icon"


@bawiki_router(rf"^{RES_ROUTE_URL}/{RES_TYPE_SHITTIM_STUDENT_ICON}/(\d+)$")
async def _(url: URL, route: Route, **_):
    student_id = url.parts[-1]
    icon = await get_student_icon(student_id)
    return await route.fulfill(body=icon, content_type="image/png")
