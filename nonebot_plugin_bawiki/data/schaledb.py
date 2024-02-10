import asyncio
import math
import time
from datetime import datetime, timedelta
from io import BytesIO
from typing import Any, Dict, List, NamedTuple, Optional, cast
from typing_extensions import Unpack

from nonebot_plugin_htmlrender import get_new_page
from PIL import Image, ImageFilter
from PIL.Image import Resampling
from pil_utils import BuildImage, Text2Image, text2image
from playwright.async_api import Page, ViewportSize

from ..config import config
from ..resource import (
    CALENDER_BANNER_PATH,
    GRADIENT_BG_PATH,
    SCHALE_UTIL_CSS_PATH,
    SCHALE_UTIL_JS_PATH,
)
from ..util import (
    AsyncReqKwargs,
    RespType as Rt,
    async_req,
    img_invert_rgba,
    parse_time_delta,
    read_image,
    split_list,
)

PAGE_KWARGS = {
    "is_mobile": True,
    "viewport": ViewportSize(width=767, height=800),
}


async def schale_get(url: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    kwargs["base_urls"] = config.ba_schale_url
    return await async_req(url, **kwargs)


async def schale_get_stu_data(loc: str = "cn") -> List[Dict[str, Any]]:
    return await schale_get(f"data/{loc}/students.min.json")


async def schale_get_config() -> Dict[str, Any]:
    return await schale_get("data/config.min.json")


async def schale_get_localization(loc: str = "cn") -> Dict[str, Any]:
    return cast(dict, await schale_get(f"data/{loc}/localization.min.json"))


async def schale_get_raids(loc: str = "cn") -> Dict[str, Any]:
    return cast(dict, await schale_get(f"data/{loc}/raids.min.json"))


async def schale_get_stu_dict(key: str = "Name") -> dict:
    return {x[key]: x for x in await schale_get_stu_data()}


async def schale_get_stu_info(stu: str) -> bytes:
    async with cast(Page, get_new_page(**PAGE_KWARGS)) as page:
        await page.goto(config.ba_schale_url, wait_until="domcontentloaded")

        await page.goto(
            f"{config.ba_schale_url}?chara={stu}",
            timeout=config.ba_screenshot_timeout * 1000,
            wait_until="networkidle",
        )
        await page.add_style_tag(content=SCHALE_UTIL_CSS_PATH.read_text(encoding="u8"))
        await page.evaluate(SCHALE_UTIL_JS_PATH.read_text(encoding="u8"))
        return await page.screenshot(full_page=True, type="jpeg")


async def schale_calender(server: str) -> BytesIO:
    students, s_config, localization, raids = await asyncio.gather(
        schale_get_stu_dict("Id"),
        schale_get_config(),
        schale_get_localization(),
        schale_get_raids(),
    )
    region_index_map: Dict[str, int] = {
        x["Name"]: i for i, x in enumerate(s_config["Regions"])
    }
    return await schale_get_calender(
        region_index_map[server],
        students,
        s_config,
        localization,
        raids,
    )


class CurrentEventTuple(NamedTuple):
    event: dict
    start: datetime
    end: datetime
    remain: timedelta


def find_current_event(
    ev: List[dict],
    now: Optional[datetime] = None,
) -> Optional[CurrentEventTuple]:
    if not now:
        now = datetime.now().astimezone()
    for _e in ev:
        _start = datetime.fromtimestamp(_e["start"]).astimezone()
        _end = datetime.fromtimestamp(_e["end"]).astimezone()
        if _start <= now < _end:
            _remain = _end - now
            return CurrentEventTuple(_e, _start, _end, _remain)
    return None


async def schale_get_calender(
    server_index: int,
    students: Dict[str, Dict],
    s_config: dict,
    localization: dict,
    raids: dict,
) -> BytesIO:
    region = s_config["Regions"][server_index]
    now = datetime.now().astimezone()

    pic_bg = BuildImage.new("RGBA", (1400, 640), (255, 255, 255, 70))

    def format_time(_start: datetime, _end: datetime, _remain: timedelta) -> str:
        dd, hh, mm, ss = parse_time_delta(_remain)
        return (
            f"{_start} ~ {_end} | "
            f"剩余 [b][color=#fc6475]{dd}天 {hh:0>2d}:{mm:0>2d}:{ss:0>2d}[color=#fc6475][/b]"
        )

    async def draw_gacha():
        c_gacha = region["CurrentGacha"]
        if not (r := find_current_event(c_gacha)):
            return None

        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150),
            "特选招募",
            weight="bold",
            max_fontsize=80,
        )
        g = r.event
        t = format_time(r.start, r.end, r.remain)
        pic = pic.paste(
            ti := text2image(
                t,
                (255, 255, 255, 0),
                fontsize=45,
                max_width=1350,
                align="center",
            ),
            (int((1400 - ti.width) / 2), 150),
            alpha=True,
        )
        stu = [students[x] for x in g["characters"]]

        async def process_avatar(s: dict):
            return (
                BuildImage.open(
                    BytesIO(
                        await schale_get(
                            f'images/student/collection/{s["Id"]}.webp',
                            resp_type=Rt.BYTES,
                        ),
                    ),
                )
                .resize((300, 340))
                .paste(
                    BuildImage.new("RGBA", (300, 65), (255, 255, 255, 120)),
                    (0, 275),
                    alpha=True,
                )
                .convert("RGB")
                .circle_corner(25)
                .draw_text((0, 275, 300, 340), s["Name"], max_fontsize=50)
            )

        avatars = await asyncio.gather(*[process_avatar(x) for x in stu])
        ava_len = len(avatars)
        x_index = int((1400 - (300 + 25) * ava_len + 25) / 2)

        for p in avatars:
            pic = pic.paste(p, (x_index, 250), alpha=True)
            x_index += p.width + 25

        return pic

    async def draw_event():
        c_event = region["CurrentEvents"]
        if not (r := find_current_event(c_event)):
            return None

        pic = pic_bg.copy().draw_text(
            (25, 25, 1375, 150),
            "当前活动",
            weight="bold",
            max_fontsize=80,
        )

        g = r.event
        t = format_time(r.start, r.end, r.remain)
        pic = pic.paste(
            ti := text2image(
                t,
                (255, 255, 255, 0),
                fontsize=45,
                max_width=1350,
                align="center",
            ),
            (int((1400 - ti.width) / 2), 150),
            alpha=True,
        )
        ev = g["event"]
        ev_name = ""
        if ev >= 10000:
            ev_name = " (复刻)"
            ev %= 10000
        ev_name = localization["EventName"][str(ev)] + ev_name

        ev_bg, ev_img = await asyncio.gather(
            schale_get(
                f"images/campaign/Campaign_Event_{ev}_Normal.png",
                resp_type=Rt.BYTES,
            ),
            schale_get(
                f"images/eventlogo/{ev}_{'Tw' if server_index else 'Jp'}.webp",
                resp_type=Rt.BYTES,
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
                alpha=True,
            )
            .convert("RGB")
            .circle_corner(25)
            .draw_text(
                (0, ev_bg.height - 65, ev_bg.width, ev_bg.height),
                ev_name,
                max_fontsize=50,
            )
        )
        return pic.paste(
            ev_bg,
            (int((pic.width - ev_bg.width) / 2), 250),
            alpha=True,
        )

    async def draw_raid():
        if not (r := find_current_event(region["CurrentRaid"])):
            return None

        pic = pic_bg.copy()

        ri = r.event
        t = format_time(r.start, r.end, r.remain)
        pic = pic.paste(
            ti := text2image(
                t,
                (255, 255, 255, 0),
                fontsize=45,
                max_width=1350,
                align="center",
            ),
            (int((1400 - ti.width) / 2), 150),
            alpha=True,
        )

        raid_type = ri["type"]
        time_atk = raid_type == "TimeAttack"
        type_key = "TimeAttack" if time_atk else "Raid"

        raid = {x["Id"]: x for x in raids[type_key]}
        c_ri = raid[ri["raid"]]
        pic = pic.draw_text(
            (25, 25, 1375, 150),
            localization["StageType"][type_key],
            weight="bold",
            max_fontsize=80,
        )

        if time_atk:
            tk_bg = {
                "Shooting": "TimeAttack_SlotBG_02",
                "Defense": "TimeAttack_SlotBG_01",
                "Destruction": "TimeAttack_SlotBG_03",
            }
            bg_url = f'images/timeattack/{tk_bg[c_ri["DungeonType"]]}.png'
            fg_url = f'images/enemy/{c_ri["Icon"]}.webp'
        else:
            bg_url = f'images/raid/Boss_Portrait_{c_ri["PathName"]}_LobbyBG'
            if len(c_ri["Terrain"]) > 1 and ri["terrain"] == c_ri["Terrain"][1]:
                bg_url += f'_{ri["terrain"]}'
            bg_url = f"{bg_url}.png"
            fg_url = f'images/raid/Boss_Portrait_{c_ri["PathName"]}_Lobby.png'
        terrain = c_ri["Terrain"] if time_atk else ri["terrain"]

        color_map = {
            "LightArmor": (167, 12, 25),
            "Explosion": (167, 12, 25),
            "HeavyArmor": (178, 109, 31),
            "Pierce": (178, 109, 31),
            "Unarmed": (33, 111, 156),
            "Mystic": (33, 111, 156),
            "Normal": (115, 115, 115),
        }
        atk_color = color_map[c_ri["BulletType" if time_atk else "BulletTypeInsane"]]
        def_color = color_map[c_ri["ArmorType"]]

        c_bg, c_fg, icon_def, icon_atk, icon_tr = await asyncio.gather(
            *(
                schale_get(bg_url, resp_type=Rt.BYTES),
                schale_get(fg_url, resp_type=Rt.BYTES),
                schale_get("images/ui/Type_Defense_s.png", resp_type=Rt.BYTES),
                schale_get("images/ui/Type_Attack_s.png", resp_type=Rt.BYTES),
                schale_get(f"images/ui/Terrain_{terrain}.png", resp_type=Rt.BYTES),
            ),
        )

        icon_def = (
            BuildImage.new("RGBA", (64, 64), def_color)
            .paste(
                (BuildImage.open(BytesIO(icon_def)).convert("RGBA").resize_height(48)),
                (8, 8),
                alpha=True,
            )
            .circle()
        )
        icon_atk = (
            BuildImage.new("RGBA", (64, 64), atk_color)
            .paste(
                (BuildImage.open(BytesIO(icon_atk)).convert("RGBA").resize_height(48)),
                (8, 8),
                alpha=True,
            )
            .circle()
        )
        icon_tr = (
            BuildImage.new("RGBA", (64, 64), "#ffffff")
            .paste(
                img_invert_rgba(Image.open(BytesIO(icon_tr)).convert("RGBA")),
                (-2, -2),
                alpha=True,
            )
            .circle()
        )

        c_bg = (
            BuildImage.open(BytesIO(c_bg))
            .convert("RGBA")
            .resize_height(340)
            .filter(ImageFilter.GaussianBlur(3))
        )
        c_fg = BuildImage.open(BytesIO(c_fg)).convert("RGBA").resize_height(c_bg.height)
        c_bg = (
            c_bg.paste(
                c_fg,
                (int((c_bg.width - c_fg.width) / 2), 0),
                alpha=True,
            )
            .paste(
                BuildImage.new("RGBA", (c_bg.width, 65), (255, 255, 255, 120)),
                (0, c_bg.height - 65),
                alpha=True,
            )
            .paste(icon_atk, (10, 10), alpha=True)
            .paste(icon_def, (10, 79), alpha=True)
            .paste(icon_tr, (10, 147), alpha=True)
            .convert("RGB")
            .circle_corner(25)
            .draw_text(
                (0, c_bg.height - 65, c_bg.width, c_bg.height),
                (
                    localization["TimeAttackStage"][c_ri["DungeonType"]]
                    if time_atk
                    else (c_ri["Name"])
                ),
                max_fontsize=50,
            )
        )
        return pic.paste(c_bg, (int((pic.width - c_bg.width) / 2), 250), alpha=True)

    async def draw_birth():
        now_t = time.mktime(now.date().timetuple())
        now_w = now.weekday()
        this_week_t = now_t - now_w * 86400
        next_week_t = now_t + (7 - now_w) * 86400
        next_next_week_t = next_week_t + 7 * 86400

        birth_this_week = []
        birth_next_week = []
        for s in [x for x in students.values() if x["IsReleased"][server_index]]:
            try:
                birth = time.mktime(
                    time.strptime(f'{now.year}/{s["BirthDay"]}', "%Y/%m/%d"),
                )
            except ValueError:
                continue
            if this_week_t <= birth < next_week_t:
                birth_this_week.append(s)
            elif next_week_t <= birth <= next_next_week_t:
                birth_next_week.append(s)

        if (not birth_this_week) and (not birth_next_week):
            return None

        img_per_line = 7
        sort_key = lambda x: tuple(  # noqa: E731
            f"{x:0>2}" for x in cast(str, x["BirthDay"]).split("/")
        )
        p_h = 0
        if birth_this_week:
            birth_this_week.sort(key=sort_key)
            p_h += 70 + 220 * math.ceil(len(birth_this_week) / img_per_line)

        if birth_next_week:
            birth_next_week.sort(key=sort_key)
            p_h += 70 + 220 * math.ceil(len(birth_next_week) / img_per_line)
            if birth_this_week:
                p_h += 25

        padding = 25
        min_height = 640
        title_h = 125
        height = max(padding * 3 + title_h + p_h, min_height)
        width = 1400
        pic = BuildImage.new("RGBA", (width, height), (255, 255, 255, 70)).draw_text(
            (25, 25, 1375, 150),
            "学生生日",
            weight="bold",
            max_fontsize=80,
        )
        stu_pics = [
            BuildImage.open(BytesIO(x)).convert("RGBA").resize_height(180).circle()
            for x in await asyncio.gather(
                *(
                    schale_get(
                        f'images/student/icon/{x["Id"]}.webp',
                        resp_type=Rt.BYTES,
                    )
                    for x in birth_this_week + birth_next_week
                ),
            )
        ]

        y_offset = title_h + padding
        if height >= min_height:
            y_offset += (height - (padding // 2) - title_h - p_h) // 2

        def draw_birth_stu(title: str, students: List[dict]):
            nonlocal y_offset

            subtitle = Text2Image.from_text(title, fontsize=45)
            subtitle.draw_on_image(pic.image, ((width - subtitle.width) // 2, y_offset))
            y_offset += 70

            for line in split_list(students, img_per_line):
                x_offset = (width - (190 * len(line))) // 2
                for stu in line:
                    pic.paste(
                        stu_pics.pop(0),
                        (x_offset, y_offset),
                        alpha=True,
                    ).draw_text(
                        (x_offset, y_offset + 180, x_offset + 180, y_offset + 220),
                        stu["BirthDay"],
                    )
                    x_offset += 190
                y_offset += 220

        if birth_this_week:
            draw_birth_stu("本周", birth_this_week)
            y_offset += 25

        if birth_next_week:
            draw_birth_stu("下周", birth_next_week)

        return pic

    img = await asyncio.gather(  # type: ignore
        draw_gacha(),
        draw_event(),
        draw_raid(),
        draw_birth(),
    )
    img: List[BuildImage] = [x for x in img if x]
    if not img:
        img.append(
            pic_bg.copy().draw_text(
                (0, 0, 1400, 640),
                "没有获取到任何数据",
                max_fontsize=60,
            ),
        )

    bg_w = 1500
    bg_h = 200 + sum([x.height + 50 for x in img])
    bg = (
        BuildImage.new("RGBA", (bg_w, bg_h))
        .paste((await read_image(CALENDER_BANNER_PATH)).resize((1500, 150)))
        .draw_text(
            (50, 0, 1480, 150),
            f"SchaleDB丨活动日程丨{localization['ServerName'][str(server_index)]}",
            max_fontsize=100,
            weight="bold",
            fill="#ffffff",
            halign="left",
        )
        .paste(
            (await read_image(GRADIENT_BG_PATH)).resize(
                (1500, bg_h - 150),
                resample=Resampling.NEAREST,
            ),
            (0, 150),
        )
    )

    h_index = 200
    for im in img:
        bg.paste(im.circle_corner(10), (50, h_index), alpha=True)
        h_index += im.height + 50
    return bg.convert("RGB").save("JPEG")


async def get_fav_li(lvl: int) -> List[dict]:
    return [
        x
        for x in await schale_get_stu_data()
        if (x["MemoryLobby"] and x["MemoryLobby"][0] == lvl)
    ]


async def draw_fav_li(stu_li: List[dict]) -> BytesIO:
    txt_h = 48
    pic_h = 144
    icon_w = 182
    icon_h = pic_h + txt_h
    line_max_icon = 6

    if (li_len := len(stu_li)) <= line_max_icon:
        line = 1
        length = li_len
    else:
        line = math.ceil(li_len / line_max_icon)
        length = line_max_icon

    img = (await read_image(GRADIENT_BG_PATH)).resize(
        (icon_w * length, icon_h * line + 5),
        resample=Resampling.NEAREST,
    )

    async def draw_stu(name_: str, stu_id_: int, line_: int, index_: int):
        left = index_ * icon_w
        top = line_ * icon_h + 5

        ret = await schale_get(
            f"images/student/lobby/{stu_id_}.webp",
            resp_type=Rt.BYTES,
        )
        icon_img = Image.open(BytesIO(ret)).convert("RGBA")
        img.paste(icon_img, (left, top), alpha=True)
        img.draw_text(
            (left, top + pic_h, left + icon_w, top + icon_h),
            name_,
            max_fontsize=25,
            min_fontsize=1,
        )

    task_li = []
    line = 0
    i = 0
    for stu in stu_li:
        if i == line_max_icon:
            i = 0
            line += 1
        task_li.append(draw_stu(stu["Name"], stu["Id"], line, i))
        i += 1
    await asyncio.gather(*task_li)

    return img.convert("RGB").save("JPEG")
