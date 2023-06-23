from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..config import config
from ..data.bawiki import recover_stu_alia
from ..data.schaledb import schale_get_stu_dict, schale_get_stu_info

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "学生图鉴",
        "trigger_method": "指令",
        "trigger_condition": "ba学生图鉴",
        "brief_des": "查询学生详情（SchaleDB）",
        "detail_des": (
            "访问对应学生SchaleDB页面并截图，支持部分学生别名\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba学生图鉴 白子</ft>\n"
            "- <ft color=(238,120,0)>ba学生图鉴 xcw</ft>"
        ),
    },
]


cmd_stu_schale = on_command("ba学生图鉴")


@cmd_stu_schale.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        await matcher.finish("请提供学生名称")

    try:
        ret = await schale_get_stu_dict()
    except:
        logger.exception("获取学生列表出错")
        await matcher.finish("获取学生列表表出错，请检查后台输出")

    if not ret:
        await matcher.finish("没有获取到学生列表数据")

    if not (data := ret.get(await recover_stu_alia(arg))):
        await matcher.finish("未找到该学生")

    stu_name = data["PathName"]
    await matcher.send(f"请稍等，正在截取SchaleDB页面～\n{config.ba_schale_url}?chara={stu_name}")

    try:
        img = MessageSegment.image(await schale_get_stu_info(stu_name))
    except:
        logger.exception(f"截取schale db页面出错 chara={stu_name}")
        await matcher.finish("截取页面出错，请检查后台输出")

    await matcher.finish(img)
