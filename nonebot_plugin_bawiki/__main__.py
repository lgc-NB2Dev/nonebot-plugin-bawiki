from nonebot import on_command, logger
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

    li = Message()
    for i in ret:
        des = i["title"] + (f"\n{x}" if (x := i["description"]) else "")
        des = des.replace("<br>", "")
        li += (
            f'{format_timestamp(i["begin_at"])} - {format_timestamp(i["end_at"])}\n'
            f"{des}"
        )

        if pic := i["picture"]:
            if (not pic.startswith("https:")) and (not pic.startswith("http:")):
                pic = "https:" + pic
            li += MessageSegment.image(pic)

        li += "\n==============\n"

    li.pop(-1)

    await matcher.finish(li)


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
        return matcher.finish("未找到该学生")

    url = f"https://ba.gamekee.com/{sid}.html"
    await matcher.send(f"请稍等，正在截取Wiki页面……\n{url}")

    try:
        async with get_new_page() as page:  # type:Page
            await page.goto(url)
            await page.wait_for_load_state("networkidle")

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
