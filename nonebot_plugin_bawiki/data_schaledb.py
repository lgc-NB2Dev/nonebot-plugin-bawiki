import asyncio
import math
import time
from datetime import date, datetime
from io import BytesIO

from PIL import Image
from aiohttp import ClientSession
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot_plugin_htmlrender import get_new_page
from nonebot_plugin_imageutils import BuildImage
from playwright.async_api import Page, ViewportSize

from .config import config
from .const import MIRROR_SCHALE_URL, RES_SCHALE_BG, SCHALE_DB_DIFFERENT, SCHALE_URL
from .util import parse_time_delta

PAGE_KWARGS = {
    "is_mobile": True,
    "viewport": ViewportSize(width=767, height=800),
}


async def schale_get(suffix):
    async with ClientSession() as c:
        async with c.get(f"{SCHALE_URL}{suffix}", proxy=config.proxy) as r:
            return await r.json()


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
    c_gacha = region["current_gacha"]
    c_event = region["current_events"]
    c_raid = region["current_raid"]
    now = datetime.now()

    def find_event(ev):
        for _e in ev:
            _start = datetime.fromtimestamp(_e["start"])
            _end = datetime.fromtimestamp(_e["end"])
            if _start <= now < _end:
                _remain = _end - now
                return _e, _start, _end, _remain

    def format_time(_start, _end, _remain):
        dd, hh, mm, ss = parse_time_delta(_remain)
        return f"{_start} ~ {_end} | 剩余 {dd}天 {hh:0>2d}:{mm:0>2d}:{ss:0>2d}"

    im = []
    if r := find_event(c_gacha):
        g = r[0]
        t = format_time(*(r[1:]))
        gacha_stu = "\n".join(
            [
                f'{x["Name"]}({"★" * x["StarGrade"]})'
                for x in [students[x] for x in g["characters"]]
            ]
        )
        im.append(f"当前卡池\n{t}\n{gacha_stu}")

    if r := find_event(c_event):
        g = r[0]
        t = format_time(*(r[1:]))
        ev = g["event"]
        ev_name = ""
        if ev >= 10000:
            ev_name = " 复刻"
            ev -= 10000
        ev_name = localization["EventName"][str(ev)] + ev_name
        im.append(f"当前活动\n{t}\n{ev_name}")

    if r := find_event(c_raid):
        ri = r[0]
        t = format_time(*(r[1:]))

        tp = "TimeAttack" if (time_atk := (ri["raid"] >= 1000)) else "Raid"
        raids = {x["Id"]: x for x in raids[tp]}
        c_ri = raids[ri["raid"]]

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
        im.append(f"{localization['StageType'][tp]}\n{t}\n{detail}")

    now_t = time.mktime(now.date().timetuple())
    now_w = now.weekday()
    this_week_t = now_t - now_w * 86400
    next_week_t = now_t + (7 - now_w) * 86400
    next_next_week_t = next_week_t + 7 * 86400

    birth_this_week = []
    birth_next_week = []
    for s in [x for x in students.values() if x["IsReleased"][server]]:
        birth = time.mktime(time.strptime(f'{now.year}/{s["BirthDay"]}', "%Y/%m/%d"))
        if this_week_t <= birth < next_week_t:
            birth_this_week.append(s)
        elif next_week_t <= birth <= next_next_week_t:
            birth_next_week.append(s)

    sort_key = lambda x: x["BirthDay"].split("/")
    pattern = "- {PersonalName} {Birthday}"
    if birth_this_week:
        birth_this_week.sort(key=sort_key)
        s = "\n".join([pattern.format(**x) for x in birth_this_week])
        im.append(f"以下学生将在本周迎来生日：\n{s}")

    if birth_next_week:
        birth_next_week.sort(key=sort_key)
        s = "\n".join([pattern.format(**x) for x in birth_next_week])
        im.append(f"以下学生将在下周迎来生日：\n{s}")

    return "\n============\n".join(im)


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
