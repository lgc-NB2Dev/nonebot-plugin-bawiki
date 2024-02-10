import hashlib
import json
import shutil
from typing import Dict, List, Optional

import anyio
from pydantic import BaseModel

from ..config import config
from ..resource import CACHE_DIR, DATA_DIR
from ..util import RespType as Rt, async_req

ARONA_CACHE_DIR = CACHE_DIR / "arona"
if config.ba_auto_clear_cache_path and ARONA_CACHE_DIR.exists():
    shutil.rmtree(ARONA_CACHE_DIR)
if not ARONA_CACHE_DIR.exists():
    ARONA_CACHE_DIR.mkdir(parents=True)

ARONA_ALIAS_PATH = DATA_DIR / "arona_alias.json"  # {"alias": "name"}
if not ARONA_ALIAS_PATH.exists():
    ARONA_ALIAS_PATH.write_text("{}", encoding="u8")


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
        file_path = anyio.Path(ARONA_CACHE_DIR / hash_str)
        if await file_path.exists():
            return await file_path.read_bytes()

    content = await async_req(
        f"image{path}",
        base_urls=config.ba_arona_cdn_url,
        resp_type=Rt.BYTES,
    )

    if not hash_str:
        hash_str = hashlib.md5(content).hexdigest()  # noqa: S324

    file_path = anyio.Path(ARONA_CACHE_DIR / hash_str)
    await file_path.write_bytes(content)

    return content


async def search_exact(name: str) -> Optional[List[ImageModel]]:
    resp: dict = await async_req(
        "api/v1/image",
        base_urls=config.ba_arona_api_url,
        params={"name": name},
    )
    return ImageAPIResult(**resp).data


async def search(name: str) -> Optional[List[ImageModel]]:
    alias_dict = json.loads(ARONA_ALIAS_PATH.read_text(encoding="u8"))
    recovered = alias_dict[lowered] if (lowered := name.lower()) in alias_dict else None
    if recovered and (resp := await search_exact(recovered)):
        return resp
    return await search_exact(name)


def set_alias(name: Optional[str], alias: List[str]) -> Dict[str, Optional[str]]:
    data = json.loads(ARONA_ALIAS_PATH.read_text(encoding="u8"))
    original_dict: Dict[str, Optional[str]] = {}

    for a in alias:
        original_dict[a] = data.get(a)
        if name is None:
            data.pop(a, None)
        else:
            data[a] = name

    ARONA_ALIAS_PATH.write_text(json.dumps(data, ensure_ascii=False), encoding="u8")
    return original_dict
