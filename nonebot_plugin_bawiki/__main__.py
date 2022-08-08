from datetime import datetime
from pathlib import Path

import jinja2
from nonebot import logger, on_command
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page

from .data_source import get_calender, get_stu_li
from .util import format_timestamp

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

    for i in ret:
        if pic := i["picture"]:
            if (not pic.startswith("https:")) and (not pic.startswith("http:")):
                i["picture"] = "https:" + pic

        begin = i["begin_at"]
        end = i["end_at"]
        i["date"] = f"{format_timestamp(begin)} ~ {format_timestamp(end)}"

        time_remain = datetime.fromtimestamp(end) - datetime.now()
        mm, ss = divmod(time_remain.seconds, 60)
        hh, mm = divmod(mm, 60)
        i["dd"] = time_remain.days or 0
        i["hh"] = hh
        i["mm"] = mm
        i["ss"] = ss

    try:
        html = jinja2.Template(
            (Path(__file__).parent / "res" / "calender.html.jinja").read_text("utf-8")
        ).render(info=ret)

        async with get_new_page() as page:  # type:Page
            await page.set_content(html, wait_until="networkidle")
            pic = await (
                await page.query_selector('xpath=//div[@id="calendar-box"]')
            ).screenshot()
    except:
        logger.exception(f"渲染或截取页面出错")
        return await matcher.finish(f"渲染或截取页面出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(pic))


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

    if not (sid := ret.get(arg)):
        return await matcher.finish("未找到该学生")

    url = f"https://ba.gamekee.com/{sid}.html"
    await matcher.send(f"请稍等，正在截取Wiki页面……\n{url}")

    try:
        async with get_new_page() as page:  # type:Page
            await page.goto(url, wait_until="networkidle", timeout=60 * 1000)

            # 删掉header
            await page.add_script_tag(
                content='document.getElementsByClassName("wiki-header")'
                ".forEach((v)=>{v.remove()})"
            )

            # 展开折叠的语音
            folds = await page.query_selector_all(
                'xpath=//div[@class="fold-table-btn"]'
            )
            for i in folds:
                try:
                    await i.click()
                except:
                    pass

            img = await (
                await page.query_selector('xpath=//div[@class="wiki-detail-body"]')
            ).screenshot()
    except:
        logger.exception(f"截取wiki页面出错 {url}")
        return await matcher.finish(f"截取页面出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))
