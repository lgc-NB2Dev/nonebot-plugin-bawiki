from dataclasses import dataclass
from typing import List

import requests
from bs4 import BeautifulSoup, ResultSet, Tag


@dataclass()
class GameKeeVoice:
    title: str
    jp: str
    cn: str
    url: str


def get_gamekee_wiki_page(url, **kwargs):
    ret = requests.get(
        url, headers={"game-id": "0", "game-alias": "ba"}, **kwargs
    ).json()
    if ret["code"] != 0:
        raise ConnectionError(ret["msg"])
    return ret["data"]


def game_kee_get_voice(cid):
    wiki_html = get_gamekee_wiki_page(
        f"https://ba.gamekee.com/v1/content/detail/{cid}"
    )["content"]
    bs = BeautifulSoup(wiki_html, "lxml")
    audios = bs.select(".mould-table>tbody>tr>td>div>div>audio")

    parsed: List[GameKeeVoice] = []
    for au in audios:
        url: str = au["src"]
        if not url.startswith("http"):
            url = f"https:{url}"

        tr1: Tag = au.parent.parent.parent.parent
        tds: ResultSet[Tag] = tr1.find_all("td")
        title = tds[0].text.strip()
        jp = "\n".join(tds[2].stripped_strings)

        tr2 = tr1.next_sibling
        cn = "\n".join(tr2.stripped_strings)
        parsed.append(GameKeeVoice(title, jp, cn, url))

    return parsed


def main():
    voices = game_kee_get_voice("170297")
    print(
        "\n================\n".join(
            [f"{x.title} | {x.url}\n{x.jp}\n{x.cn}" for x in voices]
        )
    )


if __name__ == "__main__":
    main()
