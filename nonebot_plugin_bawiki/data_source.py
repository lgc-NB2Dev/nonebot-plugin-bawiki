import asyncio
import time

from aiohttp import ClientSession
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page


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

    li = None
    for i in ret["entry_list"]:
        if i["id"] == 23941:

            for ii in i["child"]:
                if ii["id"] == 49443:
                    li = ii["child"]

    return {x["name"]: x["content_id"] for x in li}


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


if __name__ == "__main__":

    async def main():
        import jinja2
        from util import format_timestamp
        from datetime import datetime
        from pathlib import Path

        ret = await get_calender()

        for i in ret:
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
        print(html)

    asyncio.run(main())
