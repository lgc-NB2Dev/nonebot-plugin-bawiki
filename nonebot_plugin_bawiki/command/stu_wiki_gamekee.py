from typing import TYPE_CHECKING

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..config import config
from ..data.bawiki import recover_stu_alia
from ..data.gamekee import (
    game_kee_get_page,
    game_kee_get_stu_cid_li,
    game_kee_page_url,
)
from ..help import FT_E, FT_S
from ..util import send_forward_msg

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
            f"- {FT_S}ba学生wiki 白子{FT_E}\n"
            f"- {FT_S}ba学生wiki xcw{FT_E}"
        ),
    },
]


cmd_stu_wiki = on_command("ba学生wiki", aliases={"ba学生Wiki", "ba学生WIKI"})


@cmd_stu_wiki.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    matcher: Matcher,
    cmd_arg: Message = CommandArg(),
):
    arg = cmd_arg.extract_plain_text().strip()
    if not arg:
        await matcher.finish("请提供学生名称")

    try:
        ret = await game_kee_get_stu_cid_li()
    except Exception:
        logger.exception("获取学生列表出错")
        await matcher.finish("获取学生列表出错，请检查后台输出")

    if not ret:
        await matcher.finish("没有获取到学生列表数据")

    if not (sid := ret.get(await recover_stu_alia(arg, game_kee=True))):
        await matcher.finish("未找到该学生")

    url = game_kee_page_url(sid)
    await matcher.send(f"请稍等，正在截取Wiki页面……\n{url}")

    try:
        images = await game_kee_get_page(url)
    except Exception:
        logger.exception(f"截取wiki页面出错 {url}")
        await matcher.finish("截取页面出错，请检查后台输出")

    img_seg = [MessageSegment.image(x) for x in images]
    if config.ba_use_forward_msg:
        await send_forward_msg(bot, event, img_seg)
    else:
        await matcher.finish(Message(img_seg))
