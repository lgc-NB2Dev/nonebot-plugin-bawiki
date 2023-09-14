import shutil
from pathlib import Path

from nonebot import logger
from pil_utils import BuildImage

RES_PATH = Path(__file__).parent / "res"
DATA_PATH = Path.cwd() / "data" / "BAWiki"
CACHE_PATH = DATA_PATH / "cache"

_OLD_CACHE_FOLDER = Path.cwd() / "cache"
_OLD_CACHE_PATH = _OLD_CACHE_FOLDER / "BAWiki"

if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

if _OLD_CACHE_PATH.exists():
    logger.warning("Moving old cache to new path...")
    shutil.move(str(_OLD_CACHE_PATH), CACHE_PATH)

    if not any(_OLD_CACHE_FOLDER.iterdir()):
        _OLD_CACHE_FOLDER.rmdir()

if not CACHE_PATH.exists():
    CACHE_PATH.mkdir(parents=True)

RES_CALENDER_BANNER = BuildImage.open(RES_PATH / "calender_banner.png")
RES_GRADIENT_BG = BuildImage.open(RES_PATH / "gradient.png")
RES_GACHA_BG = BuildImage.open(RES_PATH / "gacha_bg.png")
RES_GACHA_BG_OLD = BuildImage.open(RES_PATH / "gacha_bg_old.png")
RES_GACHA_CARD_BG = BuildImage.open(RES_PATH / "gacha_card_bg.png")
RES_GACHA_CARD_MASK = BuildImage.open(RES_PATH / "gacha_card_mask.png").convert("RGBA")
RES_GACHA_NEW = BuildImage.open(RES_PATH / "gacha_new.png")
RES_GACHA_PICKUP = BuildImage.open(RES_PATH / "gacha_pickup.png")
RES_GACHA_STAR = BuildImage.open(RES_PATH / "gacha_star.png")
RES_GACHA_STU_ERR = BuildImage.open(RES_PATH / "gacha_stu_err.png")

RES_WEB_DIR = RES_PATH / "web"
RES_GAMEKEE_UTIL_JS_PATH = RES_WEB_DIR / "gamekee_util.js"
RES_SCHALE_UTIL_JS_PATH = RES_WEB_DIR / "schale_util.js"
RES_SCHALE_UTIL_CSS_PATH = RES_WEB_DIR / "schale_util.css"

GAMEKEE_UTIL_JS = RES_GAMEKEE_UTIL_JS_PATH.read_text(encoding="u8")
SCHALE_UTIL_JS = RES_SCHALE_UTIL_JS_PATH.read_text(encoding="u8")
SCHALE_UTIL_CSS = RES_SCHALE_UTIL_CSS_PATH.read_text(encoding="u8")
