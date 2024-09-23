import asyncio
import datetime
import os

from typing import Set

from aiohttp import ClientConnectorError
from loguru import logger

from app.pkg.server_tools.tools import Server
from app.pkg.network_tools.tools import ServerHerald, GameServerNotFoundError
from app.pkg.world_tools.tools import WorldManager


from datetime import datetime


async def snapshots_loop(servers: Set[Server], api_key: str):
    ServerHerald.API_TOKEN = api_key
    while True:
        for server in servers:
            if server.settings['send_server_saves_to_server']:
                try:
                    last_save_on_server = await ServerHerald.get_last_save(server.settings['server_name'])
                    if not last_save_on_server:
                        logger.debug('Сервера с именем {} не существует, создаю его', server.settings['server_name'])
                        await ServerHerald.create_game_server(server.settings['server_name'])
                        last_save_on_server = await ServerHerald.get_last_save(server.settings['server_name'])

                    for save in server.get_backup_path_list():
                        save = Server.fix_path(save)
                        if datetime.fromtimestamp(os.path.getctime(save + 'Sandbox.sbc')) > datetime.fromtimestamp(last_save_on_server.timestamp()):
                            world_master = WorldManager(save, rw='r')
                            world_master.execute_commands(commands=['send_dump_to_server'])
                            await ServerHerald.send_save(world_master.gamesave_dict, server)
                            del world_master
                        await asyncio.sleep(0)
                except ClientConnectorError:
                    logger.debug('Cервер для обработки сейвов лежит. Попробую подключиться позже.')
                except Exception as ex:
                    logger.exception(ex)
        await asyncio.sleep(60 * 2)
