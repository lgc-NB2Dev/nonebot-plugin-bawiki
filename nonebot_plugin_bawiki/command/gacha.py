from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional

from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..config import config
from ..data.bawiki import db_get_gacha_data, db_get_stu_alias
from ..data.gacha import gacha, get_gacha_cool_down, set_gacha_cool_down
from ..data.schaledb import schale_get_stu_dict
from ..util import recover_alia

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "模拟抽卡",
        "trigger_method": "指令",
        "trigger_condition": "ba抽卡",
        "brief_des": "模拟抽卡",
        "detail_des": (
            "模拟抽卡\n"
            "可以使用 <ft color=(238,120,0)>ba切换卡池</ft> 指令来切换卡池\n"
            "可以指定抽卡次数，默认10次\n"
            " \n"
            "可以用这些指令触发：\n"
            "- <ft color=(238,120,0)>ba抽卡</ft>\n"
            "- <ft color=(238,120,0)>ba招募</ft>\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba抽卡</ft>\n"
            "- <ft color=(238,120,0)>ba抽卡 20</ft>"
        ),
    },
    {
        "func": "切换卡池",
        "trigger_method": "指令",
        "trigger_condition": "ba切换卡池",
        "brief_des": "设置模拟抽卡的UP池",
        "detail_des": (
            "设置模拟抽卡功能的UP池角色\n"
            "默认从当前数据源UP池中轮流切换\n"
            "当参数为 <ft color=(238,120,0)>常驻</ft> 时，切换到常驻池（没有UP）\n"
            "可以自定义池子UP角色，支持2星与3星角色，参数中学生名称用空格分隔，支持部分学生别名\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba切换卡池</ft>\n"
            "- <ft color=(238,120,0)>ba切换卡池 常驻</ft>\n"
            "- <ft color=(238,120,0)>ba切换卡池 小桃 小绿</ft>"
        ),
    },
]


cmd_change_pool = on_command("ba切换卡池")
cmd_gacha_once = on_command("ba抽卡", aliases={"ba招募"})


@dataclass()
class GachaPool:
    name: str
    pool: List[int]
    index: Optional[int] = None


STATIC_POOL = GachaPool(name="常驻池", pool=[])
gacha_pool_index: Dict[str, GachaPool] = {}


def get_1st_pool(data: dict) -> Optional[GachaPool]:
    if not data:
        return None

    pool_data = data["current_pools"]
    if not pool_data:
        return None

    pool = pool_data[0]
    return GachaPool(name=pool["name"], pool=pool["pool"], index=0)


@cmd_change_pool.handle()
async def _(matcher: Matcher, event: MessageEvent, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip().lower()
    qq = event.get_user_id()

    if arg:
        if "常驻" in arg:
            current = STATIC_POOL
        else:
            pool = []
            try:
                stu_li = await schale_get_stu_dict()
                stu_alias = await db_get_stu_alias()
            except Exception:
                logger.exception("获取学生列表或别名失败")
                await matcher.finish("获取学生列表或别名失败，请检查后台输出")

            for i in arg.split():
                if not (stu := stu_li.get(recover_alia(i, stu_alias))):
                    await matcher.finish(f"未找到学生 {i}")
                if stu["StarGrade"] == 1:
                    await matcher.finish("不能UP一星角色")
                pool.append(stu)

            current = GachaPool(
                name=f"自定义卡池（{'、'.join([x['Name'] for x in pool])}）",
                pool=[x["Id"] for x in pool],
            )

    else:
        try:
            gacha_data = await db_get_gacha_data()
        except Exception:
            logger.exception("获取抽卡基本数据失败")
            await matcher.finish("获取抽卡基本数据失败，请检查后台输出")

        pool_data = gacha_data["current_pools"]
        first_pool = get_1st_pool(gacha_data)
        if not first_pool:
            await matcher.finish("当前没有可切换的卡池")

        pool_obj = gacha_pool_index.get(qq) or first_pool
        if not pool_obj:
            await matcher.finish("当前没有UP池可供切换")

        if (index := pool_obj.index) is not None:
            index += 1
            if len(pool_data) <= index:
                index = 0
        else:
            index = 0

        pool = pool_data[index]
        current = GachaPool(name=pool["name"], pool=pool["pool"], index=index)

    gacha_pool_index[qq] = current
    await matcher.finish(f"已切换到卡池 {current.name}")


@cmd_gacha_once.handle()
async def _(
    matcher: Matcher,
    event: MessageEvent,
    cmd_arg: Message = CommandArg(),
):
    user_id = event.user_id
    group_id = event.group_id if isinstance(event, GroupMessageEvent) else None

    if cool_down := get_gacha_cool_down(user_id, group_id):
        await matcher.finish(f"你先别急，先等 {cool_down} 秒再来抽吧qwq")

    gacha_times = 10
    arg = cmd_arg.extract_plain_text().strip().lower()
    if arg:
        if not arg.isdigit():
            await matcher.finish("请输入有效的整数")
        gacha_times = int(arg)
        if not (
            gacha_times >= 1
            and (config.ba_gacha_max < 1 or gacha_times <= config.ba_gacha_max)
        ):
            await matcher.finish(f"请输入有效的抽卡次数，在1~{config.ba_gacha_max}之间")

    try:
        gacha_data = await db_get_gacha_data()
    except Exception:
        logger.exception("获取抽卡基本数据失败")
        await matcher.finish("获取抽卡基本数据失败，请检查后台输出")

    pool_obj = gacha_pool_index.get(qq := event.get_user_id()) or get_1st_pool(
        gacha_data,
    )
    if not pool_obj:
        await matcher.send("数据源内没有提供当期UP池，已自动切换到常驻池")
        pool_obj = STATIC_POOL
        gacha_pool_index[qq] = STATIC_POOL

    set_gacha_cool_down(user_id, group_id)
    try:
        img = await gacha(qq, gacha_times, gacha_data, pool_obj.pool)
    except Exception:
        logger.exception("抽卡错误")
        await matcher.finish("抽卡出错了，请检查后台输出")

    await matcher.finish(
        MessageSegment.at(event.user_id) + f"当前抽取卡池：{pool_obj.name}" + img,
    )
