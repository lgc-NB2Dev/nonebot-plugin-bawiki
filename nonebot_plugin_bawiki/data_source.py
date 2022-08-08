import asyncio
import time

from aiohttp import ClientSession


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
