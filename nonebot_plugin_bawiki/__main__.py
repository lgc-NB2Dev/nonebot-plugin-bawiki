from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg

from .const import L2D_LI, UNLOCK_L2D_FAV
from .data_source import (
    draw_fav_li,
    game_kee_page_url,
    get_calender,
    get_calender_page,
    get_game_kee_page,
    get_stu_cid_li,
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
        ret = await get_stu_cid_li()
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


l2d = on_command("bal2d", aliases={"baL2D", "balive2d", "baLive2D"})


@l2d.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    if not (url := L2D_LI.get(recover_stu_alia(arg))):
        if isinstance(url, str):
            await matcher.finish("该学生没有L2D或插件没有收录该学生的L2D")
        else:
            await matcher.finish("未找到该学生")
        return

    await matcher.finish(MessageSegment.image(url))


fav = on_command("ba好感度", aliases={"ba羁绊"})


@fav.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称或所需的羁绊等级")

    # 好感度等级
    if arg.isdigit():
        arg = int(arg)
        if arg > 9:
            return await matcher.finish("学生解锁L2D最高只需要羁绊等级9")
        if arg < 1:
            return await matcher.finish("学生解锁L2D最低只需要羁绊等级1")

        try:
            p = await draw_fav_li(arg)
        except:
            logger.exception("绘制图片出错")
            return await matcher.finish("绘制图片出错，请检查后台输出")

        return await matcher.finish(p)

    # 学生名称
    arg = recover_stu_alia(arg)
    for lvl, li in UNLOCK_L2D_FAV.items():
        for stu in li:
            if stu == arg:
                im = MessageSegment.text(f"{arg} 在羁绊等级 {lvl} 时即可解锁L2D\nL2D预览：")
                im += MessageSegment.image(p) if (p := L2D_LI.get(stu)) else "插件暂未收录"
                return await matcher.finish(im)

    return await matcher.finish("未找到学生，可能是学生不存在或者是该学生没有L2D")
