import asyncio
from typing import TYPE_CHECKING

from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher
from nonebot.typing import T_State

from ..data.shittim_chest import (
    RANK_DATA_TYPE_NAME_MAP,
    SERVER_NAME_MAP,
    RankDataType,
    ServerType,
    async_iter_all,
    get_rank_list,
    get_rank_list_by_last_rank,
    get_rank_list_top,
    get_season_list,
    render_raid_rank,
)
from ..help import FT_E, FT_S

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "国服总力档线",
        "trigger_method": "指令",
        "trigger_condition": "ba档线",
        "brief_des": "从什亭之匣查询国服总力档线",
        "detail_des": (
            "从什亭之匣查询国服指定服务器和期数的总力档线或排名\n"
            "目前仅支持查询官服最新期数的数据\n"
            " \n"
            "可以用这些指令触发：\n"
            f"- {FT_S}ba档线{FT_E}\n"
            f"- {FT_S}ba总力档线{FT_E}"
            " \n"
            "可以用这些指令查询总力排名：\n"
            f"- {FT_S}ba排名{FT_E}\n"
            f"- {FT_S}ba总力排名{FT_E}"
        ),
    },
]


cmd_raid_rank = on_command(
    "ba排名",
    aliases={"ba总力排名"},
    state={"data_type": RankDataType.Rank},
)
cmd_raid_score = on_command(
    "ba档线",
    aliases={"ba总力档线"},
    state={"data_type": RankDataType.Score},
)


@cmd_raid_rank.handle()
@cmd_raid_score.handle()
async def _(matcher: Matcher, state: T_State):
    server = ServerType.Official
    data_type: RankDataType = state["data_type"]

    server_name = SERVER_NAME_MAP[server.value]
    data_type_name = RANK_DATA_TYPE_NAME_MAP[data_type.value]

    try:
        seasons = await get_season_list()
        season = seasons[0]
        rank_list_top, rank_list_by_last_rank, rank_list = await asyncio.gather(
            get_rank_list_top(server, season.season),
            get_rank_list_by_last_rank(server, season.season),
            async_iter_all(get_rank_list(server, data_type, season.season)),
        )
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
        )
    except Exception:
        logger.exception("Error when rendering image")
        await matcher.finish("渲染图片时出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))
