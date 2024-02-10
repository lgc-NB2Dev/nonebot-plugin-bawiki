import asyncio
import datetime
from io import BytesIO
from typing import Any, Dict, List, Literal, Optional, cast
from typing_extensions import Unpack

from nonebot import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from pil_utils import BuildImage

from ..config import config
from ..util import AsyncReqKwargs, RespType as Rt, async_req, recover_alia


async def db_get(suffix: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    kwargs["base_urls"] = config.ba_bawiki_db_url
    return await async_req(suffix, **kwargs)


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


async def db_get_event_alias() -> Dict[str, List[str]]:
    return await db_get("data/event_alias.json")


async def db_get_gacha_data() -> Dict[str, Any]:
    return await db_get("data/gacha.json")


async def db_get_emoji() -> List[str]:
    return await db_get("data/emoji.json")


async def schale_to_gamekee(o: str) -> str:
    diff = await db_get_schale_to_gamekee()
    if o in diff:
        o = diff[o]
    return o.replace("(", "（").replace(")", "）")


async def recover_stu_alia(a: str, game_kee: bool = False) -> str:
    ret = recover_alia(a, await db_get_stu_alias())

    if game_kee:
        ret = await schale_to_gamekee(ret)

    return ret


async def db_wiki_stu(name: str):
    wiki = (await db_get_wiki_data())["student"]
    if not (url := wiki.get(name)):
        return "没有找到该角色的角评，可能是学生名称错误或者插件还未收录该角色角评"
    return MessageSegment.image(await db_get(url, resp_type=Rt.BYTES))


async def db_wiki_raid(
    raid_id: Any,
    servers: Optional[List[int]] = None,
    is_wiki: bool = False,
    terrain: Optional[str] = None,
):
    if not servers:
        servers = [0, 1]
    wiki = (await db_get_wiki_data())["raid"]

    if not (boss := wiki.get(str(raid_id))):
        logger.warning(f"Raid boss {raid_id} not found")
        return "没有找到该总力战Boss"

    terrain_raid = None
    if terrain:
        if t := boss["terrains"].get(
            recover_alia(terrain, await db_get_terrain_alias()),
        ):
            terrain_raid = t
        else:
            logger.warning(f"Raid boss {raid_id} terrain {terrain} not found")
            return "还没有进行过该环境的总力战"

    img = []
    if is_wiki:
        if not (wiki_url := boss.get("wiki")):
            logger.warning(f"Raid boss {raid_id} wiki not found")
            return "该总力战Boss暂无机制介绍"
        img.append(wiki_url)
    else:
        img_ = [terrain_raid] if terrain_raid else list(boss["terrains"].values())
        for i in img_:
            img.extend(i[s] for s in servers)

    return [
        MessageSegment.image(x)
        for x in await asyncio.gather(*(db_get(x, resp_type=Rt.BYTES) for x in img))
    ]


async def db_wiki_event(event_id: Any):
    event_id = str(event_id)
    wiki = (await db_get_wiki_data())["event"]
    if not (ev := wiki.get(event_id)):
        logger.warning(f"Event {event_id} not found")
        return f"没有找到 ID 为 {event_id} 的活动"
    return Message(
        MessageSegment.image(x)
        for x in await asyncio.gather(*(db_get(x, resp_type=Rt.BYTES) for x in ev))
    )


async def db_wiki_time_atk(raid_id: int):
    if raid_id >= 1000:
        raid_id = int(raid_id / 1000)
    wiki = (await db_get_wiki_data())["time_atk"]
    if raid_id > len(wiki):
        logger.warning(f"Time atk {raid_id} not found")
        return f"没有找到该综合战术考试（目前共有{len(wiki)}个综合战术考试）"
    raid_id -= 1

    return MessageSegment.image(await db_get(wiki[raid_id], resp_type=Rt.BYTES))


async def db_wiki_craft():
    wiki = (await db_get_wiki_data())["craft"]
    return [
        MessageSegment.image(x)
        for x in await asyncio.gather(*(db_get(y, resp_type=Rt.BYTES) for y in wiki))
    ]


async def db_wiki_furniture():
    wiki = (await db_get_wiki_data())["furniture"]
    return [
        MessageSegment.image(x)
        for x in await asyncio.gather(*(db_get(y, resp_type=Rt.BYTES) for y in wiki))
    ]


async def db_future(
    future_type: Literal["global", "chinese"],
    date: Optional[datetime.datetime] = None,
    num: int = 1,
    all_img: bool = False,
):
    data = (await db_get_wiki_data())[f"{future_type}_future"]
    img = cast(bytes, await db_get(data["img"], resp_type=Rt.BYTES))

    if all_img:
        return MessageSegment.image(img)

    compare_date = date or datetime.datetime.now().astimezone()
    index = -1
    for i, v in enumerate(parts := data["parts"]):
        start, end = [
            datetime.datetime.strptime(x, "%Y/%m/%d").astimezone() for x in v["date"]
        ]
        if start <= compare_date < end:
            index = i

    if not date:
        index += 1

    if index == -1:
        return "没有找到符合日期的部分"

    sliced_parts = parts[index : index + num]

    if (pl := len(sliced_parts)) < num:
        return f"抱歉，目前后面还没有这么长的前瞻列表……（目前后面还有 {pl} 个）"

    banner_start, banner_end = data["banner"]
    pos_start = sliced_parts[0]["part"][0]
    pos_end = sliced_parts[-1]["part"][1]

    img = BuildImage.open(BytesIO(img))
    width = img.width
    banner = img.crop((0, banner_start, width, banner_end))
    content = img.crop((0, pos_start, width, pos_end))

    bg = (
        BuildImage.new("RGB", (width, banner.height + content.height))
        .paste(banner)
        .paste(content, (0, banner.height))
    )
    return MessageSegment.image(bg.save("PNG"))
