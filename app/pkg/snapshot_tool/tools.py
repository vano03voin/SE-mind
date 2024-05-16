import asyncio
import datetime
import os

from typing import Set

from app.pkg.server_tools.tools import Server
from app.pkg.network_tools.tools import ServerHerald
from app.pkg.world_tools.tools import WorldManager


async def snapshots_loop(servers: Set[Server], api_key: str):
    while True:
        for server in servers:
            world_master = WorldManager(server.get_save_path(), rw='r')
            world_master.execute_commands(commands=['send_dump_to_server'])
            # print(world_master.gamesave_dict)
            with open('example.txt', mode='w', encoding='utf-8') as f:
                f.write(world_master.gamesave_dict)
            await asyncio.sleep(0)
        # for server in servers:
        #     last_save_on_server = await ServerHerald.get_last_save(server.world_id)
        #     for save in server.get_backup_path_list():
        #         if datetime.datetime.fromtimestamp(os.path.getctime(save + 'Sandbox.sbc')) > last_save_on_server:
        #             world_master = WorldManager(save, rw='r')
        #             world_master.execute_commands(commands=['send_dump_to_server'])
        #             await ServerHerald.send_save(world_master.gamesave_dict)
        #             del world_master
        #         await asyncio.sleep(0)
        await asyncio.sleep(60 * 2)

def snapshots_loop(servers: Set[Server], api_key: str):
    while True:
        for server in servers:
            world_master = WorldManager(server.get_save_path(), rw='r')
            world_master.execute_commands(commands=['send_dump_to_server'])
            #print(world_master.gamesave_dict)
            import json
            with open('example.txt', mode='w', encoding='utf-8') as f:
                f.write(json.dumps(world_master.gamesave_dict))
            a = 1/0