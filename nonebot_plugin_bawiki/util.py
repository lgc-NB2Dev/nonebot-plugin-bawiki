import asyncio
import itertools
from datetime import datetime, timedelta
from enum import Enum, auto
from io import BytesIO
from pathlib import Path
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    cast,
)
from typing_extensions import ParamSpec, Unpack
from urllib.parse import urljoin
from weakref import WeakSet

import anyio
from async_lru import _LRUCacheWrapper, alru_cache
from httpx import AsyncClient
from nonebot import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.matcher import current_matcher
from PIL import Image, ImageOps
from pil_utils import BuildImage

from .config import config

T = TypeVar("T")
R = TypeVar("R")
K = TypeVar("K")
V = TypeVar("V")
TC = TypeVar("TC", bound=Callable)
P = ParamSpec("P")
NestedIterable = Iterable[Union[T, Iterable["NestedIterable[T]"]]]
PathType = Union[str, Path, anyio.Path]
SendableType = Union[Message, MessageSegment, str]

KEY_ILLEGAL_COUNT = "_ba_illegal_count"


# region async_req
# 这玩意真的太不优雅了
# 有必要重新写一个 request cache，可以参考 hishel


wrapped_cache_functions: "WeakSet['SupportDictCacheWrapper']" = WeakSet()


class SupportDictCacheWrapper(Generic[P, R], _LRUCacheWrapper[R]):  # type: ignore  # ignore final class
    def __init__(
        self,
        fn: Callable[P, Coroutine[Any, Any, R]],
        maxsize: Optional[int] = 128,
        typed: bool = False,
        ttl: Optional[float] = None,
    ) -> None:
        async def wrapped_func(*args, **kwargs):
            new_args, new_kwargs = self._recover_args(args, kwargs)
            return await cast(Callable, fn)(*new_args, **new_kwargs)

        super().__init__(wrapped_func, maxsize, typed, ttl)

    def _process_args(
        self,
        func: Callable[[Any], Any],
        args: Tuple,
        kwargs: Dict,
    ) -> Tuple[Tuple, Dict]:
        new_args = tuple(func(arg) for arg in args)
        new_kwargs = {}
        for k, v in kwargs.items():
            new_kwargs[k] = func(v)
        return new_args, new_kwargs

    def _convert_args(self, args: Tuple, kwargs: Dict) -> Tuple[Tuple, Dict]:
        return self._process_args(
            lambda obj: frozenset(obj.items()) if isinstance(obj, dict) else obj,
            args,
            kwargs,
        )

    def _recover_args(self, args: Tuple, kwargs: Dict) -> Tuple[Tuple, Dict]:
        return self._process_args(
            lambda obj: dict(obj) if isinstance(obj, frozenset) else obj,
            args,
            kwargs,
        )

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        new_args, new_kwargs = self._convert_args(args, kwargs)
        return await super().__call__(*new_args, **new_kwargs)


def wrapped_alru_cache(
    maxsize: Optional[int] = 128,
    typed: bool = False,
    ttl: Optional[int] = None,
):
    def wrapper(
        func: Callable[P, Coroutine[Any, Any, R]],
    ) -> SupportDictCacheWrapper[P, R]:
        wrapped = SupportDictCacheWrapper(func, maxsize, typed, ttl)
        wrapped_cache_functions.add(wrapped)
        return wrapped

    return wrapper


class RespType(Enum):
    JSON = auto()
    TEXT = auto()
    BYTES = auto()
    HEADERS = auto()


class AsyncReqKwargs(TypedDict, total=False):
    method: str
    params: Optional[Dict[Any, Any]]
    headers: Optional[Dict[str, Any]]
    content: Union[str, bytes, None]
    data: Optional[Dict[str, Any]]
    json: Optional[Any]
    proxies: Optional[str]

    base_urls: Union[str, List[str]]
    resp_type: RespType
    retries: int
    raise_for_status: bool
    sleep: float


async def base_async_req(*urls: str, **kwargs: Unpack[AsyncReqKwargs]) -> Any:
    if not urls:
        raise ValueError("No URL specified")

    method = kwargs.pop("method", "GET").upper()
    params = kwargs.pop("params", None)
    headers = kwargs.pop("headers", None)
    content = kwargs.pop("content", None)
    data = kwargs.pop("data", None)
    json = kwargs.pop("json", None)
    proxies = kwargs.pop("proxies", config.ba_proxy)

    base_urls = kwargs.pop("base_urls", [])
    resp_type = kwargs.pop("resp_type", RespType.JSON)
    retries = kwargs.pop("retries", config.ba_req_retry)
    raise_for_status = kwargs.pop("raise_for_status", True)
    sleep = kwargs.pop("sleep", 0)

    if base_urls:
        if not isinstance(base_urls, list):
            base_urls = [base_urls]
        urls = tuple(
            itertools.starmap(urljoin, itertools.product(base_urls, urls)),  # type: ignore
        )

    async def do_request(current_url: str):
        async with AsyncClient(
            proxies=proxies,
            follow_redirects=True,
            timeout=config.ba_req_timeout,
        ) as cli:
            logger.debug(
                f"{method} `{current_url}`, "
                f"{params=}, {headers=}, {content=}, {data=}, {json=}",
            )
            resp = await cli.request(
                method,
                current_url,
                params=params,
                headers=headers,
                content=content,
                data=data,
                json=json,
            )
            if raise_for_status:
                resp.raise_for_status()

            if sleep:
                await asyncio.sleep(sleep)

            if resp_type == RespType.TEXT:
                return resp.text
            if resp_type == RespType.BYTES:
                return resp.content
            if resp_type == RespType.HEADERS:
                return resp.headers
            return resp.json()  # default RespType.JSON:

    while True:
        url, *rest = urls
        try:
            return await do_request(url)
        except Exception as e:
            e_sfx = f"because error occurred while requesting `{url}`: {e!r}"
            if retries > 0:
                retries -= 1
                logger.error(f"Retrying ({retries} left) {e_sfx}")
            else:
                if not rest:
                    raise ConnectionError("All retries failed") from e
                logger.error(f"Requesting next url `{rest[0]}` {e_sfx}")
                url, *rest = rest
            logger.opt(exception=e).debug("Error Stack")


async_req = wrapped_alru_cache(ttl=config.ba_req_cache_ttl, maxsize=None)(
    base_async_req,
)


def clear_wrapped_alru_cache() -> int:
    cleared = 0
    for wrapped in wrapped_cache_functions:
        size = wrapped.cache_info().currsize
        wrapped.cache_clear()
        cleared += size
    return cleared


# endregion


def format_timestamp(t: int) -> str:
    return datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S")  # noqa: DTZ006


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


def split_list(lst: Sequence[T], n: int) -> Iterator[Sequence[T]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


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


@alru_cache()
async def read_file_cached(path: PathType) -> bytes:
    if not isinstance(path, anyio.Path):
        path = anyio.Path(path)
    return await path.read_bytes()


async def read_image(path: PathType) -> BuildImage:
    content = await read_file_cached(path)
    bio = BytesIO(content)
    return BuildImage.open(bio)


async def send_forward_msg(
    bot: Bot,
    event: MessageEvent,
    messages: Sequence[Union[str, MessageSegment, Message]],
    user_id: Optional[int] = None,
    nickname: Optional[str] = None,
):
    nodes: List[MessageSegment] = [
        MessageSegment.node_custom(
            int(bot.self_id) if user_id is None else user_id,
            "BAWiki" if nickname is None else nickname,
            Message(x),
        )
        for x in messages
    ]
    if isinstance(event, GroupMessageEvent):
        return await bot.send_group_forward_msg(group_id=event.group_id, messages=nodes)
    return await bot.send_private_forward_msg(user_id=event.user_id, messages=nodes)


def camel_case(string: str, upper_first: bool = False) -> str:
    pfx, *rest = string.split("_")
    if upper_first:
        pfx = pfx.capitalize()
    sfx = "".join(x.capitalize() for x in rest)
    return f"{pfx}{sfx}"


class IllegalOperationFinisher:
    def __init__(
        self,
        finish_message: Optional[SendableType] = None,
        limit: int = config.ba_illegal_limit,
    ):
        self.finish_message = finish_message
        self.limit = limit

    async def __call__(
        self,
        finish_message: Union[SendableType, None] = Ellipsis,  # type: ignore
    ):
        if self.limit <= 0:
            return
        matcher = current_matcher.get()
        state = matcher.state

        count = state.get(KEY_ILLEGAL_COUNT, 0) + 1
        if count >= config.ba_illegal_limit:
            await matcher.finish(
                self.finish_message if finish_message is Ellipsis else finish_message,
            )

        state[KEY_ILLEGAL_COUNT] = count
