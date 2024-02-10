from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..data.gamekee import extract_content_pic, get_level_list
from ..help import FT_E, FT_S
from ..util import RespType as Rt, async_req

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "关卡攻略",
        "trigger_method": "指令",
        "trigger_condition": "ba关卡",
        "brief_des": "获取关卡攻略",
        "detail_des": (
            "获取指定关卡攻略\n"
            "来源：GameKee\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba关卡 1-1{FT_E}\n"
            f"- {FT_S}ba关卡 H1-1{FT_E}"
        ),
    },
]


cmd_level_guide = on_command("ba关卡")


@cmd_level_guide.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg_str = arg.extract_plain_text().strip().upper()
    if not arg_str:
        await matcher.finish("请输入关卡名称")

    try:
        levels = await get_level_list()
    except Exception:
        logger.exception("获取关卡列表失败")
        await matcher.finish("获取关卡列表失败，请检查后台输出")

    if arg_str not in levels:
        await matcher.finish("未找到该关卡，请检查关卡名称是否正确")

    cid = levels[arg_str]
    try:
        imgs = await extract_content_pic(cid)
    except Exception:
        logger.exception("获取攻略图片失败")
        await matcher.finish("获取攻略图片失败，请检查后台输出")

    msg = Message()
    msg += f"https://ba.gamekee.com/{cid}.html\n"
    msg += [MessageSegment.image(await async_req(x, resp_type=Rt.BYTES)) for x in imgs]
    await matcher.finish(msg)
