import asyncio
import datetime
import aiohttp
import json
import gzip
from pprint import pprint


class ServerHerald:
    SERVER_URL = 'http://localhost:8000/'

    def __init__(self):
        pass

    @classmethod
    async def get_last_save(cls, world_id: str) -> datetime.datetime:
        server_link = cls.SERVER_URL + 'api/v2/get_last_save_time'

        async with aiohttp.ClientSession() as session:
            params = {'world_id': world_id}
            async with session.get(server_link, params=params) as resp:
                return datetime.datetime.fromtimestamp(float(await resp.text()))

    @classmethod
    async def send_save(cls, save: dict) -> None:
        server_link = cls.SERVER_URL + 'api/v2/save_world'
        params = {'world_id': save.pop('world_id')}
        gzip_save = gzip.compress(json.dumps(save).encode("utf-8"))

        async with aiohttp.ClientSession() as session:
            response = await session.post(server_link, params=params, json=save)
            print(await response.json())
            print(response)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(ServerHerald.get_last_save('1'))
