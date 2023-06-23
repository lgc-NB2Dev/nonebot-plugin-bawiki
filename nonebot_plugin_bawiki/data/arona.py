import hashlib
import shutil
from typing import List, Optional

import anyio
from pydantic import BaseModel

from ..config import config
from ..resource import CACHE_PATH
from ..util import async_req

ARONA_CACHE_PATH = CACHE_PATH / "arona"
if ARONA_CACHE_PATH.exists() and config.ba_auto_clear_arona_cache:
    shutil.rmtree(ARONA_CACHE_PATH)
if not ARONA_CACHE_PATH.exists():
    ARONA_CACHE_PATH.mkdir(parents=True)

IMAGE_TYPE_MAP = {
    1: "学生攻略",
    2: "主线地图",
    3: "杂图",
}


class ImageModel(BaseModel):
    name: str
    path: str
    hash: str  # noqa: A003
    type: int  # noqa: A003


class ImageAPIResult(BaseModel):
    status: int
    data: Optional[List[ImageModel]]
    message: str


async def get_image(path: str, hash_str: Optional[str] = None) -> bytes:
    if not path.startswith("/"):
        raise ValueError("path must start with /")

    if hash_str:
        file_path = anyio.Path(ARONA_CACHE_PATH / hash_str)
        if await file_path.exists():
            return await file_path.read_bytes()

    content = await async_req(f"{config.ba_arona_cdn_url}image{path}", raw=True)

    if not hash_str:
        hash_str = hashlib.md5(content).hexdigest()

    file_path = anyio.Path(ARONA_CACHE_PATH / hash_str)
    await file_path.write_bytes(content)

    return content


async def search(name: str) -> Optional[List[ImageModel]]:
    resp: dict = await async_req(
        f"{config.ba_arona_api_url}api/v1/image",
        params={"name": name},
    )
    return ImageAPIResult(**resp).data
