import asyncio
import discord
import datetime
import os
import threading

from discord.ext import tasks, commands

from managers import Server_manager, Restart_manager, Window_manager
import settings

SERVERS = []
MAIL_STORAGE = []

tz = datetime.timezone(datetime.timedelta(hours=settings.TIME_ZONE[0]), name=settings.TIME_ZONE[1])
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
discord_tocken = settings.DISCORD_TOCKEN

for server_data in settings.OBSERVED.keys():
    SERVERS.append(Server_manager.Server(server_data, settings.OBSERVED[server_data]))


@bot.event
async def on_ready():
    restart_loop.start()
    mail_check_loop.start()
    is_server_work_loop.start()


@bot.event
async def on_member_join(member):
    pass


@bot.event
async def on_message(ctx):
    print(ctx.content)
    #pass


def get_restart_times(test=False):
    restart_times = []
    for server in SERVERS:
        if server.settings['do_restarts']:
            for restart_hour in server.settings['restart_pram'].keys():
                restart_times.append(datetime.time(hour=restart_hour, tzinfo=tz))
    if test:
        restart_times = [datetime.time(hour=int(datetime.datetime.now().hour),
                                       minute=int(datetime.datetime.now().minute) + 1,
                                       second=0, tzinfo=tz)]
        SERVERS[0].settings['restart_pram'][int(datetime.datetime.now().hour)] = ['fix_world', 'check_security']
    return restart_times


@tasks.loop(time=get_restart_times(False))
async def restart_loop():
    for server in SERVERS:
        if server.settings['do_restarts']:
            for restart_hour in server.settings['restart_pram'].keys():
                if restart_hour == int(datetime.datetime.now().hour):
                    restart_manager = Restart_manager.RestartManager(server, MAIL_STORAGE)
                    await restart_manager.do_restart(restart_hour)
                    del restart_manager


@tasks.loop(seconds=1)
async def mail_check_loop():
    while MAIL_STORAGE:
        message = MAIL_STORAGE.pop(0)
        await msg_to_chanel(message[0], message[1])


@tasks.loop(minutes=2, seconds=0)
async def is_server_work_loop():
    for server in SERVERS:
        if server.work_status and not server.is_working():
            if server.work_status != 'boot':
                server.work_status = 'boot'
                ui = Window_manager.Window(server)
                asyncio.ensure_future(ui.ui())


async def msg_to_chanel(where, what, delay=0):
    await asyncio.sleep(delay)
    for i in where:
        my_channel = bot.get_channel(i)
        for b in what:
            await my_channel.send(b[:1990])

if __name__ == '__main__':
    if not os.path.exists('settings.py'):
        os.rename('settings_example.py', 'settings.py')
    bot.run(discord_tocken)
