"""爬取gamekee角色介绍页面l2d"""

import asyncio
import random
import re
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


async def get_stu_li():
    ret = await game_kee_request("https://ba.gamekee.com/v1/wiki/entry")

    li = None
    for i in ret["entry_list"]:
        if i["id"] == 23941:

            for ii in i["child"]:
                if ii["id"] == 49443:
                    li = ii["child"]

    return {x["name"]: x for x in li}


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


if __name__ == "__main__":
    asyncio.run(get_stu_dict())
