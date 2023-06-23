from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Message
from nonebot.internal.matcher import Matcher
from nonebot.log import logger
from nonebot.params import CommandArg

from ..data.bawiki import recover_stu_alia
from ..data.gamekee import game_kee_get_stu_cid_li, send_wiki_page

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "学生Wiki",
        "trigger_method": "指令",
        "trigger_condition": "ba学生wiki",
        "brief_des": "查询学生详情（GameKee）",
        "detail_des": (
            "访问对应学生GameKee Wiki页面并截图，支持部分学生别名\n"
            " \n"
            "指令示例：\n"
            "- <ft color=(238,120,0)>ba学生wiki 白子</ft>\n"
            "- <ft color=(238,120,0)>ba学生wiki xcw</ft>"
        ),
    },
]


cmd_stu_wiki = on_command("ba学生wiki", aliases={"ba学生Wiki", "ba学生WIKI"})


@cmd_stu_wiki.handle()
async def _(matcher: Matcher, cmd_arg: Message = CommandArg()):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        await matcher.finish("请提供学生名称")

    try:
        ret = await game_kee_get_stu_cid_li()
    except:
        logger.exception("获取学生列表出错")
        await matcher.finish("获取学生列表出错，请检查后台输出")

    if not ret:
        await matcher.finish("没有获取到学生列表数据")

    if not (sid := ret.get(await recover_stu_alia(arg, True))):
        await matcher.finish("未找到该学生")

    await send_wiki_page(sid, matcher)
