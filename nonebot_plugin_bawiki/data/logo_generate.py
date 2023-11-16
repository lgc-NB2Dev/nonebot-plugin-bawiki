from ..resource import BA_LOGO_JS_PATH
from .playwright import get_routed_page


async def get_logo(text_l: str, text_r: str, transparent_bg: bool = True) -> str:
    async with get_routed_page() as page:
        return await page.evaluate(
            BA_LOGO_JS_PATH.read_text(encoding="u8"),
            [text_l, text_r, transparent_bg],
        )
