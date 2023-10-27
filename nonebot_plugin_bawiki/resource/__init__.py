import shutil
from pathlib import Path

from nonebot import logger

RES_DIR = Path(__file__).parent / "res"

DATA_PATH = Path.cwd() / "data" / "BAWiki"
CACHE_PATH = DATA_PATH / "cache"

for _p in (DATA_PATH, CACHE_PATH):
    if not _p.exists():
        _p.mkdir(parents=True)


CALENDER_BANNER_PATH = RES_DIR / "calender_banner.png"
GRADIENT_BG_PATH = RES_DIR / "gradient.png"
GACHA_BG_PATH = RES_DIR / "gacha_bg.png"
GACHA_BG_OLD_PATH = RES_DIR / "gacha_bg_old.png"
GACHA_CARD_BG_PATH = RES_DIR / "gacha_card_bg.png"
GACHA_CARD_MASK_PATH = RES_DIR / "gacha_card_mask.png"
GACHA_NEW_PATH = RES_DIR / "gacha_new.png"
GACHA_PICKUP_PATH = RES_DIR / "gacha_pickup.png"
GACHA_STAR_PATH = RES_DIR / "gacha_star.png"
GACHA_STU_ERR_PATH = RES_DIR / "gacha_stu_err.png"


RES_WEB_DIR = RES_DIR / "web"
GAMEKEE_UTIL_JS_PATH = RES_WEB_DIR / "gamekee_util.js"
SCHALE_UTIL_JS_PATH = RES_WEB_DIR / "schale_util.js"
SCHALE_UTIL_CSS_PATH = RES_WEB_DIR / "schale_util.css"
BA_LOGO_JS_PATH = RES_WEB_DIR / "ba_logo.js"
EMPTY_HTML_PATH = RES_WEB_DIR / "empty.html"


_OLD_CACHE_FOLDER = Path.cwd() / "cache"
_OLD_CACHE_PATH = _OLD_CACHE_FOLDER / "BAWiki"
if _OLD_CACHE_PATH.exists():
    logger.warning("Deleting old cache dir...")
    shutil.rmtree(_OLD_CACHE_PATH)
