import asyncio
import datetime
import aiohttp
import json
import gzip
from pprint import pprint

from app.pkg.server_tools.tools import Server
from app.pkg.discord_tool.tools import SEDiscordBot


class GameServerNotFoundError(Exception):
    """Корневое исключение модуля Basic."""


class ServerHerald:
    API_TOKEN = ''
    DISCORD_BOT: SEDiscordBot = None

    SERVER_URL = 'http://127.0.0.1:8000/'
    API_PREFIX = 'api/'
    V_PREFIX = 'v1/'

    def __init__(self):
        pass

    @classmethod
    async def get_last_save(
            cls,
            server_name: str
    ) -> datetime.datetime:
        path = 'game_save/get_last_game_save_time/'

        async with aiohttp.ClientSession() as session:
            # params = {'path': ''.join(server_exe_path.split('/')),
            #           'token': cls.API_TOKEN}
            params = {'name': server_name,
                      'token': cls.API_TOKEN}

            async with session.get(cls._construct_link(path), params=params) as resp:
                if resp.status == 404:
                    raise GameServerNotFoundError
                print(await resp.text())
                print(resp.status)
                return datetime.datetime.fromisoformat(str(await resp.text()).strip('"'))

    @classmethod
    async def send_save(
            cls,
            save: dict,
            server: Server
    ) -> None:
        path = 'game_save/'

        params = {'name': server.settings['server_name'],
                  'token': cls.API_TOKEN}

        async with (aiohttp.ClientSession() as session):
            response = await session.post(cls._construct_link(path), params=params, json=save)

            if response.status == 201:
                response_data = await response.json()
                await cls.DISCORD_BOT.update_inform_msg('top_by_resources', response_data['top_by_resources'], server)
                await cls.DISCORD_BOT.update_inform_msg('dif_by_last_save', response_data['dif_by_last_save'], server)
            elif response.status == 500:
                print(response)

    @classmethod
    async def create_game_server(
            cls,
            server_name
    ):
        path = 'game_server/'

        params = {'token': cls.API_TOKEN}

        async with aiohttp.ClientSession() as session:
            response = await session.post(cls._construct_link(path), params=params, json={'name': server_name})

    @classmethod
    def _construct_link(cls, path):
        return cls.SERVER_URL + cls.API_PREFIX + cls.V_PREFIX + path
