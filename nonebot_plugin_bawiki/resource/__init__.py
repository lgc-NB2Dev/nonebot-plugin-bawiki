import shutil
from pathlib import Path

from nonebot import logger

DATA_DIR = Path.cwd() / "data" / "BAWiki"
CACHE_DIR = DATA_DIR / "cache"

for _p in (DATA_DIR, CACHE_DIR):
    if not _p.exists():
        _p.mkdir(parents=True)


RES_DIR = Path(__file__).parent / "res"

RES_GACHA_DIR = RES_DIR / "gacha"
GACHA_BG_PATH = RES_GACHA_DIR / "gacha_bg.webp"
GACHA_BG_OLD_PATH = RES_GACHA_DIR / "gacha_bg_old.webp"
GACHA_CARD_BG_PATH = RES_GACHA_DIR / "gacha_card_bg.png"
GACHA_CARD_MASK_PATH = RES_GACHA_DIR / "gacha_card_mask.png"
GACHA_NEW_PATH = RES_GACHA_DIR / "gacha_new.png"
GACHA_PICKUP_PATH = RES_GACHA_DIR / "gacha_pickup.png"
GACHA_STAR_PATH = RES_GACHA_DIR / "gacha_star.png"
GACHA_STU_ERR_PATH = RES_GACHA_DIR / "gacha_stu_err.png"

RES_GAMEKEE_DIR = RES_DIR / "gamekee"
GAMEKEE_UTIL_JS_PATH = RES_GAMEKEE_DIR / "gamekee_util.js"

RES_GENERAL_DIR = RES_DIR / "general"
CALENDER_BANNER_PATH = RES_GENERAL_DIR / "calender_banner.png"
GRADIENT_BG_PATH = RES_GENERAL_DIR / "gradient.webp"

RES_LOGO_DIR = RES_DIR / "logo"
BA_LOGO_JS_PATH = RES_LOGO_DIR / "ba_logo.js"

RES_SCHALE_DIR = RES_DIR / "schale"
SCHALE_UTIL_JS_PATH = RES_SCHALE_DIR / "schale_util.js"
SCHALE_UTIL_CSS_PATH = RES_SCHALE_DIR / "schale_util.css"

RES_SHITTIM_DIR = RES_DIR / "shittim"
RES_SHITTIM_TEMPLATES_DIR = RES_SHITTIM_DIR / "templates"
RES_SHITTIM_JS_DIR = RES_SHITTIM_DIR / "js"
RES_SHITTIM_CSS_DIR = RES_SHITTIM_DIR / "css"
SHITTIM_UTIL_JS_PATH = RES_SHITTIM_JS_DIR / "shittim_util.js"
SHITTIM_UTIL_CSS_PATH = RES_SHITTIM_CSS_DIR / "shittim_util.css"

EMPTY_HTML_PATH = RES_DIR / "index.html"


_OLD_CACHE_FOLDER = Path.cwd() / "cache"
_OLD_CACHE_PATH = _OLD_CACHE_FOLDER / "BAWiki"
if _OLD_CACHE_PATH.exists():
    logger.warning("Deleting old cache dir...")
    shutil.rmtree(_OLD_CACHE_PATH)
