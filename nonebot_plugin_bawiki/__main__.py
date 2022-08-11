from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg

from .const import L2D_LI
from .data_source import (
    game_kee_page_url,
    get_calender,
    get_calender_page,
    get_game_kee_page,
    get_stu_li,
    recover_stu_alia,
)

handler_calender = on_command("ba日程表")


@handler_calender.handle()
async def _(matcher: Matcher):
    try:
        ret = await get_calender()
    except:
        logger.exception("获取日程表出错")
        return await matcher.finish("获取日程表出错，请检查后台输出")

    if not ret:
        return await matcher.finish("没有获取到数据")

    try:
        pic = await get_calender_page(ret)
    except:
        logger.exception(f"渲染或截取页面出错")
        return await matcher.finish(f"渲染或截取页面出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(pic))


async def send_wiki_page(sid, matcher: Matcher):
    url = game_kee_page_url(sid)
    await matcher.send(f"请稍等，正在截取Wiki页面……\n{url}")

    try:
        img = await get_game_kee_page(url)
    except:
        logger.exception(f"截取wiki页面出错 {url}")
        return await matcher.finish(f"截取页面出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))


stu_wiki = on_command("ba学生图鉴")


@stu_wiki.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    try:
        ret = await get_stu_li()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表表出错，请检查后台输出")

    if not ret:
        return await matcher.finish("没有获取到学生列表数据")

    if not (sid := ret.get(recover_stu_alia(arg))):
        return await matcher.finish("未找到该学生")

    await send_wiki_page(sid, matcher)


new_stu = on_command("ba新学生")


@new_stu.handle()
async def _(matcher: Matcher):
    await send_wiki_page(155684, matcher)


l2d = on_command("bal2d")


@l2d.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    if not (url := L2D_LI.get(recover_stu_alia(arg))):
        return await matcher.finish("该学生没有L2D或插件没有收录该学生的L2D")

    await matcher.finish(MessageSegment.image(url))
