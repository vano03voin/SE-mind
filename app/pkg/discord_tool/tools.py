import asyncio
import discord
import datetime
import time
import os

from discord.ext import tasks, commands
from typing import Set

from app.pkg.restart_tools.tools import RestartManager
from app.pkg.server_tools.tools import Server
from app.pkg.ui_tools.popup import Window
from app.pkg.discord_tool.cogs import bot_commands
from app.pkg.network_tools.tools import ServerHerald
from app.pkg.world_tools.tools import WorldManager


class SEDiscordBot(commands.Bot):
    utc_offset = -(time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) // 3600
    tz = datetime.timezone(datetime.timedelta(hours=utc_offset), name='Lockal Time')

    def __init__(self, servers: Set[Server]):
        super().__init__(command_prefix="$", intents=discord.Intents.all())
        discord.utils.setup_logging()
        self.servers = servers
        self.mail_box = []

    async def start_bot(self, config):
        # cogs
        await bot_commands.setup(self)
        # loops
        if config['DEFAULT']['observe_custom_restart']:
            asyncio.create_task(self.restart_loop())
        if config['DEFAULT']['observe_silent_crash']:
            asyncio.create_task(self.is_server_work_loop())
        if config['DEFAULT']['send_backups_to_server'] and config['DEFAULT']['api_key'] or True:
            asyncio.create_task(self.snapshots_loop(config['DEFAULT']['api_key']))

        if config['DEFAULT']['discord_tocken']:
            await self.start(config['DEFAULT']['discord_tocken'], reconnect=True)

    async def on_ready(self):
        #print('im ready.')
        pass

    async def on_message(self, message):
        #print(message.content)
        await self.process_commands(message)

    async def is_server_work_loop(self):
        while True:
            for server in self.servers:
                if server.work_status and not server.is_working():
                    if server.work_status != 'boot':
                        server.work_status = 'boot'
                        ui = Window(server)
                        asyncio.create_task(ui.ui())
            await asyncio.sleep(4*60)

    async def snapshots_loop(self, api_key: str):
        while True:
            for server in self.servers:
                last_save_on_server = await ServerHerald.get_last_save(server.world_id)
                for save in server.get_backup_path_list():
                    if datetime.datetime.fromtimestamp(os.path.getctime(save+'Sandbox.sbc')) > last_save_on_server:
                        world_master = WorldManager(save, rw='r')
                        world_master.execute_commands(commands=['send_dump_to_server'])
                        await ServerHerald.send_save(world_master.gamesave_dict)
                        del world_master
                    await asyncio.sleep(10)
            await asyncio.sleep(60*2)

    async def restart_loop(self):
        _last_hour = datetime.datetime.now().hour
        while True:
            if _last_hour != datetime.datetime.now().hour:
                _last_hour = datetime.datetime.now().hour
                for server in self.servers:
                    if server.settings['use_custom_restart'] and server.settings['use_discord_bridge']:
                        for restart_hour in server.settings.get('restart_times', '').split(','):
                            if int(restart_hour) == int(datetime.datetime.now().hour):
                                restart_manager = RestartManager(server, send_sms=self.msg_to_chanel)
                                await restart_manager.do_restart()
                                del restart_manager
            await asyncio.sleep(10*60)

    async def msg_to_chanel(self, where: str, what: list, delay=0):
        await asyncio.sleep(delay)
        my_channel = self.get_channel(int(where))
        for msg in what:
            await my_channel.send(msg[:1995])
