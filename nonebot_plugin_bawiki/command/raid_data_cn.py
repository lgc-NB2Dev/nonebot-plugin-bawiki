import asyncio
from typing import TYPE_CHECKING, Awaitable, Callable, Dict, Optional, Tuple

from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.adapters.onebot.v11.message import Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.typing import T_State

from ..config import config
from ..data.shittim_chest import (
    RAID_ANALYSIS_URL,
    RANK_DATA_TYPE_NAME_MAP,
    SERVER_NAME_MAP,
    RankDataType,
    RankRecord,
    Season,
    ServerType,
    async_iter_all,
    get_alice_friends,
    get_diligent_achievers,
    get_participation_chart_data,
    get_raid_chart_data,
    get_rank_list,
    get_rank_list_by_last_rank,
    get_rank_list_top,
    get_season_list,
    render_raid_analysis,
    render_raid_rank,
    render_rank_detail,
)
from ..help import FT_E, FT_S

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "国服总力数据",
        "trigger_method": "指令",
        "trigger_condition": "ba帮助 国服总力",
        "brief_des": "从什亭之匣查询国服总力相关数据",
        "detail_des": (
            "查询国服总力相关数据\n"
            f"数据来源：什亭之匣（{config.ba_shittim_url}）\n"
            " \n"
            "下面指令中的可选参数介绍，每个参数间需以空格分隔：\n"
            f"- {FT_S}服务器名称{FT_E} 可选值 “官服” 或 “B服”，默认为官服；\n"
            f"- {FT_S}期数序号{FT_E} 可以使用指令 {FT_S}ba总力列表{FT_E} 查询，默认为最新一期；\n"
            " \n"
            "使用以下指令查询总力档线：（可选参数：服务器名称、期数序号）\n"
            f"- {FT_S}ba总力档线{FT_E}\n"
            f"- {FT_S}ba档线{FT_E}\n"
            " \n"
            "使用以下指令查询总力统计概览：（无参数）\n"
            f"- {FT_S}ba总力统计{FT_E}\n"
            " \n"
            "使用以下指令查询往期总力第 1 名：（可选参数：服务器名称）\n"
            f"- {FT_S}ba小心卷狗{FT_E}\n"
            " \n"
            "使用以下指令查询往期总力第 20001 名：（可选参数：服务器名称）\n"
            f"- {FT_S}ba爱丽丝的伙伴{FT_E}\n"
            f"- {FT_S}ba爱丽丝伙伴{FT_E}"
        ),
    },
]


def parse_args(raw_arg: str) -> Tuple[ServerType, Optional[int]]:
    args = raw_arg.strip().split()

    server = ServerType.Official
    season: Optional[int] = None

    for arg in args:
        if server_id := next(
            (k for k, v in SERVER_NAME_MAP.items() if v.lower() == arg.lower()),
            None,
        ):
            server = ServerType(server_id)
        elif arg.isdigit():
            season = int(arg)
        else:
            raise ValueError(f"参数 `{arg}` 无效")

    return server, season


async def get_season_by_index(season_index: Optional[int]) -> Season:
    seasons = await get_season_list()
    return (
        seasons[0]
        if season_index is None
        else next(x for x in seasons if x.season == season_index)
    )


cmd_raid_list = on_command("ba总力列表")


@cmd_raid_list.handle()
async def _(matcher: Matcher):
    try:
        seasons = await get_season_list()
    except Exception:
        logger.exception("Error when getting rank data")
        await matcher.finish("获取数据时出错，请检查后台输出")

    if not seasons:
        await matcher.finish("暂无数据")

    # seasons.sort(key=lambda season: season.season, reverse=True)
    await matcher.finish(
        "\n".join(
            f"第 {season.season} 期 - {season.season_map.value} {season.boss}"
            for season in seasons
        ),
    )


cmd_raid_score = on_command(
    "ba总力档线",
    aliases={"ba档线"},
    state={"data_type": RankDataType.Score},
)


@cmd_raid_score.handle()
async def _(matcher: Matcher, state: T_State, arg_msg: Message = CommandArg()):
    try:
        server, season_index = parse_args(arg_msg.extract_plain_text())
    except ValueError as e:
        await matcher.finish(str(e))

    data_type: RankDataType = state["data_type"]

    server_name = SERVER_NAME_MAP[server.value]
    data_type_name = RANK_DATA_TYPE_NAME_MAP[data_type.value]

    try:
        season = await get_season_by_index(season_index)
        season_index = season.season
        (
            rank_list_top,
            rank_list_by_last_rank,
            rank_list,
            raid_chart,
            participation_chart,
        ) = await asyncio.gather(
            get_rank_list_top(server, season_index),
            get_rank_list_by_last_rank(server, season_index),
            async_iter_all(get_rank_list(server, data_type, season_index)),
            get_raid_chart_data(server, season_index),
            get_participation_chart_data(server, season_index),
        )
    except StopIteration:
        await matcher.finish("期数不存在")
    except Exception:
        logger.exception("Error when getting rank data")
        await matcher.finish("获取数据时出错，请检查后台输出")

    if not rank_list:
        await matcher.finish(f"暂无{data_type_name}数据")

    try:
        img = await render_raid_rank(
            server_name,
            data_type_name,
            season,
            rank_list_top,
            rank_list_by_last_rank,
            rank_list,
            raid_chart,
            participation_chart,
        )
    except Exception:
        logger.exception("Error when rendering image")
        await matcher.finish("渲染图片时出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))


cmd_raid_analysis = on_command("ba总力统计")


@cmd_raid_analysis.handle()
async def _(matcher: Matcher):
    try:
        img = await render_raid_analysis()
    except Exception:
        logger.exception("Error when rendering image")
        await matcher.finish("渲染图片时出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img) + f"详情请访问 {RAID_ANALYSIS_URL}")


cmd_alice_friends = on_command(
    "ba爱丽丝的伙伴",
    aliases={"ba爱丽丝伙伴"},
    state={"func": get_alice_friends, "title": "爱丽丝的伙伴"},
)
cmd_diligent_achievers = on_command(
    "ba小心卷狗",
    state={"func": get_diligent_achievers, "title": "小心卷狗"},
)


@cmd_alice_friends.handle()
@cmd_diligent_achievers.handle()
async def _(matcher: Matcher, state: T_State, arg_msg: Message = CommandArg()):
    try:
        server, _ = parse_args(arg_msg.extract_plain_text())
    except ValueError as e:
        await matcher.finish(str(e))

    title: str = f'{state["title"]}（{SERVER_NAME_MAP[server.value]}）'
    func: Callable[[ServerType], Awaitable[Dict[int, RankRecord]]] = state["func"]

    try:
        season_list, rank_list = await asyncio.gather(get_season_list(), func(server))
    except Exception:
        logger.exception("Error when getting rank data")
        await matcher.finish("获取数据时出错，请检查后台输出")

    try:
        img = await render_rank_detail(title, season_list, rank_list)
    except Exception:
        logger.exception("Error when rendering image")
        await matcher.finish("渲染图片时出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))
