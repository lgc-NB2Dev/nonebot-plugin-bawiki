from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher

from ..data.shittim_chest import ServerType, get_season_list, render_raid_rank

cmd_raid_rank = on_command("ba总力档线")


@cmd_raid_rank.handle()
async def _(matcher: Matcher):
    server = ServerType.Official
    seasons = await get_season_list()
    img = await render_raid_rank(server, seasons[0])
    await matcher.finish(MessageSegment.image(img))
