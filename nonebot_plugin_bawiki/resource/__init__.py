from pathlib import Path

from pil_utils import BuildImage

RES_PATH = Path(__file__).parent / "res"

CACHE_PATH = Path.cwd() / "cache" / "BAWiki"
if not CACHE_PATH.exists():
    CACHE_PATH.mkdir(parents=True)

DATA_PATH = Path.cwd() / "data" / "BAWiki"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)

RES_CALENDER_BANNER = BuildImage.open(RES_PATH / "calender_banner.png")
RES_GRADIENT_BG = BuildImage.open(RES_PATH / "gradient.png")
RES_GACHA_BG = BuildImage.open(RES_PATH / "gacha_bg.png")
RES_GACHA_CARD_BG = BuildImage.open(RES_PATH / "gacha_card_bg.png")
RES_GACHA_CARD_MASK = BuildImage.open(RES_PATH / "gacha_card_mask.png").convert("RGBA")
RES_GACHA_NEW = BuildImage.open(RES_PATH / "gacha_new.png")
RES_GACHA_PICKUP = BuildImage.open(RES_PATH / "gacha_pickup.png")
RES_GACHA_STAR = BuildImage.open(RES_PATH / "gacha_star.png")
RES_GACHA_STU_ERR = BuildImage.open(RES_PATH / "gacha_stu_err.png")
