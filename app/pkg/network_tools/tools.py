import asyncio
import datetime
import aiohttp
import json
import gzip
from pprint import pprint


class ServerHerald:
    API_TOKEN = ''

    SERVER_URL = 'http://127.0.0.1:8000/'
    API_PREFIX = 'api/'
    V_PREFIX = 'v1/'

    def __init__(self):
        pass

    @classmethod
    async def get_last_save(
            cls,
            server_exe_path: str
    ) -> datetime.datetime:
        path = 'game_save/get_last_game_save_time/'

        print(cls._construct_link(path))
        print(hash(server_exe_path))

        async with aiohttp.ClientSession() as session:
            # params = {'path': ''.join(server_exe_path.split('/')),
            #           'token': cls.API_TOKEN}
            params = {'path': 'string',
                      'token': cls.API_TOKEN}

            async with session.get(cls._construct_link(path), params=params) as resp:
                return datetime.datetime.fromisoformat(str(await resp.text()).strip('"'))

    @classmethod
    async def send_save(
            cls,
            save: dict,
            server_exe_path: str
    ) -> None:
        path = 'game_save/'

        params = {'path': server_exe_path,
                  'token': cls.API_TOKEN}
        params = {'path': 'string',
                  'token': cls.API_TOKEN}

        async with aiohttp.ClientSession() as session:
            response = await session.post(cls._construct_link(path), params=params, json=save)
            print(response)

    @classmethod
    def _construct_link(cls, path):
        return cls.SERVER_URL + cls.API_PREFIX + cls.V_PREFIX + path
