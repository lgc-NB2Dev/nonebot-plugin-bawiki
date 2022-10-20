import datetime
import json
from typing import Dict, List

from PIL import Image, ImageOps
from aiohttp import ClientSession

from .config import config


def format_timestamp(t):
    return datetime.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def recover_alia(origin: str, alia_dict: Dict[str, List[str]]):
    origin = replace_brackets(origin.lower()).strip()

    # 精确匹配
    for k, li in alia_dict.items():
        if origin in li or origin == k:
            return k

    # 没找到，模糊匹配
    origin_ = origin.replace(" ", "")
    for k, li in alia_dict.items():
        li = [x.replace(" ", "") for x in ([k] + li)]
        for v in li:
            if origin_ in v:
                return k

    return origin


def parse_time_delta(t: datetime.timedelta):
    mm, ss = divmod(t.seconds, 60)
    hh, mm = divmod(mm, 60)
    dd = t.days or 0
    return dd, hh, mm, ss


def img_invert_rgba(im: Image.Image):
    # https://stackoverflow.com/questions/2498875/how-to-invert-colors-of-image-with-pil-python-imaging
    r, g, b, a = im.split()
    rgb_image = Image.merge("RGB", (r, g, b))
    inverted_image = ImageOps.invert(rgb_image)
    r2, g2, b2 = inverted_image.split()
    final_transparent_image = Image.merge("RGBA", (r2, g2, b2, a))
    return final_transparent_image


async def async_req(
    url, is_json=True, raw=False, method="GET", **kwargs
) -> str | bytes | dict | list:
    async with ClientSession() as c:
        async with c.request(method, url, **kwargs, proxy=config.proxy) as r:
            ret = (await r.read()) if raw else (await r.text())
            if is_json:
                ret = json.loads(ret)
            return ret


def replace_brackets(original: str):
    return original.replace("（", "(").replace("）", "(")
