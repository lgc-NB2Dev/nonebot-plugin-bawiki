import asyncio
from argparse import Namespace

from nonebot import logger, on_command, on_shell_command
from nonebot.adapters.onebot.v11 import ActionFailed, Message, MessageSegment
from nonebot.exception import FinishedException, ParserExit
from nonebot.internal.matcher import Matcher
from nonebot.params import CommandArg, ShellCommandArgs
from nonebot.permission import SUPERUSER
from nonebot.rule import ArgumentParser
from nonebot_plugin_apscheduler import scheduler

from .const import BAWIKI_DB_URL, SCHALE_URL
from .data_bawiki import (
    db_get_extra_l2d_list,
    db_get_raid_alias,
    db_get_terrain_alias,
    db_wiki_raid,
    db_wiki_stu,
    recover_stu_alia,
    schale_to_gamekee,
)
from .data_gamekee import (
    game_kee_calender,
    game_kee_page_url,
    get_game_kee_page,
    get_stu_cid_li,
    grab_l2d,
)
from .data_schaledb import (
    draw_fav_li,
    find_current_event,
    schale_calender,
    schale_get_common,
    schale_get_stu_dict,
    schale_get_stu_info,
)
from .util import async_req, clear_req_cache, recover_alia


@scheduler.scheduled_job("interval", hours=3)
async def _():
    clear_req_cache()


h_clear_cache = on_command("ba清空缓存", aliases={"ba清除缓存"}, permission=SUPERUSER)


@h_clear_cache.handle()
async def _(matcher: Matcher):
    clear_req_cache()
    await matcher.finish("缓存已清空～")


handler_calender = on_command("ba日程表")


@handler_calender.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg: str = arg.extract_plain_text()

    await matcher.send("正在绘制图片，请稍等")
    try:
        if "schale" in (arg := arg.lower()):
            arg = arg.replace("schale", "").strip()
            servers = []

            if (not arg) or ("日" in arg) or ("j" in arg):
                servers.append(0)
            if (not arg) or ("国际服" in arg) or ("g" in arg):
                servers.append(1)

            await asyncio.gather(
                *[
                    matcher.send(x)
                    for x in (
                        await asyncio.gather(*[schale_calender(x) for x in servers])
                    )
                ]
            )
            await matcher.finish()
        else:
            await matcher.finish(await game_kee_calender())
    except (FinishedException, ActionFailed):
        raise
    except:
        logger.exception("绘制日程表图片出错")
        return await matcher.finish("绘制日程表图片出错，请检查后台输出")


async def send_wiki_page(sid, matcher: Matcher):
    url = game_kee_page_url(sid)
    await matcher.send(f"请稍等，正在截取Wiki页面……\n{url}")

    try:
        img = await get_game_kee_page(url)
    except:
        logger.exception(f"截取wiki页面出错 {url}")
        return await matcher.finish("截取页面出错，请检查后台输出")

    await matcher.finish(MessageSegment.image(img))


stu_schale = on_command("ba学生图鉴")


@stu_schale.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    try:
        ret = await schale_get_stu_dict()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表表出错，请检查后台输出")

    if not ret:
        return await matcher.finish("没有获取到学生列表数据")

    if not (data := ret.get(await recover_stu_alia(arg))):
        return await matcher.finish("未找到该学生")

    stu_name = data["PathName"]
    await matcher.send(f"请稍等，正在截取SchaleDB页面～\n" f"{SCHALE_URL}?chara={stu_name}")

    try:
        img = MessageSegment.image(await schale_get_stu_info(stu_name))
    except:
        logger.exception(f"截取schale db页面出错 chara={stu_name}")
        return await matcher.finish("截取页面出错，请检查后台输出")

    await matcher.finish(img)


stu_rank = on_command("ba学生评价", aliases={"ba角评"})


@stu_rank.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    try:
        im = await db_wiki_stu(await recover_stu_alia(arg))
    except:
        logger.exception(f"获取角评出错")
        return await matcher.finish("获取角评出错，请检查后台输出")

    await matcher.finish(im)


stu_wiki = on_command("ba学生wiki", aliases={"ba学生Wiki", "ba学生WIKI"})


@stu_wiki.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称")

    try:
        ret = await get_stu_cid_li()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表出错，请检查后台输出")

    if not ret:
        return await matcher.finish("没有获取到学生列表数据")

    if not (sid := ret.get(await recover_stu_alia(arg, True))):
        return await matcher.finish("未找到该学生")

    await send_wiki_page(sid, matcher)


fav = on_command("ba好感度", aliases={"ba羁绊", "bal2d", "baL2D", "balive2d", "baLive2D"})


@fav.handle()
async def _(matcher: Matcher, arg: Message = CommandArg()):
    async def get_l2d(stu_name):
        if r := (await db_get_extra_l2d_list()).get(stu_name):
            return f"{BAWIKI_DB_URL}{r}"

        return await grab_l2d((await get_stu_cid_li()).get(stu_name))

    arg = arg.extract_plain_text().strip()
    if not arg:
        return await matcher.finish("请提供学生名称或所需的羁绊等级")

    # 好感度等级
    if arg.isdigit():
        arg = int(arg)
        if arg > 9:
            return await matcher.finish("学生解锁L2D最高只需要羁绊等级9")
        if arg < 1:
            return await matcher.finish("学生解锁L2D最低只需要羁绊等级1")

        try:
            p = await draw_fav_li(arg)
        except:
            logger.exception("绘制图片出错")
            return await matcher.finish("绘制图片出错，请检查后台输出")

        return await matcher.finish(p)

    # 学生名称
    arg = await recover_stu_alia(arg)

    try:
        ret = await schale_get_stu_dict()
    except:
        logger.exception("获取学生列表出错")
        return await matcher.finish("获取学生列表表出错，请检查后台输出")

    if stu := ret.get(arg):
        if not (lvl := stu["MemoryLobby"]):
            return await matcher.finish("该学生没有L2D")

        im = MessageSegment.text(f'{stu["Name"]} 在羁绊等级 {lvl[0]} 时即可解锁L2D\nL2D预览：')
        if p := await get_l2d(await schale_to_gamekee(arg)):
            im += [MessageSegment.image(await async_req(x, raw=True)) for x in p]
        else:
            im += (
                "没找到该学生的L2D看板\n"
                "可能原因：\n"
                "- GameKee页面爬取不到角色L2D图片\n"
                "- GameKee和插件没有收录该学生的L2D\n"
            )
        return await matcher.finish(im)

    return await matcher.finish("未找到学生")


raid_wiki_parser = ArgumentParser("ba总力战")
raid_wiki_parser.add_argument(
    "name", nargs="?", default=None, help="总力战Boss名称，不指定默认取当前服务器总力战Boss"
)
raid_wiki_parser.add_argument(
    "-s",
    "--server",
    nargs="*",
    help="服务器名称，`j`或`日`代表日服，`g`或`国`代表国际服，可指定多个，默认全选",
    default=["j", "g"],
)
raid_wiki_parser.add_argument("-t", "--terrain", help="指定总力战环境，不指定默认全选，不带Boss名称该参数无效")
raid_wiki_parser.add_argument(
    "-w", "--wiki", action="store_true", help="发送该总力战Boss的技能机制而不是配队推荐"
)

raid_wiki = on_shell_command("ba总力战", parser=raid_wiki_parser)


@raid_wiki.handle()
async def _(matcher: Matcher, foo: ParserExit = ShellCommandArgs()):
    im = ""
    if foo.status != 0:
        im = "参数错误\n"
    await matcher.finish(f"{im}{foo.message}")


@raid_wiki.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    if not args.server:
        await matcher.finish(f"请指定server参数")

    server = set()
    for s in args.server:
        if ("日" in s) or ("j" in s):
            server.add(0)
        elif ("国" in s) or ("g" in s):
            server.add(1)
    server = list(server)
    server.sort()

    tasks = []
    if not args.name:
        try:
            common = await schale_get_common()
            for s in server:
                raid = common["regions"][s]["current_raid"]
                if (r := find_current_event(raid)[0]) and (raid := r["raid"]) < 1000:
                    tasks.append(db_wiki_raid(raid, [s], args.wiki, r.get("terrain")))
        except:
            logger.exception(f"获取当前总力战失败")
            return await matcher.finish(f"获取当前总力战失败")

        if not tasks:
            return await matcher.finish(f"目前服务器没有正在进行的总力战，请手动指定")
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
            )
        )

    try:
        ret = await asyncio.gather(*tasks)
    except:
        logger.exception("获取总力战wiki失败")
        return await matcher.finish(f"获取图片失败，请检查后台输出")

    im = Message()
    for i, v in enumerate(ret):
        if (is_str := isinstance(v, str)) and (not i == 0):
            im += "\n"

        if is_str:
            im += v
        else:
            im.extend([MessageSegment.image(x) for x in v])

    await matcher.finish(im)
