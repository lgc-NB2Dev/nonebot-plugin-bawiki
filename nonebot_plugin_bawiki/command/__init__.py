import importlib
from pathlib import Path
from typing import List, TypedDict

from nonebot import logger
from pypinyin import lazy_pinyin


class HelpDict(TypedDict):
    func: str
    trigger_method: str
    trigger_condition: str
    brief_des: str
    detail_des: str


HelpList = List[HelpDict]

help_list: HelpList = []


def sort_help():
    help_list.sort(key=lambda x: "".join(lazy_pinyin(x["func"])))


def append_and_sort_help(help_dict: HelpDict):
    help_list.append(help_dict)
    sort_help()


def load_commands():
    for module in Path(__file__).parent.iterdir():
        if module.name.startswith("_"):
            continue

        module = importlib.import_module(f".{module.stem}", __package__)
        assert module

        if not hasattr(module, "help_list"):
            logger.warning(f"Command module `{module.__name__}` has no `help_list`")
        else:
            help_list.extend(module.help_list)

    sort_help()
