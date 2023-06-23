import asyncio
import contextlib
import itertools
import re
import time
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, NoReturn, Union, cast

from bs4 import BeautifulSoup, ResultSet, Tag
from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.internal.matcher import Matcher
from nonebot_plugin_htmlrender import get_new_page
from PIL.Image import Resampling
from pil_utils import BuildImage, text2image
from playwright.async_api import Page

from ..config import config
from ..resource import RES_CALENDER_BANNER, RES_GRADIENT_BG
from ..util import async_req, parse_time_delta


async def game_kee_request(url: str, **kwargs) -> Union[List, Dict[str, Any]]:
    ret = cast(
        dict,
        await async_req(
            f"{config.ba_gamekee_url}{url}",
            headers={"game-id": "0", "game-alias": "ba"},
            proxy=None,
            **kwargs,
        ),
    )
    if ret["code"] != 0:
        raise ConnectionError(ret["msg"])
    return ret["data"]


async def game_kee_get_calender() -> List[dict]:
    ret = cast(list, await game_kee_request("v1/wiki/index"))

    for i in ret:
        if i["module"]["id"] == 12:
            li: list = i["list"]

            now = time.time()
            li = [x for x in li if (now < x["end_at"])]

            li.sort(key=lambda x: x["begin_at"] if now < x["begin_at"] else x["end_at"])
            li.sort(key=lambda x: now < x["begin_at"])
            li.sort(key=lambda x: x["importance"], reverse=True)
            return li

    return []


async def game_kee_get_stu_li() -> Dict[str, dict]:
    ret = cast(dict, await game_kee_request("v1/wiki/entry"))

    for i in ret["entry_list"]:
        if i["id"] == 23941:
            for ii in i["child"]:
                if ii["id"] == 49443:
                    return {x["name"]: x for x in ii["child"]}

    return {}


async def game_kee_get_stu_cid_li() -> Dict[str, int]:
    return {x: y["content_id"] for x, y in (await game_kee_get_stu_li()).items()}


def game_kee_page_url(sid: int) -> str:
    return f"{config.ba_gamekee_url}{sid}.html"


async def game_kee_get_page(url: str) -> bytes:
    async with cast(Page, get_new_page()) as page:
        await page.goto(url, timeout=60 * 1000)

        # 删掉header
        await page.add_script_tag(
            content='document.getElementsByClassName("wiki-header")'
            ".forEach((v)=>{v.remove()})",
        )

        # 展开折叠的语音
        folds = await page.query_selector_all('xpath=//div[@class="fold-table-btn"]')
        for i in folds:
            with contextlib.suppress(Exception):
                await i.click()

        # 隐藏 header 和 footer
        js_str = "(obj) => { obj.style.display = 'none' }"
        await page.eval_on_selector(".wiki-header", js_str)
        await page.eval_on_selector(".wiki-footer", js_str)

        element = await page.query_selector('xpath=//div[@class="wiki-detail-body"]')
        if not element:
            raise ValueError
        return await element.screenshot()


async def send_wiki_page(sid: int, matcher: Matcher) -> NoReturn:
    url = game_kee_page_url(sid)
    await matcher.send(f"请稍等，正在截取Wiki页面……\n{url}")

    try:
        img = await game_kee_get_page(url)
    except:
        logger.exception(f"截取wiki页面出错 {url}")
        await matcher.finish("截取页面出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))


async def game_kee_calender() -> Union[MessageSegment, str]:
    ret = await game_kee_get_calender()
    if not ret:
        return "没有获取到GameKee日程表数据"

    pic = await game_kee_get_calender_page(ret)
    return MessageSegment.image(pic)


async def game_kee_get_calender_page(ret, has_pic=True) -> BytesIO:
    now = datetime.now()

    async def draw(it: dict):
        _p = None
        if has_pic and (_p := it.get("picture")):
            try:
                _p = (
                    BuildImage.open(BytesIO(await async_req(f"https:{_p}", raw=True)))
                    .resize_width(1290)
                    .circle_corner(15)
                )
            except:
                logger.exception("下载日程表图片失败")

        begin = datetime.fromtimestamp(it["begin_at"])
        end = datetime.fromtimestamp(it["end_at"])
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
            + (_p.height + 25 if _p else 0)
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
        img.paste(title_p, (60, ii), True)
        ii += title_p.height + 25
        img.paste(time_p, (60, ii), True)
        ii += time_p.height + 25
        if _p:
            img.paste(_p, (60, ii), True)
            ii += _p.height + 25
        if desc_p:
            img.paste(desc_p, (60, ii), True)
            ii += desc_p.height + 25
        img.paste(remain_p, (60, ii), True)
        # img = img.circle_corner(15)

        return img

    pics: List[BuildImage] = await asyncio.gather(  # type: ignore
        *[draw(x) for x in ret],
    )

    bg_w = 1500
    bg_h = 200 + sum([x.height + 50 for x in pics])
    bg = (
        BuildImage.new("RGBA", (bg_w, bg_h))
        .paste(RES_CALENDER_BANNER.copy().resize((1500, 150)))
        .draw_text(
            (50, 0, 1480, 150),
            "GameKee丨活动日程",
            max_fontsize=100,
            weight="bold",
            fill="#ffffff",
            halign="left",
        )
        .paste(
            RES_GRADIENT_BG.copy().resize(
                (1500, bg_h - 150),
                resample=Resampling.NEAREST,
            ),
            (0, 150),
        )
    )

    index = 200
    for p in pics:
        bg.paste(p.circle_corner(10), (50, index), True)
        index += p.height + 50

    return bg.save_jpg()


async def game_kee_grab_l2d(cid) -> List[str]:
    ret = cast(
        dict,
        await game_kee_request(f"v1/content/detail/{cid}"),
    )
    content: str = ret["content"]

    x = content.find('<div class="input-wrapper">官方介绍</div>')
    x = content.find('class="slide-item" data-index="2"', x)
    y = content.find('data-index="3"', x)

    content: str = content[x:y]

    img = re.findall('data-real="([^"]*)"', content)

    return [f"https:{x}" for x in img]


@dataclass()
class GameKeeVoice:
    title: str
    jp: str
    cn: str
    url: str


async def game_kee_get_voice(cid) -> List[GameKeeVoice]:
    wiki_html = (
        cast(
            dict,
            await game_kee_request(f"v1/content/detail/{cid}"),
        )
    )["content"]
    bs = BeautifulSoup(wiki_html, "lxml")
    audios = bs.select(".mould-table>tbody>tr>td>div>div>audio")

    parsed: List[GameKeeVoice] = []
    for au in audios:
        url: str = cast(str, au["src"])
        if not url.startswith("http"):
            url = f"https:{url}"

        tr1: Tag = au.parent.parent.parent.parent  # type: ignore
        tds: ResultSet[Tag] = tr1.find_all("td")
        title = tds[0].text.strip()
        jp = "\n".join(tds[2].stripped_strings)

        tr2 = tr1.next_sibling
        cn = "\n".join(tr2.stripped_strings)  # type: ignore
        parsed.append(GameKeeVoice(title, jp, cn, url))

    return parsed


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
    img_urls = [f"https:{x}" if x.startswith("//") else x for x in img_urls]
    return img_urls
