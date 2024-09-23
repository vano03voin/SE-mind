"""Модуль работы с сетью (SE-mind-Server)"""
import asyncio
import datetime
import aiohttp
from loguru import logger

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

    @classmethod
    async def get_last_save(
            cls,
            server_name: str
    ) -> datetime.datetime | None:
        path = 'game_save/get_last_game_save_time/'

        async with aiohttp.ClientSession() as session:
            params = {'game_server_name': server_name,
                      'token': cls.API_TOKEN}

            async with session.get(cls._construct_link(path), params=params) as resp:
                if resp.status == 404:
                    return
                save_time = datetime.datetime.fromisoformat(str(await resp.text()).strip('"'))
                logger.debug('Время последнего сохранение на сервере: {}', await resp.text())
                return save_time

    @classmethod
    async def send_save(
            cls,
            save: dict,
            server: Server
    ) -> None:
        path = 'game_save/'

        params = {'game_server_name': server.settings['server_name'],
                  'token': cls.API_TOKEN}

        async with (aiohttp.ClientSession() as session):
            response = await session.post(cls._construct_link(path), params=params, json=save)

            if response.status == 201:
                logger.debug('Cейв отправлен успешно')
            elif response.status == 500 or response.status == 409:
                logger.debug('Случайно отправил старый сейв, {} {}', server.settings['server_name'], await response.text())
            else:
                logger.error('Ошибка отправки сейва {} {}', server.settings['server_name'], response)

    @classmethod
    async def create_game_server(
            cls,
            server_name
    ):
        path = 'game_server/'

        params = {'token': cls.API_TOKEN}

        async with aiohttp.ClientSession() as session:
            await session.post(cls._construct_link(path), params=params, json={'name': server_name})

    @classmethod
    def _construct_link(cls, path):
        return cls.SERVER_URL + cls.API_PREFIX + cls.V_PREFIX + path
