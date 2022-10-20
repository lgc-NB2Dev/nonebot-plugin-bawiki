import asyncio
from typing import Any, Dict, List

from nonebot.adapters.onebot.v11 import MessageSegment

from .const import BAWIKI_DB_URL
from .util import async_req, recover_alia


async def db_get(suffix, raw=False):
    return await async_req(f"{BAWIKI_DB_URL}{suffix}", raw=raw)


async def db_get_wiki_data() -> Dict[str, Any]:
    return await db_get("data/wiki.json")


async def db_get_stu_alias() -> Dict[str, List[str]]:
    return await db_get("data/stu_alias.json")


async def db_get_schale_to_gamekee() -> Dict[str, str]:
    return await db_get("data/schale_to_gamekee.json")


async def db_get_extra_l2d_list() -> Dict[str, List[str]]:
    return await db_get("data/extra_l2d_list.json")


async def db_get_raid_alias() -> Dict[str, List[str]]:
    return await db_get("data/raid_alias.json")


async def db_get_terrain_alias() -> Dict[str, List[str]]:
    return await db_get("data/terrain_alias.json")


async def schale_to_gamekee(o: str) -> str:
    diff = await db_get_schale_to_gamekee()
    if o in diff:
        o = diff[o]
    return o.replace("(", "（").replace(")", "）")


async def recover_stu_alia(a, game_kee=False) -> str:
    ret = recover_alia(a, await db_get_stu_alias())

    if game_kee:
        ret = await schale_to_gamekee(ret)

    return ret


async def db_wiki_stu(name):
    wiki = (await db_get_wiki_data())["student"]
    if not (url := wiki.get(name)):
        return "没有找到该角色的角评，可能是学生名称错误或者插件还未收录该角色角评"
    return MessageSegment.image(await db_get(url, True))


async def db_wiki_raid(raid_id, servers=None, is_wiki=False, terrain=None):
    if not servers:
        servers = [0, 1]
    wiki = (await db_get_wiki_data())["raid"]

    if not (boss := wiki.get(str(raid_id))):
        return "没有找到该总力战Boss"

    terrain_raid = None
    if terrain:
        if t := boss["terrains"].get(
            recover_alia(terrain, await db_get_terrain_alias())
        ):
            terrain_raid = t
        else:
            return "还没有进行过该环境的总力战"

    img = []
    if is_wiki:
        if not (wiki_url := boss.get("wiki")):
            return "该总力战Boss暂无机制介绍"
        img.append(wiki_url)
    else:
        if terrain_raid:
            img_ = [terrain_raid]
        else:
            img_ = list(boss["terrains"].values())
        for i in img_:
            for s in servers:
                img.append(i[s])

    return await asyncio.gather(*[db_get(x, True) for x in img])
