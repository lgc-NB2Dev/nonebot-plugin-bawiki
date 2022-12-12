from pathlib import Path

SCHALE_URL = "https://lonqie.github.io/SchaleDB/"
MIRROR_SCHALE_URL = "http://schale.lgc2333.top/"

BAWIKI_DB_URL = "https://bawiki.lgc2333.top/"

RES_PATH = Path(__file__).parent / "res"

DATA_PATH = Path.cwd() / "data" / "BAWiki"
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)
