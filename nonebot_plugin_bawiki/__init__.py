from nonebot.plugin import PluginMetadata

from .__main__ import *  # type:ignore

__version__ = "0.5.0b5"
__plugin_meta__ = PluginMetadata(
    name="BAWiki",
    description="碧蓝档案Wiki插件",
    usage=(
        "感谢各位sensei使用本插件！\n"
        "插件有缓存机制，每3小时自动清空一次，如果插件遇到问题可以先手动清空缓存试一下捏\n"
        "装载PicMenu插件即可查看插件详细菜单哦\n"
        "祝玩得愉快～"
    ),
    extra={
        "menu_data": [
            {
                "func": "日程表",
                "trigger_method": "指令",
                "trigger_condition": "ba日程表",
                "brief_des": "查看活动日程表",
                "detail_des": (
                    "查看当前未结束的卡池、活动以及起止时间，"
                    "默认为GameKee源，可以在指令后带参数使用SchaleDB数据源\n"
                    " \n"
                    "指令示例：\n"
                    "- <ft color=(238,120,0)>ba日程表</ft> （GameKee源）\n"
                    "- <ft color=(238,120,0)>ba日程表 schaledb</ft> （SchaleDB源，日服国际服一起发）\n"
                    "- <ft color=(238,120,0)>ba日程表 schale 国际服</ft> （SchaleDB源，国际服）"
                ),
            },
            {
                "func": "学生图鉴",
                "trigger_method": "指令",
                "trigger_condition": "ba学生图鉴",
                "brief_des": "查询学生详情（SchaleDB）",
                "detail_des": (
                    "访问对应学生SchaleDB页面并截图，支持部分学生别名\n"
                    " \n"
                    "指令示例：\n"
                    "- <ft color=(238,120,0)>ba学生图鉴 白子</ft>\n"
                    "- <ft color=(238,120,0)>ba学生图鉴 xcw</ft>"
                ),
            },
            {
                "func": "学生Wiki",
                "trigger_method": "指令",
                "trigger_condition": "ba学生wiki",
                "brief_des": "查询学生详情（GameKee）",
                "detail_des": (
                    "访问对应学生GameKee Wiki页面并截图，支持部分学生别名\n"
                    " \n"
                    "可以用这些指令触发：\n"
                    "- <ft color=(238,120,0)>ba学生wiki</ft>\n"
                    "- <ft color=(238,120,0)>ba学生Wiki</ft>\n"
                    "- <ft color=(238,120,0)>ba学生WIKI</ft>\n"
                    " \n"
                    "指令示例：\n"
                    "- <ft color=(238,120,0)>ba学生wiki 白子</ft>\n"
                    "- <ft color=(238,120,0)>ba学生wiki xcw</ft>"
                ),
            },
            {
                "func": "羁绊查询",
                "trigger_method": "指令",
                "trigger_condition": "ba羁绊",
                "brief_des": "查询学生解锁L2D需求的羁绊等级",
                "detail_des": (
                    "使用学生名称查询该学生解锁L2D看板需求的羁绊等级以及L2D预览，"
                    "或者使用羁绊等级级数查询哪些学生达到该等级时解锁L2D看板\n"
                    "使用学生名称查询时支持部分学生别名\n"
                    " \n"
                    "可以用这些指令触发：\n"
                    "- <ft color=(238,120,0)>ba羁绊</ft>\n"
                    "- <ft color=(238,120,0)>ba好感度</ft>\n"
                    "- <ft color=(238,120,0)>bal2d</ft>\n"
                    " \n"
                    "指令示例：\n"
                    "- <ft color=(238,120,0)>ba羁绊 xcw</ft>\n"
                    "- <ft color=(238,120,0)>ba羁绊 9</ft>"
                ),
            },
            {
                "func": "角色评价",
                "trigger_method": "指令",
                "trigger_condition": "ba角评",
                "brief_des": "查询学生角评一图流",
                "detail_des": (
                    "发送一张指定角色的评价图\n"
                    "支持部分学生别名\n"
                    "角评图作者 B站@夜猫咪喵喵猫\n"
                    " \n"
                    "可以用这些指令触发：\n"
                    "- <ft color=(238,120,0)>ba学生评价</ft>\n"
                    "- <ft color=(238,120,0)>ba角评</ft>\n"
                    " \n"
                    "指令示例：\n"
                    "- <ft color=(238,120,0)>ba学生评价 白子</ft>\n"
                    "- <ft color=(238,120,0)>ba角评 xcw</ft>"
                ),
            },
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
                    "使用 <ft color=(238,120,0)>ba总力战 -h</ft> 查询指令用法\n"
                    " \n"
                    "指令示例：\n"
                    "- <ft color=(238,120,0)>ba总力战</ft>（日服&国际服当前总力战Boss配队攻略）\n"
                    "- <ft color=(238,120,0)>ba总力战 -s j</ft>（日服当前总力战Boss配队攻略）\n"
                    "- <ft color=(238,120,0)>ba总力战 -s j -w</ft>（日服当前总力战Boss机制图）\n"
                    "- <ft color=(238,120,0)>ba总力战 寿司</ft>（Kaiten FX Mk.0 配队攻略）\n"
                    "- <ft color=(238,120,0)>ba总力战 寿司 -t 屋外</ft>（Kaiten FX Mk.0 屋外战配队攻略）\n"
                ),
            },
            {
                "func": "清空缓存",
                "trigger_method": "超级用户 指令",
                "trigger_condition": "ba清空缓存",
                "brief_des": "清空插件请求缓存",
                "detail_des": (
                    "手动清空插件请求网络缓存下来的数据（正常3小时清空一次）\n"
                    "如果插件出问题了，或者你想提前看到新内容，不妨试试清空一下插件缓存\n"
                    "注：该指令只能由<ft color=(238,120,0)>超级用户</ft>触发\n"
                    " \n"
                    "可以用这些指令触发：\n"
                    "- <ft color=(238,120,0)>ba清空缓存</ft>\n"
                    "- <ft color=(238,120,0)>ba清除缓存</ft>"
                ),
            },
        ],
        "menu_template": "default",
    },
)
