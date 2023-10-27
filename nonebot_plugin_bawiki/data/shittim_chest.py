from datetime import datetime
from enum import Enum
from typing import Any, Dict, List
from typing_extensions import Unpack

from pydantic import BaseModel, Field, parse_obj_as, validator

from ..config import config
from ..util import AsyncReqKwargs, ResponseType, async_req, get_proxy_url


class ServerType(Enum):
    Official = 1  # 官服
    Bilibili = 2  # B服


class RankDataType(Enum):
    Rank = 1  # 排名
    Score = 2  # 档线


def time_validator(v: str):
    try:
        return datetime.strptime(v, "%Y-%m-%d %H:%M")
    except ValueError as e:
        raise ValueError(f"Time `{v}` format error") from e


class SeasonMap(BaseModel):
    key: str
    value: str


class Season(BaseModel):
    season: int
    season_map: SeasonMap = Field(alias="map")
    boss_id: int = Field(alias="bossId")
    boss: str
    start_time: datetime = Field(alias="startTime")
    end_time: datetime = Field(alias="endTime")

    _validator_time = validator(
        "start_time",
        "end_time",
        pre=True,
        allow_reuse=True,
    )(time_validator)


class Character(BaseModel):
    has_weapon: bool = Field(alias="hasWeapon")
    is_assist: bool = Field(alias="isAssist")
    level: int
    slot_index: int = Field(alias="slotIndex")
    star_grade: int = Field(alias="starGrade")
    unique_id: int = Field(alias="uniqueId")
    bullet_type: str = Field(alias="bulletType")
    tactic_role: str = Field(alias="tacticRole")


class TryNumberInfo(BaseModel):
    try_number: int = Field(alias="tryNumber")
    main_characters: List[Character] = Field(alias="mainCharacters")
    support_characters: List[Character] = Field(alias="supportCharacters")


class RankRecord(BaseModel):
    rank: int
    best_ranking_point: int = Field(alias="bestRankingPoint")
    level: int
    nickname: str
    represent_character_unique_id: int = Field(alias="representCharacterUniqueId")
    tier: int
    hard: str
    battle_time: str = Field(alias="battleTime")
    boss_id: int = Field(alias="bossId")
    try_number_infos: List[TryNumberInfo] = Field(alias="tryNumberInfos")
    record_time: datetime = Field(alias="recordTime")


class Rank(BaseModel):
    page: int
    size: int
    total_pages: int = Field(alias="totalPages")
    records: List[RankRecord]
    last_page: bool = Field(alias="lastPage")


class RaidChart(BaseModel):
    data: Dict[int, List[int]]
    time: List[datetime]


async def shittim_get(url: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    kwargs = kwargs.copy()
    kwargs["base_url"] = config.ba_shittim_chest_api_url
    kwargs["proxies"] = get_proxy_url(is_oversea=True)

    resp = await async_req(url, **kwargs)
    return resp["data"]


async def get_season_list() -> List[Season]:
    return parse_obj_as(List[Season], await shittim_get("api/season/list"))


async def get_rank_list(
    server: ServerType,
    date_type: RankDataType,
    season: int,
    page: int = 1,
    size: int = 100,
) -> Rank:
    return parse_obj_as(
        Rank,
        await shittim_get(
            f"api/rank/list/{server.value}/{date_type.value}/{season}",
            params={"page": page, "size": size},
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
    return await async_req(
        f"web_students_original_icon/{student_id}.png",
        base_url=config.ba_shittim_chest_data_url,
        response_type=ResponseType.BYTES,
    )
