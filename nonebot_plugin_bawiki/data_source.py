import asyncio
import math
import time
from datetime import datetime
from io import BytesIO
from pathlib import Path

import jinja2
from PIL import Image, ImageDraw, ImageFont
from aiohttp import ClientSession
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page

from .const import STU_ALIAS, UNLOCK_L2D_FAV
from .util import format_timestamp


async def game_kee_request(url, **kwargs):
    async with ClientSession() as s:
        async with s.get(
            url, headers={"game-id": "0", "game-alias": "ba"}, **kwargs
        ) as r:
            ret = await r.json()
            if not ret["code"] == 0:
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


async def draw_fav_li(lvl):
    if not (li := UNLOCK_L2D_FAV.get(lvl)):
        return f"没有学生在羁绊等级{lvl}时解锁L2D"

    txt_h = 96
    pic_h = 456
    icon_w = 404
    icon_h = pic_h + txt_h
    line_max_icon = 6
    txt_y_offset = -8

    if (l := len(li)) <= line_max_icon:
        line = 1
        length = l
    else:
        line = math.ceil(l / line_max_icon)
        length = line_max_icon

    img = Image.new("RGB", (icon_w * length, icon_h * line), (255, 255, 255))
    font = ImageFont.truetype(
        str((Path(__file__).parent / "res" / "SourceHanSansSC-Bold-2.otf")), 50
    )

    async def draw_stu(name_, url_, line_, index_):
        img_card = Image.new("RGB", (icon_w, icon_h), (255, 255, 255))

        async with ClientSession() as s:
            async with s.get(f"https:{url_}") as r:
                ret = await r.read()
        icon_img = Image.open(BytesIO(ret))
        img_card.paste(icon_img, (0, 0))

        font_w, font_h = font.getsize(name_)
        draw_x = 0 if font_w >= icon_w else round((icon_w - font_w) / 2)
        draw_y = round((txt_h - font_h) / 2) + pic_h + txt_y_offset
        draw = ImageDraw.Draw(img_card)
        draw.text((draw_x, draw_y), name_, (0, 0, 0), font)

        img.paste(img_card, (index_ * icon_w, line_ * icon_h))

    stu_li = await get_stu_li()
    task_li = []
    l = 0
    i = 0
    for stu in li:
        if i == line_max_icon:
            i = 0
            l += 1
        task_li.append(draw_stu(stu, stu_li[stu]["icon"], l, i))
        i += 1
    await asyncio.gather(*task_li)

    ret_io = BytesIO()
    img.save(ret_io, "PNG")
    return MessageSegment.text(f"羁绊等级 {lvl} 时解锁L2D的学生有以下这些：") + MessageSegment.image(
        ret_io
    )
