import asyncio
import time

from aiohttp import ClientSession


async def game_kee_request(url, **kwargs):
    async with ClientSession() as s:
        async with s.get(
                url,
                headers={
                    'game-id': '0',
                    'game-alias': 'ba'
                },
                **kwargs
        ) as r:
            ret = await r.json()
            if not ret['code'] == 0:
                raise ConnectionError(ret['msg'])
            return ret['data']


async def get_calender():
    ret = await game_kee_request('https://ba.gamekee.com/v1/wiki/index')

    for i in ret:
        if i['module']['id'] == 12:
            li: list = i['list']

            now = time.time()
            li = [x for x in li if x['end_at'] >= now]

            li.sort(key=lambda x: x['end_at'])
            li.sort(key=lambda x: x['importance'], reverse=True)
            return li


async def get_stu_li():
    ret = await game_kee_request('https://ba.gamekee.com/v1/wiki/entry')

    li = None
    for i in ret['entry_list']:
        if i['id'] == 23941:

            for ii in i['child']:
                if ii['id'] == 49443:
                    li = ii['child']

    return {x['name']: x['content_id'] for x in li}


if __name__ == '__main__':
    async def main():
        print(await get_stu_li())


    asyncio.run(main())
