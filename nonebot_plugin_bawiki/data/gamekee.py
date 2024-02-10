import asyncio
import itertools
import re
import time
import urllib.parse
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Literal, Optional, cast
from typing_extensions import Unpack

from bs4 import BeautifulSoup, PageElement, ResultSet, Tag
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from PIL import Image
from PIL.Image import Resampling
from pil_utils import BuildImage, text2image
from playwright.async_api import Page

from ..config import config
from ..resource import CALENDER_BANNER_PATH, GAMEKEE_UTIL_JS_PATH, GRADIENT_BG_PATH
from ..util import (
    AsyncReqKwargs,
    RespType as Rt,
    async_req,
    i2b,
    parse_time_delta,
    read_image,
    split_pic,
)


async def game_kee_request(url: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    kwargs["base_urls"] = config.ba_gamekee_url

    headers = kwargs.get("headers") or {}
    headers.update({"Game-Id": "829", "Game-Alias": "ba"})
    kwargs["headers"] = headers

    resp = await async_req(url, **kwargs)
    if resp["code"] != 0:
        raise ValueError(resp["msg"])
    return resp["data"]


async def game_kee_get_calender() -> List[dict]:
    ret = cast(list, await game_kee_request("v1/wiki/index"))

    module = next(
        (x for x in ret if x["module"]["id"] == 12),
        None,
    )
    if not module:
        return []

    li: list = module["list"]

    now = time.time()
    li = [x for x in li if (now < x["end_at"])]

    li.sort(key=lambda x: x["begin_at"] if now < x["begin_at"] else x["end_at"])
    li.sort(key=lambda x: now < x["begin_at"])
    li.sort(key=lambda x: x["importance"], reverse=True)
    return li


async def game_kee_get_stu_li() -> Dict[str, dict]:
    ret = cast(dict, await game_kee_request("v1/wiki/entry"))

    entry_stu = next(
        (x for x in ret["entry_list"] if x["id"] == 23941),
        None,
    )
    if not entry_stu:
        return {}

    entry_stu_all = next(
        (x for x in entry_stu["child"] if x["id"] == 49443),
        None,
    )
    if not entry_stu_all:
        return {}

    return {x["name"]: x for x in entry_stu_all["child"]}


async def game_kee_get_stu_cid_li() -> Dict[str, int]:
    return {x: y["content_id"] for x, y in (await game_kee_get_stu_li()).items()}


def game_kee_page_url(sid: int) -> str:
    return urllib.parse.urljoin(config.ba_gamekee_url, f"{sid}.html")


async def game_kee_get_page(url: str) -> List[BytesIO]:
    async with cast(Page, get_new_page()) as page:
        await page.goto(url, timeout=config.ba_screenshot_timeout * 1000)

        await page.evaluate(GAMEKEE_UTIL_JS_PATH.read_text(encoding="u8"))

        # 太长了
        # 展开折叠的语音
        # folds = await page.query_selector_all("div.fold-table-btn")
        # for i in folds:
        #     with contextlib.suppress(Exception):
        #         await i.click()

        element = await page.query_selector("div.wiki-detail-body")
        assert element
        pic_bytes = await element.screenshot(type="jpeg")

    pic = Image.open(BytesIO(pic_bytes))
    return list(map(i2b, split_pic(pic)))


async def game_kee_calender(
    servers: Optional[List[Literal["Jp", "Global", "Cn"]]] = None,
) -> Optional[List[BytesIO]]:
    ret = await game_kee_get_calender()

    if ret and servers:
        server_name_map = {
            "Jp": "日服",
            "Global": "国际服",
            "Cn": "国服",
        }
        server_names = [server_name_map[x] for x in servers]
        ret = [x for x in ret if x["pub_area"] in server_names]

    if not ret:
        return None

    return await game_kee_get_calender_page(ret)


def split_images(
    images: List[BuildImage],
    max_height: int,
    padding: int,
) -> List[List[BuildImage]]:
    ret = []
    cur = []
    height = 0
    for i in images:
        if height + i.height > max_height:
            ret.append(cur)
            cur = []
            height = 0
        cur.append(i)
        height += i.height + padding
    if cur:
        ret.append(cur)
    return ret


async def game_kee_get_calender_page(
    ret: List[Dict],
    has_pic: bool = True,
) -> List[BytesIO]:
    now = datetime.now().astimezone()

    async def draw(it: dict) -> BuildImage:
        ev_pic = None
        if has_pic and (url := it.get("picture")):
            try:
                pic_bytes = await async_req(f"https:{url}", resp_type=Rt.BYTES)
                ev_pic = BuildImage.open(BytesIO(pic_bytes))
            except Exception:
                logger.exception("下载日程表图片失败")

        begin = datetime.fromtimestamp(it["begin_at"]).astimezone()
        end = datetime.fromtimestamp(it["end_at"]).astimezone()
        started = begin <= now
        time_remain = (end if started else begin) - now
        dd, hh, mm, ss = parse_time_delta(time_remain)

        # logger.debug(f'{it["title"]} | {started} | {time_remain}')

        title_p = text2image(
            f'[b]{it["title"]}[/b]',
            "#ffffff00",
            max_width=1290,
            fontsize=65,
        )
        time_p = text2image(
            f"{begin} ~ {end}",
            "#ffffff00",
            max_width=1290,
            fontsize=40,
        )
        desc_p = (
            text2image(
                desc.replace("<br>", ""),
                "#ffffff00",
                max_width=1290,
                fontsize=40,
            )
            if (desc := it["description"])
            else None
        )
        remain_p = text2image(
            f"剩余 [color=#fc6475]{dd}[/color] 天 [color=#fc6475]{hh}[/color] 时 "
            f"[color=#fc6475]{mm}[/color] 分 [color=#fc6475]{ss}[/color] 秒"
            f'{"结束" if started else "开始"}',
            "#ffffff00",
            max_width=1290,
            fontsize=50,
        )

        h = (
            100
            + (title_p.height + 25)
            + (time_p.height + 25)
            + (ev_pic.height + 25 if ev_pic else 0)
            + (desc_p.height + 25 if desc_p else 0)
            + remain_p.height
        )
        img = BuildImage.new("RGBA", (1400, h), (255, 255, 255, 70)).draw_rectangle(
            (0, 0, 10, h),
            "#fc6475" if it["importance"] else "#4acf75",
        )

        if not started:
            img.draw_rectangle((1250, 0, 1400, 60), "gray")
            img.draw_text((1250, 0, 1400, 60), "未开始", max_fontsize=50, fill="white")

        ii = 50
        img.paste(title_p, (60, ii), alpha=True)
        ii += title_p.height + 25
        img.paste(time_p, (60, ii), alpha=True)
        ii += time_p.height + 25
        if ev_pic:
            img.paste(ev_pic.resize_width(1290).circle_corner(15), (60, ii), alpha=True)
            ii += ev_pic.height + 25
        if desc_p:
            img.paste(desc_p, (60, ii), alpha=True)
            ii += desc_p.height + 25
        img.paste(remain_p, (60, ii), alpha=True)
        return img

    async def draw_list(li: List[BuildImage], title: str) -> BuildImage:
        bg_w = 1500
        bg_h = 200 + sum([x.height + 50 for x in li])
        bg = (
            BuildImage.new("RGBA", (bg_w, bg_h))
            .paste((await read_image(CALENDER_BANNER_PATH)).resize((1500, 150)))
            .draw_text(
                (50, 0, 1480, 150),
                title,
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

        index = 200
        for p in li:
            bg.paste(p.circle_corner(10), (50, index), alpha=True)
            index += p.height + 50
        return bg

    important_data = []
    common_data = []
    for data in ret:
        (important_data if data["importance"] else common_data).append(data)

    important_pics, common_pics = await asyncio.gather(
        asyncio.gather(*(draw(x) for x in important_data)),
        asyncio.gather(*(draw(x) for x in common_data)),
    )

    max_height = 6000
    if not common_pics:
        pics = [important_pics]
    else:
        chain = itertools.chain(important_pics, common_pics)
        pics: List[List[BuildImage]] = (
            [list(chain)]
            if sum(x.height + 50 for x in chain) <= max_height + 50
            else [important_pics, *split_images(common_pics, max_height, 50)]
        )

    title_prefix = "GameKee丨活动日程"
    if len(pics) == 1:
        images = await asyncio.gather(*(draw_list(pics[0], title_prefix)))
    else:
        if len(pics[-1]) < 3:
            extra = pics.pop()
            pics[-1].extend(extra)
        images = await asyncio.gather(
            *(draw_list(x, f"{title_prefix}丨P{i}") for i, x in enumerate(pics, 1)),
        )

    return [x.convert("RGB").save_jpg() for x in images]


async def game_kee_grab_l2d(cid: int) -> List[str]:
    ret: dict = await game_kee_request(f"v1/content/detail/{cid}")
    content: str = ret["content"]

    soup = BeautifulSoup(content, "lxml")

    l2d_nav_title = soup.find("div", class_="input-wrapper", string="Live2D")
    assert l2d_nav_title
    assert l2d_nav_title.parent
    data_index = l2d_nav_title.parent["data-index"]

    assert l2d_nav_title.parent.parent
    slide_contents = next(
        (x for x in l2d_nav_title.parent.parent.next_siblings if isinstance(x, Tag)),
        None,
    )
    assert slide_contents

    l2d_content = slide_contents.find("div", attrs={"data-index": data_index})
    assert isinstance(l2d_content, Tag)
    images = l2d_content.select(".div-img > img")

    image_urls = [x["data-real"] for x in images]
    return [f"https:{x}" for x in image_urls]


@dataclass()
class GameKeeVoice:
    title: str
    jp: str
    cn: str
    url: str


def parse_voice_elem(elem: Tag) -> GameKeeVoice:
    url: str = cast(str, elem["src"])
    if not url.startswith("http"):
        url = f"https:{url}"

    tr1: Tag = elem.parent.parent.parent.parent  # type: ignore
    tds: ResultSet[Tag] = tr1.find_all("td")
    title = tds[0].text.strip()
    jp = "\n".join(tds[2].stripped_strings)

    tr2 = tr1.next_sibling
    cn = "\n".join(tr2.stripped_strings)  # type: ignore
    return GameKeeVoice(title, jp, cn, url)


def merge_voice_dialogue(voices: List[List[GameKeeVoice]]) -> List[List[GameKeeVoice]]:
    main_voices = voices[0]
    other_voice_entries = voices[1:]

    for voice_entry in other_voice_entries:
        for voice in (x for x in voice_entry if (not x.jp) or (not x.cn)):
            corresponding_voice = next(
                (x for x in main_voices if x.title == voice.title),
                None,
            )
            if not corresponding_voice:
                continue

            if not voice.jp:
                voice.jp = corresponding_voice.jp
            if not voice.cn:
                voice.cn = corresponding_voice.cn

    return voices


async def game_kee_get_voice(cid: int, is_chinese: bool = False) -> List[GameKeeVoice]:
    wiki_html = (
        cast(
            dict,
            await game_kee_request(f"v1/content/detail/{cid}"),
        )
    )["content"]
    bs = BeautifulSoup(wiki_html, "lxml")

    multi_lang_voices = [
        [parse_voice_elem(x) for x in audios]
        for table_fathers in bs.select(".slide-item")
        if
        (
            # 选择 tables
            (tables := table_fathers.select(".table-overflow > .mould-table"))
            # 检查 tables 中是否有语音，如果有，就取出语音到变量 aus -> audios
            and (
                audios := next(
                    (aus for child in tables if (aus := child.find_all("audio"))),
                    None,  # type: ignore
                )
            )
        )
    ]
    if multi_lang_voices:
        return merge_voice_dialogue(multi_lang_voices)[1 if is_chinese else 0]

    # 没有中配
    if is_chinese:
        return []
    return next(
        [parse_voice_elem(x) for x in a]
        for x in bs.select(".mould-table")
        if (a := x.find_all("audio"))
    )


async def get_level_list() -> Dict[str, int]:
    entry = cast(dict, await game_kee_request("v1/wiki/entry"))
    entry_list: List[Dict] = entry["entry_list"]
    guide_entry: List[Dict] = next(x["child"] for x in entry_list if x["id"] == 50284)
    levels = itertools.chain(
        *(x["child"] for x in guide_entry if cast(str, x["name"]).endswith("章")),
    )
    return {
        n.upper(): x["content_id"]
        for x in levels
        if re.match(r"^(H)?(TR|\d+)-(\d+)$", (n := cast(str, x["name"])))
    }


async def extract_content_pic(cid: int) -> List[str]:
    wiki_html = (
        cast(
            dict,
            await game_kee_request(f"v1/content/detail/{cid}"),
        )
    )["content"]
    bs = BeautifulSoup(wiki_html, "lxml")
    img_elem = bs.find_all("img")
    img_urls = cast(List[str], [x["src"] for x in img_elem])
    return [f"https:{x}" if x.startswith("//") else x for x in img_urls]


@dataclass()
class MangaMetadata:
    category: str
    name: str
    cid: int


@dataclass()
class MangaContent:
    title: str
    content: str
    images: List[str]


async def get_manga_list() -> List[MangaMetadata]:
    entry = cast(dict, await game_kee_request("v1/wiki/entry"))
    entry_list: List[Dict] = entry["entry_list"]
    guide_entry: List[Dict] = next(x["child"] for x in entry_list if x["id"] == 51508)

    manga_list: List[MangaMetadata] = []

    current_category = "ぶるーあーかいぶっ！"
    for entry in guide_entry:
        category = entry["name"]
        if category.startswith("【"):
            current_category = category[1 : category.find("】")]
        manga_list.extend(
            MangaMetadata(
                category=current_category,
                name=x["name"],
                cid=x["content_id"],
            )
            for x in entry["child"]
        )

    return manga_list


def tags_to_str(tag: PageElement) -> str:
    def process(elem: PageElement) -> str:
        if c := getattr(elem, "contents", None):
            return "".join([s for x in c if (s := process(x))])
        text = elem if isinstance(elem, str) else elem.text
        if s := text.strip().replace("\u200b", ""):
            return s
        if hasattr(elem, "name") and (elem.name == "img" or elem.name == "br"):  # type: ignore
            return "\n"
        return ""

    text = process(tag).strip()
    if not text:
        return text

    lines = text.splitlines()
    last_line = lines[-1]
    if last_line.strip().endswith(">"):
        lines.pop()
    return "\n".join(lines).strip()


async def get_manga_content(cid: int) -> MangaContent:
    article = cast(dict, await game_kee_request(f"v1/content/detail/{cid}"))
    soup = BeautifulSoup(article["content"], "lxml")

    content = tags_to_str(soup).strip()
    if "汉化：" in content:
        content = content.replace("汉化：", "\n汉化：").replace("\n）", "）")

    return MangaContent(
        title=article["title"],
        content=content,
        images=[
            f"https:{src}"
            for x in soup.find_all("img")
            if (not (src := x["src"]).endswith(".gif")) and "gamekee" in src
        ],
    )
