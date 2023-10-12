import asyncio
import datetime
import time
import os

from pprint import pprint

from app.pkg.server_tools.tools import Server
from app.pkg.ui_tools.tools import MainWindow
from app.pkg.discord_tool.tools import SEDiscordBot

SERVERS = set()


async def main():
    main_window = MainWindow(SERVERS)

    main_window_coro = asyncio.create_task(main_window.run_window())

    await main_window_coro

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
