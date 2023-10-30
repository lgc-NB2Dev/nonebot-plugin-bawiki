from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.log import logger
from nonebot.matcher import Matcher

from ..data.bawiki import db_wiki_furniture

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "互动家具总览",
        "trigger_method": "指令",
        "trigger_condition": "ba互动家具",
        "brief_des": "查询互动家具总览图",
        "detail_des": "发送咖啡厅内所有互动家具以及对应学生的总览图\n图片作者 B站@夜猫咪喵喵猫",
    },
]


cmd_furniture_wiki = on_command("ba互动家具")


@cmd_furniture_wiki.handle()
async def _(matcher: Matcher):
    try:
        im = await db_wiki_furniture()
    except Exception:
        logger.exception("获取互动家具wiki图片错误")
        await matcher.finish("获取图片失败，请检查后台输出")

    await matcher.finish(Message(im))
