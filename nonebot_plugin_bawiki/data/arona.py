import hashlib
import shutil
from typing import List, Optional

import anyio
from httpx import AsyncClient
from pydantic import BaseModel

from ..config import config
from ..resource import DATA_PATH

CACHE_PATH = DATA_PATH / "arona_cache"
if CACHE_PATH.exists() and config.ba_auto_clear_arona_cache:
    shutil.rmtree(CACHE_PATH)
if not CACHE_PATH.exists():
    CACHE_PATH.mkdir(parents=True)

IMAGE_TYPE_MAP = {
    1: "学生攻略",
    2: "主线地图",
    3: "杂图",
}


class ImageModel(BaseModel):
    id: int  # noqa: A003
    name: str
    path: str
    hash: str  # noqa: A003
    type: int  # noqa: A003


class ImageAPIResult(BaseModel):
    status: int
    data: List[ImageModel]
    message: str


async def get_image(path: str, hash_str: Optional[str] = None) -> bytes:
    if hash_str:
        file_path = anyio.Path(CACHE_PATH / hash_str)
        if await file_path.exists():
            return await file_path.read_bytes()

    async with AsyncClient() as client:
        resp = await client.get(f"{config.ba_arona_cdn_url}image{path}")
        resp.raise_for_status()
        content = resp.content

    if not hash_str:
        hash_str = hashlib.md5(content).hexdigest()
    file_path = anyio.Path(CACHE_PATH / hash_str)

    await file_path.write_bytes(resp.content)
    return content


async def search_image(name: str) -> List[ImageModel]:
    pass
