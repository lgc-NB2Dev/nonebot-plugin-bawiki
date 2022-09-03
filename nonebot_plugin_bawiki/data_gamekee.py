import time
from datetime import datetime
from pathlib import Path

import jinja2
from aiohttp import ClientSession
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page

from .const import STU_ALIAS
from .util import format_timestamp


async def game_kee_request(url, **kwargs):
    async with ClientSession() as s:
        async with s.get(
            url, headers={"game-id": "0", "game-alias": "ba"}, **kwargs
        ) as r:
            ret = await r.json()
            if ret["code"] != 0:
                raise ConnectionError(ret["msg"])
            return ret["data"]


async def get_calender():
    ret = await game_kee_request("https://ba.gamekee.com/v1/wiki/index")

    for i in ret:
        if i["module"]["id"] == 12:
            li: list = i["list"]

            now = time.time()
            li = [x for x in li if (x["end_at"] >= now >= x["begin_at"])]

            li.sort(key=lambda x: x["end_at"])
            li.sort(key=lambda x: x["importance"], reverse=True)
            return li


async def get_stu_li():
    ret = await game_kee_request("https://ba.gamekee.com/v1/wiki/entry")

    for i in ret["entry_list"]:
        if i["id"] == 23941:

            for ii in i["child"]:
                if ii["id"] == 49443:
                    return {x["name"]: x for x in ii["child"]}


async def get_stu_cid_li():
    return {x: y["content_id"] for x, y in (await get_stu_li()).items()}


def game_kee_page_url(sid):
    return f"https://ba.gamekee.com/{sid}.html"


async def get_game_kee_page(url):
    async with get_new_page() as page:  # type:Page
        await page.goto(url, timeout=60 * 1000)

        # 删掉header
        await page.add_script_tag(
            content='document.getElementsByClassName("wiki-header")'
            ".forEach((v)=>{v.remove()})"
        )

        # 展开折叠的语音
        folds = await page.query_selector_all('xpath=//div[@class="fold-table-btn"]')
        for i in folds:
            try:
                await i.click()
            except:
                pass

        return await (
            await page.query_selector('xpath=//div[@class="wiki-detail-body"]')
        ).screenshot()


async def get_calender_page(ret):
    for i in ret:
        if pic := i["picture"]:
            if (not pic.startswith("https:")) and (not pic.startswith("http:")):
                i["picture"] = f"https:{pic}"

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

    html = jinja2.Template(
        (Path(__file__).parent / "res" / "calender.html.jinja").read_text("utf-8")
    ).render(info=ret)

    async with get_new_page() as page:  # type:Page
        await page.set_content(html)
        return await (
            await page.query_selector('xpath=//div[@id="calendar-box"]')
        ).screenshot()


def recover_alia(origin: str, alia_dict: dict):
    origin = origin.lower()

    # 精确匹配
    for k, li in alia_dict.items():
        if origin in li or origin == k:
            return k

    # 没找到，模糊匹配
    for k, li in alia_dict.items():
        li = [k] + li
        for v in li:
            if (v in origin) or (origin in v):
                return k

    return origin


def recover_stu_alia(a):
    return recover_alia(a, STU_ALIAS)
