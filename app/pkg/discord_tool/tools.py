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


class SEDiscordBot(commands.Bot):
    utc_offset = -(time.timezone if (time.localtime().tm_isdst == 0) else time.altzone) // 3600
    tz = datetime.timezone(datetime.timedelta(hours=utc_offset), name='Lockal Time')

    def __init__(self, servers: Set[Server]):
        super().__init__(command_prefix="$", intents=discord.Intents.all())
        discord.utils.setup_logging()
        self.servers = servers
        self.mail_box = []

    async def start_bot(self, tocken: str):
        # cogs
        await bot_commands.setup(self)
        # loops
        asyncio.create_task(self.restart_loop())
        asyncio.create_task(self.is_server_work_loop())

        await self.start(tocken, reconnect=True)

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
