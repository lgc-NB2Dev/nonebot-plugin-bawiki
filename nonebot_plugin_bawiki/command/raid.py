import asyncio
from argparse import Namespace
from typing import TYPE_CHECKING

from nonebot import on_shell_command
from nonebot.exception import ParserExit
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser

from ..data.bawiki import db_get_raid_alias, db_get_terrain_alias, db_wiki_raid
from ..data.schaledb import find_current_event, schale_get_config
from ..help import FT_E, FT_S
from ..util import recover_alia, splice_msg

if TYPE_CHECKING:
    from . import HelpList

help_list: "HelpList" = [
    {
        "func": "总力战一图流",
        "trigger_method": "指令",
        "trigger_condition": "ba总力战",
        "brief_des": "查询总力战推荐配队/Boss机制",
        "detail_des": (
            "发送当前或指定总力战Boss的配队/机制一图流攻略图\n"
            "支持部分Boss别名\n"
            "图片作者 B站@夜猫咪喵喵猫\n"
            " \n"
            f"使用 {FT_S}ba总力战 -h{FT_E} 查询指令用法\n"
            " \n"
            "指令示例：\n"
            f"- {FT_S}ba总力战{FT_E}（日服&国际服当前总力战Boss配队攻略）\n"
            f"- {FT_S}ba总力战 -s j{FT_E}（日服当前总力战Boss配队攻略）\n"
            f"- {FT_S}ba总力战 -s j -w{FT_E}（日服当前总力战Boss机制图）\n"
            f"- {FT_S}ba总力战 寿司{FT_E}（Kaiten FX Mk.0 配队攻略）\n"
            f"- {FT_S}ba总力战 寿司 -t 屋外{FT_E}（Kaiten FX Mk.0 屋外战配队攻略）"
        ),
    },
]


raid_wiki_parser = ArgumentParser("ba总力战")
raid_wiki_parser.add_argument(
    "name",
    nargs="?",
    default=None,
    help="总力战Boss名称，不指定默认取当前服务器总力战Boss",
)
raid_wiki_parser.add_argument(
    "-s",
    "--server",
    nargs="*",
    help="服务器名称，`j`或`日`代表日服，`g`或`国际`代表国际服，`c`或`国`代表国服，可指定多个，默认全选",
    default=["j", "g", "c"],
)
raid_wiki_parser.add_argument(
    "-t",
    "--terrain",
    help="指定总力战环境，不指定默认全选，不带Boss名称该参数无效",
)
raid_wiki_parser.add_argument(
    "-w",
    "--wiki",
    action="store_true",
    help="发送该总力战Boss的技能机制而不是配队推荐",
)

cmd_raid_wiki = on_shell_command("ba总力战", parser=raid_wiki_parser)


@cmd_raid_wiki.handle()
async def _(matcher: Matcher, foo: ParserExit = ShellCommandArgs()):
    im = ""
    if foo.status != 0:
        im = "参数错误\n"
    await matcher.finish(f"{im}{foo.message}")


@cmd_raid_wiki.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    if not args.server:
        await matcher.finish("请指定server参数")

    keys = {
        0: ("日", "j"),
        1: ("国际", "g"),
        2: ("国", "c"),
    }

    server = set()
    for s in args.server:
        for i, k in keys.items():
            if s in k:
                server.add(i)
    server = list(server)
    server.sort()

    tasks = []
    if not args.name:
        try:
            common = await schale_get_config()
            for s in server:
                raid = common["Regions"][s]["CurrentRaid"]
                if (r := find_current_event(raid)) and (raid := r[0]["raid"]) < 1000:
                    tasks.append(
                        db_wiki_raid(raid, [s], args.wiki, r[0].get("terrain")),
                    )
        except Exception:
            logger.exception("获取当前总力战失败")
            await matcher.finish("获取当前总力战失败")

        if not tasks:
            await matcher.finish("目前服务器没有正在进行的总力战，请手动指定")
    else:
        tasks.append(
            db_wiki_raid(
                recover_alia(args.name, await db_get_raid_alias()),
                server,
                args.wiki,
                (
                    recover_alia(args.terrain, await db_get_terrain_alias())
                    if args.terrain
                    else None
                ),
            ),
        )

    try:
        ret = await asyncio.gather(*tasks)
    except Exception:
        logger.exception("获取总力战wiki失败")
        await matcher.finish("获取图片失败，请检查后台输出")

    await matcher.finish(splice_msg(ret))
