import asyncio
import math
import random
import re
import time
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from aiohttp import ClientSession

from const import UNLOCK_L2D_FAV


async def game_kee_request(url, **kwargs):
    async with ClientSession() as s:
        async with s.get(
                url, headers={"game-id": "0", "game-alias": "ba"}, **kwargs
        ) as r:
            ret = await r.json()
            if not ret["code"] == 0:
                raise ConnectionError(ret["msg"])
            return ret["data"]


async def get_stu_li():
    ret = await game_kee_request("https://ba.gamekee.com/v1/wiki/entry")

    li = None
    for i in ret["entry_list"]:
        if i["id"] == 23941:

            for ii in i["child"]:
                if ii["id"] == 49443:
                    li = ii["child"]

    return {x["name"]: x for x in li}


async def test_l2d_fav():
    v = []
    s = await get_stu_li()
    for i in UNLOCK_L2D_FAV.values():
        v.extend(i)
    for i in v:
        if not (i in s.keys()):
            print(i)


async def get_stu_dict():
    s = await get_stu_li()
    l = {x: "" for x in s}

    for x, y in s.items():
        try:
            r: dict = await game_kee_request(
                f"https://ba.gamekee.com/v1/content/detail/{y}"
            )
            r: str = r["content"]

            i = r.find('<div class="input-wrapper">官方介绍</div>')
            i = r.find('class="slide-item" data-index="2"', i)
            ii = r.find('data-index="3"', i)

            r: str = r[i:ii]

            img = re.findall('data-real="([^"]*)"', r)

            for i in img:
                if ".gif" in i:
                    l[x] = i

            if not l[x]:
                l[x] = img[0]

            l[x] = "https:" + l[x]
            print(x, l[x])
        except:
            print(f"err:{x}")
        time.sleep(random.randint(1, 5))

    print("{")
    for x, y in l.items():
        print(f'    "{x}":"{y}",')
    print("}")


async def draw_fav_li(lvl):
    li = ['美咲', "美游"]

    txt_h = 96
    pic_h = 456
    icon_w = 404
    icon_h = pic_h + txt_h
    line_max_icon = 9
    txt_y_offset = -8

    if (l := len(li)) <= line_max_icon:
        line = 1
        length = l
    else:
        line = math.ceil(l / line_max_icon)
        length = line_max_icon

    img = Image.new('RGB', (icon_w * length, icon_h * line), (255, 255, 255))
    font = ImageFont.truetype(str((Path(__file__).parent / 'res' / 'SourceHanSansSC-Bold-2.otf')), 50)

    async def draw_stu(name_, url_, line_, index_):
        img_card = Image.new('RGB', (icon_w, icon_h), (255, 255, 255))

        async with ClientSession() as s:
            async with s.get(f'https:{url_}') as r:
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
        task_li.append(draw_stu(stu, stu_li[stu]['icon'], l, i))
        i += 1
    await asyncio.gather(*task_li)

    ret_io = BytesIO()
    img.save(ret_io, 'PNG')
    img.show()


if __name__ == "__main__":
    asyncio.run(draw_fav_li(5))
