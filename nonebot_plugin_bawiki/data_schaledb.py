import asyncio
import math
import time
from datetime import datetime
from io import BytesIO

from PIL import Image, ImageFilter
from aiohttp import ClientSession
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_htmlrender import get_new_page
from nonebot_plugin_imageutils import BuildImage, text2image
from playwright.async_api import Page, ViewportSize

from .config import config
from .const import MIRROR_SCHALE_URL, RES_SCHALE_BG, SCHALE_DB_DIFFERENT, SCHALE_URL
from .util import parse_time_delta

PAGE_KWARGS = {
    "is_mobile": True,
    "viewport": ViewportSize(width=767, height=800),
}


async def schale_get(suffix, raw=False):
    async with ClientSession() as c:
        async with c.get(f"{SCHALE_URL}{suffix}", proxy=config.proxy) as r:
            return (await r.read()) if raw else (await r.json())


async def schale_get_stu_data():
    return await schale_get("data/cn/students.min.json")


async def schale_get_common():
    return await schale_get("data/common.min.json")


async def schale_get_localization():
    return await schale_get("data/cn/localization.min.json")


async def schale_get_raids():
    return await schale_get("data/raids.min.json")


async def schale_get_stu_dict():
    ret = await schale_get_stu_data()
    data = {x["Name"].replace("(", "（").replace(")", "）"): x for x in ret}

    for schale, gamekee in SCHALE_DB_DIFFERENT.items():
        if schale in data:
            data[gamekee] = data[schale]
            del data[schale]

    return data


async def schale_get_stu_info(stu):
    async with get_new_page(**PAGE_KWARGS) as page:  # type:Page
        await page.goto(
            f"{MIRROR_SCHALE_URL}?chara={stu}",
            timeout=60 * 1000,
            wait_until="networkidle",
        )

        # 进度条拉最大
        await page.add_script_tag(content="utilStuSetAllProgressMax();")

        return await page.screenshot(full_page=True)


async def schale_get_calender(server=1):
    students, common, localization, raids = await asyncio.gather(
        schale_get_stu_data(),
        schale_get_common(),
        schale_get_localization(),
        schale_get_raids(),
    )
    students = {x["Id"]: x for x in students}

    region = common["regions"][server]
    now = datetime.now()

    pic_bg = BuildImage.new("RGBA", (1400, 640), (255, 255, 255, 70))

    def find_event(ev):
        for _e in ev:
            _start = datetime.fromtimestamp(_e["start"])
            _end = datetime.fromtimestamp(_e["end"])
            if _start <= now < _end:
                _remain = _end - now
                return _e, _start, _end, _remain

    def format_time(_start, _end, _remain):
        dd, hh, mm, ss = parse_time_delta(_remain)
        return (
            f"{_start} ~ {_end} | "
            f"剩余 [b][color=#fc6475]{dd}天 {hh:0>2d}:{mm:0>2d}:{ss:0>2d}[color=#fc6475][/b]"
        )

    async def draw_gacha():
        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150), "特选招募", weight="bold", max_fontsize=80
        )
        c_gacha = region["current_gacha"]
        if r := find_event(c_gacha):
            g = r[0]
            t = format_time(*(r[1:]))
            pic = pic.paste(
                ti := text2image(
                    t, (255, 255, 255, 0), fontsize=45, max_width=1350, align="center"
                ),
                (int((1400 - ti.width) / 2), 150),
                True,
            )
            stu = [students[x] for x in g["characters"]]

            async def process_avatar(s):
                return (
                    BuildImage.open(
                        BytesIO(
                            await schale_get(
                                f'images/student/collection/{s["CollectionTexture"]}.webp',
                                raw=True,
                            )
                        )
                    )
                    .resize((300, 340))
                    .paste(
                        BuildImage.new("RGBA", (300, 65), (255, 255, 255, 120)),
                        (0, 275),
                        True,
                    )
                    .convert("RGB")
                    .circle_corner(25)
                    .draw_text((0, 275, 300, 340), s["PersonalName"], max_fontsize=50)
                )

            avatars = await asyncio.gather(*[process_avatar(x) for x in stu])
            ava_len = len(avatars)
            x_index = int((1400 - (300 + 25) * ava_len + 25) / 2)

            for p in avatars:
                pic = pic.paste(p, (x_index, 250), True)
                x_index += p.width + 25

            return pic

        return pic.draw_text((25, 200, 1375, 615), "没有获取到数据", max_fontsize=60)

    async def draw_event():
        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150), "当前活动", weight="bold", max_fontsize=80
        )
        c_event = region["current_events"]
        if r := find_event(c_event):
            g = r[0]
            t = format_time(*(r[1:]))
            pic = pic.paste(
                ti := text2image(
                    t, (255, 255, 255, 0), fontsize=45, max_width=1350, align="center"
                ),
                (int((1400 - ti.width) / 2), 150),
                True,
            )
            ev = g["event"]
            ev_name = ""
            if ev >= 10000:
                ev_name = " (复刻)"
                ev %= 10000
            ev_name = localization["EventName"][str(ev)] + ev_name

            ev_bg, ev_img = await asyncio.gather(
                schale_get(f"images/campaign/Campaign_Event_{ev}_Normal.png", True),
                schale_get(
                    f"images/eventlogo/Event_{ev}_{'Tw' if server else 'Jp'}.png", True
                ),
            )

            ev_bg = (
                BuildImage.open(BytesIO(ev_bg))
                .convert("RGBA")
                .resize_height(340)
                .filter(ImageFilter.GaussianBlur(3))
            )
            ev_bg = (
                ev_bg.paste(
                    BuildImage.open(BytesIO(ev_img))
                    .convert("RGBA")
                    .resize(
                        (ev_bg.width, ev_bg.height - 65),
                        keep_ratio=True,
                        inside=True,
                        bg_color=(255, 255, 255, 0),
                    ),
                    alpha=True,
                )
                .paste(
                    BuildImage.new("RGBA", (ev_bg.width, 65), (255, 255, 255, 120)),
                    (0, ev_bg.height - 65),
                    True,
                )
                .convert("RGB")
                .circle_corner(25)
                .draw_text(
                    (0, ev_bg.height - 65, ev_bg.width, ev_bg.height), ev_name, 50
                )
            )
            return pic.paste(ev_bg, (int((pic.width - ev_bg.width) / 2), 250), True)

        return pic.draw_text((25, 200, 1375, 615), "没有获取到数据", max_fontsize=60)

    async def draw_raid():
        pic = pic_bg.copy()
        c_raid = region["current_raid"]
        if r := find_event(c_raid):
            ri = r[0]
            t = format_time(*(r[1:]))
            pic = pic.paste(
                ti := text2image(
                    t, (255, 255, 255, 0), fontsize=45, max_width=1350, align="center"
                ),
                (int((1400 - ti.width) / 2), 150),
                True,
            )

            tp = "TimeAttack" if (time_atk := (ri["raid"] >= 1000)) else "Raid"
            raid = {x["Id"]: x for x in raids[tp]}
            c_ri = raid[ri["raid"]]
            pic = pic.draw_text(
                (25, 25, 1375, 150),
                localization["StageType"][tp],
                weight="bold",
                max_fontsize=80,
            )

            detail = (
                localization["TimeAttackStage"][c_ri["DungeonType"]]
                if time_atk
                else (c_ri["NameCn"] or c_ri["NameJp"])
            )
            atk_t = c_ri["Terrain"] if time_atk else ri.get("terrain")
            detail += f' | {localization["AdaptationType"][atk_t]}战'
            detail += f' | {localization["ArmorType"][c_ri["ArmorType"]]}'
            if not time_atk:
                detail += f' | Insane难度攻击类型：{localization["BulletType"][c_ri["BulletTypeInsane"]]}'

        return pic.draw_text((25, 200, 1375, 615), "没有获取到数据", max_fontsize=60)

    async def draw_birth():
        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150), "学生生日", weight="bold", max_fontsize=80
        )
        now_t = time.mktime(now.date().timetuple())
        now_w = now.weekday()
        this_week_t = now_t - now_w * 86400
        next_week_t = now_t + (7 - now_w) * 86400
        next_next_week_t = next_week_t + 7 * 86400

        birth_this_week = []
        birth_next_week = []
        for s in [x for x in students.values() if x["IsReleased"][server]]:
            birth = time.mktime(
                time.strptime(f'{now.year}/{s["BirthDay"]}', "%Y/%m/%d")
            )
            if this_week_t <= birth < next_week_t:
                birth_this_week.append(s)
            elif next_week_t <= birth <= next_next_week_t:
                birth_next_week.append(s)

        sort_key = lambda x: x["BirthDay"].split("/")
        pattern = "- {PersonalName} {Birthday}"
        if birth_this_week:
            birth_this_week.sort(key=sort_key)
            s = "\n".join([pattern.format(**x) for x in birth_this_week])

        if birth_next_week:
            birth_next_week.sort(key=sort_key)
            s = "\n".join([pattern.format(**x) for x in birth_next_week])

        return pic.draw_text((25, 200, 1375, 615), "没有学生近期生日", max_fontsize=60)

    img = await asyncio.gather(draw_gacha(), draw_event(), draw_raid(), draw_birth())
    bg = (
        BuildImage.open(RES_SCHALE_BG)
        .convert("RGBA")
        .resize((1500, sum([x.height + 25 for x in img]) + 75), keep_ratio=True)
    )

    h_index = 50
    for im in img:
        bg.paste(im, (50, h_index), True)
        h_index += im.height + 25
    return bg.convert("RGB").save("png")


async def draw_fav_li(lvl):
    try:
        stu_li = [
            x
            for x in await schale_get_stu_data()
            if (x["MemoryLobby"] and x["MemoryLobby"][0] == lvl)
        ]
    except:
        logger.exception("获取schale db学生数据失败")
        return "获取SchaleDB学生数据失败，请检查后台输出"

    if not stu_li:
        return f"没有学生在羁绊等级{lvl}时解锁L2D"

    txt_h = 48
    pic_h = 144
    icon_w = 182
    icon_h = pic_h + txt_h
    line_max_icon = 6

    if (l := len(stu_li)) <= line_max_icon:
        line = 1
        length = l
    else:
        line = math.ceil(l / line_max_icon)
        length = line_max_icon

    img = BuildImage.open(RES_SCHALE_BG).resize(
        (icon_w * length, icon_h * line + 5), keep_ratio=True
    )

    async def draw_stu(name_, dev_name_, line_, index_):
        left = index_ * icon_w
        top = line_ * icon_h + 5
        async with ClientSession() as s:
            async with s.get(
                f"{SCHALE_URL}images/student/lobby/Lobbyillust_Icon_{dev_name_}_01.png",
                proxy=config.proxy,
            ) as r:
                ret = await r.read()
        icon_img = Image.open(BytesIO(ret)).convert("RGBA")
        img.paste(icon_img, (left, top), icon_img)
        img.draw_text(
            (left, top + pic_h, left + icon_w, top + icon_h),
            name_,
            max_fontsize=25,
            min_fontsize=1,
        )

    task_li = []
    l = 0
    i = 0
    for stu in stu_li:
        if i == line_max_icon:
            i = 0
            l += 1
        task_li.append(draw_stu(stu["Name"], stu["DevName"], l, i))
        i += 1
    await asyncio.gather(*task_li)

    return MessageSegment.text(f"羁绊等级 {lvl} 时解锁L2D的学生有以下这些：") + MessageSegment.image(
        img.save("png")
    )
