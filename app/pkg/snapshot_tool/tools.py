import asyncio
import datetime
import os

from typing import Set

from aiohttp import ClientConnectorError

from app.pkg.server_tools.tools import Server
from app.pkg.network_tools.tools import ServerHerald, GameServerNotFoundError
from app.pkg.world_tools.tools import WorldManager


from datetime import datetime


async def snapshots_loop(servers: Set[Server], api_key: str, discord_bot):
    ServerHerald.API_TOKEN = api_key
    ServerHerald.DISCORD_BOT = discord_bot
    while True:
        for server in servers:
            if server.settings['send_server_saves_to_server']:
                try:
                    try:
                        last_save_on_server = await ServerHerald.get_last_save(server.settings['server_name'])
                    except GameServerNotFoundError:
                        await ServerHerald.create_game_server(server.settings['server_name'])
                        last_save_on_server = await ServerHerald.get_last_save(server.settings['server_name'])
                    print('awd', server.get_backup_path_list())
                    for save in server.get_backup_path_list():
                        # print(datetime.fromtimestamp(os.path.getctime(save + 'Sandbox.sbc')))
                        # if datetime.fromtimestamp(os.path.getctime(save + 'Sandbox.sbc')) > last_save_on_server:
                        print(save + 'Sandbox.sbc')
                        if datetime.fromtimestamp(os.path.getctime(save + 'Sandbox.sbc')) > datetime.fromtimestamp(last_save_on_server.timestamp()):
                            world_master = WorldManager(save, rw='r')
                            world_master.execute_commands(commands=['send_dump_to_server'])
                            await ServerHerald.send_save(world_master.gamesave_dict, server)
                            del world_master
                        await asyncio.sleep(0)
                except ClientConnectorError:
                    print('сервер вано для сейвов упал. Попробую подключиться позже.')
                except GameServerNotFoundError:
                    await ServerHerald.create_game_server(server.settings['server_name'])
        await asyncio.sleep(60 * 2)
