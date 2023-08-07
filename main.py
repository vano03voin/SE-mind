import asyncio
import discord
import os

# from discord.ext.commands import Bot
from discord.ext import tasks, commands
# from discord.utils import get
import datetime

from managers import Server_manager, Restart_manager
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


@bot.event
async def on_member_join(member):
    pass


@bot.event
async def on_message(ctx):
    # print(ctx.content)
    pass


def get_restart_times():
    restart_times = []
    for server in SERVERS:
        if server.settings['do_restarts']:
            for restart_hour in server.settings['restart_pram'].keys():
                restart_times.append(datetime.time(hour=restart_hour, tzinfo=tz))
    return restart_times


restart_time = get_restart_times()


#restart_time = [datetime.time(hour=20, minute=10, second=0, tzinfo=tz)]
# @tasks.loop(hours = 6)


@tasks.loop(time=restart_time)
async def restart_loop():
    for server in SERVERS:
        if server.settings['do_restarts']:
            for restart_hour in server.settings['restart_pram'].keys():
                if restart_hour == int(datetime.datetime.now().hour):
                    await restart(server, restart_hour)


async def restart(server, restar_hour):
    restart_manager = Restart_manager.RestartManager(server)
    delay = await restart_manager.delay_before_restart()
    for i in range(5):
        await msg_to_chanel([server.settings['discord']['sebd']],
                            [f'!say  \n ! \n RESTART IN {delay // 60} MIN {delay % 60} SEK \n ! ',
                             f'!notify " RESTART IN {delay // 60} MIN {delay % 60} SEK " 5000 Red'])
        delay = delay // 2 + 1
        await asyncio.sleep(delay)
    await asyncio.sleep(delay)

    if server.settings['do_server_use_depatch_savefix']:
        await msg_to_chanel([server.settings['discord']['ingame_chat']],
                            ['Say admin that restart dont work with depatch'])
    else:
        await msg_to_chanel([server.settings['discord']['sebd']], ['!stop'])
        await asyncio.sleep(restart_manager.SAFE_SAVING_TIME)
    server.turn_off()
    try:
        restart_manager.world_manager.execute_commands(server.settings['restart_pram'][restar_hour])
    except:
        print('it often happends when SANDBOX_0_0_0.sbs dont exist')
        raise
    await server.turn_on(safe=True)


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
