from datetime import datetime, timedelta
from enum import Enum, auto
from functools import lru_cache, partial
from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Sequence,
    TypedDict,
    TypeVar,
    Union,
)
from typing_extensions import Unpack

from async_lru import alru_cache
from httpx import AsyncClient
from nonebot import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from PIL import Image, ImageOps
from pil_utils import BuildImage

from .config import config

T = TypeVar("T")
NestedIterable = Iterable[Union[T, Iterable["NestedIterable[T]"]]]


class ResponseType(Enum):
    JSON = auto()
    TEXT = auto()
    BYTES = auto()


class AsyncReqKwargs(TypedDict, total=False):
    method: str
    params: Optional[Dict[Any, Any]]
    headers: Optional[Dict[str, Any]]
    content: Union[str, bytes, None]
    data: Optional[Dict[str, Any]]
    json: Optional[Any]

    base_url: str
    proxies: Optional[str]

    response_type: ResponseType
    retries: int
    raise_for_status: bool


@alru_cache(ttl=config.ba_req_cache_ttl, maxsize=None)
async def async_req(*urls: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    if not urls:
        raise ValueError("No URL specified")

    method = kwargs.pop("method", "GET")
    params = kwargs.pop("params", None)
    headers = kwargs.pop("headers", None)
    content = kwargs.pop("content", None)
    data = kwargs.pop("data", None)
    json = kwargs.pop("json", None)

    base_url = kwargs.pop("base_url", "")
    proxies = kwargs.pop("proxies", None)

    response_type = kwargs.pop("response_type", ResponseType.JSON)
    retries = kwargs.pop("retries", config.ba_req_retry)
    raise_for_status = kwargs.pop("raise_for_status", True)

    url, rest = urls[0], urls[1:]
    try:
        async with AsyncClient(
            base_url=base_url,
            proxies=proxies,
            follow_redirects=True,
        ) as cli:
            resp = await cli.request(
                method,
                url,
                params=params,
                headers=headers,
                content=content,
                data=data,
                json=json,
            )
            if raise_for_status:
                resp.raise_for_status()

            if response_type == ResponseType.JSON:
                return await resp.json()
            if response_type == ResponseType.TEXT:
                return resp.text
            return resp.content

    except Exception as e:
        recursive_func = partial(async_req, **kwargs)

        if retries <= 0:
            if not rest:
                raise

            logger.error(
                f"Requesting next url because error occurred while requesting {url}: {e!r}",
            )
            logger.opt(exception=e).debug("Error Stack")
            return await recursive_func(*rest)

        retries -= 1
        logger.error(
            f"Retrying ({retries} left) because error occurred while requesting {url}: {e!r}",
        )
        logger.opt(exception=e).debug("Error Stack")
        return await recursive_func(*urls)


def clear_req_cache() -> int:
    info = async_req.cache_info()
    async_req.cache_clear()
    return info.currsize


def get_proxy_url(is_oversea: bool) -> Optional[str]:
    proxy = config.ba_oversea_proxy if is_oversea else config.ba_cn_proxy
    if proxy is None:
        return None
    return proxy or None


def format_timestamp(t: int) -> str:
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")


def recover_alia(origin: str, alia_dict: Dict[str, List[str]]):
    origin = replace_brackets(origin).strip()
    origin_ = origin.lower()

    # 精确匹配
    for k, li in alia_dict.items():
        if origin_ in li or origin_ == k:
            return k

    # 没找到，模糊匹配
    origin_ = origin.replace(" ", "")
    for k, li in alia_dict.items():
        li = [x.replace(" ", "") for x in ([k, *li])]
        for v in li:
            if origin_ in v:
                return k

    return origin


class ParsedTimeDelta(NamedTuple):
    days: int
    hours: int
    minutes: int
    seconds: int


def parse_time_delta(t: timedelta) -> ParsedTimeDelta:
    mm, ss = divmod(t.seconds, 60)
    hh, mm = divmod(mm, 60)
    dd = t.days or 0
    return ParsedTimeDelta(dd, hh, mm, ss)


def img_invert_rgba(im: Image.Image) -> Image.Image:
    # https://stackoverflow.com/questions/2498875/how-to-invert-colors-of-image-with-pil-python-imaging
    r, g, b, a = im.split()
    rgb_image = Image.merge("RGB", (r, g, b))
    inverted_image = ImageOps.invert(rgb_image)
    r2, g2, b2 = inverted_image.split()
    return Image.merge("RGBA", (r2, g2, b2, a))


def replace_brackets(original: str) -> str:
    return original.replace("（", "(").replace("）", "(")


def splice_msg(msgs: Sequence[Union[str, MessageSegment, Message]]) -> Message:
    im = Message()
    for i, v in enumerate(msgs):
        if isinstance(v, str) and (i != 0):
            v = f"\n{v}"
        im += v
    return im


def split_list(li: Iterable[T], length: int) -> List[List[T]]:
    latest = []
    tmp = []
    for n, i in enumerate(li):
        tmp.append(i)
        if (n + 1) % length == 0:
            latest.append(tmp)
            tmp = []
    if tmp:
        latest.append(tmp)
    return latest


def split_pic(pic: Image.Image, max_height: int = 4096) -> List[Image.Image]:
    pw, ph = pic.size
    if ph <= max_height:
        return [pic]

    ret = []
    need_merge_last = ph % max_height < max_height // 2
    iter_times = ph // max_height

    now_h = 0
    for i in range(iter_times):
        if i == iter_times - 1 and need_merge_last:
            ret.append(pic.crop((0, now_h, pw, ph)))
            break

        ret.append(pic.crop((0, now_h, pw, now_h + max_height)))
        now_h += max_height

    return ret


def i2b(image: Image.Image, img_format: str = "JPEG") -> BytesIO:
    buf = BytesIO()
    image.save(buf, img_format)
    buf.seek(0)
    return buf


@lru_cache(maxsize=8)
def read_image(path: Path) -> BuildImage:
    content = path.read_bytes()
    bio = BytesIO(content)
    return BuildImage.open(bio)
